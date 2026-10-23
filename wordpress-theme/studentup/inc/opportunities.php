<?php
/**
 * StudentUp Active Opportunities Board.
 *
 * The board is a live view over published posts. It never deletes article
 * URLs; it simply hides a notice from the active list after its verified
 * studentup_last_date has passed. Missing dates remain visible with "Not
 * announced" rather than receiving a guessed deadline.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function studentup_opportunity_sections() {
	return array(
		'ts'          => array( 'label' => 'TS Govt Jobs', 'icon' => 'bank' ),
		'ap'          => array( 'label' => 'AP Govt Jobs', 'icon' => 'bank' ),
		'central'     => array( 'label' => 'Central Govt Jobs', 'icon' => 'flag' ),
		'walkin'      => array( 'label' => 'Walk-in Jobs', 'icon' => 'walk' ),
		'outsourcing' => array( 'label' => 'Outsourcing & Contract Jobs', 'icon' => 'person' ),
		'job-melas'   => array( 'label' => 'Job Melas & Job Fairs', 'icon' => 'person' ),
		'software'    => array( 'label' => 'Software Jobs', 'icon' => 'laptop' ),
		'private'     => array( 'label' => 'Private Jobs', 'icon' => 'building' ),
		'scholarships'=> array( 'label' => 'Scholarships', 'icon' => 'school' ),
		'results'     => array( 'label' => 'Results', 'icon' => 'doc' ),
		'hall-tickets' => array( 'label' => 'Hall Tickets', 'icon' => 'ticket' ),
		'current-affairs' => array( 'label' => 'Daily Current Affairs', 'icon' => 'news' ),
	);
}

function studentup_opportunity_last_date( $post_id ) {
	$iso = trim( (string) get_post_meta( $post_id, 'studentup_last_date', true ) );
	return preg_match( '/^20\d{2}-\d{2}-\d{2}$/', $iso ) ? $iso : '';
}

function studentup_opportunity_is_expired( $last_date ) {
	if ( '' === $last_date ) {
		return false; // Unknown is not the same as expired.
	}
	$stamp = strtotime( $last_date . ' 23:59:59' );
	return $stamp && $stamp < current_time( 'timestamp' ); // phpcs:ignore WordPress.DateTime.CurrentTimeTimestamp
}

function studentup_opportunity_days_left( $last_date ) {
	if ( '' === $last_date ) {
		return null;
	}
	$end   = strtotime( $last_date . ' 23:59:59' );
	$today = current_time( 'timestamp' ); // phpcs:ignore WordPress.DateTime.CurrentTimeTimestamp
	return (int) floor( ( $end - $today ) / DAY_IN_SECONDS );
}

/**
 * 1.9.163: is this URL an OFFICIAL organisation page (never a news publisher)?
 * Bot stores the publisher it rewrote from in studentup_source_url; that must
 * never be labelled "Official". Official = government/education TLDs, or the
 * same host as the verified organisation URL (studentup_org_url) / apply URL.
 */
function studentup_is_official_url( $url, $post_id = 0 ) {
	$host = strtolower( (string) wp_parse_url( (string) $url, PHP_URL_HOST ) );
	if ( '' === $host ) {
		return false;
	}
	$host = preg_replace( '/^www\./', '', $host );
	if ( preg_match( '/\.(gov|nic|ac|edu|res|mil)\.in$|\.gov$|\.edu$|\.ac\.[a-z]{2}$|cgg\.gov\.in$|apcfss\.in$|\.org\.in$/', $host ) ) {
		return true;
	}
	foreach ( array( 'studentup_org_url', 'studentup_apply_url' ) as $k ) {
		$u = (string) get_post_meta( (int) $post_id, $k, true );
		$h = preg_replace( '/^www\./', '', strtolower( (string) wp_parse_url( $u, PHP_URL_HOST ) ) );
		if ( '' !== $h && ( $h === $host || substr( $host, -strlen( '.' . $h ) ) === '.' . $h || substr( $h, -strlen( '.' . $host ) ) === '.' . $host ) ) {
			return true;
		}
	}
	return (bool) apply_filters( 'studentup_is_official_url', false, $url, $host, $post_id );
}

