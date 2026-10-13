<?php
/**
 * v294 — "Post Your News" (reader submissions) + Breaking News section rules.
 *
 * Owner (2026-10-14):
 *  · Daily Quiz pakkana "Post your news" — readers send success stories,
 *    photos, videos, district information. We approve → we post.
 *    Google Form attach cheyyochu (Settings → Verified Success Story Google Form URL).
 *  · Open chesthe aa section (page) chupinchali — approved stories motivational ga.
 *  · Breaking News = separate section (district news). Click → category opens.
 *    Breaking posts HOME PAGE lo chupinchoddu — only Breaking News open chesina
 *    vallaki kanipinchali.
 *
 * Honesty contract: form URL lekapote iframe render kaadu (WhatsApp/Telegram
 * send buttons matrame — avi real). Approved stories lekapote grid render kaadu.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Page slug for the submissions page (firstrun creates it). */
define( 'STUDENTUP_POSTNEWS_SLUG', 'post-your-news' );

/**
 * URL of the Post Your News page ('' when the page is not published yet).
 *
 * @return string
 */
function studentup_postnews_url() {
	$url = function_exists( 'studentup_mega_page_url' ) ? studentup_mega_page_url( array( STUDENTUP_POSTNEWS_SLUG, 'share-your-story' ) ) : '';
	if ( ! $url ) {
		$page = get_page_by_path( STUDENTUP_POSTNEWS_SLUG );
		if ( $page instanceof WP_Post && 'publish' === get_post_status( $page ) ) {
			$url = (string) get_permalink( $page );
		}
	}
	return $url;
}

/**
 * Configured Google Form URL (embed-safe) or ''.
 *
 * @return string
 */
function studentup_postnews_form_url() {
	$u = function_exists( 'studentup_opt' ) ? trim( (string) studentup_opt( 'success_story_form_url', '' ) ) : '';
	if ( ! $u || ! preg_match( '#^https?://#i', $u ) ) {
		return '';
	}
	return esc_url_raw( $u );
}

/**
 * Google Form "embedded=true" variant (only for docs.google.com/forms URLs).
 *
 * @param string $url form url.
 * @return string '' when not embeddable.
 */
function studentup_postnews_embed_url( $url ) {
	$host = wp_parse_url( $url, PHP_URL_HOST );
	if ( ! $host || ! preg_match( '#(^|\.)docs\.google\.com$#i', $host ) || false === stripos( $url, '/forms/' ) ) {
		return '';
	}
	$url = preg_replace( '#/(viewform|edit)(\?.*)?$#i', '/viewform', $url );
	return add_query_arg( 'embedded', 'true', $url );
}

/**
 * Compact CTA card — sits under the Daily Quiz on the home grid.
 * Renders only when the page exists (no dead links).
 *
 * @return void
 */
