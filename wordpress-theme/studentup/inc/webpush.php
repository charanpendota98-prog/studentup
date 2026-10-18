<?php
/**
 * v163 — Real Web Push (VAPID).
 *
 * Telegram/WhatsApp share links unnayi, kani avi reader **maname** click
 * cheyyali. Web push veru: browser closed unna, phone lo direct notification
 * velthundi. Return traffic ki top sites #1 lever idi.
 *
 * Ee file chese pani:
 *  - subscription store (sonta table, `wp_options` kaadu — vela subscriptions
 *    autoload option lo pedithe prati page load slow avutundi),
 *  - REST: subscribe / unsubscribe (public, rate-limited) + list (auth only,
 *    bot ee endpoint nunchi subscriptions teesukoni push pampistundi),
 *  - prompt UI — **immediate ga adagam**. Chrome abusive-permission
 *    penalty ki adi ne karanam. Reader 2nd pageview leda oka click taruvata
 *    ne adugutundi, "No thanks" ante 30 rojulu malli adagadu.
 *
 * Push *pampadam* bot pani (`python run.py --push-send`), endukante VAPID
 * signing ki proper crypto library kavali.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'STUDENTUP_PUSH_TABLE', 'studentup_push_subs' );

/**
 * Subscriptions table (theme activate ayinappudu / version marinappudu).
 */
function studentup_push_install_table() {
	global $wpdb;
	$table   = $wpdb->prefix . STUDENTUP_PUSH_TABLE;
	$current = (string) get_option( 'su_push_db_version', '' );
	if ( '1' === $current ) {
		return;
	}
	require_once ABSPATH . 'wp-admin/includes/upgrade.php';
	$charset = $wpdb->get_charset_collate();
	$sql     = "CREATE TABLE {$table} (
		id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		endpoint varchar(500) NOT NULL,
		p256dh varchar(255) NOT NULL,
		auth varchar(255) NOT NULL,
		created datetime NOT NULL,
		PRIMARY KEY  (id),
		UNIQUE KEY endpoint (endpoint(191))
	) {$charset};";
	dbDelta( $sql );
	update_option( 'su_push_db_version', '1', false );
}
add_action( 'after_switch_theme', 'studentup_push_install_table' );
add_action( 'admin_init', 'studentup_push_install_table' );

/**
 * VAPID public key (bot `--push-keys` tho generate chesi ikkada pettali).
 *
 * @return string
 */
function studentup_push_public_key() {
	return trim( (string) get_option( 'studentup_push_public_key', '' ) );
}

/**
 * Push ON aa? Key lekapothe feature motham off — half-working prompt
 * chupinchi reader permission waste cheyyadam cheddha.
 *
 * @return bool
 */
function studentup_push_enabled() {
	return (bool) studentup_opt( 'webpush', '1' ) && '' !== studentup_push_public_key();
}

/**
 * REST routes.
 */
function studentup_push_routes() {
	register_rest_route(
		'studentup/v1',
		'/push-subscribe',
		array(
			'methods'             => 'POST',
			'permission_callback' => '__return_true',
			'callback'            => 'studentup_push_subscribe',
			'args'                => array(
				'endpoint' => array( 'required' => true, 'type' => 'string' ),
				'p256dh'   => array( 'required' => true, 'type' => 'string' ),
				'auth'     => array( 'required' => true, 'type' => 'string' ),
			),
		)
	);
	register_rest_route(
		'studentup/v1',
		'/push-subscribers',
		array(
			'methods'             => 'GET',
			// Bot application-password tho login avutundi; public ki list ivvam.
			'permission_callback' => function () {
				return current_user_can( 'edit_posts' );
			},
			'callback'            => 'studentup_push_list',
		)
	);
}
add_action( 'rest_api_init', 'studentup_push_routes' );

/**
 * Subscribe (public).
 *
 * @param WP_REST_Request $req request.
 * @return WP_REST_Response|WP_Error
 */
