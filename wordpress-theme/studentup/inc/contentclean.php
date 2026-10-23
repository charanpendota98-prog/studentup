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
		// 1.9.164 owner screenshots (live): class names vary across old bot
		// versions, so also strip by TEXT markers — any innermost block that
		// carries a promo kicker/disclosure or a source/provenance line.
		// Nested boxes ("STUDENTUP · మా సేవ" wrapping "SPONSORED · PARTNER")
		// are removed inside-out by looping.
		$html = studentup_strip_blocks_with_marker( $html, array(
			'SPONSORED · PARTNER', 'SPONSORED · COLLEGE PARTNER', 'SPONSORED', 'Sponsored · Partner',
			'direct link to our partner', 'not a paid advertisement', 'Advertisement —', 'Advertisement -',
			'STUDENTUP · మా సేవ', '🔎 Source', '🔎 Sources', 'Source check తేదీ', '· checked 20',
			'Official Website‌లో ఒకసారి ధృవీకరించుకోండి', 'రూపొందించబడింది. Source',
		) );
		// 1.9.165: per-post <style> with a Google Fonts @import (old bot MOBILE_CSS)
		// — render-blocking request on every article; theme already loads the font.
		$html = preg_replace( '#<style\b[^>]*>[^<]*@import\s+url\([^<]*fonts\.googleapis[^<]*</style>#isu', '', $html );
		// 1.9.165: stale baked countdown ("29 days left") → theme pill from meta is live.
		$html = preg_replace( '#\s*[—–-]\s*<strong>\s*\d+\s+days left\s*</strong>[^<]*#iu', '', $html );
		$html = preg_replace( '#Last date to apply:#iu', 'దరఖాస్తు చివరి తేదీ:', $html );
		// Standalone "More updates: <category>" line (theme shows its own related block).
		$html = preg_replace( '#<p[^>]*>\s*(?:<strong>)?\s*(?:More updates|మరిన్ని అప్‌డేట్స్|మరిన్ని అప్‌డేట్‌లు)\s*:?.*?</p>#isu', '', $html );
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
	// 1.9.169 — defects seen on live posts (old bot output), fixed at render time
	// so every already-published post is clean without re-saving.
	// 7) Orphan ad-plugin shortcodes printed as text once the plugin is gone.
	$html = preg_replace_callback( '#(?:<p[^>]*>\s*)?\[(adinsert|quads|adrotate|ad_\w+|advanced_ads\w*|ad)\b[^\]]*\](?:\s*</p>)?#i', function ( $m ) {
		return shortcode_exists( strtolower( $m[1] ) ) ? $m[0] : '';
	}, $html );
	// 8) Rupee written in another Indic script (Gemini bleed: "ರೂ.35,000") → ₹.
	$html = preg_replace( '/(?:ರೂ|ರೂಪಾಯಿ|रु|रू|रुपये|ரூ|രൂ|રૂ)\s*\.?\s*(?=\d)/u', '₹', $html );
	// 9) English FAQ heading inside a Telugu article.
	$html = preg_replace( '#(<h2\b[^>]*>)\s*Frequently Asked Questions(?:\s*\(FAQ\))?\s*(</h2>)#i', '$1తరచుగా అడిగే ప్రశ్నలు (FAQ)$2', $html );
	// 10) Robotic intro/outro lines: "Quick Overview: ఈ పోస్ట్‌లో … ఇచ్చాము", "చివరి అప్‌డేట్:" em-line,
	//     "ఈ ఆర్టికల్ … ఆశిస్తున్నాము / షేర్ చేయండి / కామెంట్స్ విభాగంలో" closers.
	$html = preg_replace( '#<p[^>]*>(?:\s*<strong>)?[^<]{0,80}?Quick Overview\s*:?(?:</strong>)?[^<]*?(?:ఇచ్చాము|ఇక్కడ ఉన్నాయి)[^<]*</p>\s*#isu', '', $html );
	$html = preg_replace( '#<p[^>]*>\s*<em>\s*చివరి అప్‌డేట్\s*:[^<]*</em>\s*</p>\s*#isu', '', $html );
	$html = preg_replace( '#<p[^>]*>(?:(?!</p>).){0,400}?(?:ఆశిస్తున్నాము|కామెంట్స్ విభాగంలో|కామెంట్ చేయండి|స్నేహితులకు (?:మరియు )?(?:తోటి విద్యార్థులకు )?షేర్ చేయండి|చివరి వరకు చదవండి|పూర్తిగా ఇచ్చాము)(?:(?!</p>).)*</p>\s*#isu', '', $html );
	// 11) The same image repeated in the body (featured + inline + "second"): keep the first.
	if ( substr_count( $html, '<figure' ) > 1 ) {
		$seen = array();
		$html = preg_replace_callback( '#<figure\b[^>]*>.*?</figure>\s*#is', function ( $f ) use ( &$seen ) {
			if ( ! preg_match( '#src="([^"]+)"#', $f[0], $sm ) ) {
				return $f[0];
			}
			$key = strtolower( basename( strtok( $sm[1], '?' ) ) );
			$key = preg_replace( '/-\d+x\d+(?=\.\w+$)/', '', $key );
			if ( isset( $seen[ $key ] ) ) {
				return '';
			}
			$seen[ $key ] = true;
			return $f[0];
		}, $html );
	}
	// 13) Bot "అధికారిక లింక్స్" box: only official hosts (live showed etvbharat.com
	//     there — a publisher leak). Box with nothing official left is removed.
	if ( false !== strpos( $html, 'su-official-links' ) && function_exists( 'studentup_is_official_url' ) ) {
		$pid  = (int) get_the_ID();
		$html = preg_replace_callback( '#<section[^>]*class="[^"]*\bsu-official-links\b[^"]*"[^>]*>.*?</section>\s*#is', function ( $box ) use ( $pid ) {
			$kept = 0;
			$out  = preg_replace_callback( '#<li>\s*<a\s+href="([^"]+)"[^>]*>.*?</a>\s*</li>\s*#is', function ( $li ) use ( $pid, &$kept ) {
				if ( studentup_is_official_url( html_entity_decode( $li[1] ), $pid ) ) {
					$kept++;
					return preg_replace( '/\s*\(\s*[\d.,]+\s*(?:KB|MB|GB)\s*\)\s*(?:View|Download)?\s*(?=<\/a>)/i', '', $li[0] );
				}
				return '';
			}, $box[0] );
			return $kept > 0 ? $out : '';
		}, $html );
	}
	// 12) Caption that merely repeats the post title.
	$title = get_the_title();
	if ( $title ) {
		$html = preg_replace_callback( '#<figcaption>(.*?)</figcaption>#is', function ( $c ) use ( $title ) {
			return ( trim( wp_strip_all_tags( $c[1] ) ) === trim( wp_strip_all_tags( $title ) ) ) ? '' : $c[0];
		}, $html );
	}
	return $html;
}

