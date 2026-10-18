<?php
/**
 * v1.9.123 — Programmatic SEO: organisation landing pages.
 *
 * /org/tspsc/ · /org/appsc/ · /org/ssc/ · /org/rrb/ … (+ /page/N/)
 *
 * Why: "TSPSC notifications 2026", "APPSC latest jobs", "SSC CGL 2026" are
 * entity searches with steady volume; a page per organisation that lists
 * every StudentUp post about it (newest first) + the official site link is
 * the standard topic-cluster hub top job portals rank with. Posts match by
 * title (organisation name/alias in the post title) — real data only; an
 * organisation with no matching posts returns 404 (no thin pages).
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Organisation map: slug => [ short name, full name, official url, aliases[] ].
 * Official URLs are the well-known public portals (links only, no claims).
 *
 * @return array
 */
function studentup_org_map() {
	return array(
		'tspsc'     => array( 'TSPSC', 'Telangana State Public Service Commission', 'https://www.tspsc.gov.in/', array( 'tspsc', 'tgpsc' ) ),
		'appsc'     => array( 'APPSC', 'Andhra Pradesh Public Service Commission', 'https://psc.ap.gov.in/', array( 'appsc' ) ),
		'ts-police' => array( 'TS Police', 'Telangana State Level Police Recruitment Board', 'https://www.tslprb.in/', array( 'ts police', 'tslprb', 'telangana police' ) ),
		'ap-police' => array( 'AP Police', 'Andhra Pradesh State Level Police Recruitment Board', 'https://slprb.ap.gov.in/', array( 'ap police', 'slprb', 'andhra pradesh police' ) ),
		'ts-dsc'    => array( 'TS DSC', 'Telangana DSC (Teacher Recruitment)', 'https://schooledu.telangana.gov.in/', array( 'ts dsc', 'tg dsc', 'telangana dsc' ) ),
		'ap-dsc'    => array( 'AP DSC', 'Andhra Pradesh DSC (Teacher Recruitment)', 'https://apdsc.apcfss.in/', array( 'ap dsc', 'andhra pradesh dsc' ) ),
		'ssc'       => array( 'SSC', 'Staff Selection Commission', 'https://ssc.gov.in/', array( 'ssc cgl', 'ssc chsl', 'ssc gd', 'ssc mts', 'ssc je', 'ssc cpo', 'ssc stenographer', 'staff selection commission' ) ),
		'rrb'       => array( 'RRB', 'Railway Recruitment Boards', 'https://indianrailways.gov.in/', array( 'rrb', 'railway recruitment', 'rrc ' ) ),
		'upsc'      => array( 'UPSC', 'Union Public Service Commission', 'https://upsc.gov.in/', array( 'upsc', 'civil services', 'nda ', 'cds ' ) ),
		'ibps'      => array( 'IBPS', 'Institute of Banking Personnel Selection', 'https://www.ibps.in/', array( 'ibps' ) ),
		'sbi'       => array( 'SBI', 'State Bank of India', 'https://sbi.co.in/web/careers', array( 'sbi' ) ),
		'india-post' => array( 'India Post', 'India Post (GDS / Postal)', 'https://indiapostgdsonline.gov.in/', array( 'india post', 'gds ', 'postal', 'post office' ) ),
		'singareni' => array( 'Singareni', 'Singareni Collieries Company Limited', 'https://scclmines.com/', array( 'singareni', 'sccl' ) ),
		'isro'      => array( 'ISRO', 'Indian Space Research Organisation', 'https://www.isro.gov.in/Careers.html', array( 'isro' ) ),
		'drdo'      => array( 'DRDO', 'Defence Research and Development Organisation', 'https://www.drdo.gov.in/', array( 'drdo' ) ),
		'indian-army' => array( 'Indian Army', 'Indian Army', 'https://joinindianarmy.nic.in/', array( 'indian army', 'agniveer army', 'army recruitment' ) ),
		'indian-navy' => array( 'Indian Navy', 'Indian Navy', 'https://www.joinindiannavy.gov.in/', array( 'indian navy', 'navy agniveer' ) ),
		'air-force' => array( 'Indian Air Force', 'Indian Air Force', 'https://agnipathvayu.cdac.in/', array( 'air force', 'iaf ', 'agniveer vayu' ) ),
		'gurukulam' => array( 'Gurukulam', 'TS / AP Gurukulam Societies', 'https://tgprb.telangana.gov.in/', array( 'gurukulam', 'tgprb', 'treirb' ) ),
		'nhm'       => array( 'NHM', 'National Health Mission (TS / AP)', 'https://nhm.gov.in/', array( 'nhm ', 'national health mission' ) ),
		'bsnl'      => array( 'BSNL', 'Bharat Sanchar Nigam Limited', 'https://www.bsnl.co.in/', array( 'bsnl' ) ),
		'ecil'      => array( 'ECIL', 'Electronics Corporation of India Limited', 'https://www.ecil.co.in/', array( 'ecil' ) ),
		'ntpc'      => array( 'NTPC', 'NTPC Limited', 'https://careers.ntpc.co.in/', array( 'ntpc' ) ),
		'lic'       => array( 'LIC', 'Life Insurance Corporation of India', 'https://licindia.in/careers', array( 'lic ' ) ),
		'tet'       => array( 'TET', 'TS / AP Teacher Eligibility Test', 'https://tstet.cgg.gov.in/', array( 'tet ', 'tstet', 'aptet' ) ),
		'eamcet'    => array( 'EAPCET', 'TS / AP EAPCET (EAMCET)', 'https://eapcet.tsche.ac.in/', array( 'eamcet', 'eapcet' ) ),
	);
}