function studentup_push_subscribe( $req ) {
	if ( ! studentup_push_enabled() ) {
		return new WP_Error( 'su_push_off', 'Push off', array( 'status' => 403 ) );
	}
	global $wpdb;

	$endpoint = esc_url_raw( (string) $req->get_param( 'endpoint' ) );
	$p256dh   = sanitize_text_field( (string) $req->get_param( 'p256dh' ) );
	$auth     = sanitize_text_field( (string) $req->get_param( 'auth' ) );

	// Only real push services. Ee check lekapothe ee endpoint ni open
	// relay la vaadukovachu.
	$host = wp_parse_url( $endpoint, PHP_URL_HOST );
	$ok   = $host && (bool) preg_match(
		'~(\.googleapis\.com|\.mozilla\.com|\.mozaws\.net|\.windows\.com|\.apple\.com)$~i',
		$host
	);
	if ( ! $ok || strlen( $endpoint ) > 500 || '' === $p256dh || '' === $auth ) {
		return new WP_Error( 'su_push_bad', 'Bad subscription', array( 'status' => 400 ) );
	}
	// v1.9.147 (security review): public endpoint had no rate limit or table cap —
	// a script could insert unlimited rows (DB bloat + push-fanout cost).
	$ip  = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '0.0.0.0';
	$rl  = 'su_push_rl_' . substr( wp_hash( $ip ), 0, 24 );
	$hit = (int) get_transient( $rl );
	if ( $hit >= 5 ) {
		return new WP_Error( 'su_push_rate', 'Too many requests', array( 'status' => 429 ) );
	}
	set_transient( $rl, $hit + 1, 10 * MINUTE_IN_SECONDS );
	if ( strlen( $p256dh ) > 200 || strlen( $auth ) > 100 || ! preg_match( '#^https://#', $endpoint ) ) {
		return new WP_Error( 'su_push_bad', 'Bad subscription', array( 'status' => 400 ) );
	}
	$cap   = (int) apply_filters( 'studentup_push_max_subscribers', 200000 );
	$total = (int) get_transient( 'su_push_total' );
	if ( ! $total ) {
		$total = (int) $wpdb->get_var( 'SELECT COUNT(*) FROM ' . $wpdb->prefix . STUDENTUP_PUSH_TABLE ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery
		set_transient( 'su_push_total', max( 1, $total ), 5 * MINUTE_IN_SECONDS );
	}
	if ( $total >= $cap ) {
		return new WP_Error( 'su_push_full', 'Subscriber limit reached', array( 'status' => 503 ) );
	}

	$table = $wpdb->prefix . STUDENTUP_PUSH_TABLE;
	// phpcs:disable WordPress.DB.DirectDatabaseQuery
	$wpdb->query(
		$wpdb->prepare(
			"INSERT INTO {$table} (endpoint, p256dh, auth, created) VALUES (%s, %s, %s, %s)
			 ON DUPLICATE KEY UPDATE p256dh = VALUES(p256dh), auth = VALUES(auth)",
			$endpoint,
			$p256dh,
			$auth,
			current_time( 'mysql' )
		)
	);
	// phpcs:enable
	return rest_ensure_response( array( 'ok' => true ) );
}

/**
 * Subscriber list (auth only) — bot ee data tho push pampistundi.
 *
 * @return WP_REST_Response
 */
function studentup_push_list() {
	global $wpdb;
	$table = $wpdb->prefix . STUDENTUP_PUSH_TABLE;
	// phpcs:disable WordPress.DB.DirectDatabaseQuery
	$rows = $wpdb->get_results( "SELECT endpoint, p256dh, auth FROM {$table} LIMIT 20000", ARRAY_A );
	// phpcs:enable
	return rest_ensure_response( array( 'count' => count( (array) $rows ), 'subs' => $rows ) );
}

/**
 * Prompt UI — engagement taruvata ne.
 */
function studentup_push_prompt() {
	if ( is_admin() || ! studentup_push_enabled() ) {
		return;
	}
	$data = array(
		'key'  => studentup_push_public_key(),
		'rest' => esc_url_raw( rest_url( 'studentup/v1/push-subscribe' ) ),
		'sw'   => esc_url_raw( add_query_arg( 'studentup_sw', '1', home_url( '/' ) ) ),
		'icon' => function_exists( 'studentup_ui_icon' ) ? studentup_ui_icon( 'bell', 15 ) : '',
	);
	?>
	<script>
	(function () {
		var CFG = <?php echo wp_json_encode( $data ); ?>;
		if (!('serviceWorker' in navigator) || !('PushManager' in window)) { return; }
		if (Notification.permission === 'denied') { return; }

		var KEY = 'su-push-v1';
		var store = {};
		try { store = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { store = {}; }
		var muted = !!store.done || (store.snoozeUntil && Date.now() < store.snoozeUntil);   /* v305: bell tap ki auto-prompt kaadu, user intent → eppudaina */

		// Reader engage ayyaka ne adugutam: 2nd pageview, leda 25s + scroll.
		store.views = (store.views || 0) + 1;
		try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {}
		var engaged = store.views >= 2;

		function b64(base64String) {
			var pad = '='.repeat((4 - base64String.length % 4) % 4);
			var raw = atob((base64String + pad).replace(/-/g, '+').replace(/_/g, '/'));
			var out = new Uint8Array(raw.length);
			for (var i = 0; i < raw.length; i++) { out[i] = raw.charCodeAt(i); }
			return out;
		}

		function save(sub) {
			var j = sub.toJSON();
			return fetch(CFG.rest, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					endpoint: j.endpoint,
					p256dh: j.keys && j.keys.p256dh,
					auth: j.keys && j.keys.auth
				})
			});
		}

		function subscribe() {
			navigator.serviceWorker.register(CFG.sw).then(function (reg) {
				return reg.pushManager.subscribe({
					userVisibleOnly: true,
					applicationServerKey: b64(CFG.key)
				});
			}).then(save).then(function () {
				store.done = true;
				try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {}
				bar.remove();
			}).catch(function () { bar.remove(); });
		}

		var bar = null;
		function show(force) {
			if (bar || (!force && (!engaged || muted)) || store.done) { return; }
			bar = document.createElement('div');
			bar.className = 'su-push-bar';
			bar.innerHTML = '<span class="su-push-txt">' + CFG.icon + ' Kotha jobs &amp; results alerts kavala?</span>'
				+ '<button type="button" class="su-push-yes"><?php echo esc_html__( 'Yes, alert cheyandi', 'studentup' ); ?></button>'
				+ '<button type="button" class="su-push-no"><?php echo esc_html__( 'No thanks', 'studentup' ); ?></button>';   /* v305 FIX: PHP concat JS lo undedi → SyntaxError → bar eppudu kanipinchaledu */
			document.body.appendChild(bar);
			bar.querySelector('.su-push-yes').addEventListener('click', subscribe);
			bar.querySelector('.su-push-no').addEventListener('click', function () {
				store.snoozeUntil = Date.now() + 30 * 24 * 3600 * 1000;
				try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {}
				bar.remove();
			});
		}

		if (engaged && !muted) { window.setTimeout(show, 4000); }
		/* v305: "Alerts" bell (mobile menu / bottom nav / mega) → subscribe avvakapothe ikkade opt-in; already ON ante Telegram/WhatsApp channel ki */
		var bells = document.querySelectorAll('[data-su-alerts]');
		for (var bi = 0; bi < bells.length; bi++) {
			bells[bi].addEventListener('click', function (ev) {
				if (store.done) { return; }
				ev.preventDefault();
				show(true);
				if (bar) { bar.scrollIntoView && bar.scrollIntoView({ block: 'end' }); }
			});
		}
	})();
	</script>
	<?php
}
add_action( 'wp_footer', 'studentup_push_prompt', 30 );

