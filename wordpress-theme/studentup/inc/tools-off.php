<?php
/**
 * v248 — TOOLS OFF (owner decision).
 *
 * Owner: "tools em vaddu — age calculator ilaanti vi vaddu, space waste
 * avtundi. Daani badulu SEO + keywords + Rank Math + Google top ranking
 * meeda focus cheyyi."
 *
 * Enduku ide correct:
 *   · Calculators / resume maker / compare / workspace pages = thin,
 *     low-search-volume pages. Avi crawl budget tintayi, internal link
 *     equity ni divide chestayi, AdSense ki "thin content" risk.
 *   · Mobile lo avi screen space tinesayi — money sections kindaki potayi.
 *
 * Em chestundi (code delete cheyyakunda, clean ga OFF):
 *   1. Tool shortcodes anni khaali string return chestayi (page break kaadu).
 *   2. Tool pages (tools/saved/compare/workspace/resume…) → noindex,nofollow
 *      + sitemap nunchi tholagimpu (thin page Google ki pampam).
 *   3. firstrun ikapai aa pages create cheyyadu (inc/firstrun.php v248 filter).
 *   4. Articles lo tool CTA blocks render avvavu.
 *
 * Marali kavali ante: add_filter( 'studentup_tools_enabled', '__return_true' );
 *
 * @package StudentUp
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Tools ON unnaya? Default: OFF (v248 owner decision).
 */
function studentup_tools_enabled() {
	return (bool) apply_filters( 'studentup_tools_enabled', false );
}

/**
 * OFF ayina tool shortcodes list.
 */
function studentup_tools_shortcodes() {
	return array(
		'studentup_age_calc',
		'studentup_fee_calc',
		'studentup_score_calc',
		'studentup_resume_maker',
		'studentup_compare',
		'studentup_saved',
		'studentup_workspace',
		'studentup_syllabus_tracker',
	);
}

/**
 * OFF ayina tool page slugs.
 */
function studentup_tools_slugs() {
	return array( 'tools', 'saved', 'compare', 'workspace', 'resume-maker', 'syllabus-tracker' );
}

/**
 * 1. Shortcodes ni khaali chestam (late priority — original register ayyaka).
 */
function studentup_tools_off_shortcodes() {
	if ( studentup_tools_enabled() ) {
		return;
	}
	foreach ( studentup_tools_shortcodes() as $tag ) {
		remove_all_shortcodes_for_tag_safe( $tag );
	}
}
add_action( 'init', 'studentup_tools_off_shortcodes', 99 );

/**
 * WordPress lo per-tag remove lekapovadam valla chinna helper.
 * (remove_shortcode() unna, re-register cheyyadam safe — khaali return.)
 */
function remove_all_shortcodes_for_tag_safe( $tag ) {
	if ( ! is_string( $tag ) || '' === $tag ) {
		return;
	}
	if ( shortcode_exists( $tag ) ) {
		remove_shortcode( $tag );
	}
	add_shortcode( $tag, '__return_empty_string' );
}

/**
 * Ee page tool page aa?
 */
function studentup_is_tool_page() {
	if ( ! is_page() ) {
		return false;
	}
	$post = get_post();
	if ( ! $post instanceof WP_Post ) {
		return false;
	}
	return in_array( (string) $post->post_name, studentup_tools_slugs(), true );
}

/**
 * 2a. Tool pages → noindex, nofollow (thin content Google index lo vaddu).
 */
function studentup_tools_off_robots( $robots ) {
	if ( studentup_tools_enabled() || ! studentup_is_tool_page() ) {
		return $robots;
	}
	$robots['index']  = 'noindex';
	$robots['follow'] = 'nofollow';
	unset( $robots['max-image-preview'], $robots['max-snippet'] );
	return $robots;
}
add_filter( 'wp_robots', 'studentup_tools_off_robots', 20 );

/**
 * 2b. Sitemap (core + theme) nunchi tool pages ni teesestam.
 */
function studentup_tools_off_sitemap( $args, $post_type ) {
	if ( studentup_tools_enabled() || 'page' !== $post_type ) {
		return $args;
	}
	$ids = array();
	foreach ( studentup_tools_slugs() as $slug ) {
		$page = get_page_by_path( $slug );
		if ( $page instanceof WP_Post ) {
			$ids[] = (int) $page->ID;
		}
	}
	if ( $ids ) {
		$existing              = isset( $args['post__not_in'] ) && is_array( $args['post__not_in'] )
			? $args['post__not_in'] : array();
		$args['post__not_in'] = array_merge( $existing, $ids );
	}
	return $args;
}
add_filter( 'wp_sitemaps_posts_query_args', 'studentup_tools_off_sitemap', 10, 2 );

/**
 * 3. firstrun ikapai tool pages create cheyyadu.
 */
function studentup_tools_off_firstrun( $pages ) {
	if ( studentup_tools_enabled() || ! is_array( $pages ) ) {
		return $pages;
	}
	foreach ( studentup_tools_slugs() as $slug ) {
		unset( $pages[ $slug ] );
	}
	return $pages;
}
add_filter( 'studentup_firstrun_pages', 'studentup_tools_off_firstrun', 10 );
