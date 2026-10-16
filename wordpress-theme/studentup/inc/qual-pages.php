<?php
/**
 * v1.9.122 — Programmatic SEO: qualification landing pages.
 *
 * /jobs/10th/ · /jobs/inter/ · /jobs/iti/ · /jobs/diploma/ · /jobs/degree/ ·
 * /jobs/pg/ · /jobs/btech/  (+ /page/N/)
 *
 * Why: "10th pass govt jobs telangana", "degree jobs ap 2026" are the highest
 * volume long-tail searches in this niche. Until now the only qualification
 * view was ?qual=degree on the home grid — a noindex query-param variant, so
 * Google could never rank it. These are clean, self-canonical, indexable
 * routes with a unique H1/title/description built ONLY from real post data
 * (count, closing-soon items). Zero matching posts → 404 (no thin pages).
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Current qualification route slug ('' when not on one).
 *
 * @return string
 */
function studentup_qual_page_slug() {
	$slug  = (string) get_query_var( 'studentup_qual_page' );
	$terms = function_exists( 'studentup_qual_terms' ) ? studentup_qual_terms() : array();
	return isset( $terms[ $slug ] ) ? $slug : '';
}

function studentup_qual_page_url( $slug ) {
	return home_url( '/jobs/' . rawurlencode( $slug ) . '/' );
}

/**
 * Human label for a slug ("Degree", "SSC · 10th").
 */
function studentup_qual_page_label( $slug ) {
	$terms = studentup_qual_terms();
	return isset( $terms[ $slug ] ) ? $terms[ $slug ] : $slug;
}

/* ---------------------------------------------------------------- routing */

function studentup_qual_pages_rewrite() {
	$keys = implode( '|', array_map( 'preg_quote', array_keys( studentup_qual_terms() ) ) );
	add_rewrite_rule( '^jobs/(' . $keys . ')/page/([0-9]+)/?$', 'index.php?studentup_qual_page=$matches[1]&paged=$matches[2]', 'top' );
	add_rewrite_rule( '^jobs/(' . $keys . ')/?$', 'index.php?studentup_qual_page=$matches[1]', 'top' );
}
add_action( 'init', 'studentup_qual_pages_rewrite', 1 );

add_filter( 'query_vars', function ( $vars ) {
	$vars[] = 'studentup_qual_page';
	return $vars;
} );

// Rewrite rules refresh once after theme switch / first load of this version.
add_action( 'init', function () {
	if ( get_option( 'studentup_qual_pages_flushed' ) !== '1' ) {
		studentup_qual_pages_rewrite();
		flush_rewrite_rules( false );
		update_option( 'studentup_qual_pages_flushed', '1' );
	}
}, 99 );

/**
 * Main query: published posts carrying this qualification, breaking news excluded.
 */
function studentup_qual_pages_query( $q ) {
	if ( is_admin() || ! $q->is_main_query() ) {
		return;
	}
	$slug = sanitize_key( (string) $q->get( 'studentup_qual_page' ) );
	$terms = studentup_qual_terms();
	if ( '' === $slug || ! isset( $terms[ $slug ] ) ) {
		return;
	}
	$q->set( 'post_type', 'post' );
	$q->set( 'post_status', 'publish' );
	$q->set( 'ignore_sticky_posts', true );
	$q->set( 'meta_query', array( array( // phpcs:ignore WordPress.DB.SlowDBQuery
		'key'     => 'studentup_qual',
		'value'   => $slug,
		'compare' => 'LIKE',
	) ) );
	if ( function_exists( 'studentup_breaking_term_ids' ) ) {
		$q->set( 'category__not_in', array_map( 'intval', (array) studentup_breaking_term_ids() ) );
	}
	$q->is_home    = false;
	$q->is_archive = true;
}
add_action( 'pre_get_posts', 'studentup_qual_pages_query', 8 );

