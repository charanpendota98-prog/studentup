<?php
/**
 * v100: optional AI/search-readable site guide at /llms.txt.
 *
 * This is a public editorial index, not a ranking instruction. Search engines
 * and AI assistants may use it as a concise map, but canonical article pages,
 * normal crawling, citations and human editorial quality remain authoritative.
 * Drafts, private evidence, credentials and internal automation data never
 * appear here.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Serve a concise, public site map for tools that understand llms.txt.
 */
function studentup_llms_txt() {
	if ( ! isset( $_SERVER['REQUEST_URI'] ) ) {
		return;
	}
	$path = strtok( (string) wp_unslash( $_SERVER['REQUEST_URI'] ), '?' ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
	if ( rtrim( (string) $path, '/' ) !== '/llms.txt' ) {
		return;
	}

	$home = home_url( '/' );
	$lines = array(
		'# StudentUp.in',
		'> Telugu + English public information for Telangana and Andhra Pradesh students, job seekers, applicants and families.',
		'> StudentUp publishes original, source-checked explainers for jobs, recruitment, scholarships, exams, results, admissions and government schemes.',
		'',
		'## Editorial standards',
		'- Prefer official notifications and government portals; cross-check important facts before publishing.',
		'- Do not treat a missing date, vacancy, fee, salary or eligibility detail as confirmed.',
		'- Canonical article pages contain the current reader-facing answer and official links.',
		'- If an article conflicts with the official notification, the official notification wins.',
		'',
		'## Main sections',
		'- [Home](' . $home . ')',
		'- [Telangana Government Jobs](' . $home . 'category/ts-govt-jobs/)',
		'- [Andhra Pradesh Government Jobs](' . $home . 'category/ap-govt-jobs/)',
		'- [Central Government Jobs](' . $home . 'category/central-govt-jobs/)',
		'- [Software Jobs](' . $home . 'category/software-jobs/)',
		'- [Private Jobs](' . $home . 'category/private-jobs/)',
		'- [Part-Time Jobs](' . $home . 'category/part-time-jobs/)',
		'- [Walk-in Jobs](' . $home . 'category/walkin-jobs/)',
		'- [Outsourcing Jobs](' . $home . 'category/outsourcing-jobs/)',
		'- [Abroad Jobs](' . $home . 'category/abroad-jobs/)',
		'- [Scholarships](' . $home . 'category/scholarships/)',
		'- [Internships and Apprenticeships](' . $home . 'category/internships/)',
		'- [Hall Tickets](' . $home . 'category/hall-tickets/)',
		'- [Results](' . $home . 'category/results/)',
		'- [Upcoming Exams](' . $home . 'category/upcoming-exams/)',
		'- [Exam Tips](' . $home . 'category/exam-tips/)',
		'- [Online Education](' . $home . 'category/online-education/)',
		'- [Current Affairs](' . $home . 'category/current-affairs/)',
		'- [Success Stories](' . $home . 'category/success-stories/)',
		'- [About Us](' . $home . 'about-us/)',
		'- [Editorial Policy](' . $home . 'editorial-policy/)',
		'- [Corrections and Contact](' . $home . 'contact/)',
		'',
		'## Student tools',
		'- [Latest active jobs board](' . $home . 'latest-jobs/) — expired notices automatically hidden',
		'- [Compare jobs side by side](' . $home . 'compare/)',
		'- [My Workspace — application tracker](' . $home . 'workspace/)',
		'- [Saved posts](' . $home . 'saved/)',
		'',
		'## Recent public articles',
	);

	$posts = get_posts(
		array(
			'numberposts' => 60,
			'post_status' => 'publish',
			'orderby'     => 'modified',
			'order'       => 'DESC',
		)
	);
	$shown = 0;
	foreach ( $posts as $post ) {
		// v177: expired job posts AI assistants ki "recent" ga recommend cheyyakudadhu —
		// board policy laaga (expired notices hidden) ikkada kuda filter.
		if ( $shown >= 30 ) {
			break;
		}
		$last = (string) get_post_meta( $post->ID, 'studentup_last_date', true );
		if ( '' !== $last && function_exists( 'studentup_opportunity_is_expired' ) && studentup_opportunity_is_expired( $last ) ) {
			continue;
		}
		$url   = get_permalink( $post );
		$title = wp_strip_all_tags( get_the_title( $post ) );
		if ( $url && $title ) {
			// 1.9.159 GEO: one-line facts per entry so AI answer engines can cite the
			// right page with the right deadline without fetching every article.
			$lines[] = '- [' . $title . '](' . $url . ')' . studentup_llms_entry_facts( $post, $last );
			++$shown;
		}
	}
	$lines[] = '';
	$lines[] = '## Full text for answer engines';
	$lines[] = '- [llms-full.txt](' . $home . 'llms-full.txt) — latest active articles as clean text with key facts (updated every 15 minutes)';
	$lines[] = '';
	$lines[] = '## Machine-readable feeds';
	$lines[] = '- [XML Sitemap](' . $home . 'sitemap.xml)';
	$lines[] = '- [News Sitemap](' . $home . 'news-sitemap.xml)';

	status_header( 200 );
	header( 'Content-Type: text/plain; charset=utf-8' );
	header( 'Cache-Control: public, max-age=900' );
	// Plain-text response: HTML escaping would turn readable ampersands into
	// ``&amp;`` tokens for clients consuming this machine-readable document.
	echo implode( "\n", $lines );
	exit;
}
add_action( 'template_redirect', 'studentup_llms_txt', 1 );

/**
 * 1.9.159: " — last date 2026-11-02 · updated 2026-10-19 · <excerpt>" (only real data; nothing invented).
 */
function studentup_llms_entry_facts( $post, $last = '' ) {
	$bits = array();
	if ( '' !== (string) $last ) {
		$bits[] = 'last date ' . wp_strip_all_tags( (string) $last );
	}
	$bits[] = 'updated ' . get_the_modified_date( 'Y-m-d', $post );
	$ex = wp_strip_all_tags( get_the_excerpt( $post ) );
	$ex = trim( preg_replace( '/\s+/u', ' ', $ex ) );
	if ( '' !== $ex ) {
		$bits[] = mb_substr( $ex, 0, 160 );
	}
	return $bits ? ' — ' . implode( ' · ', $bits ) : '';
}

/**
 * 1.9.159 GEO: /llms-full.txt — the newest active articles as clean plain text
 * (title, URL, dates, key facts, body). Answer engines (ChatGPT search,
 * Perplexity, Gemini grounding, Claude) ground on exactly this kind of
 * document; it is public content only, never drafts, never expired notices.
 */
function studentup_llms_full_txt() {
	if ( ! isset( $_SERVER['REQUEST_URI'] ) ) {
		return;
	}
	$path = strtok( (string) wp_unslash( $_SERVER['REQUEST_URI'] ), '?' ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
	if ( rtrim( (string) $path, '/' ) !== '/llms-full.txt' ) {
		return;
	}
	$cache = get_transient( 'studentup_llms_full' );
	if ( false === $cache ) {
		$home  = home_url( '/' );
		$out   = array(
			'# StudentUp.in — full text of latest active articles',
			'> Source: ' . $home . ' · Guide: ' . $home . 'llms.txt · Generated ' . gmdate( 'Y-m-d H:i' ) . ' UTC',
			'> Each article: title, canonical URL, published/updated dates, verified key facts, body text. Official notification always wins over this text.',
			'',
		);
		$posts = get_posts(
			array(
				'numberposts' => 40,
				'post_status' => 'publish',
				'orderby'     => 'modified',
				'order'       => 'DESC',
			)
		);
		$shown = 0;
		$bytes = 0;
		$facts = array(
			'studentup_qual'      => 'Qualification',
			'studentup_last_date' => 'Last date',
			'studentup_vacancies' => 'Vacancies',
			'studentup_salary'    => 'Salary',
			'studentup_fee'       => 'Application fee',
			'studentup_apply_url' => 'Apply link',
			'studentup_org_url'   => 'Organisation website',
		);
		foreach ( $posts as $post ) {
			if ( $shown >= 25 || $bytes > 350000 ) {
				break;
			}
			$last = (string) get_post_meta( $post->ID, 'studentup_last_date', true );
			if ( '' !== $last && function_exists( 'studentup_opportunity_is_expired' ) && studentup_opportunity_is_expired( $last ) ) {
				continue;
			}
			$title = wp_strip_all_tags( get_the_title( $post ) );
			$url   = get_permalink( $post );
			if ( ! $title || ! $url ) {
				continue;
			}
			$block   = array();
			$block[] = '## ' . $title;
			$block[] = 'URL: ' . $url;
			$block[] = 'Published: ' . get_the_date( 'Y-m-d', $post ) . ' · Updated: ' . get_the_modified_date( 'Y-m-d', $post );
			$cats    = wp_get_post_categories( $post->ID, array( 'fields' => 'names' ) );
			if ( $cats ) {
				$block[] = 'Section: ' . implode( ', ', array_map( 'wp_strip_all_tags', $cats ) );
			}
			$kf = array();
			foreach ( $facts as $key => $label ) {
				$v = trim( (string) get_post_meta( $post->ID, $key, true ) );
				if ( '' !== $v ) {
					$kf[] = '- ' . $label . ': ' . wp_strip_all_tags( $v );
				}
			}
			if ( $kf ) {
				$block[] = 'Key facts:';
				$block   = array_merge( $block, $kf );
			}
			$body = (string) $post->post_content;
			$body = preg_replace( '/<(script|style|table)[^>]*>.*?<\/\1>/is', ' ', $body );
			$body = preg_replace( '/<\/(p|li|h[1-6]|div|br)>/i', "\n", $body );
			$body = preg_replace( '/<h([2-3])[^>]*>/i', "\n### ", $body );
			$body = wp_strip_all_tags( strip_shortcodes( $body ) );
			$body = html_entity_decode( $body, ENT_QUOTES, 'UTF-8' );
			$body = preg_replace( "/[ \t]+/u", ' ', $body );
			$body = preg_replace( "/\n{3,}/u", "\n\n", trim( $body ) );
			$body = mb_substr( $body, 0, 12000 );
			$block[] = '';
			$block[] = $body;
			$block[] = '';
			$block[] = '---';
			$block[] = '';
			$txt     = implode( "\n", $block );
			$bytes  += strlen( $txt );
			$out[]   = $txt;
			++$shown;
		}
		$cache = implode( "\n", $out );
		set_transient( 'studentup_llms_full', $cache, 15 * MINUTE_IN_SECONDS );
	}
	status_header( 200 );
	header( 'Content-Type: text/plain; charset=utf-8' );
	header( 'Cache-Control: public, max-age=900' );
	echo $cache; // phpcs:ignore WordPress.Security.EscapeOutput -- plain-text document
	exit;
}
add_action( 'template_redirect', 'studentup_llms_full_txt', 1 );


/**
 * 1.9.159: refresh llms-full cache whenever a post is published/updated.
 */
function studentup_llms_full_bust() {
	delete_transient( 'studentup_llms_full' );
}
add_action( 'save_post', 'studentup_llms_full_bust' );
add_action( 'transition_post_status', 'studentup_llms_full_bust' );