function studentup_source_verification_notice( $post_id = 0 ) {
	// 1.9.163 AUDIT FIX: this line used to print "Source verification · Open
	// official source" in English and LINKED THE PUBLISHER (news18/sakshi/HT)
	// stored in studentup_source_url on every bot post — owner rule v340: never
	// show source details on posts. Now: Telugu trust line, links ONLY the
	// verified official organisation site (studentup_org_url); publisher URL is
	// never rendered. Nothing official → nothing rendered.
	$post_id = $post_id ? (int) $post_id : (int) get_the_ID();
	$org_url = trim( (string) get_post_meta( $post_id, 'studentup_org_url', true ) );
	$checked = trim( (string) get_post_meta( $post_id, 'studentup_source_checked', true ) );
	if ( ! preg_match( '#^https?://#i', $org_url ) || ! filter_var( $org_url, FILTER_VALIDATE_URL ) ) { // display-only check (wp_http_validate_url does DNS)
		return '';
	}
	$checked_stamp = preg_match( '/^20\d{2}-\d{2}-\d{2}$/', $checked ) ? strtotime( $checked . ' 12:00:00' ) : false;
	$host          = preg_replace( '#^www\.#', '', (string) wp_parse_url( $org_url, PHP_URL_HOST ) );
	$html          = '<div class="su-source-trust" role="note">' . studentup_ui_icon( 'check', 13 ) . ' '
		. '<a href="' . esc_url( $org_url ) . '" target="_blank" rel="noopener noreferrer">' . esc_html( $host ) . '</a> '
		. esc_html__( 'అధికారిక నోటిఫికేషన్ ఆధారంగా', 'studentup' );
	if ( $checked_stamp ) {
		$html .= ' · ' . esc_html__( 'చివరిగా సరిచూసినది', 'studentup' ) . ': ' . esc_html( function_exists( 'studentup_ui_te_date' ) ? studentup_ui_te_date( wp_date( 'j F Y', $checked_stamp ), 'j F Y' ) : wp_date( 'j F Y', $checked_stamp ) );
	}
	return $html . '</div>';
}

/**
 * v184: deadline cheppakapoyina chala puratana post ni board nunchi teestam.
 *
 * Govt notices ki last date cheppakapovadam common (results / admit card).
 * Kaani 120+ rojula puratana notice "active" ga chupinchadam reader ni confuse
 * chestundi. Filter tho marchachu: add_filter( 'studentup_opportunity_stale_days',
 * fn() => 0 );  (0 = off)
 */
function studentup_opportunity_stale_days() {
	$days = (int) apply_filters( 'studentup_opportunity_stale_days', 120 );
	return max( 0, $days );
}

function studentup_opportunity_is_stale( $post ) {
	$stale = studentup_opportunity_stale_days();
	if ( $stale < 1 ) {
		return false;
	}
	if ( '' !== studentup_opportunity_last_date( $post->ID ) ) {
		return false; // deadline unte adi ne decide chestundi.
	}
	$published = strtotime( (string) $post->post_date_gmt . ' UTC' );
	if ( ! $published ) {
		return false; // date teliyadu → guess cheyyadu.
	}
	return ( time() - $published ) > ( $stale * DAY_IN_SECONDS );
}

/**
 * v184: same recruitment ki kotha post vaste puratana di board nunchi teesestam.
 *
 * Bot `title_key()` (autoblog/opportunity_digest.py) tho same rules: SEO
 * suffixes + year + punctuation teesi first 60 chars; chinna title (<10) ki key
 * ledu (collision risk). Telugu titles ki key raadu — adi kuda safe (dedupe ledu).
 */
function studentup_opportunity_title_key( $title ) {
	$text = strtolower( wp_strip_all_tags( (string) $title ) );
	$text = preg_replace( '/\b20\d{2}\b/', ' ', $text );
	$text = preg_replace(
		'/\b(?:notification|notifications|recruitment|apply online|application|' .
		'complete details|complete guide|latest update|official notification|' .
		'result|results|hall ticket|admit card|merit list|answer key|' .
		'revised|extended|update|job|jobs|posts?|vacancy|vacancies)\b/',
		' ', $text );
	$text = preg_replace( '/[^a-z0-9]+/', '', $text );
	return strlen( $text ) >= 10 ? substr( $text, 0, 60 ) : '';
}

/**
 * v1.9.173: evergreen guide / preparation-plan posts (bot `--calendar`) are
 * useful articles but NOT openings — they must not sit in the Latest Jobs
 * board or job tickers next to real notifications (reader clicks expecting
 * a vacancy and finds a study plan → trust loss). Title-only test, no guess.
 */