/* =====================================================================
 * v305 AUTO PUSH ENGINE — post publish ayite automatic ga push.
 *
 *  publish → studentup_push_enqueue_on_publish() → queue (option)
 *          → bot `run.py --push-auto` (approval-poll lo prathi 5 min + publish taruvata ventane)
 *            GET  /studentup/v1/push-queue       (ready items — quiet hours / daily cap already apply)
 *            POST /studentup/v1/push-queue/ack   (sent / expired / failed stats → log, expired subs delete)
 *
 *  Rules (owner: no spam, no fake):
 *   - kotha publish matrame (update/edit ki push ledu), 48h kante paata posts kaadu (bulk import safety)
 *   - daily cap (default 3) — Breaking + Results/Hall-ticket "high" items cap ni bypass chestayi
 *   - quiet hours 22:00–07:00 IST hold (high items bypass)
 *   - same title (normalized) 7 rojulu lo malli push kaadu
 *   - body real meta nunchi matrame (vacancies · qualification · last date); data lekapote excerpt
 * ===================================================================== */

/**
 * Queue (option, autoload off).
 *
 * @return array
 */
function studentup_push_queue_get() {
	$q = get_option( 'studentup_push_queue', array() );
	return is_array( $q ) ? array_values( $q ) : array();
}

/**
 * @param array $q queue.
 */