function studentup_org_page_slug() {
	$s   = (string) get_query_var( 'studentup_org_page' );
	$map = studentup_org_map();
	return isset( $map[ $s ] ) ? $s : '';
}

function studentup_org_page_url( $slug ) {
	return home_url( '/org/' . rawurlencode( $slug ) . '/' );
}

/**
 * Detect organisation slug from a post title (first match wins).
 *
 * @param string $title post title.
 * @return string slug|''.
 */
function studentup_org_from_title( $title ) {
	$t = ' ' . mb_strtolower( wp_strip_all_tags( (string) $title ) ) . ' ';
	$t = preg_replace( '/[\s\x{2013}\x{2014}:,\-]+/u', ' ', $t ); // "TSPSC-Group" / "SSC: CGL" boundaries
	foreach ( studentup_org_map() as $slug => $row ) {
		foreach ( $row[3] as $alias ) {
			if ( false !== strpos( $t, ' ' . $alias ) ) {
				return $slug;
			}
		}
	}
	return '';
}

/* ---------------------------------------------------------------- routing */

function studentup_org_pages_rewrite() {
	$keys = implode( '|', array_map( 'preg_quote', array_keys( studentup_org_map() ) ) );
	add_rewrite_rule( '^org/(' . $keys . ')/page/([0-9]+)/?$', 'index.php?studentup_org_page=$matches[1]&paged=$matches[2]', 'top' );
	add_rewrite_rule( '^org/(' . $keys . ')/?$', 'index.php?studentup_org_page=$matches[1]', 'top' );
}
add_action( 'init', 'studentup_org_pages_rewrite', 1 );

add_filter( 'query_vars', function ( $vars ) {
	$vars[] = 'studentup_org_page';
	return $vars;
} );

add_action( 'init', function () {
	if ( get_option( 'studentup_org_pages_flushed' ) !== '1' ) {
		studentup_org_pages_rewrite();
		flush_rewrite_rules( false );
		update_option( 'studentup_org_pages_flushed', '1' );
	}
}, 99 );