function studentup_is_guide_post( $post_id ) {
	$title = mb_strtolower( wp_strip_all_tags( (string) get_the_title( $post_id ) ) );
	if ( '' === $title ) {
		return false;
	}
	$markers = array(
		'ప్రిపరేషన్', 'గైడ్', 'ఎలా చేయాలి', 'కెరీర్ ఆప్షన్స్', 'స్టడీ ప్లాన్', 'సిలబస్, పుస్తకాలు',
		'preparation plan', 'preparation guide', 'preparation strategy', 'study plan',
		'complete guide', 'how to apply', 'career options', 'step by step', 'స్టెప్ బై స్టెప్',
	);
	foreach ( $markers as $m ) {
		if ( false !== mb_strpos( $title, mb_strtolower( $m ) ) ) {
			return true;
		}
	}
	return false;
}

function studentup_opportunity_category_slugs( $post_id ) {
	return array_map( 'sanitize_key', wp_list_pluck( (array) get_the_category( $post_id ), 'slug' ) );
}

function studentup_opportunity_section_for_post( $post_id ) {
	if ( studentup_is_guide_post( $post_id ) ) {
		return ''; // v1.9.173: guides are articles, not openings.
	}
	$cats  = studentup_opportunity_category_slugs( $post_id );
	$title = mb_strtolower( wp_strip_all_tags( get_the_title( $post_id ) . ' ' . get_post_field( 'post_content', $post_id ) ) );
	$blob  = $title . ' ' . implode( ' ', $cats );
	$has   = static function ( $needles ) use ( $blob ) {
		foreach ( $needles as $needle ) {
			if ( false !== mb_strpos( $blob, mb_strtolower( $needle ) ) ) {
				return true;
			}
		}
		return false;
	};

	// A mela is a useful sub-section even when older posts are stored under
	// Walkin Jobs. Check this before the broader walk-in match.
	if ( $has( array( 'job mela', 'job fair', 'mega job fair', 'employment fair', 'mela' ) ) ) {
		return 'job-melas';
	}
	$aliases = array(
		'ts'           => array( 'ts-jobs', 'ts-govt-jobs', 'telangana-govt-jobs' ),
		'ap'           => array( 'ap-jobs', 'ap-govt-jobs', 'andhra-pradesh-govt-jobs' ),
		'central'      => array( 'central', 'central-jobs', 'central-govt-jobs' ),
		'walkin'       => array( 'walkin', 'walkin-jobs', 'walk-in-jobs' ),
		'outsourcing'  => array( 'outsourcing', 'outsourcing-jobs', 'contract', 'contract-basis' ),
		'software'     => array( 'software', 'software-jobs' ),
		'private'      => array( 'private', 'private-jobs' ),
		'scholarships' => array( 'scholarship', 'scholarships' ),
		'results'      => array( 'result', 'results' ),
		'hall-tickets' => array( 'hall-ticket', 'hall-tickets', 'hallticket' ),
		'current-affairs' => array( 'current', 'current-affairs', 'daily-current-affairs' ),
	);
	foreach ( $aliases as $key => $values ) {
		if ( array_intersect( $cats, $values ) ) {
			return $key;
		}
	}
	// Legacy category repair view: a misfiled old article still lands in the
	// reader's expected section without silently changing its taxonomy.
	if ( $has( array( 'scholarship', 'fellowship', 'nsp', 'epass', 'e-pass' ) ) ) {
		return 'scholarships';
	}
	if ( $has( array_merge( array( 'result', 'scorecard', 'answer key', 'merit list' ), studentup_topic_keywords( 'result' ) ) ) ) {
		return 'results';
	}
	if ( $has( array_merge( array( 'hall ticket', 'admit card', 'call letter' ), studentup_topic_keywords( 'hallticket' ) ) ) ) {
		return 'hall-tickets';
	}
	if ( $has( array( 'current affairs', 'daily current', 'daily gk', 'daily news' ) ) ) {
		return 'current-affairs';
	}
	// v183: outsourcing/contract posts (pipeline lo 'Outsourcing Jobs' category) —
	// idi lekapote aa posts board lo e section lo kanipinchavu.
	if ( $has( array( 'outsourcing', 'contract basis', 'contractual', 'outsourced',
		'guest faculty', 'honorarium' ) ) ) {
		return 'outsourcing';
	}
	if ( $has( array( 'walk-in', 'walk in', 'walkin', 'direct interview' ) ) ) {
		return 'walkin';
	}
	if ( $has( array( 'software', 'developer', 'full stack', 'data analyst', 'devops', 'it job' ) ) ) {
		return 'software';
	}
	if ( $has( array( 'tcs', 'infosys', 'wipro', 'private job', 'off campus', 'mnc' ) ) ) {
		return 'private';
	}
	if ( $has( array( 'tspsc', 'tgpsc', 'telangana', 'ts police', 'gurukul' ) ) ) {
		return 'ts';
	}
	if ( $has( array( 'appsc', 'andhra pradesh', 'ap police', 'apsrtc', 'ap dsc' ) ) ) {
		return 'ap';
	}
	if ( $has( array( 'ssc', 'upsc', 'rrb', 'railway', 'ibps', 'sbi', 'army', 'navy' ) ) ) {
		return 'central';
	}
	return '';
}

