<?php
/**
 * v1.9.167 Affiliate layer (books / test series / courses).
 *
 * Rules (owner): no new boxes on a post — ONE honest row inside the existing
 * Important Links box; renders ONLY when the owner enabled it, a tag/URL is
 * configured and the post matches a mapping. Never labelled "Sponsored";
 * a plain affiliate disclosure line is shown (Google + consumer honesty).
 *
 * Options (StudentUp Settings → Ads & monetisation):
 *   affiliate_enabled  '0'/'1'
 *   amazon_tag         Amazon Associates tag (e.g. studentup-21) → appended as ?tag=
 *   affiliate_map      JSON: [{"match":"tspsc group 2|group-2","label":"TSPSC Group 2 Books",
 *                              "url":"https://www.amazon.in/s?k=tspsc+group+2+books"}]
 *                      match = case-insensitive regex alternatives against title+slug+category.
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

/**
 * Parse the owner mapping once per request.
 *
 * @return array<int,array<string,string>>
 */
function studentup_affiliate_map() {
	static $map = null;
	if ( null !== $map ) {
		return $map;
	}
	$map = array();
	$raw = json_decode( (string) studentup_opt( 'affiliate_map', '' ), true );
	if ( ! is_array( $raw ) ) {
		return $map;
	}
	foreach ( $raw as $row ) {
		if ( ! is_array( $row ) ) {
			continue;
		}
		$match = isset( $row['match'] ) ? trim( (string) $row['match'] ) : '';
		$url   = isset( $row['url'] ) ? esc_url_raw( (string) $row['url'] ) : '';
		$label = isset( $row['label'] ) ? wp_strip_all_tags( (string) $row['label'] ) : '';
		if ( '' === $match || '' === $url || '' === $label || ! preg_match( '#^https://#i', $url ) ) {
			continue;
		}
		$map[] = array( 'match' => $match, 'url' => $url, 'label' => $label );
	}
	return $map;
}

/**
 * Add the Associates tag to amazon.* URLs when missing.
 *
 * @param string $url destination.
 * @return string
 */
function studentup_affiliate_url( $url ) {
	$tag  = preg_replace( '/[^a-z0-9\-]/i', '', (string) studentup_opt( 'amazon_tag', '' ) );
	$host = (string) wp_parse_url( $url, PHP_URL_HOST );
	if ( $tag && preg_match( '/(^|\.)amazon\./i', $host ) && false === strpos( $url, 'tag=' ) ) {
		$url = add_query_arg( 'tag', $tag, $url );
	}
	return $url;
}

/**
 * Pick the first mapping that matches the post (title + slug + categories).
 *
 * @param int $post_id post.
 * @return array<string,string>|null
 */
function studentup_affiliate_pick( $post_id ) {
	if ( '1' !== (string) studentup_opt( 'affiliate_enabled', '0' ) ) {
		return null;
	}
	$map = studentup_affiliate_map();
	if ( ! $map ) {
		return null;
	}
	$cats = array();
	foreach ( (array) get_the_category( $post_id ) as $c ) {
		$cats[] = $c->name . ' ' . $c->slug;
	}
	$hay = strtolower( get_the_title( $post_id ) . ' ' . get_post_field( 'post_name', $post_id ) . ' ' . implode( ' ', $cats ) );
	foreach ( $map as $row ) {
		$re = '#(?:' . str_replace( '#', '\#', $row['match'] ) . ')#iu';
		if ( @preg_match( $re, $hay ) ) { // phpcs:ignore WordPress.PHP.NoSilencedErrors -- owner regex may be invalid
			return array( 'label' => $row['label'], 'url' => studentup_affiliate_url( $row['url'] ) );
		}
	}
	return null;
}

/**
 * Row for the Important Links box: [label, url, icon, kind, primary].
 *
 * @param int $post_id post.
 * @return array<int,mixed>|null
 */
function studentup_affiliate_row( $post_id ) {
	$pick = studentup_affiliate_pick( $post_id );
	if ( ! $pick ) {
		return null;
	}
	return array( $pick['label'], $pick['url'], 'book', 'affiliate', false );
}
