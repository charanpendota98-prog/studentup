<?php
/**
 * v80: lightweight 301 redirect manager (P29).
 *
 * Enduku: slug marina/old URL unna prathi link link-juice pothundi + 404.
 * RankMath lekapoina redirects pani cheyyali — adi idi. Owner format
 * (StudentUp → Advanced → redirects_json):
 *   {"/old-slug/": "/new-slug/", "/jobs/old/": "/jobs/ts-jobs/"}
 *
 * Rules (master prompt P29):
 *   · exact-path match (query string ignore — tracking params safe)
 *   · self/loop target aite skip (redirect loop impossible)
 *   · target kuda map lo unte final target ki DIRECT 301 (chain ledu)
 *   · only relative paths (open-redirect impossible — external URL reject)
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Raw map (assoc array) — invalid JSON aite empty.
 *
 * @return array<string,string>
 */
function studentup_redirect_map() {
	$raw = (string) studentup_opt( 'redirects_json', '' );
	if ( '' === trim( $raw ) ) {
		return array();
	}
	$map = json_decode( $raw, true );
	if ( ! is_array( $map ) ) {
		return array();
	}
	$out = array();
	foreach ( $map as $from => $to ) {
		$from = '/' . ltrim( trim( (string) $from ), '/' );
		$to   = trim( (string) $to );
		if ( '' === $from || '' === $to || $from === $to ) {
			continue;   // self-target = loop → skip
		}
		if ( preg_match( '#^https?://#i', $to ) || strpos( $to, '//' ) === 0 ) {
			continue;   // external target = open redirect → reject
		}
		$out[ trailingslashit( $from ) ] = '/' . ltrim( $to, '/' );
	}
	return $out;
}

/**
 * Chain resolve: /a→/b→/c aite /a nunchi DIRECT /c (max 5 hops, loop-safe).
 */
function studentup_redirect_resolve( $path, $map ) {
	$seen = array();
	$cur  = trailingslashit( $path );
	for ( $i = 0; $i < 5; $i++ ) {
		if ( ! isset( $map[ $cur ] ) ) {
			return $cur;   // chain end (leda map ledu)
		}
		if ( isset( $seen[ $cur ] ) ) {
			return '';     // loop → redirect vaddu (404 normal)
		}
		$seen[ $cur ] = true;
		$cur          = trailingslashit( $map[ $cur ] );
	}
	return $cur;
}

function studentup_redirect_maybe() {
	// 404 aina pages kevalam — normal pages ni touch cheyyamu.
	if ( is_admin() || ! is_404() ) {
		return;
	}
	$map = studentup_redirect_map();
	if ( ! $map ) {
		return;
	}
	$path = (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
	if ( '' === $path ) {
		$path = '/';
	}
	$final = studentup_redirect_resolve( $path, $map );
	if ( '' === $final || trailingslashit( $path ) === $final ) {
		return;   // loop leda no-match → normal 404
	}
	wp_safe_redirect( home_url( $final ), 301 );
	exit;
}
add_action( 'template_redirect', 'studentup_redirect_maybe', 2 );

/**
 * v1.9.173: duplicate-post 301. Bot `--dedupe-posts --apply` keeps ONE post
 * per notification and turns the twins into drafts with their Rank Math
 * canonical pointed at the keeper. A drafted twin's old URL (already indexed /
 * shared on WhatsApp) would 404 — here it 301s to the keeper instead, so
 * links and ranking signals consolidate. Only fires on a 404, only for a
 * non-public post whose canonical is an internal URL on this site.
 */
function studentup_redirect_merged_duplicate() {
	if ( is_admin() || ! is_404() ) {
		return;
	}
	$path = trim( (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH ), '/' ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
	if ( '' === $path || false !== strpos( $path, '/' ) ) {
		return; // only top-level post slugs (permalink /%postname%/).
	}
	$slug = sanitize_title( $path );
	if ( '' === $slug ) {
		return;
	}
	$q = new WP_Query(
		array(
			'name'                   => $slug,
			'post_type'              => 'post',
			'post_status'            => array( 'draft', 'pending', 'private', 'future' ),
			'posts_per_page'         => 1,
			'fields'                 => 'ids',
			'no_found_rows'          => true,
			'update_post_term_cache' => false,
		)
	);
	if ( empty( $q->posts ) ) {
		return;
	}
	$pid    = (int) $q->posts[0];
	$target = trim( (string) get_post_meta( $pid, 'rank_math_canonical_url', true ) );
	if ( '' === $target ) {
		return;
	}
	$home = wp_parse_url( home_url( '/' ), PHP_URL_HOST );
	$host = wp_parse_url( $target, PHP_URL_HOST );
	if ( ! $host || strtolower( $host ) !== strtolower( (string) $home ) ) {
		return; // internal targets only (open-redirect impossible).
	}
	$tpath = trailingslashit( (string) wp_parse_url( $target, PHP_URL_PATH ) );
	if ( '/' . $slug . '/' === $tpath ) {
		return; // self → loop; normal 404.
	}
	$dest = get_page_by_path( trim( $tpath, '/' ), OBJECT, 'post' );
	if ( ! $dest || 'publish' !== $dest->post_status ) {
		return; // keeper gone too → honest 404.
	}
	wp_safe_redirect( get_permalink( $dest ), 301 );
	exit;
}
add_action( 'template_redirect', 'studentup_redirect_merged_duplicate', 3 );