function studentup_org_pages_query( $q ) {
	if ( is_admin() || ! $q->is_main_query() ) {
		return;
	}
	$slug = sanitize_key( (string) $q->get( 'studentup_org_page' ) );
	$map  = studentup_org_map();
	if ( '' === $slug || ! isset( $map[ $slug ] ) ) {
		return;
	}
	$q->set( 'post_type', 'post' );
	$q->set( 'post_status', 'publish' );
	$q->set( 'ignore_sticky_posts', true );
	$q->set( 'studentup_org_aliases', $map[ $slug ][3] );
	if ( function_exists( 'studentup_breaking_term_ids' ) ) {
		$q->set( 'category__not_in', array_map( 'intval', (array) studentup_breaking_term_ids() ) );
	}
	$q->is_home    = false;
	$q->is_archive = true;
}
add_action( 'pre_get_posts', 'studentup_org_pages_query', 8 );

// Title match (organisation alias in post_title) — indexed-friendly LIKE on title only.
add_filter( 'posts_where', function ( $where, $q ) {
	$aliases = $q->get( 'studentup_org_aliases' );
	if ( empty( $aliases ) || ! is_array( $aliases ) ) {
		return $where;
	}
	global $wpdb;
	$parts = array();
	foreach ( $aliases as $a ) {
		// word-start boundary: " alias" anywhere or "alias" at the very start
		// (so "lic " never matches "public", "nda " never matches "Kondapur").
		$parts[] = $wpdb->prepare( "{$wpdb->posts}.post_title LIKE %s", '% ' . $wpdb->esc_like( $a ) . '%' );
		$parts[] = $wpdb->prepare( "{$wpdb->posts}.post_title LIKE %s", $wpdb->esc_like( $a ) . '%' );
	}
	return $where . ' AND (' . implode( ' OR ', $parts ) . ')';
}, 10, 2 );

