<?php
/**
 * v312 — AUTO CACHE PURGE on theme version change.
 *
 * Why: live site kept serving OLD CSS/JS after theme uploads (LiteSpeed / CDN /
 * combined CSS) → quiz questions hidden, old trending strip, old footer. Now the
 * first admin request after a new theme version purges every known page cache
 * + CSS/JS optimiser cache automatically, and shows a one-line notice.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Purge every cache layer we can reach (all calls are guarded; no fatal if a plugin is absent).
 *
 * @return string[] names of layers purged.
 */
function studentup_purge_all_caches() {
	$done = array();
	// LiteSpeed Cache (pages + CSS/JS combine + object + CCSS).
	if ( has_action( 'litespeed_purge_all' ) || defined( 'LSCWP_V' ) ) {
		do_action( 'litespeed_purge_all' );
		do_action( 'litespeed_purge_cssjs' );
		$done[] = 'LiteSpeed';
	}
	if ( function_exists( 'wp_cache_clear_cache' ) ) {
		wp_cache_clear_cache();
		$done[] = 'WP Super Cache';
	}
	if ( function_exists( 'w3tc_flush_all' ) ) {
		w3tc_flush_all();
		$done[] = 'W3 Total Cache';
	}
	if ( function_exists( 'rocket_clean_domain' ) ) {
		rocket_clean_domain();
		if ( function_exists( 'rocket_clean_minify' ) ) {
			rocket_clean_minify();
		}
		$done[] = 'WP Rocket';
	}
	if ( function_exists( 'wpfc_clear_all_cache' ) ) {
		wpfc_clear_all_cache( true );
		$done[] = 'WP Fastest Cache';
	}
	if ( class_exists( 'autoptimizeCache' ) && method_exists( 'autoptimizeCache', 'clearall' ) ) {
		autoptimizeCache::clearall();
		$done[] = 'Autoptimize';
	}
	if ( function_exists( 'sg_cachepress_purge_cache' ) ) {
		sg_cachepress_purge_cache();
		$done[] = 'SiteGround';
	}
	if ( class_exists( 'Breeze_PurgeCache' ) && method_exists( 'Breeze_PurgeCache', 'breeze_cache_flush' ) ) {
		Breeze_PurgeCache::breeze_cache_flush();
		$done[] = 'Breeze';
	}
	if ( function_exists( 'wp_cache_flush' ) ) {
		wp_cache_flush();
	}
	do_action( 'cache_enabler_clear_complete_cache' );
	do_action( 'studentup_after_purge', $done );
	return $done;
}

/**
 * Version change detector — runs once per theme version (admin side), and on activation.
 */
function studentup_purge_on_version_change() {
	if ( ! is_admin() || wp_doing_ajax() ) {
		return;
	}
	$cur = defined( 'STUDENTUP_VERSION' ) ? (string) STUDENTUP_VERSION : '0';
	if ( get_option( 'studentup_purged_version' ) === $cur ) {
		return;
	}
	update_option( 'studentup_purged_version', $cur, false );
	$done = studentup_purge_all_caches();
	set_transient( 'studentup_purge_notice', $done ? implode( ', ', $done ) : 'WordPress object cache', 120 );
}
add_action( 'admin_init', 'studentup_purge_on_version_change', 5 );
add_action( 'after_switch_theme', 'studentup_purge_all_caches', 30 );

/**
 * One-line admin notice after an automatic purge.
 */
function studentup_purge_notice() {
	$what = get_transient( 'studentup_purge_notice' );
	if ( ! $what || ! current_user_can( 'edit_theme_options' ) ) {
		return;
	}
	delete_transient( 'studentup_purge_notice' );
	printf(
		'<div class="notice notice-success is-dismissible"><p><b>StudentUp %1$s</b> — cache purged (%2$s). Phone/laptop lo hard refresh (Ctrl+Shift+R) cheyandi.</p></div>',
		esc_html( (string) STUDENTUP_VERSION ),
		esc_html( (string) $what )
	);
}
add_action( 'admin_notices', 'studentup_purge_notice' );

/**
 * Front-end safety: if a CDN/page cache still serves an old HTML page, make the stylesheet
 * URLs themselves carry the version (already) AND send no-transform so optimisers don't
 * re-combine theme CSS into a stale bundle.
 */
function studentup_no_transform_headers() {
	if ( ! is_admin() && ! headers_sent() ) {
		header( 'Cache-Control: no-transform', false );
	}
}
add_action( 'send_headers', 'studentup_no_transform_headers' );
