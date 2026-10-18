<?php
/**
 * v227 — TRUST + LEADS layer (launch checklist #23, #24, #26, #27, #31, #33).
 *
 * Mundu ee 6 items "owner pani" ani vadilesam. Nijam: **system** ni code
 * kattagaladu — kevalam content (nijamaina review text, photo, address,
 * response time) matrame owner ivvali. Ikkada aa system anta build chesam.
 *
 * Golden rule (anni functions lo): **data lekapote emi render kaadu.**
 * Khali star box, fake "5.0 ★ (0 reviews)", dummy map — ivi trust ni
 * champutai, penchavu. Google ki kooda fake review schema penalty.
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

/* -------------------------------------------------------------------------
 * Helpers
 * ---------------------------------------------------------------------- */

/**
 * JSON option ni array ga chaduvudam (tappu JSON unte khali array).
 *
 * @param string $raw   Raw JSON option value.
 * @param int    $limit Max rows.
 * @return array
 */
function studentup_trust_rows( $raw, $limit = 6 ) {
	$raw = (string) $raw;
	if ( '' === trim( $raw ) ) {
		return array();
	}
	$data = json_decode( $raw, true );
	if ( ! is_array( $data ) ) {
		return array();
	}
	$out = array();
	foreach ( $data as $row ) {
		if ( is_array( $row ) ) {
			$out[] = $row;
		}
		if ( count( $out ) >= (int) $limit ) {
			break;
		}
	}
	return $out;
}

/* -------------------------------------------------------------------------
 * #23 — Real reviews (+ Review schema, nijamaina vi unte matrame)
 * ---------------------------------------------------------------------- */

/**
 * [studentup_reviews] — StudentUp → Options lo JSON ga pettina reviews.
 *
 * Format: [{"name":"Ravi","text":"...","role":"TS Police 2025","stars":5}]
 *
 * @return string
 */
function studentup_reviews_shortcode() {
	$rows = studentup_trust_rows( studentup_opt( 'reviews_json', '' ), 6 );
	if ( ! $rows ) {
		return ''; // reviews ledu → box ledu. Khali box kanna emi leka povadam better.
	}
	$out = '<section class="su-reviews" aria-label="' . esc_attr__( 'Student reviews', 'studentup' ) . '"><div class="su-reviews-grid">';
	foreach ( $rows as $r ) {
		$name  = isset( $r['name'] ) ? (string) $r['name'] : '';
		$text  = isset( $r['text'] ) ? (string) $r['text'] : '';
		$role  = isset( $r['role'] ) ? (string) $r['role'] : '';
		$stars = isset( $r['stars'] ) ? max( 1, min( 5, (int) $r['stars'] ) ) : 5;
		if ( '' === $name || '' === $text ) {
			continue; // adha-nindina row skip.
		}
		$out .= '<figure class="su-review">';
		$out .= '<div class="su-review-stars" aria-label="' . esc_attr( $stars ) . ' out of 5">'
			. str_repeat( '★', $stars ) . '<span>' . str_repeat( '☆', 5 - $stars ) . '</span></div>';
		$out .= '<blockquote>' . esc_html( $text ) . '</blockquote>';
		$out .= '<figcaption><b>' . esc_html( $name ) . '</b>';
		if ( '' !== $role ) {
			$out .= '<small>' . esc_html( $role ) . '</small>';
		}
		$out .= '</figcaption></figure>';
	}
	$out .= '</div></section>';
	return $out;
}
add_shortcode( 'studentup_reviews', 'studentup_reviews_shortcode' );

/**
 * Review schema — nijamaina reviews unte matrame. Fake aggregateRating ledu.
 */
