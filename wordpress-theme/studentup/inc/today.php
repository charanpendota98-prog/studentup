<?php
/**
 * v1.9.134 — "ఈరోజు అప్‌డేట్స్" date-wise updates page (/today/).
 *
 * Why: the highest-return habit on job portals (Eenadu Pratibha, Sakshi
 * Education) is the DATE-WISE list — a reader opens the same URL every
 * morning and scans "today · yesterday · earlier this week". Our home grid
 * is newest-first but not grouped by day; this page is that daily habit URL.
 *
 * Real data only: published posts from the last 14 days (Breaking News
 * excluded), grouped by publish day in site timezone; deadline pill only
 * from a valid `studentup_last_date`; no posts → 404 (no thin page).
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'STUDENTUP_TODAY_DAYS', 14 );
define( 'STUDENTUP_TODAY_MAX', 80 );

function studentup_today_url() {
	return home_url( '/today/' );
}

function studentup_is_today_page() {
	return '1' === (string) get_query_var( 'studentup_today' );
}

/* ---------------------------------------------------------------- routing */

function studentup_today_rewrite() {
	add_rewrite_rule( '^today/?$', 'index.php?studentup_today=1', 'top' );
}
add_action( 'init', 'studentup_today_rewrite', 1 );

add_filter( 'query_vars', function ( $vars ) {
	$vars[] = 'studentup_today';
	return $vars;
} );

add_action( 'init', function () {
	if ( get_option( 'studentup_today_flushed' ) !== '1' ) {
		studentup_today_rewrite();
		flush_rewrite_rules( false );
		update_option( 'studentup_today_flushed', '1' );
	}
}, 99 );

add_action( 'pre_get_posts', function ( $q ) {
	if ( is_admin() || ! $q->is_main_query() || '1' !== (string) $q->get( 'studentup_today' ) ) {
		return;
	}
	$q->set( 'post_type', 'post' );
	$q->set( 'post_status', 'publish' );
	$q->set( 'ignore_sticky_posts', true );
	$q->set( 'posts_per_page', STUDENTUP_TODAY_MAX );
	$q->set( 'no_found_rows', true );
	$q->set( 'orderby', 'date' );
	$q->set( 'order', 'DESC' );
	$q->set( 'date_query', array( array( 'after' => STUDENTUP_TODAY_DAYS . ' days ago', 'inclusive' => true ) ) );
	if ( function_exists( 'studentup_breaking_term_ids' ) ) {
		$q->set( 'category__not_in', array_map( 'intval', (array) studentup_breaking_term_ids() ) );
	}
	$q->is_home    = false;
	$q->is_archive = true;
}, 8 );

add_filter( 'template_include', function ( $template ) {
	if ( ! studentup_is_today_page() ) {
		return $template;
	}
	global $wp_query;
	if ( ! $wp_query->have_posts() ) {
		$wp_query->set_404();
		status_header( 404 );
		return get_404_template();
	}
	$wp_query->is_404 = false;
	status_header( 200 );
	return get_template_directory() . '/page-today.php';
} );

/* -------------------------------------------------------------------- SEO */

function studentup_today_h1() {
	return __( 'Today’s updates — jobs, results, hall tickets', 'studentup' );
}

function studentup_today_title() {
	/* translators: %s: today's date */
	return sprintf( __( 'Today’s updates (%s) — latest jobs, results, hall tickets', 'studentup' ), wp_date( 'j F Y' ) )
		. ' — ' . wp_strip_all_tags( get_bloginfo( 'name' ) );
}

function studentup_today_desc() {
	global $wp_query;
	$n = $wp_query instanceof WP_Query ? count( (array) $wp_query->posts ) : 0;
	/* translators: 1: number of updates, 2: number of days */
	return sprintf( __( '%1$d updates from the last %2$d days, grouped by date: notifications, last dates, results, hall tickets — Telugu. Updated every day.', 'studentup' ), $n, STUDENTUP_TODAY_DAYS );
}

foreach ( array( 'pre_get_document_title', 'rank_math/frontend/title' ) as $su_h ) {
	add_filter( $su_h, function ( $t ) {
		return studentup_is_today_page() ? studentup_today_title() : $t;
	}, 99 );
}
add_filter( 'rank_math/frontend/description', function ( $d ) {
	return studentup_is_today_page() ? studentup_today_desc() : $d;
}, 99 );
foreach ( array( 'rank_math/frontend/canonical', 'rank_math/opengraph/url', 'studentup_seo_list_url' ) as $su_h ) {
	add_filter( $su_h, function ( $u ) {
		return studentup_is_today_page() ? studentup_today_url() : $u;
	}, 99 );
}
add_filter( 'studentup_seo_list_title', function ( $t ) {
	return studentup_is_today_page() ? studentup_today_h1() : $t;
} );
add_filter( 'studentup_seo_list_desc', function ( $d ) {
	return studentup_is_today_page() ? studentup_today_desc() : $d;
} );
add_filter( 'get_the_archive_title', function ( $title ) {
	return studentup_is_today_page() ? __( 'Today’s updates', 'studentup' ) : $title;
} );
add_filter( 'wp_robots', function ( $robots ) {
	if ( studentup_is_today_page() ) {
		unset( $robots['noindex'] );
		$robots['max-image-preview'] = 'large';
	}
	return $robots;
}, 99 );

