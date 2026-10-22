<?php
/**
 * v248 — SEO MAX layer (Rank Math + Google top-ranking ki migilina pieces).
 *
 * Theme lo already unnavi: canonical · BreadcrumbList · NewsArticle ·
 * JobPosting · FAQPage · WebSite+SearchAction · Organization · Person ·
 * hreflang · news sitemap · IndexNow · llms.txt · OG/Twitter · auto
 * internal links · TOC. Ivi duplicate cheyyam.
 *
 * Ikkada add chesevi — Google 2026 lo nijam ga matter ayyevi:
 *   1. rel=prev/next  — paged archives lo pagination signal (crawl depth).
 *   2. speakable schema — voice search / Assistant eligibility (headline+summary).
 *   3. news_keywords + article:tag  — Google News/Discover topical signal.
 *   4. article:modified_time + og:updated_time — freshness signal.
 *   5. Paged archives → "Page N" title suffix + noindex kaadu, canonical self
 *      (duplicate-content confusion aagutundi).
 *   6. Empty/thin archive → noindex (thin page Google ki pampam).
 *   7. Internal link depth helper: prathi single lo "parent category" link
 *      (orphan page undakudadu).
 *
 * HONESTY: keyword stuffing, fake review/rating schema, fake dates — okkati
 * kuda ledu. Anni values real post data nunchi matrame.
 *
 * @package StudentUp
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/* ------------------------------------------------------------------ 1+4+5 */

/**
 * rel=prev/next + article modified time + og:updated_time.
 */
function studentup_seo_max_head() {
	if ( is_admin() || is_feed() ) {
		return;
	}

	// --- 1. Pagination: rel prev/next (archives + paged singles) ---
	global $wp_query;
	$paged = max( 1, (int) get_query_var( 'paged' ), (int) get_query_var( 'page' ) );
	$max   = isset( $wp_query->max_num_pages ) ? (int) $wp_query->max_num_pages : 0;
	// 1.9.168: virtual routes (/latest-jobs/, org/qual pages) have no /page/N/ —
	// rel=next pointed to a 404 (found by crawl QA).
	$virtual = get_query_var( 'studentup_opportunities' ) || get_query_var( 'studentup_org_page' ) || get_query_var( 'studentup_qual_page' ) || get_query_var( 'studentup_today' );
	if ( ! is_singular() && $max > 1 && ! $virtual ) {
		if ( $paged > 1 ) {
			$prev = get_pagenum_link( $paged - 1 );
			if ( $prev ) {
				printf( '<link rel="prev" href="%s" />' . "\n", esc_url( $prev ) );
			}
		}
		if ( $paged < $max ) {
			$next = get_pagenum_link( $paged + 1 );
			if ( $next ) {
				printf( '<link rel="next" href="%s" />' . "\n", esc_url( $next ) );
			}
		}
	}

	if ( ! is_singular() ) {
		return;
	}

	// --- 4. Freshness signals (real post dates matrame) ---
	$mod = get_post_modified_time( 'c', true );
	if ( $mod ) {
		printf( '<meta property="article:modified_time" content="%s" />' . "\n", esc_attr( $mod ) );
		printf( '<meta property="og:updated_time" content="%s" />' . "\n", esc_attr( $mod ) );
	}

	// --- 3. news_keywords + article:tag (real terms matrame, max 10) ---
	$terms = array();
	foreach ( array( 'category', 'post_tag' ) as $tax ) {
		$got = get_the_terms( get_the_ID(), $tax );
		if ( is_array( $got ) ) {
			foreach ( $got as $t ) {
				if ( isset( $t->name ) && '' !== trim( $t->name ) ) {
					$terms[] = trim( $t->name );
				}
			}
		}
	}
	$terms = array_slice( array_unique( $terms ), 0, 10 );
	if ( $terms ) {
		printf( '<meta name="news_keywords" content="%s" />' . "\n",
			esc_attr( implode( ', ', $terms ) ) );
		foreach ( $terms as $t ) {
			printf( '<meta property="article:tag" content="%s" />' . "\n", esc_attr( $t ) );
		}
	}
}
add_action( 'wp_head', 'studentup_seo_max_head', 8 );