function studentup_reviews_schema() {
	if ( ! is_front_page() ) {
		return;
	}
	$rows = studentup_trust_rows( studentup_opt( 'reviews_json', '' ), 10 );
	if ( count( $rows ) < 1 ) {
		return;
	}
	$reviews = array();
	$total   = 0;
	foreach ( $rows as $r ) {
		$name = isset( $r['name'] ) ? (string) $r['name'] : '';
		$text = isset( $r['text'] ) ? (string) $r['text'] : '';
		if ( '' === $name || '' === $text ) {
			continue;
		}
		$stars     = isset( $r['stars'] ) ? max( 1, min( 5, (int) $r['stars'] ) ) : 5;
		$total    += $stars;
		$reviews[] = array(
			'@type'        => 'Review',
			'author'       => array( '@type' => 'Person', 'name' => $name ),
			'reviewBody'   => $text,
			'reviewRating' => array(
				'@type'       => 'Rating',
				'ratingValue' => $stars,
				'bestRating'  => 5,
			),
		);
	}
	if ( ! $reviews ) {
		return;
	}
	$data = array(
		'@context'        => 'https://schema.org',
		'@type'           => 'Organization',
		'name'            => get_bloginfo( 'name' ),
		'url'             => home_url( '/' ),
		'review'          => $reviews,
		'aggregateRating' => array(
			'@type'       => 'AggregateRating',
			'ratingValue' => round( $total / count( $reviews ), 1 ),
			'reviewCount' => count( $reviews ),
			'bestRating'  => 5,
		),
	);
	$json = wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
	if ( is_string( $json ) ) {
		echo '<script type="application/ld+json">' . $json . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput
	}
}
add_action( 'wp_head', 'studentup_reviews_schema', 21 );

/* -------------------------------------------------------------------------
 * #24 — Case studies (Problem → Solution → Result)
 * ---------------------------------------------------------------------- */

/**
 * [studentup_case_studies]
 *
 * Format: [{"title":"...","problem":"...","solution":"...","result":"..."}]
 *
 * @return string
 */
function studentup_case_studies_shortcode() {
	$rows = studentup_trust_rows( studentup_opt( 'cases_json', '' ), 6 );
	if ( ! $rows ) {
		return '';
	}
	$out = '<section class="su-cases" aria-label="' . esc_attr__( 'Case studies', 'studentup' ) . '"><div class="su-cases-grid">';
	foreach ( $rows as $c ) {
		$title  = isset( $c['title'] ) ? (string) $c['title'] : '';
		$result = isset( $c['result'] ) ? (string) $c['result'] : '';
		if ( '' === $title || '' === $result ) {
			continue;
		}
		$out .= '<article class="su-case"><h3>' . esc_html( $title ) . '</h3>';
		foreach ( array( 'problem' => 'Problem', 'solution' => 'What we did' ) as $k => $label ) {
			if ( ! empty( $c[ $k ] ) ) {
				$out .= '<p><b>' . esc_html( $label ) . ':</b> ' . esc_html( (string) $c[ $k ] ) . '</p>';
			}
		}
		$out .= '<p class="su-case-result"><b>Result:</b> ' . esc_html( $result ) . '</p></article>';
	}
	$out .= '</div></section>';
	return $out;
}
add_shortcode( 'studentup_case_studies', 'studentup_case_studies_shortcode' );

/* -------------------------------------------------------------------------
 * #26 — Real team / owner block
 * ---------------------------------------------------------------------- */

/**
 * [studentup_team]
 *
 * Format: [{"name":"...","role":"...","photo":"https://...","bio":"..."}]
 *
 * @return string
 */
function studentup_team_shortcode() {
	$rows = studentup_trust_rows( studentup_opt( 'team_json', '' ), 8 );
	if ( ! $rows ) {
		return '';
	}
	$out = '<section class="su-team" aria-label="' . esc_attr__( 'Our team', 'studentup' ) . '"><div class="su-team-grid">';
	foreach ( $rows as $m ) {
		$name = isset( $m['name'] ) ? (string) $m['name'] : '';
		if ( '' === $name ) {
			continue;
		}
		$out .= '<div class="su-member">';
		if ( ! empty( $m['photo'] ) ) {
			$out .= '<img src="' . esc_url( (string) $m['photo'] ) . '" alt="'
				. esc_attr( $name ) . '" width="96" height="96" loading="lazy" decoding="async">';
		}
		$out .= '<b>' . esc_html( $name ) . '</b>';
		if ( ! empty( $m['role'] ) ) {
			$out .= '<small>' . esc_html( (string) $m['role'] ) . '</small>';
		}
		if ( ! empty( $m['bio'] ) ) {
			$out .= '<p>' . esc_html( (string) $m['bio'] ) . '</p>';
		}
		$out .= '</div>';
	}
	$out .= '</div></section>';
	return $out;
}
add_shortcode( 'studentup_team', 'studentup_team_shortcode' );