function studentup_opportunity_board_posts( $limit = 180 ) {
	$q = new WP_Query(
		array(
			'post_type'           => 'post',
			'post_status'         => 'publish',
			'posts_per_page'      => max( 20, (int) $limit ),
			'orderby'             => 'date',
			'order'               => 'DESC',
			'ignore_sticky_posts' => true,
			'no_found_rows'       => true,
		)
	);
	$out = array();
	foreach ( $q->posts as $post ) {
		$last = studentup_opportunity_last_date( $post->ID );
		if ( studentup_opportunity_is_expired( $last ) ) {
			continue; // last date ayyipoyindi → board nunchi out.
		}
		if ( studentup_opportunity_is_stale( $post ) ) {
			continue; // v184: deadline lekunda 120+ rojula puratana → out.
		}
		$section = studentup_opportunity_section_for_post( $post->ID );
		if ( '' === $section ) {
			continue;
		}
		$apply_url = trim( (string) get_post_meta( $post->ID, 'studentup_apply_url', true ) );
		if ( ! wp_http_validate_url( $apply_url ) ) {
			$apply_url = '';
		}
		$source_url = trim( (string) get_post_meta( $post->ID, 'studentup_source_url', true ) );
		if ( ! wp_http_validate_url( $source_url ) ) {
			$source_url = '';
		}
		$source_checked = trim( (string) get_post_meta( $post->ID, 'studentup_source_checked', true ) );
		if ( ! preg_match( '/^20\d{2}-\d{2}-\d{2}$/', $source_checked ) ) {
			$source_checked = '';
		}
		$out[] = array(
			'id'         => (int) $post->ID,
			'title'      => get_the_title( $post->ID ),
			'link'       => get_permalink( $post->ID ),
			'last_date'  => $last,
			'days_left'  => studentup_opportunity_days_left( $last ),
			'section'    => $section,
			'qualification' => trim( (string) get_post_meta( $post->ID, 'studentup_qual', true ) ),
			'salary'     => trim( (string) get_post_meta( $post->ID, 'studentup_salary', true ) ),
			'vacancies'  => trim( (string) get_post_meta( $post->ID, 'studentup_vacancies', true ) ),
			'apply_url'  => $apply_url,
			'source_url' => $source_url,
			'source_checked' => $source_checked,
			'date'       => get_the_date( 'c', $post->ID ),
			'updated'    => get_the_modified_date( 'c', $post->ID ),
			'thumbnail'  => get_the_post_thumbnail_url( $post->ID, 'studentup-card' ),
		);
	}
	// v184: same recruitment ki kotha post vaste puratana di teesestam
	// (newest wins; okate section + okate title key).
	$by_key = array();
	$deduped = array();
	foreach ( $out as $row ) {
		$key = $row['section'] . '|' . studentup_opportunity_title_key( $row['title'] );
		if ( '|' === substr( $key, -1 ) ) {
			$deduped[] = $row;
			continue;
		}
		if ( ! isset( $by_key[ $key ] ) ) {
			$by_key[ $key ] = count( $deduped );
			$deduped[] = $row;
			continue;
		}
		$idx = $by_key[ $key ];
		if ( strtotime( $row['date'] ) > strtotime( $deduped[ $idx ]['date'] ) ) {
			$deduped[ $idx ] = $row;
		}
	}
	$out = $deduped;
	// Closing dates are more useful at the top; undated posts follow newest-first.
	usort(
		$out,
		static function ( $a, $b ) {
			$ad = null === $a['days_left'] ? 999999 : (int) $a['days_left'];
			$bd = null === $b['days_left'] ? 999999 : (int) $b['days_left'];
			if ( $ad !== $bd ) {
				return $ad <=> $bd;
			}
			return strcmp( (string) $b['date'], (string) $a['date'] );
		}
	);
	return $out;
}

