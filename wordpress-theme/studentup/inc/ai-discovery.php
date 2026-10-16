<?php
/**
 * v251 — AI / Answer-Engine discovery layer.
 *
 * Owner: "Google lo mana page/website suggest avvali — AI kuda suggest cheyyali."
 *
 * 2026 lo traffic rendu dari nunchi vastundi:
 *   1. Google Search (classic + AI Overviews)
 *   2. AI assistants (ChatGPT/Gemini/Perplexity/Copilot) — avi mana page ni
 *      *cite* cheyyali. Citation ravalante: crawler ki access + clean entity
 *      data + answer-first structure kavali.
 *
 * Ee file add chesevi (ekkada duplicate ledu):
 *   1. robots.txt lo AI crawlers ki EXPLICIT allow + llms.txt + sitemaps
 *      pointer (GPTBot · ChatGPT-User · OAI-SearchBot · ClaudeBot ·
 *      PerplexityBot · Google-Extended · CCBot · Bingbot · Applebot-Extended).
 *      Block cheyyadam ante AI lo kanipinchakapovadam — anduke allow.
 *   2. SiteNavigationElement schema → Google sitelinks + AI ki site structure.
 *   3. Organization ki `sameAs` + `knowsAbout` (entity/knowledge-graph signal).
 *   4. Prathi article ki `about` + `mentions` (real categories/tags nunchi) —
 *      entity-based retrieval lo ide major signal.
 *   5. `<meta name="description">` tho paatu answer-first TL;DR ni AI ki
 *      `abstract` property ga ivvadam.
 *
 * HONESTY: ikkada fake entity, fake author, fake rating emi ledu — anni
 * values real site data nunchi.
 *
 * @package StudentUp
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/* ------------------------------------------------------- 1. robots.txt */

/**
 * AI crawlers ki explicit allow + llms.txt pointer.
 *
 * @param string $output Existing robots.txt body.
 * @param bool   $public Site public aa?
 * @return string
 */
function studentup_ai_robots( $output, $public ) {
	if ( ! $public ) {
		return $output; // staging/private site — em marchakudadu
	}
	$home  = untrailingslashit( home_url() );
	$bots  = array(
		'GPTBot',              // OpenAI training + search index
		'ChatGPT-User',        // ChatGPT browsing (user ki answer istunnapudu)
		'OAI-SearchBot',       // OpenAI search
		'ClaudeBot',           // Anthropic
		'Claude-User',
		'PerplexityBot',       // Perplexity
		'Perplexity-User',
		'Google-Extended',     // Gemini / AI Overviews grounding
		'Applebot-Extended',   // Apple Intelligence
		'CCBot',               // Common Crawl (chaala models ki source)
		'Bingbot',             // Copilot
		'DuckAssistBot',
	);
	$lines = array( '', '# v251 — AI assistants & answer engines: explicitly allowed.' );
	foreach ( $bots as $bot ) {
		$lines[] = 'User-agent: ' . $bot;
		$lines[] = 'Allow: /';
		$lines[] = 'Disallow: /wp-admin/';
		$lines[] = '';
	}
	$lines[] = '# Editorial site guide for AI tools:';
	$lines[] = '# ' . $home . '/llms.txt';
	$lines[] = 'Sitemap: ' . $home . '/wp-sitemap.xml';

	return $output . implode( "\n", $lines ) . "\n";
}
add_filter( 'robots_txt', 'studentup_ai_robots', 30, 2 );

/* --------------------------------------------- 2+3. site-level entity data */

/**
 * SiteNavigationElement + Organization entity (home page meeda).
 */
function studentup_ai_site_schema() {
	if ( is_admin() || is_feed() || ! ( is_front_page() || is_home() ) ) {
		return;
	}
	$home = untrailingslashit( home_url() );

	$nav_items = array();
	$menu      = wp_get_nav_menu_items( 'primary' );
	if ( is_array( $menu ) ) {
		$pos = 1;
		foreach ( $menu as $item ) {
			if ( ! isset( $item->url, $item->title ) || '' === (string) $item->url ) {
				continue;
			}
			$nav_items[] = array(
				'@type'    => 'SiteNavigationElement',
				'position' => $pos++,
				'name'     => wp_strip_all_tags( (string) $item->title ),
				'url'      => esc_url_raw( (string) $item->url ),
			);
			if ( $pos > 20 ) {
				break;
			}
		}
	}
	if ( ! $nav_items ) {
		// Menu set cheyyakapothe real categories nunchi (fake links ledu).
		$cats = get_categories( array( 'number' => 10, 'hide_empty' => true ) );
		$pos  = 1;
		foreach ( (array) $cats as $cat ) {
			$nav_items[] = array(
				'@type'    => 'SiteNavigationElement',
				'position' => $pos++,
				'name'     => $cat->name,
				'url'      => esc_url_raw( (string) get_category_link( $cat->term_id ) ),
			);
		}
	}

	$topics = array();
	foreach ( (array) get_categories( array( 'number' => 12, 'hide_empty' => true ) ) as $cat ) {
		$topics[] = $cat->name;
	}

	$graph = array();
	if ( $nav_items ) {
		$graph[] = array(
			'@type'           => 'ItemList',
			'name'            => get_bloginfo( 'name' ) . ' — main sections',
			'itemListElement' => $nav_items,
		);
	}
	// v1.9.119: SAME entity id as schema.php (#org) — two Organization ids for one
	// site split the knowledge-graph signal. knowsAbout/sameAs merge onto #org.
	$org = array(
		'@type' => 'Organization',
		'@id'   => $home . '/#org',
	);
	if ( $topics ) {
		$org['knowsAbout'] = $topics;
	}
	// sameAs — existing StudentUp settings nunchi matrame (kotha option ledu,
	// fake profile link ledu). studentup_social_links() footer/header lo
	// already vade helper.
	$social = function_exists( 'studentup_social_links' ) ? (array) studentup_social_links() : array();
	$same   = array_filter(
		array_map(
			function ( $row ) {
				if ( is_array( $row ) ) {
					return isset( $row['url'] ) ? (string) $row['url'] : '';
				}
				return (string) $row;
			},
			$social
		),
		function ( $u ) {
			return 0 === strpos( (string) $u, 'http' );
		}
	);
	if ( $same ) {
		$org['sameAs'] = array_values( $same );
	}
	$graph[] = $org;

	echo '<script type="application/ld+json">'
		. wp_json_encode(
			array( '@context' => 'https://schema.org', '@graph' => $graph ),
			JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
		)
		. '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_ai_site_schema', 11 );

