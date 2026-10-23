<?php
/**
 * v1.9.172 Brand palette — one primary colour drives the whole theme.
 *
 * All CSS now reads var(--navy) / var(--blue) / var(--link) / var(--dark) …
 * (defaults = Saffron in style.css). Appearance → Customize → "Brand colour"
 * lets the owner pick a preset or any custom primary; the derived palette is
 * computed here (HSL shifts) and printed as `:root:root{…}` so it beats the
 * stylesheet defaults regardless of load order — no rebuild, no cache-bust.
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

/**
 * Presets: hand-tuned, AA-safe (white on --navy ≥ 4.5:1; --navy on white ≥ 4.5:1).
 *
 * @return array
 */
function studentup_brand_presets() {
	return array(
		'saffron' => array( 'label' => 'Saffron Orange', 'primary' => '#e87722' ),
		'teal'    => array( 'label' => 'Teal Green', 'primary' => '#0d7e6b' ),
		'purple'  => array( 'label' => 'Royal Purple', 'primary' => '#6c3483' ),
		'navy'    => array( 'label' => 'Navy Blue', 'primary' => '#0f2e62' ),
		'pink'    => array( 'label' => 'Pink', 'primary' => '#db2777' ),
		'red'     => array( 'label' => 'Deep Red', 'primary' => '#c0392b' ),
	);
}

/** @return string hex */
function studentup_brand_primary() {
	$custom = sanitize_hex_color( (string) get_theme_mod( 'studentup_brand_custom', '' ) );
	if ( $custom ) {
		return strtolower( $custom );
	}
	$presets = studentup_brand_presets();
	$key     = (string) get_theme_mod( 'studentup_brand', 'saffron' );
	return isset( $presets[ $key ] ) ? $presets[ $key ]['primary'] : $presets['saffron']['primary'];
}

/* ---- tiny colour maths (PHP 7.4 safe) ---- */
function studentup_hex_rgb( $hex ) {
	$hex = ltrim( $hex, '#' );
	if ( strlen( $hex ) === 3 ) {
		$hex = $hex[0] . $hex[0] . $hex[1] . $hex[1] . $hex[2] . $hex[2];
	}
	return array( hexdec( substr( $hex, 0, 2 ) ), hexdec( substr( $hex, 2, 2 ) ), hexdec( substr( $hex, 4, 2 ) ) );
}
function studentup_rgb_hex( $r, $g, $b ) {
	return sprintf( '#%02x%02x%02x', max( 0, min( 255, (int) round( $r ) ) ), max( 0, min( 255, (int) round( $g ) ) ), max( 0, min( 255, (int) round( $b ) ) ) );
}
function studentup_rgb_hsl( $r, $g, $b ) {
	$r /= 255; $g /= 255; $b /= 255;
	$max = max( $r, $g, $b ); $min = min( $r, $g, $b ); $l = ( $max + $min ) / 2; $h = 0; $s = 0;
	if ( $max !== $min ) {
		$d = $max - $min;
		$s = $l > 0.5 ? $d / ( 2 - $max - $min ) : $d / ( $max + $min );
		if ( $max === $r ) { $h = ( $g - $b ) / $d + ( $g < $b ? 6 : 0 ); } elseif ( $max === $g ) { $h = ( $b - $r ) / $d + 2; } else { $h = ( $r - $g ) / $d + 4; }
		$h /= 6;
	}
	return array( $h, $s, $l );
}
function studentup_hsl_rgb( $h, $s, $l ) {
	if ( $s == 0 ) { $v = $l * 255; return array( $v, $v, $v ); } // phpcs:ignore Universal.Operators.StrictComparisons
	$q = $l < 0.5 ? $l * ( 1 + $s ) : $l + $s - $l * $s; $p = 2 * $l - $q;
	$f = static function ( $t ) use ( $p, $q ) {
		if ( $t < 0 ) { $t += 1; } if ( $t > 1 ) { $t -= 1; }
		if ( $t < 1 / 6 ) { return $p + ( $q - $p ) * 6 * $t; } if ( $t < 1 / 2 ) { return $q; } if ( $t < 2 / 3 ) { return $p + ( $q - $p ) * ( 2 / 3 - $t ) * 6; } return $p;
	};
	return array( $f( $h + 1 / 3 ) * 255, $f( $h ) * 255, $f( $h - 1 / 3 ) * 255 );
}
function studentup_luminance( $hex ) {
	list( $r, $g, $b ) = studentup_hex_rgb( $hex );
	$f = static function ( $c ) { $c /= 255; return $c <= 0.03928 ? $c / 12.92 : pow( ( $c + 0.055 ) / 1.055, 2.4 ); };
	return 0.2126 * $f( $r ) + 0.7152 * $f( $g ) + 0.0722 * $f( $b );
}
function studentup_contrast( $a, $b ) {
	$la = studentup_luminance( $a ); $lb = studentup_luminance( $b );
	return ( max( $la, $lb ) + 0.05 ) / ( min( $la, $lb ) + 0.05 );
}
/** Same hue/saturation at a target lightness. */
function studentup_shade( $hex, $l ) {
	list( $r, $g, $b ) = studentup_hex_rgb( $hex );
	list( $h, $s ) = studentup_rgb_hsl( $r, $g, $b );
	list( $r2, $g2, $b2 ) = studentup_hsl_rgb( $h, $s, max( 0, min( 1, $l ) ) );
	return studentup_rgb_hex( $r2, $g2, $b2 );
}
/** Darken until white text on it reaches 4.5:1 (never lighten). */
function studentup_aa_ink( $hex, $min = 4.5 ) {
	list( $r, $g, $b ) = studentup_hex_rgb( $hex );
	list( , , $l ) = studentup_rgb_hsl( $r, $g, $b );
	$out = $hex;
	for ( $i = 0; $i < 40 && studentup_contrast( '#ffffff', $out ) < $min; $i++ ) {
		$l  -= 0.015;
		$out = studentup_shade( $hex, $l );
	}
	return $out;
}