function studentup_qual_pages_template( $template ) {
	$slug = studentup_qual_page_slug();
	if ( '' === $slug ) {
		return $template;
	}
	global $wp_query;
	if ( ! $wp_query->have_posts() ) {
		// Golden rule: data lekapote page ledu (thin page → 404, noindex by core).
		$wp_query->set_404();
		status_header( 404 );
		return get_404_template();
	}
	$wp_query->is_404 = false;
	status_header( 200 );
	return get_template_directory() . '/page-qual.php';
}
add_filter( 'template_include', 'studentup_qual_pages_template' );

/* -------------------------------------------------------------------- SEO */

function studentup_qual_page_h1( $slug ) {
	/* translators: %s qualification label */
	return sprintf( '%s Govt Jobs %s — Telangana & AP Notifications', studentup_qual_page_label( $slug ), gmdate( 'Y' ) );
}

function studentup_qual_page_title( $slug ) {
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	$t     = studentup_qual_page_h1( $slug ) . ' — ' . wp_strip_all_tags( get_bloginfo( 'name' ) );
	return $paged > 1 ? $t . ' — Page ' . $paged : $t;
}

function studentup_qual_page_desc( $slug ) {
	global $wp_query;
	$n      = isset( $wp_query->found_posts ) ? (int) $wp_query->found_posts : 0;
	$titles = array();
	foreach ( array_slice( (array) $wp_query->posts, 0, 2 ) as $p ) {
		$titles[] = wp_strip_all_tags( get_the_title( $p ) );
	}
	$d = sprintf( '%s qualification tho apply cheyyagala %d govt job notifications — TS & AP. Last date, vacancies, official apply link okate chota.', studentup_qual_page_label( $slug ), $n );
	if ( $titles ) {
		$d .= ' Latest: ' . implode( ' · ', $titles ) . '.';
	}
	return $d;
}

add_filter( 'pre_get_document_title', function ( $title ) {
	$s = studentup_qual_page_slug();
	return $s ? studentup_qual_page_title( $s ) : $title;
}, 99 );
add_filter( 'rank_math/frontend/title', function ( $title ) {
	$s = studentup_qual_page_slug();
	return $s ? studentup_qual_page_title( $s ) : $title;
}, 99 );
add_filter( 'rank_math/frontend/description', function ( $d ) {
	$s = studentup_qual_page_slug();
	return $s ? studentup_qual_page_desc( $s ) : $d;
}, 99 );
add_filter( 'rank_math/frontend/canonical', function ( $c ) {
	$s = studentup_qual_page_slug();
	if ( ! $s ) {
		return $c;
	}
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	return $paged > 1 ? get_pagenum_link( $paged ) : studentup_qual_page_url( $s );
}, 99 );
add_filter( 'rank_math/opengraph/url', function ( $u ) {
	$s = studentup_qual_page_slug();
	return $s ? studentup_qual_page_url( $s ) : $u;
}, 99 );
// Theme fallback head (Rank Math inactive).
add_filter( 'studentup_seo_list_url', function ( $u ) {
	$s = studentup_qual_page_slug();
	if ( ! $s ) {
		return $u;
	}
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	return $paged > 1 ? get_pagenum_link( $paged ) : studentup_qual_page_url( $s );
} );
add_filter( 'studentup_seo_list_title', function ( $t ) {
	$s = studentup_qual_page_slug();
	return $s ? studentup_qual_page_h1( $s ) : $t;
} );
add_filter( 'studentup_seo_list_desc', function ( $d ) {
	$s = studentup_qual_page_slug();
	return $s ? studentup_qual_page_desc( $s ) : $d;
} );
// Keep the ?qual= noindex logic from treating this clean route as a variant.
add_filter( 'wp_robots', function ( $robots ) {
	if ( studentup_qual_page_slug() ) {
		unset( $robots['noindex'] );
		$robots['max-image-preview'] = 'large';
	}
	return $robots;
}, 99 );

/**
 * ItemList + CollectionPage schema (real items on this page only).
 */