function studentup_push_queue_set( $q ) {
	$q = array_slice( array_values( (array) $q ), -50 );
	if ( false === get_option( 'studentup_push_queue', false ) ) {
		add_option( 'studentup_push_queue', $q, '', 'no' );
		return;
	}
	update_option( 'studentup_push_queue', $q, 'no' );
}

/**
 * Post kind: breaking / result / job / other — priority + icon decide cheyyadaniki.
 *
 * @param int $post_id post.
 * @return string
 */
function studentup_push_kind( $post_id ) {
	$slugs = array();
	foreach ( (array) get_the_category( $post_id ) as $c ) {
		$slugs[] = $c->slug;
		$anc     = get_ancestors( $c->term_id, 'category' );
		foreach ( $anc as $a ) {
			$t = get_term( $a, 'category' );
			if ( $t && ! is_wp_error( $t ) ) {
				$slugs[] = $t->slug;
			}
		}
	}
	$s = implode( ' ', $slugs );
	if ( false !== strpos( $s, 'breaking' ) ) {
		return 'breaking';
	}
	if ( preg_match( '/result|hall-?ticket|admit|answer-?key/', $s ) ) {
		return 'result';
	}
	if ( preg_match( '/job|recruit|notification|walk-?in|scholarship|admission/', $s ) ) {
		return 'job';
	}
	return 'other';
}

/**
 * Notification body — real meta matrame; lekapote excerpt (hint/fake text ledu).
 *
 * @param int $post_id post.
 * @return string
 */
function studentup_push_body( $post_id ) {
	$bits = array();
	$vac  = trim( (string) get_post_meta( $post_id, 'studentup_vacancies', true ) );
	$qual = trim( (string) get_post_meta( $post_id, 'studentup_qual', true ) );
	$last = trim( (string) get_post_meta( $post_id, 'studentup_last_date', true ) );
	if ( $vac && preg_match( '/^[\d,]+$/', $vac ) ) {
		$bits[] = $vac . ' posts';
	}
	if ( $qual && function_exists( 'studentup_qual_pretty' ) ) {
		$bits[] = studentup_qual_pretty( $qual );
	}
	if ( $last && preg_match( '/^\d{4}-\d{2}-\d{2}$/', $last ) ) {
		$ts = strtotime( $last . ' 12:00:00' );
		if ( $ts && $ts >= strtotime( 'today' ) ) {
			$bits[] = 'Last date ' . wp_date( 'd M', $ts );
		}
	}
	if ( $bits ) {
		return implode( ' · ', $bits );
	}
	$ex = wp_strip_all_tags( get_the_excerpt( $post_id ) );
	return mb_substr( trim( preg_replace( '/\s+/', ' ', $ex ) ), 0, 110 );
}

/**
 * Publish hook.
 *
 * @param string  $new  new status.
 * @param string  $old  old status.
 * @param WP_Post $post post.
 */
function studentup_push_enqueue_on_publish( $new, $old, $post ) {
	if ( 'publish' !== $new || 'publish' === $old || ! $post instanceof WP_Post || 'post' !== $post->post_type ) {
		return;
	}
	if ( ! studentup_push_enabled() || ! studentup_opt( 'push_auto', '1' ) ) {
		return;
	}
	if ( ( time() - get_post_time( 'U', true, $post ) ) > 2 * DAY_IN_SECONDS ) {
		return; // bulk import / backdated — push vaddu.
	}
	$title = html_entity_decode( wp_strip_all_tags( get_the_title( $post ) ), ENT_QUOTES, 'UTF-8' );
	$norm  = preg_replace( '/[^a-z0-9\p{Telugu}]+/u', '', mb_strtolower( $title ) );
	$seen  = get_option( 'studentup_push_seen', array() );
	$seen  = is_array( $seen ) ? $seen : array();
	$now   = time();
	foreach ( $seen as $k => $t ) {
		if ( $now - (int) $t > 7 * DAY_IN_SECONDS ) {
			unset( $seen[ $k ] );
		}
	}
	if ( isset( $seen[ $norm ] ) ) {
		return; // same title 7 days lo already pushed/queued.
	}
	$seen[ $norm ] = $now;
	update_option( 'studentup_push_seen', $seen, 'no' );

	// Meta/featured image REST create lo post insert TARUVATA save avutayi → ikkada id matrame;
	// title/body/image GET time lo fresh ga hydrate (studentup_push_hydrate()).
	$q   = studentup_push_queue_get();
	$q[] = array( 'id' => (int) $post->ID, 'ts' => $now );
	studentup_push_queue_set( $q );
}
add_action( 'transition_post_status', 'studentup_push_enqueue_on_publish', 20, 3 );