/**
 * Full derived palette for a primary colour.
 *
 * @param string $primary hex.
 * @return array name => value
 */
function studentup_brand_palette( $primary ) {
	$ink   = studentup_aa_ink( $primary );          // --navy: text + solid buttons (white text AA)
	$link  = studentup_aa_ink( $primary, 4.6 );     // --link
	$rgb   = static function ( $hex ) { return implode( ',', studentup_hex_rgb( $hex ) ); };
	list( $r, $g, $b ) = studentup_hex_rgb( $primary );
	list( , , $l ) = studentup_rgb_hsl( $r, $g, $b );
	return array(
		'navy'        => $ink,
		'navy-rgb'    => $rgb( $ink ),
		'blue'        => $primary,
		'blue-rgb'    => $rgb( $primary ),
		'link'        => $link,
		'link-rgb'    => $rgb( $link ),
		'accent2'     => studentup_shade( $primary, min( 0.62, $l + 0.08 ) ),
		'accent2-rgb' => $rgb( studentup_shade( $primary, min( 0.62, $l + 0.08 ) ) ),
		'accent3'     => studentup_shade( $primary, max( 0.3, $l - 0.04 ) ),
		'dark'        => studentup_shade( $primary, 0.13 ),
		'dark-rgb'    => $rgb( studentup_shade( $primary, 0.13 ) ),
		'dark2'       => studentup_shade( $primary, 0.09 ),
		'deep'        => studentup_shade( $primary, 0.26 ),
		'tint1'       => studentup_shade( $primary, 0.66 ),
		'tint2'       => studentup_shade( $primary, 0.76 ),
		'tint3'       => studentup_shade( $primary, 0.86 ),
		'pale'        => studentup_shade( $primary, 0.94 ),
		'pale2'       => studentup_shade( $primary, 0.975 ),
	);
}

/** Hex used for <meta theme-color> + manifest. */
function studentup_brand_theme_color() {
	$p = studentup_brand_palette( studentup_brand_primary() );
	return $p['navy'];
}

/** Print the override (only when the owner changed the default). */
function studentup_brand_head_css() {
	$primary = studentup_brand_primary();
	if ( $primary === studentup_brand_presets()['saffron']['primary'] && ! is_customize_preview() ) {
		return; // defaults already in style.css — zero bytes added
	}
	$css = '';
	foreach ( studentup_brand_palette( $primary ) as $k => $v ) {
		$css .= '--' . $k . ':' . $v . ';';
	}
	echo '<style id="su-brand">:root:root{' . $css . '}</style>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput -- generated from sanitized hex values only
}
add_action( 'wp_head', 'studentup_brand_head_css', 1 );

/** Customizer: preset + custom primary. */
function studentup_brand_customize( $wp_customize ) {
	$wp_customize->add_section( 'studentup_brand', array( 'title' => 'StudentUp Brand colour', 'priority' => 25 ) );
	$choices = array();
	foreach ( studentup_brand_presets() as $k => $p ) {
		$choices[ $k ] = $p['label'] . ' (' . $p['primary'] . ')';
	}
	$wp_customize->add_setting( 'studentup_brand', array( 'default' => 'saffron', 'sanitize_callback' => 'sanitize_key' ) );
	$wp_customize->add_control( 'studentup_brand', array( 'section' => 'studentup_brand', 'label' => 'Preset', 'type' => 'select', 'choices' => $choices ) );
	$wp_customize->add_setting( 'studentup_brand_custom', array( 'default' => '', 'sanitize_callback' => 'sanitize_hex_color' ) );
	$wp_customize->add_control( new WP_Customize_Color_Control( $wp_customize, 'studentup_brand_custom', array( 'section' => 'studentup_brand', 'label' => 'Custom primary (overrides preset; leave empty for preset)' ) ) );
}
add_action( 'customize_register', 'studentup_brand_customize' );
