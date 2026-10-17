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
		$html = studentup_clean_legacy_bot_chrome( $html );
	}

	/* 3) Khali shells clean — pైn strip tarvata migిలే blank blocks. */
	$html = preg_replace( '#<p[^>]*>(?:\s|&nbsp;|<br\s*/?>)*</p>#i', '', $html );
	$html = preg_replace( '#<(h[1-6])[^>]*>(?:\s|&nbsp;)*</\1>#i', '', $html );

	return $html;
}
add_filter( 'the_content', 'studentup_strip_foreign_block_placeholders', 9 );
add_filter( 'the_excerpt', 'studentup_strip_foreign_block_placeholders', 9 );

/**
 * v1.9.129 — older bot drafts baked editorial chrome into post_content. Owner
 * rules: no source domains line, no "Related Questions" repeat, no duplicate
 * FAQ section, FAQ questions are h3 (short TOC), no machine phrasing.
 * Render-time only — stored content untouched.
 *
 * @param string $html Post content.
 * @return string
 */
function studentup_clean_legacy_bot_chrome( $html ) {
	// 1) "🔎 Source: domain, domain · checked …" line + legacy trust box.
	$html = preg_replace( '#<p[^>]*class="[^"]*\bsu-source\b[^"]*"[^>]*>.*?</p>#is', '', $html );
	$html = preg_replace( '#<section[^>]*class="[^"]*\bsu-trust-box\b[^"]*"[^>]*>.*?</section>#is', '', $html );
	// 2) "<kw> — Related Questions" h2 + its h3/p items (until next h2 or end).
	$html = preg_replace( '#<h2[^>]*id="related-questions"[^>]*>.*?</h2>(?:(?!<h2[\s>]).)*#is', '', $html );
	// 3) Duplicate FAQ sections: keep the first, drop later ones (heading + question blocks).
	$faq_re = '#<h2[^>]*>\s*(?:frequently asked questions|faqs?|తరచుగా అడిగే ప్రశ్నలు)[^<]*</h2>#iu';
	if ( preg_match_all( $faq_re, $html, $fm, PREG_OFFSET_CAPTURE ) && count( $fm[0] ) > 1 ) {
		for ( $i = count( $fm[0] ) - 1; $i >= 1; $i-- ) {
			$start = $fm[0][ $i ][1];
			$rest  = substr( $html, $start + strlen( $fm[0][ $i ][0] ) );
			$cut   = strlen( $rest );
			if ( preg_match_all( '#<h2[^>]*>(.*?)</h2>#is', $rest, $hm, PREG_OFFSET_CAPTURE ) ) {
				foreach ( $hm[0] as $k => $h ) {
					$txt = trim( wp_strip_all_tags( $hm[1][ $k ][0] ) );
					if ( '?' !== substr( $txt, -1 ) ) {
						$cut = $h[1];
						break;
					}
				}
			}
			$html = substr( $html, 0, $start ) . substr( $rest, $cut );
		}
	}
	// 4) After the FAQ heading, question headings written as h2 → h3.
	if ( preg_match( $faq_re, $html, $m1, PREG_OFFSET_CAPTURE ) ) {
		$pos  = $m1[0][1] + strlen( $m1[0][0] );
		$tail = substr( $html, $pos );
		$tail = preg_replace( '#<h2([^>]*)>(\s*[^<]*\?\s*)</h2>#u', '<h3$1>$2</h3>', $tail );
		$html = substr( $html, 0, $pos ) . $tail;
	}
	// 5) Baked TOC: drop question / FAQ entries (short TOC = section headings only).
	if ( false !== strpos( $html, 'su-toc' ) ) {
		$html = preg_replace_callback( '#(<(?:nav|div)[^>]*class="[^"]*\bsu-toc\b[^"]*"[^>]*>)(.*?)(</(?:nav|div)>)#is', function ( $mm ) {
			$n     = 0;
			$inner = preg_replace_callback( '#<li>\s*<a[^>]*>(.*?)</a>\s*</li>#is', function ( $li ) use ( &$n ) {
				$t = trim( wp_strip_all_tags( $li[1] ) );
				if ( '?' === substr( $t, -1 ) || preg_match( '/^(frequently asked|faq|తరచుగా అడిగే)/iu', $t ) || false !== stripos( $t, 'related questions' ) || $n >= 7 ) {
					return '';
				}
				$n++;
				return $li[0];
			}, $mm[2] );
			return $mm[1] . $inner . $mm[3];
		}, $html );
	}
	// 6) Machine phrasing.
	$html = preg_replace( '#\s*,?\s*(?:as per|according to|per) (?:the )?source (?:evidence|text|data)\b#i', '', $html );
	return $html;
}