/**
 * 1.9.164: remove the innermost <aside|section|div|p|blockquote> that contains
 * any marker text. Loops so nested promo boxes disappear inside-out. Markers
 * are matched case-sensitively as given (plus lowercase variant for ASCII).
 *
 * @param string $html    Content.
 * @param array  $markers Plain-text markers.
 * @return string
 */
function studentup_strip_blocks_with_marker( $html, $markers ) {
	if ( ! is_string( $html ) || '' === $html ) {
		return $html;
	}
	$hit = false;
	foreach ( $markers as $m ) {
		if ( false !== strpos( $html, $m ) ) {
			$hit = true;
			break;
		}
	}
	if ( ! $hit ) {
		return $html;
	}
	$alt = implode( '|', array_map( 'preg_quote', $markers, array_fill( 0, count( $markers ), '#' ) ) );
	// innermost element: no same-tag opening between the opening tag and the marker.
	$re  = '#<(aside|section|div|p|blockquote)\b[^>]*>(?:(?!<\1\b)(?!</\1>).)*?(?:' . $alt . ')(?:(?!<\1\b)(?!</\1>).)*?</\1>#isu';
	// 0) OUTERMOST promo container first (aside/section wrapping a marker) —
	//    balanced scan, so the whole box goes, not just the kicker line.
	$html = studentup_remove_enclosing_blocks( $html, $markers, array( 'aside', 'section' ) );
	for ( $i = 0; $i < 8; $i++ ) {
		$new = preg_replace( $re, '', $html );
		if ( null === $new || $new === $html ) {
			break;
		}
		$html = $new;
	}
	// Any marker left as bare text (no wrapper) — drop that text line.
	$html = preg_replace( '#(?:^|>)[^<]*(?:' . $alt . ')[^<]*(?=<|$)#u', '>', $html );
	return $html;
}

/**
 * 1.9.164: remove the OUTERMOST <aside>/<section> that encloses a marker, using
 * a balanced tag scan (handles nested boxes). Max 12 removals per call.
 *
 * @param string $html    Content.
 * @param array  $markers Plain-text markers.
 * @param array  $tags    Container tag names.
 * @return string
 */
function studentup_remove_enclosing_blocks( $html, $markers, $tags ) {
	for ( $guard = 0; $guard < 12; $guard++ ) {
		$mpos = false;
		foreach ( $markers as $m ) {
			$pp = strpos( $html, $m );
			if ( false !== $pp && ( false === $mpos || $pp < $mpos ) ) {
				$mpos = $pp;
			}
		}
		if ( false === $mpos ) {
			return $html;
		}
		// tokens: opening/closing tags of the container names, with offsets.
		$tagre = '#<(/?)(' . implode( '|', $tags ) . ')\b[^>]*>#i';
		if ( ! preg_match_all( $tagre, $html, $tm, PREG_OFFSET_CAPTURE ) ) {
			return $html;
		}
		$stack = array();
		$outer = null; // array(start, end) of outermost container containing $mpos
		$depth_at_marker = null;
		foreach ( $tm[0] as $i => $tok ) {
			$off   = $tok[1];
			$close = '/' === $tm[1][ $i ][0];
			if ( $off > $mpos && null === $depth_at_marker ) {
				$depth_at_marker = count( $stack );
				if ( 0 === $depth_at_marker ) {
					break; // marker not inside any container → nothing to do here
				}
				$outer = array( 'start' => $stack[0], 'end' => null );
			}
			if ( ! $close ) {
				$stack[] = $off;
			} else {
				array_pop( $stack );
				if ( null !== $outer && 0 === count( $stack ) ) {
					$outer['end'] = $off + strlen( $tok[0] );
					break;
				}
			}
		}
		if ( null === $outer || null === $outer['end'] ) {
			// marker outside any container (or unbalanced) → leave for the innermost pass
			return $html;
		}
		$html = substr( $html, 0, $outer['start'] ) . substr( $html, $outer['end'] );
	}
	return $html;
}
