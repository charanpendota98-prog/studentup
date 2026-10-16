<?php
/**
 * v1.9.116 — Content language signals (Telugu).
 *
 * Site prose is Telugu (bot v323 rule) but WordPress locale is often en_US, so
 * <html lang="en-US"> told Google/screen-readers/TTS the wrong language.
 * This module makes every language signal consistent: html lang, hreflang,
 * og:locale, schema inLanguage. Option `content_lang` (default te-IN).
 *
 * @package studentup
 */

defined( 'ABSPATH' ) || exit;

/**
 * BCP-47 tag of the content language (te-IN default).
 */
function studentup_content_lang_tag() {
	$tag = function_exists( 'studentup_opt' ) ? (string) studentup_opt( 'content_lang', 'te-IN' ) : 'te-IN';
	$tag = preg_replace( '/[^A-Za-z-]/', '', $tag );
	return '' === $tag ? 'te-IN' : $tag;
}

/**
 * <html lang="te-IN"> when the WP locale disagrees with the content language.
 */
function studentup_html_lang_attr( $output ) {
	$tag = studentup_content_lang_tag();
	if ( false !== stripos( $output, 'lang="' . $tag . '"' ) ) {
		return $output;
	}
	$output = preg_replace( '/\slang="[^"]*"/i', '', (string) $output );
	return trim( $output . ' lang="' . esc_attr( $tag ) . '"' );
}
add_filter( 'language_attributes', 'studentup_html_lang_attr', 20 );

/**
 * og:locale — only when no SEO plugin owns the head.
 */
function studentup_og_locale() {
	if ( class_exists( 'RankMath' ) || defined( 'WPSEO_VERSION' ) || defined( 'SEOPRESS_VERSION' ) ) {
		return;
	}
	echo '<meta property="og:locale" content="' . esc_attr( str_replace( '-', '_', studentup_content_lang_tag() ) ) . '">' . "\n";
}
add_action( 'wp_head', 'studentup_og_locale', 7 );
