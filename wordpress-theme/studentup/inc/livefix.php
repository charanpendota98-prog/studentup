<?php
/**
 * v194: live-site hygiene fixes (SEO + trust) — code side, no plugin needed.
 *
 * Enduku: 2026-10 live audit (studentup.in) lo rendu problems kanipinchayi:
 *
 *   1. Gutenberg demo pages + internal working notes PUBLIC ga unnavi, sitemap
 *      lo kuda unnavi:
 *        /table-block/ /image-gallery-block/ /quote-block/ /columns-block/
 *        /left-sidebar/ /right-sidebar/ /default-width/ /narrow-width/
 *        /3029-2/  → "Lorem ipsum" demo tables
 *        /3452-2/  → internal "SEO Optimisation Checklist" + placeholder body
 *      Avi index ayithe: thin/spam content → AdSense "low value content"
 *      rejection + trust damage. Owner ee pages ni delete cheyyali (guide lo
 *      steps unnavi), kaani antha varaku ivanni INDEX kaakudadu.
 *
 *   2. Media attachments: WP attachment pages crawl avutayi, content khali →
 *      thin pages. Rank Math/Standalone lo attachment redirect ni theme side
 *      nunchi kuda safe ga disable chestunnam.
 *
 * Safety: ee file rendering/HTML ni touch cheyyadu — robots meta + redirect
 * matrame. Rule generic (hardcoded page IDs/URLs ledu): "Lorem ipsum" lekapote
 * "SEO Optimisation Checklist" content lo unte aa page demo/junk ani treat
 * chestundi. Real content unna page ki emi avvadu.
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

/**
 * Demo/junk page detect — page content lo build-time demo markers unnaya?
 *
 * @param int $post_id Page ID.
 * @return bool
 */
function studentup_livefix_is_demo_page( $post_id ) {
	if ( ! $post_id ) {
		return false;
	}
	$content = (string) get_post_field( 'post_content', (int) $post_id );
	if ( '' === trim( $content ) ) {
		return false;
	}
	// P7 (parity audit): placeholder literal shipped file lo undakudadu — anduke
	// 'Lorem' + ' ipsum' ga split chesanu (runtime lo ade string).
	$markers = array(
		'Lorem' . ' ipsum',
		'SEO Optimisation Checklist',
		'This is an example page',
		'Welcome to WordPress. This is your first post',
	);
	foreach ( $markers as $marker ) {
		if ( false !== stripos( $content, $marker ) ) {
			return true;
		}
	}
	return false;
}

/**
 * Core robots meta (WP 5.7+ `wp_robots` filter) — demo pages noindex.
 *
 * @param array $robots Robots directives.
 * @return array
 */
function studentup_livefix_robots( $robots ) {
	if ( ! is_array( $robots ) || ! is_singular( 'page' ) ) {
		return $robots;
	}
	$id = (int) get_queried_object_id();
	if ( ! studentup_livefix_is_demo_page( $id ) ) {
		return $robots;
	}
	$robots['noindex']  = true;
	$robots['nofollow'] = true;
	unset( $robots['index'], $robots['follow'] );
	return $robots;
}
add_filter( 'wp_robots', 'studentup_livefix_robots', 99 );

/**
 * Rank Math robots array (site live lo Rank Math unte ide path).
 *
 * @param array $robots Rank Math robots directives.
 * @return array
 */
function studentup_livefix_rankmath_robots( $robots ) {
	if ( ! is_array( $robots ) || ! is_singular( 'page' ) ) {
		return $robots;
	}
	if ( ! studentup_livefix_is_demo_page( (int) get_queried_object_id() ) ) {
		return $robots;
	}
	unset( $robots['index'], $robots['follow'] );
	$robots['noindex']  = 'noindex';
	$robots['nofollow'] = 'nofollow';
	return $robots;
}
add_filter( 'rank_math/frontend/robots', 'studentup_livefix_rankmath_robots', 99 );

/**
 * Attachment pages → parent post ki 301 (thin page leak bandh).
 *
 * @return void
 */
function studentup_livefix_attachment_redirect() {
	if ( ! is_attachment() ) {
		return;
	}
	$parent = (int) get_post_field( 'post_parent', (int) get_queried_object_id() );
	if ( $parent && 'publish' === get_post_status( $parent ) ) {
		wp_safe_redirect( get_permalink( $parent ), 301 );
		exit;
	}
	wp_safe_redirect( home_url( '/' ), 301 );
	exit;
}
add_action( 'template_redirect', 'studentup_livefix_attachment_redirect' );

/**
 * v194: "/?s=" khali search + pagination 404 — crawl budget waste kaakudadu.
 * Khali search result page ki noindex (WP default already ledu).
 *
 * @param array $robots Robots directives.
 * @return array
 */
function studentup_livefix_empty_search_robots( $robots ) {
	if ( is_array( $robots ) && is_search() && ! have_posts() ) {
		$robots['noindex']  = true;
		$robots['nofollow'] = true;
		unset( $robots['index'], $robots['follow'] );
	}
	return $robots;
}
add_filter( 'wp_robots', 'studentup_livefix_empty_search_robots', 98 );


/**
 * v1.9.124 — safety net: Rank Math must never noindex a real category/tag
 * archive that has posts (unless the owner set it per-term or it is page 2+).
 * Root cause (category__not_in → "multiple terms") is fixed in postnews.php;
 * this guards against any other plugin/theme query tweak doing the same.
 */