/* -------------------------------------------------------------------------
 * #27 — Map + directions (address nunchi automatic — embed code avasaram ledu)
 * ---------------------------------------------------------------------- */

/**
 * [studentup_map] — Options lo address unte Google Maps embed + directions.
 *
 * Owner Google Maps nunchi embed code copy cheyyakkarledu — address chaalu.
 *
 * @return string
 */
function studentup_map_shortcode() {
	$addr = trim( (string) studentup_opt( 'ic_address', '' ) );
	$city = trim( (string) studentup_opt( 'ic_city', '' ) );
	if ( '' === $addr ) {
		return ''; // address ledu → fake map ledu.
	}
	$full  = $city ? $addr . ', ' . $city : $addr;
	$query = rawurlencode( $full );
	$embed = 'https://www.google.com/maps?q=' . $query . '&output=embed';
	$dirs  = 'https://www.google.com/maps/dir/?api=1&destination=' . $query;
	$out   = '<section class="su-map" aria-label="' . esc_attr__( 'Our location', 'studentup' ) . '">';
	$out  .= '<iframe title="' . esc_attr( $full ) . '" src="' . esc_url( $embed )
		. '" width="100%" height="280" style="border:0;border-radius:14px" '
		. 'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>';
	$out  .= '<p class="su-map-addr">' . esc_html( $full ) . '</p>';
	$out  .= '<a class="bluebtn" href="' . esc_url( $dirs ) . '" target="_blank" rel="noopener">'
		. 'Get Directions</a></section>';
	return $out;
}
add_shortcode( 'studentup_map', 'studentup_map_shortcode' );

/* -------------------------------------------------------------------------
 * #33 — Response-time promise (prathi contact block kinda)
 * ---------------------------------------------------------------------- */

/**
 * [studentup_response_time]
 *
 * @return string
 */
function studentup_response_time_shortcode() {
	$line = trim( (string) studentup_opt( 'response_time', '' ) );
	if ( '' === $line ) {
		return ''; // promise ledu → line ledu. Nilabettaleni promise cheyyaddu.
	}
	return '<p class="su-response-time"><span aria-hidden="true">⏱</span> '
		. esc_html( $line ) . '</p>';
}
add_shortcode( 'studentup_response_time', 'studentup_response_time_shortcode' );

/**
 * Internet Center box kinda response-time line automatic ga.
 *
 * @param string $html Existing contact block HTML.
 * @return string
 */
function studentup_append_response_time( $html ) {
	$line = studentup_response_time_shortcode();
	return $line ? $html . $line : $html;
}
add_filter( 'studentup_contact_block', 'studentup_append_response_time', 10, 1 );

/* -------------------------------------------------------------------------
 * #31 — Thank-you page (lead confirm + GA4 conversion event)
 * ---------------------------------------------------------------------- */

/**
 * Thank-you page lo GA4 generate_lead event fire cheyyadam.
 */
function studentup_thankyou_event() {
	if ( ! is_page( 'thank-you' ) ) {
		return;
	}
	$js = "try{if(typeof gtag==='function'){gtag('event','generate_lead',"
		. "{event_category:'lead',event_label:'thank-you',value:1});}}catch(e){}";
	wp_register_script( 'studentup-thanks', '', array(), STUDENTUP_VERSION, true );
	wp_enqueue_script( 'studentup-thanks' );
	wp_add_inline_script( 'studentup-thanks', $js );
}
add_action( 'wp_enqueue_scripts', 'studentup_thankyou_event', 31 );

/**
 * Thank-you page noindex — Google lo ee page rank avvakudadu.
 */
function studentup_thankyou_noindex() {
	if ( is_page( 'thank-you' ) ) {
		echo '<meta name="robots" content="noindex,follow">' . "\n";
	}
}
add_action( 'wp_head', 'studentup_thankyou_noindex', 2 );