/* ----------------------------------------------------------------- render */

/**
 * Group the main-query posts by site-timezone day.
 *
 * @return array<string,array{label:string,posts:WP_Post[]}>
 */
function studentup_today_groups() {
	global $wp_query;
	$today     = wp_date( 'Y-m-d' );
	$yesterday = wp_date( 'Y-m-d', time() - DAY_IN_SECONDS );
	$groups    = array();
	foreach ( (array) $wp_query->posts as $p ) {
		if ( ! ( $p instanceof WP_Post ) ) {
			continue;
		}
		$day = get_the_date( 'Y-m-d', $p );
		if ( ! isset( $groups[ $day ] ) ) {
			if ( $day === $today ) {
				$label = __( 'Today', 'studentup' );
			} elseif ( $day === $yesterday ) {
				$label = __( 'Yesterday', 'studentup' );
			} else {
				$wd    = array( __( 'Sunday', 'studentup' ), __( 'Monday', 'studentup' ), __( 'Tuesday', 'studentup' ), __( 'Wednesday', 'studentup' ), __( 'Thursday', 'studentup' ), __( 'Friday', 'studentup' ), __( 'Saturday', 'studentup' ) );
				$label = get_the_date( 'j F', $p ) . ', ' . $wd[ (int) get_the_date( 'w', $p ) ];
			}
			$groups[ $day ] = array( 'label' => $label, 'posts' => array() );
		}
		$groups[ $day ]['posts'][] = $p;
	}
	return $groups;
}

/**
 * Deadline chip from real meta only (Y-m-d, today or later).
 *
 * @param int $post_id Post ID.
 * @return string HTML or ''.
 */
function studentup_today_deadline( $post_id ) {
	$raw = (string) get_post_meta( $post_id, 'studentup_last_date', true );
	if ( ! preg_match( '/^\d{4}-\d{2}-\d{2}$/', $raw ) ) {
		return '';
	}
	$ts = strtotime( $raw . ' 23:59:59' );
	if ( ! $ts ) {
		return '';
	}
	$days = (int) floor( ( $ts - current_time( 'timestamp' ) ) / DAY_IN_SECONDS ); // phpcs:ignore WordPress.DateTime.CurrentTimeTimestamp
	if ( $days < 0 || $days > 60 ) {
		return '';
	}
	/* translators: %s: number of days */
	$txt = 0 === $days ? __( 'Last day today', 'studentup' ) : sprintf( _n( '%s Day Left', '%s Days Left', $days, 'studentup' ), number_format_i18n( $days ) );
	return '<span class="su-today-dl' . ( $days <= 3 ? ' is-hot' : '' ) . '">' . esc_html( $txt ) . '</span>';
}

function studentup_today_list() {
	$groups = studentup_today_groups();
	if ( ! $groups ) {
		return;
	}
	echo '<div class="su-today">';
	foreach ( $groups as $day => $g ) {
		echo '<section class="su-today-day" aria-labelledby="su-td-' . esc_attr( $day ) . '">';
		echo '<h2 id="su-td-' . esc_attr( $day ) . '"><time datetime="' . esc_attr( $day ) . '">' . esc_html( $g['label'] ) . '</time> <span>' . esc_html( number_format_i18n( count( $g['posts'] ) ) ) . '</span></h2>';
		echo '<ol>';
		foreach ( $g['posts'] as $p ) {
			$cats = get_the_category( $p->ID );
			$cat  = $cats ? $cats[0] : null;
			echo '<li>';
			echo '<a class="su-today-t" href="' . esc_url( get_permalink( $p ) ) . '">' . esc_html( wp_strip_all_tags( get_the_title( $p ) ) ) . '</a>';
			echo '<span class="su-today-meta">';
			if ( $cat ) {
				echo '<a class="su-today-cat" href="' . esc_url( get_category_link( $cat ) ) . '">' . esc_html( $cat->name ) . '</a>';
			}
			echo '<time datetime="' . esc_attr( get_the_date( 'c', $p ) ) . '">' . esc_html( get_the_date( 'g:i a', $p ) ) . '</time>';
			echo studentup_today_deadline( $p->ID ); // phpcs:ignore WordPress.Security.EscapeOutput -- escaped inside
			echo '</span>';
			echo '</li>';
		}
		echo '</ol>';
		echo '</section>';
	}
	echo '</div>';
}

/* ------------------------------------------------------------ entry points */

// Mega menu → "Updates" column first item; mobile menu quick link.
add_filter( 'studentup_mega_groups', function ( $groups ) {
	if ( ! function_exists( 'studentup_mega_item' ) || ! is_array( $groups ) ) {
		return $groups;
	}
	foreach ( $groups as $gi => $g ) {
		if ( empty( $g['cols'] ) || ! is_array( $g['cols'] ) ) {
			continue;
		}
		foreach ( $g['cols'] as $ci => $col ) {
			if ( isset( $col['title'] ) && 'Updates' === $col['title'] ) {
				array_unshift( $groups[ $gi ]['cols'][ $ci ]['items'], studentup_mega_item( 'Today’s updates', studentup_today_url(), 'Date-wise · every morning', 'clock' ) );
				return $groups;
			}
		}
	}
	return $groups;
} );