/**
 * Queue item → full payload (fresh title/meta/image at send time).
 *
 * @param array $it item.
 * @return array|null null = post inka publish lo ledu (deleted/unpublished → drop).
 */
function studentup_push_hydrate( $it ) {
	$pid  = (int) $it['id'];
	$post = get_post( $pid );
	if ( ! $post || 'publish' !== $post->post_status ) {
		return null;
	}
	$kind  = studentup_push_kind( $pid );
	$image = get_the_post_thumbnail_url( $pid, 'large' );
	$icon  = get_site_icon_url( 192 );
	$title = html_entity_decode( wp_strip_all_tags( get_the_title( $post ) ), ENT_QUOTES, 'UTF-8' );
	return array(
		'id'    => $pid,
		'title' => mb_substr( $title, 0, 80 ),
		'body'  => studentup_push_body( $pid ),
		'url'   => add_query_arg( array( 'utm_source' => 'push', 'utm_medium' => 'notification' ), get_permalink( $post ) ),
		'icon'  => $icon ? $icon : '',
		'image' => $image ? $image : '',
		'tag'   => 'su-' . $pid,
		'kind'  => $kind,
		'high'  => in_array( $kind, array( 'breaking', 'result' ), true ),
		'ts'    => (int) $it['ts'],
	);
}

/**
 * Ippudu pampocha? (IST quiet hours 22:00–07:00; high items bypass.)
 *
 * @return bool
 */
function studentup_push_quiet_now() {
	if ( ! studentup_opt( 'push_quiet', '1' ) ) {
		return false;
	}
	$h = (int) wp_date( 'G' );
	return ( $h >= 22 || $h < 7 );
}

/**
 * Daily sent counter key.
 *
 * @return string
 */
function studentup_push_day_key() {
	return 'su_push_sent_' . wp_date( 'Ymd' );
}

/**
 * GET push-queue — bot ki ready items.
 *
 * @return WP_REST_Response
 */
function studentup_push_queue_rest() {
	global $wpdb;
	$q      = studentup_push_queue_get();
	$cap    = max( 0, (int) studentup_opt( 'push_daily_cap', '3' ) );
	$sent   = (int) get_transient( studentup_push_day_key() );
	$quiet  = studentup_push_quiet_now();
	$ready  = array();
	$held   = 0;
	$budget = $cap > 0 ? max( 0, $cap - $sent ) : PHP_INT_MAX;
	$drop   = array();
	foreach ( $q as $it ) {
		$it = studentup_push_hydrate( $it );
		if ( ! $it ) {
			$drop[] = 1;
			continue;
		}
		$high = ! empty( $it['high'] );
		if ( ( $quiet && ! $high ) || ( ! $high && $budget <= 0 ) ) {
			$held++;
			continue;
		}
		if ( ! $high ) {
			$budget--;
		}
		$ready[] = $it;
	}
	if ( $drop ) { // unpublished/deleted posts → queue nunchi teeseyi
		studentup_push_queue_set( array_values( array_filter( $q, function ( $x ) {
			$p = get_post( (int) $x['id'] );
			return $p && 'publish' === $p->post_status;
		} ) ) );
	}
	$table = $wpdb->prefix . STUDENTUP_PUSH_TABLE;
	// phpcs:disable WordPress.DB.DirectDatabaseQuery
	$subs = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$table}" );
	// phpcs:enable
	return rest_ensure_response(
		array(
			'ready'       => $ready,
			'held'        => $held,
			'quiet'       => $quiet,
			'sent_today'  => $sent,
			'daily_cap'   => $cap,
			'subscribers' => $subs,
			'public_key'  => studentup_push_public_key(),
		)
	);
}

