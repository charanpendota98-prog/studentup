<?php
/**
 * v64: Auto Table of Contents (Table of contents) — H2/H3 nunchi jump links.
 *
 * Bot rase posts lo TOC already untundi (autoblog/rm100.py). Idi manual ga
 * rayabadina posts ki + bot content lo TOC lekapote. Rank Math readability
 * ki, Google jump-to-section snippet ki, reader UX ki useful.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Content lo H2/H3 ki ids + TOC ni prepend cheyyadam (single post mattrame).
 */
function studentup_content_toc( $content ) {
	if ( is_admin() || is_feed() || ! is_singular( 'post' ) ) {
		return $content;
	}
	if ( ! studentup_opt( 'toc', '1' ) ) {
		return $content;
	}
	if ( false !== strpos( $content, 'su-toc' ) || false !== strpos( $content, 'studentup-disable-toc' ) ) {
		return $content;
	}
	if ( ! preg_match_all( '/<h([23])([^>]*)>(.*?)<\/h\1>/s', $content, $m, PREG_SET_ORDER ) ) {
		return $content;
	}
	if ( count( $m ) < 3 ) {
		return $content;
	}
	$used  = array();
	$items = array();
	foreach ( $m as $h ) {
		$inner = trim( wp_strip_all_tags( $h[3] ) );
		if ( '' === $inner ) {
			continue;
		}
		// v1.9.129: short TOC — h2 sections only; no question headings, no FAQ /
		// related chrome; max 7 entries (owner rule).
		if ( '3' === (string) $h[1] || '?' === substr( $inner, -1 ) || count( $items ) >= 7
			|| preg_match( '/^(frequently asked|faq|తరచుగా అడిగే)/iu', $inner ) || false !== stripos( $inner, 'related questions' ) ) {
			continue;
		}
		if ( preg_match( '/id=["\']([^"\']+)["\']/', $h[2], $idm ) ) {
			$id = $idm[1];
		} else {
			$id = sanitize_title( $inner );
			// v1.9.119: Telugu headings → sanitize_title() gives "%e0%b0…" ids (ugly
			// anchors, Rank Math TOC check unhappy). ASCII-only ids; else sec-N.
			if ( '' === $id || false !== strpos( $id, '%' ) || ! preg_match( '/^[a-z0-9-]+$/', $id ) ) {
				$id = 'sec-' . ( count( $items ) + 1 );
			}
			$base = $id;
			$i    = 2;
			while ( in_array( $id, $used, true ) ) {
				$id = $base . '-' . $i;
				$i++;
			}
			// v1.9.119: replace only the FIRST occurrence — identical headings twice
			// produced duplicate ids and dead TOC links.
			$pos = strpos( $content, $h[0] );
			if ( false !== $pos ) {
				$content = substr_replace( $content, '<h' . $h[1] . $h[2] . ' id="' . esc_attr( $id ) . '">' . $h[3] . '</h' . $h[1] . '>', $pos, strlen( $h[0] ) );
			}
		}
		$used[]  = $id;
		$items[] = '<li><a href="#' . esc_attr( $id ) . '">' . esc_html( $inner ) . '</a></li>';
	}
	if ( count( $items ) < 3 ) {
		return $content;
	}
	$toc = '<div class="su-toc" role="navigation" aria-label="' . esc_attr__( 'Table of contents', 'studentup' ) . '">'
		. '<div class="su-toc-title">' . esc_html__( 'Table of contents', 'studentup' ) . '</div><ol>'
		. implode( '', array_slice( $items, 0, 12 ) )
		. '</ol></div>';
	// first paragraph tarvata pettali (ledu ante modatlo)
	if ( preg_match( '/<p[^>]*>.*?<\/p>/s', $content, $pm ) ) {
		// v1.9.119: first occurrence only (str_replace duplicated the TOC when the
		// same paragraph text appeared twice).
		$pos = strpos( $content, $pm[0] );
		return substr_replace( $content, $pm[0] . "\n" . $toc, $pos, strlen( $pm[0] ) );
	}
	return $toc . $content;
}
add_filter( 'the_content', 'studentup_content_toc', 12 );