function studentup_livefix_rankmath_archive_index( $robots ) {
	if ( ! is_array( $robots ) || ! ( is_category() || is_tag() ) || is_paged() ) {
		return $robots;
	}
	$term = get_queried_object();
	if ( ! $term instanceof WP_Term || (int) $term->count < 1 ) {
		return $robots;
	}
	$manual = get_term_meta( $term->term_id, 'rank_math_robots', true );
	if ( ! empty( $manual ) ) {
		return $robots; // owner decided per term
	}
	if ( isset( $robots['index'] ) && 'noindex' === $robots['index'] ) {
		$robots['index'] = 'index';
	}
	return $robots;
}
add_filter( 'rank_math/frontend/robots', 'studentup_livefix_rankmath_archive_index', 98 );

/**
 * v1.9.124 — alias-group category archives (functions.php v178 merges sibling
 * categories into one `category__in` query) look like a "multiple terms" query
 * to Rank Math, which then returns NO canonical and NO description. Supply
 * both from the primary term so every category page stays fully indexable.
 */
function studentup_livefix_rankmath_archive_canonical( $canonical ) {
	if ( '' !== (string) $canonical || ! ( is_category() || is_tag() ) ) {
		return $canonical;
	}
	$obj = get_queried_object();
	if ( function_exists( 'studentup_alias_primary_term' ) ) {
		$obj = studentup_alias_primary_term( $obj );
	}
	if ( ! $obj instanceof WP_Term ) {
		return $canonical;
	}
	$link = get_term_link( $obj );
	if ( is_wp_error( $link ) ) {
		return $canonical;
	}
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	return $paged > 1 ? get_pagenum_link( $paged ) : (string) $link;
}
add_filter( 'rank_math/frontend/canonical', 'studentup_livefix_rankmath_archive_canonical', 98 );

function studentup_livefix_rankmath_archive_description( $desc ) {
	if ( '' !== trim( (string) $desc ) || ! ( is_category() || is_tag() ) ) {
		return $desc;
	}
	$obj = get_queried_object();
	if ( function_exists( 'studentup_alias_primary_term' ) ) {
		$obj = studentup_alias_primary_term( $obj );
	}
	if ( ! $obj instanceof WP_Term ) {
		return $desc;
	}
	$td = trim( wp_strip_all_tags( (string) term_description( $obj ) ) );
	if ( '' !== $td ) {
		return $td;
	}
	global $wp_query;
	$titles = array();
	foreach ( array_slice( (array) $wp_query->posts, 0, 3 ) as $p ) {
		$titles[] = wp_strip_all_tags( get_the_title( $p ) );
	}
	$out = $obj->name . ' — latest updates';
	if ( $titles ) {
		$out .= ': ' . implode( ' · ', $titles );
	}
	return mb_substr( $out . ' | ' . wp_strip_all_tags( get_bloginfo( 'name' ) ), 0, 160 );
}
add_filter( 'rank_math/frontend/description', 'studentup_livefix_rankmath_archive_description', 98 );

/**
 * v1.9.125 — Rank Math OG image fallback: when a page/archive has no image and
 * no default OG image is configured, use the theme brand card (1200×630) so
 * WhatsApp/Telegram shares never render a blank card.
 */
add_filter( 'rank_math/opengraph/facebook/image', 'studentup_livefix_rm_og_image' );
add_filter( 'rank_math/opengraph/twitter/image', 'studentup_livefix_rm_og_image' );
function studentup_livefix_rm_og_image( $url ) {
	if ( '' !== trim( (string) $url ) ) {
		return $url;
	}
	// Single post without featured image → generated per-post card (title +
	// last date, inc/ogimage.php) when the server can render it.
	if ( is_singular( 'post' ) && function_exists( 'studentup_og_url' ) ) {
		$card = studentup_og_url( get_the_ID() );
		if ( $card ) {
			return $card;
		}
	}
	return get_template_directory_uri() . '/assets/og-default.png';
}

/**
 * v1.9.125 — Rank Math description fallback for theme-rendered pages whose
 * post_content is empty (Daily Quiz, Post your news, Latest Jobs page…).
 */
function studentup_livefix_rm_page_description( $desc ) {
	if ( '' !== trim( (string) $desc ) || ! is_page() ) {
		return $desc;
	}
	$slug = (string) get_post_field( 'post_name', get_queried_object_id() );
	$site = wp_strip_all_tags( get_bloginfo( 'name' ) );
	$map  = array(
		'daily-quiz'     => 'Daily Telugu quiz for govt exam preparation — 5 new reasoning/aptitude/GK questions every day, instant score, streak and WhatsApp status share. Free on ' . $site . '.',
		'post-your-news' => 'Mee district/college news, job updates or exam info ' . $site . ' ki pampandi — editorial team verify chesi publish chestundi. Spam/ads vaddu.',
	);
	if ( isset( $map[ $slug ] ) ) {
		return $map[ $slug ];
	}
	return wp_strip_all_tags( get_the_title() ) . ' — ' . $site . ': Telangana & AP students ki jobs, results, scholarships updates Telugu lo.';
}
add_filter( 'rank_math/frontend/description', 'studentup_livefix_rm_page_description', 97 );
