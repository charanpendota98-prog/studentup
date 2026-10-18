<?php
/**
 * v1.9.137 — Live Exams entry points.
 *
 * Owner runs live/mock exams on a separate app (exam subdomain, e.g.
 * exams.studentup.in, driven by its own bot). The theme only LINKS to it —
 * category rail tile, mega menu (Practice column), mobile menu. URL comes
 * from Settings → StudentUp → live_exam_url; empty = nothing renders.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function studentup_live_exam_url() {
	$u = function_exists( 'studentup_opt' ) ? trim( (string) studentup_opt( 'live_exam_url', 'https://exams.studentup.in/' ) ) : '';
	if ( '' === $u ) {
		return '';
	}
	$u = esc_url_raw( $u );
	return ( 0 === strpos( $u, 'http' ) ) ? $u : '';
}

// Mega menu → Practice column, right after Daily Quiz.
add_filter( 'studentup_mega_groups', function ( $groups ) {
	$u = studentup_live_exam_url();
	if ( ! $u || ! function_exists( 'studentup_mega_item' ) || ! is_array( $groups ) ) {
		return $groups;
	}
	foreach ( $groups as $gi => $g ) {
		if ( empty( $g['cols'] ) ) {
			continue;
		}
		foreach ( $g['cols'] as $ci => $col ) {
			if ( isset( $col['title'] ) && 'Practice' === $col['title'] ) {
				array_splice( $groups[ $gi ]['cols'][ $ci ]['items'], 1, 0, array( studentup_mega_item( 'Live Exams', $u, 'Timed mock tests · instant rank', 'exam' ) ) );
			}
		}
	}
	return $groups;
}, 20 );