/* ------------------------------------------------- 4+5. article entity data */

/**
 * Article `about` + `mentions` + `abstract` (AI retrieval signals).
 * Anni real post data nunchi — invent cheyyadam ledu.
 */
function studentup_ai_article_entities() {
	if ( is_admin() || is_feed() || ! is_singular( 'post' ) ) {
		return;
	}
	// v1.9.119: entities now travel INSIDE the single NewsArticle node (see
	// studentup_ai_entities_for_post + filter in schema.php). A second Article
	// node for the same URL was a duplicate-article signal in rich-results tests.
	if ( function_exists( 'studentup_newsarticle_schema' ) ) {
		return;
	}
	$post_id = get_the_ID();

	$about = array();
	foreach ( (array) get_the_category( $post_id ) as $cat ) {
		if ( isset( $cat->name ) ) {
			$about[] = array(
				'@type' => 'Thing',
				'name'  => $cat->name,
				'url'   => esc_url_raw( (string) get_category_link( $cat->term_id ) ),
			);
		}
	}
	$mentions = array();
	$tags     = get_the_tags( $post_id );
	if ( is_array( $tags ) ) {
		foreach ( array_slice( $tags, 0, 10 ) as $tag ) {
			$mentions[] = array(
				'@type' => 'Thing',
				'name'  => $tag->name,
				'url'   => esc_url_raw( (string) get_tag_link( $tag->term_id ) ),
			);
		}
	}
	if ( ! $about && ! $mentions ) {
		return;
	}

	$excerpt = wp_strip_all_tags( (string) get_the_excerpt( $post_id ) );
	$data    = array(
		'@context' => 'https://schema.org',
		'@type'    => 'Article',
		'@id'      => get_permalink( $post_id ) . '#ai-entities',
		'url'      => get_permalink( $post_id ),
		'headline' => wp_strip_all_tags( get_the_title( $post_id ) ),
	);
	if ( '' !== $excerpt ) {
		$data['abstract'] = mb_substr( $excerpt, 0, 300 );
	}
	if ( $about ) {
		$data['about'] = count( $about ) === 1 ? $about[0] : $about;
	}
	if ( $mentions ) {
		$data['mentions'] = $mentions;
	}
	$mod = get_post_modified_time( 'c', true, $post_id );
	if ( $mod ) {
		$data['dateModified'] = $mod;
	}

	echo '<script type="application/ld+json">'
		. wp_json_encode( $data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES )
		. '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_ai_article_entities', 12 );


/**
 * v1.9.119 — about/mentions (categories/tags as Things) for the NewsArticle node.
 *
 * @param int $post_id post.
 * @return array keys about|mentions (only non-empty).
 */
function studentup_ai_entities_for_post( $post_id ) {
	$about = array();
	foreach ( (array) get_the_category( $post_id ) as $cat ) {
		if ( isset( $cat->name ) ) {
			$about[] = array(
				'@type' => 'Thing',
				'name'  => $cat->name,
				'url'   => esc_url_raw( (string) get_category_link( $cat->term_id ) ),
			);
		}
	}
	$mentions = array();
	$tags     = get_the_tags( $post_id );
	if ( is_array( $tags ) ) {
		foreach ( array_slice( $tags, 0, 10 ) as $tag ) {
			$mentions[] = array(
				'@type' => 'Thing',
				'name'  => $tag->name,
				'url'   => esc_url_raw( (string) get_tag_link( $tag->term_id ) ),
			);
		}
	}
	$out = array();
	if ( $about ) {
		$out['about'] = count( $about ) === 1 ? $about[0] : $about;
	}
	if ( $mentions ) {
		$out['mentions'] = $mentions;
	}
	return $out;
}