/**
 * POST push-queue/ack — {ids:[], sent:n, expired:[endpoints], failed:n, dry:bool}
 *
 * @param WP_REST_Request $req request.
 * @return WP_REST_Response
 */
function studentup_push_queue_ack( $req ) {
	global $wpdb;
	$ids     = array_map( 'intval', (array) $req->get_param( 'ids' ) );
	$sent    = (int) $req->get_param( 'sent' );
	$failed  = (int) $req->get_param( 'failed' );
	$expired = array_filter( array_map( 'esc_url_raw', (array) $req->get_param( 'expired' ) ) );
	$dry     = (bool) $req->get_param( 'dry' );

	if ( $ids && ! $dry ) {
		$q = array_values( array_filter( studentup_push_queue_get(), function ( $it ) use ( $ids ) {
			return ! in_array( (int) $it['id'], $ids, true );
		} ) );
		studentup_push_queue_set( $q );
		if ( $sent > 0 ) { // subscribers levu ante cap count avvadu
			$key = studentup_push_day_key();
			set_transient( $key, (int) get_transient( $key ) + count( $ids ), DAY_IN_SECONDS + HOUR_IN_SECONDS );
		}
		$log   = get_option( 'studentup_push_log', array() );
		$log   = is_array( $log ) ? $log : array();
		$log[] = array( 'ts' => time(), 'ids' => $ids, 'sent' => $sent, 'failed' => $failed, 'expired' => count( $expired ) );
		update_option( 'studentup_push_log', array_slice( $log, -30 ), 'no' );
	}
	$removed = 0;
	if ( $expired ) {
		$table = $wpdb->prefix . STUDENTUP_PUSH_TABLE;
		foreach ( $expired as $ep ) {
			// phpcs:disable WordPress.DB.DirectDatabaseQuery
			$removed += (int) $wpdb->delete( $table, array( 'endpoint' => $ep ), array( '%s' ) );
			// phpcs:enable
		}
	}
	return rest_ensure_response( array( 'ok' => true, 'removed_expired' => $removed, 'queue' => count( studentup_push_queue_get() ) ) );
}

/**
 * Routes.
 */
function studentup_push_queue_routes() {
	$auth = function () {
		return current_user_can( 'edit_posts' );
	};
	register_rest_route( 'studentup/v1', '/push-queue', array(
		'methods'             => 'GET',
		'permission_callback' => $auth,
		'callback'            => 'studentup_push_queue_rest',
	) );
	register_rest_route( 'studentup/v1', '/push-queue/ack', array(
		'methods'             => 'POST',
		'permission_callback' => $auth,
		'callback'            => 'studentup_push_queue_ack',
	) );
}
add_action( 'rest_api_init', 'studentup_push_queue_routes' );

/**
 * Admin status line (StudentUp settings page lo matrame).
 */
function studentup_push_admin_status() {
	if ( ! function_exists( 'get_current_screen' ) ) {
		return;
	}
	$scr = get_current_screen();
	if ( ! $scr || false === strpos( (string) $scr->id, 'studentup' ) ) {
		return;
	}
	global $wpdb;
	$table = $wpdb->prefix . STUDENTUP_PUSH_TABLE;
	// phpcs:disable WordPress.DB.DirectDatabaseQuery
	$subs = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$table}" );
	// phpcs:enable
	$q    = count( studentup_push_queue_get() );
	$log  = get_option( 'studentup_push_log', array() );
	$last = is_array( $log ) && $log ? end( $log ) : null;
	$msg  = sprintf(
		'🔔 Push: %s · subscribers <b>%d</b> · queue <b>%d</b> · today sent <b>%d</b>/%s%s',
		studentup_push_enabled() ? 'ON' : '<b>OFF</b> (VAPID public key pettandi — <code>python run.py --push-keys</code>)',
		$subs,
		$q,
		(int) get_transient( studentup_push_day_key() ),
		(int) studentup_opt( 'push_daily_cap', '3' ),
		$last ? ' · last send ' . esc_html( wp_date( 'd M H:i', (int) $last['ts'] ) ) . ' (' . (int) $last['sent'] . ' delivered)' : ''
	);
	echo '<div class="notice notice-info"><p>' . wp_kses( $msg, array( 'b' => array(), 'code' => array() ) ) . '</p></div>';
}
add_action( 'admin_notices', 'studentup_push_admin_status' );