function studentup_qual_page_schema() {
	$s = studentup_qual_page_slug();
	if ( ! $s ) {
		return;
	}
	global $wp_query;
	$items = array();
	$i     = 0;
	foreach ( (array) $wp_query->posts as $p ) {
		$i++;
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $i,
			'url'      => get_permalink( $p ),
			'name'     => wp_strip_all_tags( get_the_title( $p ) ),
		);
	}
	$data = array(
		'@context'   => 'https://schema.org',
		'@type'      => 'CollectionPage',
		'@id'        => studentup_qual_page_url( $s ) . '#page',
		'url'        => studentup_qual_page_url( $s ),
		'name'       => studentup_qual_page_h1( $s ),
		'inLanguage' => 'te-IN',
		'isPartOf'   => array( '@id' => home_url( '/' ) . '#website' ),
		'mainEntity' => array(
			'@type'           => 'ItemList',
			'numberOfItems'   => (int) $wp_query->found_posts,
			'itemListElement' => $items,
		),
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_qual_page_schema', 8 );

/* --------------------------------------------------------- internal links */

/**
 * "Jobs by qualification" link row — only slugs that really have posts
 * (uses the cached studentup_qual_count). Used on qual pages, jobs board and
 * the footer so every landing page gets crawl paths + PageRank.
 *
 * @param string $current slug to mark active.
 * @return string HTML ('' when nothing to show).
 */
function studentup_qual_pages_links( $current = '' ) {
	if ( ! function_exists( 'studentup_qual_count' ) ) {
		return '';
	}
	$out = '';
	foreach ( studentup_qual_terms() as $slug => $label ) {
		if ( studentup_qual_count( $slug ) < 1 ) {
			continue;
		}
		$out .= '<a href="' . esc_url( studentup_qual_page_url( $slug ) ) . '"'
			. ( $slug === $current ? ' class="on" aria-current="page"' : '' ) . '>'
			. esc_html( $label ) . ' Jobs</a>';
	}
	if ( '' === $out ) {
		return '';
	}
	return '<nav class="su-qual-links" aria-label="Jobs by qualification">' . $out . '</nav>';
}

// Jobs board (/latest-jobs/) + qual pages print this row (template hook).
add_action( 'studentup_qual_links_row', function () {
	echo studentup_qual_pages_links( studentup_qual_page_slug() ); // phpcs:ignore WordPress.Security.EscapeOutput -- escaped inside
} );

// Core sitemap: list the qualification pages that have posts.
add_action( 'init', function () {
	if ( ! function_exists( 'wp_register_sitemap_provider' ) || ! class_exists( 'WP_Sitemaps_Provider' ) ) {
		return;
	}
	if ( ! class_exists( 'StudentUp_Qual_Sitemap' ) ) {
		class StudentUp_Qual_Sitemap extends WP_Sitemaps_Provider {
			public function __construct() {
				$this->name        = 'qualification';
				$this->object_type = 'qualification';
			}
			public function get_url_list( $page_num, $object_subtype = '' ) {
				$urls = array();
				if ( $page_num > 1 || ! function_exists( 'studentup_qual_count' ) ) {
					return $urls;
				}
				foreach ( studentup_qual_terms() as $slug => $label ) {
					if ( studentup_qual_count( $slug ) > 0 ) {
						$urls[] = array( 'loc' => studentup_qual_page_url( $slug ) );
					}
				}
				return $urls;
			}
			public function get_max_num_pages( $object_subtype = '' ) {
				return 1;
			}
		}
	}
	wp_register_sitemap_provider( 'qualification', new StudentUp_Qual_Sitemap() );
}, 20 );

// Breadcrumb / archive title on the route ("Archives" → "Degree Jobs").
add_filter( 'get_the_archive_title', function ( $title ) {
	$s = studentup_qual_page_slug();
	return $s ? studentup_qual_page_label( $s ) . ' Jobs' : $title;
} );