function studentup_postnews_cta() {
	$url = studentup_postnews_url();
	if ( ! $url ) {
		return;
	}
	?>
	<section class="su-postnews" aria-labelledby="su-postnews-h">
		<div class="su-postnews-head">
			<span class="su-postnews-ic" aria-hidden="true"><?php echo studentup_ui_icon( 'upload', 20 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
			<h2 id="su-postnews-h"><?php esc_html_e( 'Post your news', 'studentup' ); ?></h2>
		</div>
		<div class="su-postnews-tiles" role="list">
			<a role="listitem" href="<?php echo esc_url( $url ); ?>" data-su-ev="postnews_open"><span aria-hidden="true"><?php echo studentup_ui_icon( 'trophy', 20 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span><b><?php esc_html_e( 'Success story', 'studentup' ); ?></b></a>
			<a role="listitem" href="<?php echo esc_url( $url ); ?>" data-su-ev="postnews_open"><span aria-hidden="true"><?php echo studentup_ui_icon( 'upload', 20 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span><b><?php esc_html_e( 'Photo / Video', 'studentup' ); ?></b></a>
			<a role="listitem" href="<?php echo esc_url( $url ); ?>" data-su-ev="postnews_open"><span aria-hidden="true"><?php echo studentup_ui_icon( 'pin', 20 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span><b><?php esc_html_e( 'District update', 'studentup' ); ?></b></a>
		</div>
		<a class="su-postnews-btn" href="<?php echo esc_url( $url ); ?>" data-su-ev="postnews_open"><?php esc_html_e( 'Send now', 'studentup' ); ?> <?php echo studentup_ui_icon( 'arrow', 16 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
	</section>
	<?php
}

/**
 * Approved stories (published posts in success-stories family) — newest first.
 *
 * @param int $n max.
 * @return WP_Post[]
 */
function studentup_postnews_approved( $n = 12 ) {
	$term = function_exists( 'studentup_used_term' ) ? studentup_used_term( 'success-stories' ) : null;
	if ( ! $term ) {
		return array();
	}
	$q = new WP_Query(
		array(
			'cat'                 => (int) $term->term_id,
			'posts_per_page'      => max( 1, (int) $n ),
			'post_status'         => 'publish',
			'ignore_sticky_posts' => true,
			'no_found_rows'       => true,
		)
	);
	return $q->posts;
}

/* ------------------------------------------------------------------------- */
/* Breaking News — own section; never on the home page.                      */
/* ------------------------------------------------------------------------- */

/**
 * Breaking News category (real term) or null.
 *
 * @return WP_Term|null
 */
function studentup_breaking_term() {
	static $t = false;
	if ( false === $t ) {
		$t = null;
		foreach ( array( 'breaking-news', 'breaking' ) as $slug ) {
			$term = get_category_by_slug( $slug );
			if ( $term && ! is_wp_error( $term ) ) {
				$t = $term;
				break;
			}
		}
	}
	return $t;
}

/**
 * Breaking News section URL — category archive when it exists, else home anchor.
 *
 * @return string
 */
function studentup_breaking_section_url() {
	$t = studentup_breaking_term();
	return $t ? (string) get_category_link( $t ) : home_url( '/#breaking' );
}

/**
 * Hide breaking-news posts from every query that is NOT the breaking section
 * itself (home loops, Top 5, slider, latest, RSS home, related). Single posts,
 * search, the category archive, feeds of that category and admin stay intact.
 *
 * @param WP_Query $q query.
 * @return void
 */
function studentup_breaking_hide_from_home( $q ) {
	if ( is_admin() || ! ( $q instanceof WP_Query ) ) {
		return;
	}
	$t = studentup_breaking_term();
	if ( ! $t ) {
		return;
	}
	if ( 'post' !== (string) ( $q->get( 'post_type' ) ?: 'post' ) ) {
		return;
	}
	// Queries that explicitly ask for the breaking category → leave them alone.
	$asked = array_filter(
		array(
			(string) $q->get( 'cat' ),
			(string) $q->get( 'category_name' ),
			implode( ',', (array) $q->get( 'category__in' ) ),
			implode( ',', (array) $q->get( 'category__and' ) ),
		)
	);
	$ids = array_map( 'strval', studentup_breaking_term_ids() );
	foreach ( $asked as $v ) {
		$parts = array_map( 'trim', explode( ',', $v ) );
		if ( array_intersect( $parts, $ids ) ) {
			return;
		}
		foreach ( $parts as $slug ) {
			$slug = ltrim( $slug, '-' );
			if ( '' === $slug || is_numeric( $slug ) ) {
				continue;
			}
			$term = get_category_by_slug( $slug );
			if ( $term && in_array( (string) $term->term_id, $ids, true ) ) {
				return;
			}
		}
	}
	if ( $q->get( 'tax_query' ) || $q->get( 'p' ) || $q->get( 'name' ) || $q->get( 'post__in' ) ) {
		return;
	}
	if ( $q->is_main_query() ) {
		if ( $q->is_singular() || $q->is_search() || $q->is_tag() || $q->is_author() || $q->is_date() || $q->is_feed() ) {
			return;
		}
		if ( $q->is_category( studentup_breaking_term_ids() ) ) {
			return;
		}
	}
	$not = array_merge( (array) $q->get( 'category__not_in' ), studentup_breaking_term_ids() );
	$q->set( 'category__not_in', array_values( array_unique( array_map( 'intval', $not ) ) ) );
}
add_action( 'pre_get_posts', 'studentup_breaking_hide_from_home', 9 );

/**
 * firstrun: make sure the Breaking News category + Post Your News page exist.
 */
add_filter(
	'studentup_firstrun_pages',
	static function ( $pages ) {
		$pages = (array) $pages;
		if ( ! isset( $pages[ STUDENTUP_POSTNEWS_SLUG ] ) ) {
			$pages[ STUDENTUP_POSTNEWS_SLUG ] = 'Post Your News';
		}
		return $pages;
	},
	5
);

/**
 * Assign the page template to the submissions page (works for pages created
 * earlier too — runs once per admin load, cheap get_page_by_path).
 */
function studentup_postnews_assign_template() {
	$page = get_page_by_path( STUDENTUP_POSTNEWS_SLUG );
	if ( $page instanceof WP_Post && 'page-post-news.php' !== (string) get_post_meta( $page->ID, '_wp_page_template', true ) ) {
		update_post_meta( $page->ID, '_wp_page_template', 'page-post-news.php' );
	}
	if ( ! studentup_breaking_term() ) {
		$res = wp_insert_term(
			'Breaking News',
			'category',
			array(
				'slug'        => 'breaking-news',
				'description' => 'District-wise breaking updates. This section is shown only here, not on the home page.',
			)
		);
		if ( is_wp_error( $res ) && 'term_exists' === $res->get_error_code() ) {
			// Name exists under a different slug — nothing to do.
			return;
		}
	}
}
add_action( 'admin_init', 'studentup_postnews_assign_template' );
add_action( 'after_switch_theme', 'studentup_postnews_assign_template' );

/* ------------------------------------------------------------------------- */
/* v295: Breaking News tree — Telangana News / Andhra Pradesh News → districts */
/* ------------------------------------------------------------------------- */

/**
 * State → districts (official 33 TS + 26 AP), alphabetical.
 *
 * @return array slug => array( name, districts[] )
 */
function studentup_breaking_tree() {
	$ts = array( 'Adilabad', 'Bhadradri Kothagudem', 'Hanumakonda', 'Hyderabad', 'Jagtial', 'Jangaon', 'Jayashankar Bhupalpally', 'Jogulamba Gadwal', 'Kamareddy', 'Karimnagar', 'Khammam', 'Kumuram Bheem Asifabad', 'Mahabubabad', 'Mahabubnagar', 'Mancherial', 'Medak', 'Medchal-Malkajgiri', 'Mulugu', 'Nagarkurnool', 'Nalgonda', 'Narayanpet', 'Nirmal', 'Nizamabad', 'Peddapalli', 'Rajanna Sircilla', 'Ranga Reddy', 'Sangareddy', 'Siddipet', 'Suryapet', 'Vikarabad', 'Wanaparthy', 'Warangal', 'Yadadri Bhuvanagiri' );
	$ap = array( 'Alluri Sitharama Raju', 'Anakapalli', 'Ananthapuramu', 'Annamayya', 'Bapatla', 'Chittoor', 'Dr. B.R. Ambedkar Konaseema', 'East Godavari', 'Eluru', 'Guntur', 'Kakinada', 'Krishna', 'Kurnool', 'Nandyal', 'NTR', 'Palnadu', 'Parvathipuram Manyam', 'Prakasam', 'Sri Potti Sriramulu Nellore', 'Sri Sathya Sai', 'Srikakulam', 'Tirupati', 'Visakhapatnam', 'Vizianagaram', 'West Godavari', 'YSR Kadapa' );
	sort( $ts, SORT_NATURAL | SORT_FLAG_CASE );
	sort( $ap, SORT_NATURAL | SORT_FLAG_CASE );
	return array(
		'telangana-news'      => array( 'Telangana News', $ts, 'ts' ),
		'andhra-pradesh-news' => array( 'Andhra Pradesh News', $ap, 'ap' ),
	);
}

/**
 * Create Breaking News → state → district categories once (idempotent).
 */
function studentup_breaking_ensure_tree() {
	if ( get_option( 'studentup_breaking_tree_v1' ) ) {
		return;
	}
	$root = studentup_breaking_term();
	if ( ! $root ) {
		return;
	}
	foreach ( studentup_breaking_tree() as $slug => $st ) {
		$state = get_category_by_slug( $slug );
		if ( ! $state ) {
			$r = wp_insert_term( $st[0], 'category', array( 'slug' => $slug, 'parent' => (int) $root->term_id, 'description' => $st[0] . ' — district-wise updates.' ) );
			if ( is_wp_error( $r ) ) {
				continue;
			}
			$state = get_term( (int) $r['term_id'], 'category' );
		}
		foreach ( $st[1] as $d ) {
			$dslug = $st[2] . '-' . sanitize_title( $d );
			if ( ! get_category_by_slug( $dslug ) ) {
				wp_insert_term( $d, 'category', array( 'slug' => $dslug, 'parent' => (int) $state->term_id, 'description' => $d . ' district news.' ) );
			}
		}
	}
	update_option( 'studentup_breaking_tree_v1', time(), false );
}
add_action( 'admin_init', 'studentup_breaking_ensure_tree', 20 );

/**
 * All breaking term ids (root + states + districts) — for the home exclusion.
 *
 * @return int[]
 */
function studentup_breaking_term_ids() {
	static $ids = null;
	if ( null === $ids ) {
		$ids = array();
		$t   = studentup_breaking_term();
		if ( $t ) {
			$ids   = array( (int) $t->term_id );
			$kids  = get_term_children( (int) $t->term_id, 'category' );
			if ( ! is_wp_error( $kids ) ) {
				$ids = array_merge( $ids, array_map( 'intval', $kids ) );
			}
		}
	}
	return $ids;
}

/**
 * Which part of the tree is this category page? root | state | district | ''.
 *
 * @param WP_Term $term queried term.
 * @return string
 */
function studentup_breaking_level( $term ) {
	$root = studentup_breaking_term();
	if ( ! $root || ! ( $term instanceof WP_Term ) ) {
		return '';
	}
	if ( (int) $term->term_id === (int) $root->term_id ) {
		return 'root';
	}
	if ( (int) $term->parent === (int) $root->term_id ) {
		return 'state';
	}
	$p = get_term( (int) $term->parent, 'category' );
	if ( $p instanceof WP_Term && (int) $p->parent === (int) $root->term_id ) {
		return 'district';
	}
	return '';
}

/**
 * Breaking section navigation (archive.php):
 *  root     → 2 state cards (Telangana News · Andhra Pradesh News)
 *  state    → state tabs + alphabetical district grid (all districts)
 *  district → state tabs + district chips (current highlighted)
 *
 * @return void
 */
function studentup_breaking_section_nav() {
	if ( ! is_category() ) {
		return;
	}
	$term  = get_queried_object();
	$level = studentup_breaking_level( $term );
	if ( ! $level ) {
		return;
	}
	$root   = studentup_breaking_term();
	$states = get_terms( array( 'taxonomy' => 'category', 'parent' => (int) $root->term_id, 'hide_empty' => false, 'orderby' => 'name' ) );
	if ( is_wp_error( $states ) || ! $states ) {
		return;
	}
	$state = null;
	if ( 'state' === $level ) {
		$state = $term;
	} elseif ( 'district' === $level ) {
		$state = get_term( (int) $term->parent, 'category' );
	}
	?>
	<nav class="su-brk-nav su-brk-nav--<?php echo esc_attr( $level ); ?>" aria-label="<?php esc_attr_e( 'Breaking news by state and district', 'studentup' ); ?>">
		<div class="su-brk-states">
			<?php foreach ( $states as $st ) : ?>
				<?php $on = $state instanceof WP_Term && (int) $st->term_id === (int) $state->term_id; ?>
				<a class="<?php echo esc_attr( $on ? 'su-brk-state is-on' : 'su-brk-state' ); ?>" href="<?php echo esc_url( get_category_link( $st ) ); ?>"<?php if ( $on ) : ?> aria-current="page"<?php endif; ?>>
					<span class="su-brk-state-ic" aria-hidden="true"><?php echo studentup_ui_icon( 'pin', 20 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
					<b><?php echo esc_html( $st->name ); ?></b>
				</a>
			<?php endforeach; ?>
		</div>
		<?php if ( $state instanceof WP_Term ) : ?>
			<?php $dists = get_terms( array( 'taxonomy' => 'category', 'parent' => (int) $state->term_id, 'hide_empty' => false, 'orderby' => 'name' ) ); ?>
			<?php if ( ! is_wp_error( $dists ) && $dists ) : ?>
				<div class="su-brk-dists" role="list">
					<?php foreach ( $dists as $d ) : ?>
						<?php $on = 'district' === $level && (int) $d->term_id === (int) $term->term_id; ?>
						<a role="listitem" class="<?php echo esc_attr( $on ? 'su-brk-dist is-on' : 'su-brk-dist' ); ?>" href="<?php echo esc_url( get_category_link( $d ) ); ?>"<?php if ( $on ) : ?> aria-current="page"<?php endif; ?>><?php echo esc_html( $d->name ); ?></a>
					<?php endforeach; ?>
				</div>
			<?php endif; ?>
		<?php endif; ?>
	</nav>
	<?php
}