function studentup_org_pages_template( $template ) {
	$slug = studentup_org_page_slug();
	if ( '' === $slug ) {
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
	return get_template_directory() . '/page-org.php';
}
add_filter( 'template_include', 'studentup_org_pages_template' );

/* -------------------------------------------------------------------- SEO */

function studentup_org_page_h1( $slug ) {
	$row = studentup_org_map()[ $slug ];
	return sprintf( '%s Notifications %s — Latest Jobs, Results & Hall Tickets', $row[0], gmdate( 'Y' ) );
}

function studentup_org_page_title( $slug ) {
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	$t     = studentup_org_page_h1( $slug ) . ' — ' . wp_strip_all_tags( get_bloginfo( 'name' ) );
	return $paged > 1 ? $t . ' — Page ' . $paged : $t;
}

function studentup_org_page_desc( $slug ) {
	global $wp_query;
	$row    = studentup_org_map()[ $slug ];
	$n      = isset( $wp_query->found_posts ) ? (int) $wp_query->found_posts : 0;
	$titles = array();
	foreach ( array_slice( (array) $wp_query->posts, 0, 2 ) as $p ) {
		$titles[] = wp_strip_all_tags( get_the_title( $p ) );
	}
	$d = sprintf( '%s (%s) — %d updates Telugu lo: notifications, last dates, results, hall tickets, official link.', $row[0], $row[1], $n );
	if ( $titles ) {
		$d .= ' Latest: ' . implode( ' · ', $titles ) . '.';
	}
	return $d;
}

add_filter( 'pre_get_document_title', function ( $t ) {
	$s = studentup_org_page_slug();
	return $s ? studentup_org_page_title( $s ) : $t;
}, 99 );
add_filter( 'rank_math/frontend/title', function ( $t ) {
	$s = studentup_org_page_slug();
	return $s ? studentup_org_page_title( $s ) : $t;
}, 99 );
add_filter( 'rank_math/frontend/description', function ( $d ) {
	$s = studentup_org_page_slug();
	return $s ? studentup_org_page_desc( $s ) : $d;
}, 99 );
add_filter( 'rank_math/frontend/canonical', function ( $c ) {
	$s = studentup_org_page_slug();
	if ( ! $s ) {
		return $c;
	}
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	return $paged > 1 ? get_pagenum_link( $paged ) : studentup_org_page_url( $s );
}, 99 );
add_filter( 'rank_math/opengraph/url', function ( $u ) {
	$s = studentup_org_page_slug();
	return $s ? studentup_org_page_url( $s ) : $u;
}, 99 );
add_filter( 'studentup_seo_list_url', function ( $u ) {
	$s = studentup_org_page_slug();
	if ( ! $s ) {
		return $u;
	}
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	return $paged > 1 ? get_pagenum_link( $paged ) : studentup_org_page_url( $s );
} );
add_filter( 'studentup_seo_list_title', function ( $t ) {
	$s = studentup_org_page_slug();
	return $s ? studentup_org_page_h1( $s ) : $t;
} );
add_filter( 'studentup_seo_list_desc', function ( $d ) {
	$s = studentup_org_page_slug();
	return $s ? studentup_org_page_desc( $s ) : $d;
} );
add_filter( 'get_the_archive_title', function ( $title ) {
	$s = studentup_org_page_slug();
	return $s ? studentup_org_map()[ $s ][0] : $title;
} );
add_filter( 'wp_robots', function ( $robots ) {
	if ( studentup_org_page_slug() ) {
		unset( $robots['noindex'] );
		$robots['max-image-preview'] = 'large';
	}
	return $robots;
}, 99 );

/**
 * CollectionPage + ItemList + the Organization entity (about) — real items only.
 */
function studentup_org_page_schema() {
	if ( class_exists( 'RankMath' ) ) {
		return;   // v1.9.127: merged into Rank Math graph (inc/schema.php) — no 2nd CollectionPage.
	}
	$s = studentup_org_page_slug();
	if ( ! $s ) {
		return;
	}
	global $wp_query;
	$row   = studentup_org_map()[ $s ];
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
		'@id'        => studentup_org_page_url( $s ) . '#page',
		'url'        => studentup_org_page_url( $s ),
		'name'       => studentup_org_page_h1( $s ),
		'inLanguage' => 'te-IN',
		'isPartOf'   => array( '@id' => home_url( '/' ) . '#website' ),
		'about'      => array(
			'@type' => 'Organization',
			'name'  => $row[1],
			'url'   => $row[2],
		),
		'mainEntity' => array(
			'@type'           => 'ItemList',
			'numberOfItems'   => (int) $wp_query->found_posts,
			'itemListElement' => $items,
		),
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_org_page_schema', 8 );

/**
 * v1.9.136: ids of other posts about the same organisation as $post_id
 * (title alias match — the same rule the /org/ pages use). Newest first.
 *
 * @param int   $post_id Current post.
 * @param int   $limit   Max ids.
 * @param int[] $exclude Extra ids to skip.
 * @return int[]
 */
function studentup_org_related_ids( $post_id, $limit = 2, $exclude = array() ) {
	$slug = studentup_org_from_title( get_the_title( $post_id ) );
	if ( '' === $slug ) {
		return array();
	}
	$args = array(
		'fields'                => 'ids',
		'post_type'             => 'post',
		'post_status'           => 'publish',
		'posts_per_page'        => (int) $limit,
		'post__not_in'          => array_merge( array( (int) $post_id ), array_map( 'intval', (array) $exclude ) ),
		'ignore_sticky_posts'   => true,
		'no_found_rows'         => true,
		'update_post_meta_cache' => false,
		'update_post_term_cache' => false,
		'studentup_org_aliases' => studentup_org_map()[ $slug ][3],
	);
	if ( function_exists( 'studentup_breaking_term_ids' ) ) {
		$args['category__not_in'] = array_map( 'intval', (array) studentup_breaking_term_ids() );
	}
	$q = new WP_Query( $args );
	return array_map( 'intval', (array) $q->posts );
}

/* --------------------------------------------------------- internal links */

/**
 * Single post: "More updates: <category> · <ORG>" — org link only when the
 * post title matches a known organisation (real relation, no guess).
 */
add_filter( 'the_content', function ( $content ) {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() ) {
		return $content;
	}
	$slug = studentup_org_from_title( get_the_title() );
	if ( '' === $slug || false !== strpos( $content, 'su-org-link' ) ) {
		return $content;
	}
	$row  = studentup_org_map()[ $slug ];
	$link = ' · <a class="su-org-link" href="' . esc_url( studentup_org_page_url( $slug ) ) . '">' . esc_html( $row[0] ) . ' updates</a>';
	if ( false !== strpos( $content, 'su-parent-link' ) ) {
		return preg_replace( '/(<p class="su-parent-link">.*?)(<\/p>)/s', '$1' . str_replace( '$', '\$', $link ) . '$2', $content, 1 );
	}
	return $content . '<p class="su-parent-link">' . esc_html__( 'More updates:', 'studentup' ) . ltrim( $link, ' ·' ) . '</p>';
}, 31 );

/**
 * Cached list of organisations that currently have posts (for link rows + sitemap).
 *
 * @return array slug => count
 */
function studentup_org_pages_active() {
	$cached = get_transient( 'studentup_org_pages_active' );
	if ( is_array( $cached ) ) {
		return $cached;
	}
	global $wpdb;
	$out = array();
	foreach ( studentup_org_map() as $slug => $row ) {
		$parts = array();
		foreach ( $row[3] as $a ) {
			$parts[] = $wpdb->prepare( 'post_title LIKE %s', '% ' . $wpdb->esc_like( $a ) . '%' );
			$parts[] = $wpdb->prepare( 'post_title LIKE %s', $wpdb->esc_like( $a ) . '%' );
		}
		$n = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='post' AND post_status='publish' AND (" . implode( ' OR ', $parts ) . ')' ); // phpcs:ignore WordPress.DB.PreparedSQL.NotPrepared -- parts prepared above
		if ( $n > 0 ) {
			$out[ $slug ] = $n;
		}
	}
	set_transient( 'studentup_org_pages_active', $out, 15 * MINUTE_IN_SECONDS );
	return $out;
}
add_action( 'save_post_post', function () {
	delete_transient( 'studentup_org_pages_active' );
} );

/**
 * Link row — organisations with posts (wrapping chips).
 *
 * @param string $current active slug.
 * @return string
 */
function studentup_org_pages_links( $current = '' ) {
	$active = studentup_org_pages_active();
	if ( empty( $active ) ) {
		return '';
	}
	$map = studentup_org_map();
	$out = '';
	foreach ( $active as $slug => $n ) {
		$out .= '<a href="' . esc_url( studentup_org_page_url( $slug ) ) . '"'
			. ( $slug === $current ? ' class="on" aria-current="page"' : '' ) . '>'
			. esc_html( $map[ $slug ][0] ) . '</a>';
	}
	return '<nav class="su-qual-links su-org-links" aria-label="Updates by organisation">' . $out . '</nav>';
}
add_action( 'studentup_org_links_row', function () {
	echo studentup_org_pages_links( studentup_org_page_slug() ); // phpcs:ignore WordPress.Security.EscapeOutput -- escaped inside
} );

// Core sitemap provider.
add_action( 'init', function () {
	if ( ! function_exists( 'wp_register_sitemap_provider' ) || ! class_exists( 'WP_Sitemaps_Provider' ) ) {
		return;
	}
	if ( ! class_exists( 'StudentUp_Org_Sitemap' ) ) {
		class StudentUp_Org_Sitemap extends WP_Sitemaps_Provider {
			public function __construct() {
				$this->name        = 'organisation';
				$this->object_type = 'organisation';
			}
			public function get_url_list( $page_num, $object_subtype = '' ) {
				$urls = array();
				if ( $page_num > 1 ) {
					return $urls;
				}
				foreach ( studentup_org_pages_active() as $slug => $n ) {
					$urls[] = array( 'loc' => studentup_org_page_url( $slug ) );
				}
				return $urls;
			}
			public function get_max_num_pages( $object_subtype = '' ) {
				return 1;
			}
		}
	}
	wp_register_sitemap_provider( 'organisation', new StudentUp_Org_Sitemap() );
}, 20 );