/* -------------------------------------------------------------------- 2 */

/**
 * speakable schema — voice assistants ki ye part chadavalo cheptundi.
 * CSS selectors mana theme lo nijam ga unnavi matrame.
 */
function studentup_speakable_schema() {
	if ( is_admin() || is_feed() || ! is_singular( 'post' ) ) {
		return;
	}
	if ( class_exists( 'RankMath' ) ) {
		return; // v1.9.124: speakable merged into Rank Math's WebPage node (schema.php)
	}
	$data = array(
		'@context'  => 'https://schema.org',
		'@type'     => 'WebPage',
		'url'       => get_permalink(),
		'name'      => wp_strip_all_tags( get_the_title() ),
		'speakable' => array(
			'@type'       => 'SpeakableSpecification',
			'cssSelector' => array( '.article-head h1', '.su-quick-summary' ),
		),
	);
	echo '<script type="application/ld+json">'
		. wp_json_encode( $data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES )
		. '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_speakable_schema', 9 );

/* -------------------------------------------------------------------- 5 */

/**
 * Paged archive title lo "Page N" — duplicate title warnings povali.
 */
function studentup_seo_max_title_parts( $parts ) {
	$paged = max( (int) get_query_var( 'paged' ), (int) get_query_var( 'page' ) );
	// v1.9.119: core already fills $parts['page'] ("Page N") — only add ours when
	// core did not (was rendering "… — Page 2 – Page 2").
	if ( $paged > 1 && isset( $parts['title'] ) && empty( $parts['page'] ) ) {
		/* translators: %d: page number */
		$parts['page'] = sprintf( __( 'Page %d', 'studentup' ), $paged );
	}
	return $parts;
}
add_filter( 'document_title_parts', 'studentup_seo_max_title_parts', 20 );

/* -------------------------------------------------------------------- 6 */

/**
 * Thin/empty archive + search results → noindex (follow).
 * Nijamaina content unna pages ni eppudu noindex cheyyam.
 */
function studentup_seo_max_robots( $robots ) {
	if ( is_admin() ) {
		return $robots;
	}
	global $wp_query;
	// v1.9.119 FIX: wp_robots() takes directive => true (key only) — the old
	// `index => 'noindex'` rendered as "index:noindex", which Google does not
	// understand, so search pages were effectively NOT noindexed.
	$found = isset( $wp_query->found_posts ) ? (int) $wp_query->found_posts : -1;
	$empty_archive = ( is_archive() || is_category() || is_tag() ) && 0 === $found;
	// Thin tag archives (1 post) = low-value pages for AdSense review + crawl budget.
	$thin_tag = is_tag() && $found > 0 && $found < 2;
	if ( is_search() || $empty_archive || $thin_tag ) {
		$robots['noindex'] = true;
		$robots['follow']  = true;
		unset( $robots['index'], $robots['nofollow'], $robots['max-image-preview'], $robots['max-snippet'], $robots['max-video-preview'] );
	}
	return $robots;
}
add_filter( 'wp_robots', 'studentup_seo_max_robots', 15 );

/* -------------------------------------------------------------------- 7 */

/**
 * Orphan guard — prathi single bottom lo parent category link.
 * (Internal link depth takkuva = crawl + ranking better.)
 */
function studentup_seo_max_parent_link( $content ) {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() ) {
		return $content;
	}
	if ( false !== strpos( $content, 'su-parent-link' ) ) {
		return $content; // idempotent
	}
	$cats = get_the_category();
	if ( empty( $cats ) || ! isset( $cats[0]->term_id ) ) {
		return $content;
	}
	$url  = get_category_link( $cats[0]->term_id );
	$name = $cats[0]->name;
	if ( ! $url || '' === (string) $name ) {
		return $content;
	}
	$block = '<p class="su-parent-link">'
		. esc_html__( 'More updates:', 'studentup' ) . ' <a href="' . esc_url( $url ) . '">'
		. esc_html( $name ) . '</a></p>';
	return $content . $block;
}
add_filter( 'the_content', 'studentup_seo_max_parent_link', 30 );