function studentup_opportunity_board_url() {
	return home_url( '/latest-jobs/' );
}

function studentup_opportunity_render_card( $row ) {
	$days       = $row['days_left'];
	$days_value = null === $days ? 'unknown' : (string) $days;
	$updated    = ! empty( $row['updated'] ) ? strtotime( $row['updated'] ) : false;
	?>
	<article class="su-op-card" data-su-op-card data-su-op-title="<?php echo esc_attr( mb_strtolower( wp_strip_all_tags( $row['title'] ) ) ); ?>" data-su-op-section="<?php echo esc_attr( $row['section'] ); ?>" data-su-op-qual="<?php echo esc_attr( mb_strtolower( (string) $row['qualification'] ) ); ?>" data-su-op-days="<?php echo esc_attr( $days_value ); ?>">
		<div class="su-op-card-copy">
			<h3><a href="<?php echo esc_url( $row['link'] ); ?>"><?php echo esc_html( $row['title'] ); ?></a></h3>
			<?php if ( ! empty( $row['qualification'] ) ) : ?>
				<p class="su-op-qual"><?php echo studentup_ui_icon( 'school', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php echo esc_html( studentup_qual_pretty( $row['qualification'] ) ); ?></p>
			<?php endif; ?>
			<?php if ( ! empty( $row['salary'] ) || ! empty( $row['vacancies'] ) ) : ?>
				<p class="su-op-facts">
					<?php if ( ! empty( $row['vacancies'] ) ) : ?>
						<span class="su-op-fact"><?php echo studentup_ui_icon( 'work', 12 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php echo esc_html( $row['vacancies'] ); ?> posts</span>
					<?php endif; ?>
					<?php if ( ! empty( $row['salary'] ) ) : ?>
						<span class="su-op-fact su-op-fact-pay"><?php echo studentup_ui_icon( 'wallet', 12 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php echo esc_html( $row['salary'] ); ?></span>
					<?php endif; ?>
				</p>
			<?php endif; ?>
			<?php if ( '' !== $row['last_date'] ) : ?>
				<?php $date_class = 'su-op-date' . ( ( null !== $days && $days <= 7 ) ? ' is-soon' : '' ); ?>
				<p class="<?php echo esc_attr( $date_class ); ?>">
					<?php echo studentup_ui_icon( 'calendar', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Last date:', 'studentup' ); ?> <strong><?php echo esc_html( wp_date( 'd M Y', strtotime( $row['last_date'] . ' 12:00:00' ) ) ); ?></strong>
					<?php if ( null !== $days ) : ?>
						<span><?php echo esc_html( 0 === $days ? __( 'Last date today', 'studentup' ) : sprintf( _n( '%s Day Left', '%s Days Left', $days, 'studentup' ), number_format_i18n( $days ) ) ); ?></span>
					<?php endif; ?>
				</p>
			<?php endif; // 1.9.169: no date → no row (owner rule: missing data is not rendered; "Not announced" read as a fact on live). ?>
			<?php if ( $updated ) : ?>
				<p class="su-op-updated"><?php esc_html_e( 'Updated', 'studentup' ); ?> <?php echo esc_html( wp_date( 'd M Y', $updated ) ); ?></p>
			<?php endif; ?>
			<?php if ( ! empty( $row['source_url'] ) ) : ?>
				<p class="su-op-source"><?php echo studentup_ui_icon( 'check', 12 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Source checked', 'studentup' ); ?><?php echo ! empty( $row['source_checked'] ) ? ' ' . esc_html( wp_date( 'd M Y', strtotime( $row['source_checked'] . ' 12:00:00' ) ) ) : ''; ?> · <a href="<?php echo esc_url( $row['source_url'] ); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html__( 'Official source', 'studentup' ); ?></a></p>
			<?php endif; ?>
		</div>
		<div class="su-op-actions">
			<a class="su-op-open" href="<?php echo esc_url( $row['link'] ); ?>" aria-label="<?php echo esc_attr( __( 'Details', 'studentup' ) . ' — ' . $row['title'] ); ?>"><?php esc_html_e( 'Details', 'studentup' ); ?>&nbsp;→</a>
			<?php if ( ! empty( $row['apply_url'] ) ) : ?>
				<a class="su-op-apply" href="<?php echo esc_url( $row['apply_url'] ); ?>" target="_blank" rel="noopener noreferrer" aria-label="<?php echo esc_attr__( 'Apply Online (Official)', 'studentup' ); ?> — <?php echo esc_attr( $row['title'] ); ?>"><?php esc_html_e( 'Official Apply', 'studentup' ); ?></a>
			<?php endif; ?>
			<?php if ( function_exists( 'studentup_save_button' ) ) : ?>
				<?php echo wp_kses_post( studentup_save_button( $row['id'], 'su-save-opportunity' ) ); ?>
			<?php endif; ?>
			<?php if ( function_exists( 'studentup_tool_buttons' ) ) : ?>
				<?php echo wp_kses_post( studentup_tool_buttons( $row['id'], 'card' ) ); ?>
			<?php endif; ?>
		</div>
	</article>
	<?php
}

function studentup_opportunities_template( $template ) {
	if ( get_query_var( 'studentup_opportunities' ) ) {
		global $wp_query;
		if ( $wp_query ) {
			$wp_query->is_404 = false;
		}
		status_header( 200 );
		nocache_headers();
		return get_template_directory() . '/page-opportunities.php';
	}
	return $template;
}
add_filter( 'template_include', 'studentup_opportunities_template' );

function studentup_opportunities_rewrite() {
	add_rewrite_rule( '^latest-jobs/?$', 'index.php?studentup_opportunities=1', 'top' );
}
add_action( 'init', 'studentup_opportunities_rewrite', 1 );

function studentup_opportunities_query_var( $vars ) {
	$vars[] = 'studentup_opportunities';
	return $vars;
}
add_filter( 'query_vars', 'studentup_opportunities_query_var' );

function studentup_opportunities_activate() {
	studentup_opportunities_rewrite();
	flush_rewrite_rules();
}
add_action( 'after_switch_theme', 'studentup_opportunities_activate' );


/* ------------------------------------------------------------------ v1.9.119
 * /latest-jobs/ is a virtual route (no page object) → WP + Rank Math treated it
 * as HOME: <title>StudentUp</title>, canonical "/", og:url "/". Google saw a
 * duplicate of the homepage and never indexed the jobs board. Own title /
 * description / self-canonical now, via both core and Rank Math filters.
 * ------------------------------------------------------------------------ */

function studentup_opportunities_is_route() {
	return (bool) get_query_var( 'studentup_opportunities' );
}

function studentup_opportunities_seo_title() {
	return 'Latest Govt Jobs 2026 — TS & AP (Last Dates) — ' . wp_strip_all_tags( get_bloginfo( 'name' ) );
}

function studentup_opportunities_seo_desc() {
	return 'తెలంగాణ & ఆంధ్రప్రదేశ్ విద్యార్థుల కోసం ప్రస్తుతం ఓపెన్‌లో ఉన్న ప్రభుత్వ ఉద్యోగ నోటిఫికేషన్లు — చివరి తేదీ, అర్హత, అధికారిక దరఖాస్తు లింక్ ఒకే జాబితాలో. గడువు ముగిసినవి ఆటోమేటిక్‌గా తొలగిపోతాయి.'; // v1.9.141 Telugu
}

add_filter( 'pre_get_document_title', function ( $title ) {
	return studentup_opportunities_is_route() ? studentup_opportunities_seo_title() : $title;
}, 99 );
add_filter( 'rank_math/frontend/title', function ( $title ) {
	return studentup_opportunities_is_route() ? studentup_opportunities_seo_title() : $title;
}, 99 );
add_filter( 'rank_math/frontend/description', function ( $desc ) {
	return studentup_opportunities_is_route() ? studentup_opportunities_seo_desc() : $desc;
}, 99 );
add_filter( 'rank_math/frontend/canonical', function ( $canon ) {
	return studentup_opportunities_is_route() ? studentup_opportunity_board_url() : $canon;
}, 99 );
add_filter( 'rank_math/opengraph/url', function ( $url ) {
	return studentup_opportunities_is_route() ? studentup_opportunity_board_url() : $url;
}, 99 );
// Core/theme fallback (Rank Math inactive): list helpers return the real URL/title.
add_filter( 'studentup_seo_list_url', function ( $url ) {
	return studentup_opportunities_is_route() ? studentup_opportunity_board_url() : $url;
} );
add_filter( 'studentup_seo_list_title', function ( $t ) {
	return studentup_opportunities_is_route() ? 'Latest Govt Jobs 2026 — TS & AP (Last Dates)' : $t;
} );
add_filter( 'studentup_seo_list_desc', function ( $d ) {
	return studentup_opportunities_is_route() ? studentup_opportunities_seo_desc() : $d;
} );
