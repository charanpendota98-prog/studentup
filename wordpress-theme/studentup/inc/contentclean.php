<?php
/**
 * v213 CONTENT HYGIENE — leftover plugin block placeholders ni article nunchi
 * teesesthundi.
 *
 * Enduku: owner report — article lo "Search / Blocksy: Search Block" ane text
 * kanipistundi. Adi Blocksy theme/plugin block (`blocksy/search`) content lo
 * save ayindi; aa plugin ippudu active kaadu kabatti WordPress dani
 * "Blocksy: Search Block" ane plain placeholder/comment ga print chestundi
 * (idhi reader ki pure noise — header lo already search undi).
 *
 * Ee layer:
 *   1) `the_content` lo unregistered/foreign block placeholders ni strip
 *      chestundi (blocksy search + generic "<Plugin>: <X> Block" fallback text).
 *   2) Empty paragraph/heading shells ni (placeholder teesaka migiలే khali
 *      <p>, <p>&nbsp;</p>) clean chestundi — phone lo space waste avvadu.
 *
 * Non-destructive: DB lo post content maaradu, render time lo matrame clean.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Stray block placeholders + empty shells ni teesey.
 *
 * @param string $html Post content HTML.
 * @return string
 */
function studentup_strip_foreign_block_placeholders( $html ) {
	if ( ! is_string( $html ) || '' === trim( $html ) ) {
		return $html;
	}

	/* 1) Blocksy search block — markup variants (div/form wrapper + bare text). */
	$html = preg_replace( '#<(div|section|form|aside)[^>]*class="[^"]*(?:wp-block-blocksy|ct-search)[^"]*"[^>]*>.*?</\1>#is', '', $html );
	$html = preg_replace( '#<!--\s*/?wp:blocksy/[^>]*-->#i', '', $html );

	/* 2) Placeholder text WordPress prints for a missing block type:
	      "Blocksy: Search Block", "Blocksy: Search Block" inside <p>/<div>. */
	$html = preg_replace( '#<(p|div|span|h[1-6])[^>]*>\s*(?:Search\s*)?Blocksy\s*:\s*[^<]{0,60}?Block\s*</\1>#i', '', $html );
	$html = preg_replace( '#(?<![\w>])(?:Search\s*)?Blocksy\s*:\s*[A-Za-z0-9 ]{0,40}?Block(?![\w<])#i', '', $html );

	/* 2b) v1.9.115 owner rule: no promo boxes inside the article body on phone.
	      Older bot drafts carried their own house/sponsor blocks (<aside|section
	      class="su-ad …">) — strip them; the theme renders ONE box after the article. */
	if ( is_singular( 'post' ) ) {
		$html = preg_replace( '#<(aside|section)[^>]*class="[^"]*\bsu-ad\b[^"]*"[^>]*>.*?</\1>#is', '', $html );
		$html = preg_replace( '#<style[^>]*>[^<]*\.su-ad\{[^<]*</style>#is', '', $html );
		// Bot's own "More updates" list duplicates the theme's related block below the article.
		$html = preg_replace( '#<section[^>]*class="[^"]*\bsu-related\b[^"]*"[^>]*>.*?</section>#is', '', $html );
	}

	/* 3) Khali shells clean — pైn strip tarvata migిలే blank blocks. */
	$html = preg_replace( '#<p[^>]*>(?:\s|&nbsp;|<br\s*/?>)*</p>#i', '', $html );
	$html = preg_replace( '#<(h[1-6])[^>]*>(?:\s|&nbsp;)*</\1>#i', '', $html );

	return $html;
}
add_filter( 'the_content', 'studentup_strip_foreign_block_placeholders', 9 );
add_filter( 'the_excerpt', 'studentup_strip_foreign_block_placeholders', 9 );
