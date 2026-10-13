<?php
/**
 * v290 SMART SEARCH RESULTS — top-site level search page.
 *
 * Enduku: search visitors = highest intent (apply/hall ticket/result kosam
 * vachina vallu). WP default search = ALL words must match → "police constable
 * hall ticket 2026" laanti long queries chala sarlu 0 results → visitor
 * veltadu. Ee module:
 *   1. Related category chips (query words ↔ category names) — one-tap to hub.
 *   2. 0 results ayite "Closest matches": any-word fallback query (title first).
 *   3. "Did you mean" — nearest category/tag name (similar_text) — only when
 *      a close name exists (no fake suggestions).
 *   4. Latest 6 posts as recovery (data unte matrame).
 *   5. Posts only (pages/attachments search lo raavu), 12 per page.
 * No hint texts, no ads here (ad slots template lo ne — max 3 rule).
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Search query tuning: posts only, 12/page.
 *
 * @param WP_Query $q Query.
 * @return void
 */
function studentup_smart_search_query( $q ) {
	if ( is_admin() || ! $q->is_main_query() || ! $q->is_search() ) {
		return;
	}
	$q->set( 'post_type', 'post' );
	$q->set( 'posts_per_page', 12 );
	$q->set( 'post_status', 'publish' );
}
add_action( 'pre_get_posts', 'studentup_smart_search_query' );

/**
 * Query words (2+ chars, lower, max 6).
 *
 * @param string $s Search string.
 * @return string[]
 */
function studentup_search_words( $s ) {
	$s     = function_exists( 'mb_strtolower' ) ? mb_strtolower( (string) $s, 'UTF-8' ) : strtolower( (string) $s );
	$words = preg_split( '/[\s,\/\-]+/u', $s, -1, PREG_SPLIT_NO_EMPTY );
	$stop  = array( 'the', 'and', 'for', 'job', 'jobs', 'in', 'of', '2025', '2026', 'latest', 'new' );
	$out   = array();
	foreach ( (array) $words as $w ) {
		if ( strlen( $w ) >= 2 && ! in_array( $w, $stop, true ) ) {
			$out[] = $w;
		}
	}
	return array_slice( array_values( array_unique( $out ) ), 0, 6 );
}

/**
 * Categories whose name/slug contains any query word (max 6).
 *
 * @param string $s Search string.
 * @return WP_Term[]
 */
function studentup_search_related_cats( $s ) {
	$words = studentup_search_words( $s );
	if ( ! $words ) {
		return array();
	}
	$cats = get_categories( array( 'hide_empty' => true, 'number' => 60, 'orderby' => 'count', 'order' => 'DESC' ) );
	$hit  = array();
	foreach ( (array) $cats as $c ) {
		$hay = strtolower( $c->name . ' ' . $c->slug );
		foreach ( $words as $w ) {
			if ( false !== strpos( $hay, $w ) ) {
				$hit[] = $c;
				break;
			}
		}
		if ( count( $hit ) >= 6 ) {
			break;
		}
	}
	return $hit;
}

/**
 * "Did you mean" — nearest category/tag name when the query is a near-miss
 * (typo). Returns '' when nothing is close enough (no fake suggestion).
 *
 * @param string $s Search string.
 * @return array{name:string,url:string}|array
 */
function studentup_search_did_you_mean( $s ) {
	$s = strtolower( trim( (string) $s ) );
	if ( strlen( $s ) < 4 ) {
		return array();
	}
	$terms = get_terms( array( 'taxonomy' => array( 'category', 'post_tag' ), 'hide_empty' => true, 'number' => 300 ) );
	$best  = array();
	$score = 0;
	foreach ( (array) $terms as $t ) {
		if ( ! ( $t instanceof WP_Term ) ) {
			continue;
		}
		$name = strtolower( $t->name );
		similar_text( $s, $name, $pct );
		if ( $pct > $score && $pct >= 72 && $name !== $s ) {
			$score = $pct;
			$best  = array( 'name' => $t->name, 'url' => (string) get_term_link( $t ) );
		}
	}
	return $best;
}

/**
 * Any-word fallback: posts matching ANY query word (title weighted by WP), max 9.
 *
 * @param string $s Search string.
 * @return WP_Query|null
 */
function studentup_search_fallback_query( $s ) {
	$words = studentup_search_words( $s );
	if ( ! $words ) {
		return null;
	}
	// WP core: multiple terms via 'search_terms' needs sentence=false; we pass
	// the longest 3 words joined — core ANDs them, so query each word and merge ids.
	$ids = array();
	foreach ( array_slice( $words, 0, 3 ) as $w ) {
		$q = new WP_Query( array( 's' => $w, 'post_type' => 'post', 'post_status' => 'publish', 'posts_per_page' => 6, 'fields' => 'ids', 'no_found_rows' => true ) );
		foreach ( (array) $q->posts as $pid ) {
			$ids[ $pid ] = isset( $ids[ $pid ] ) ? $ids[ $pid ] + 1 : 1;
		}
	}
	if ( ! $ids ) {
		return null;
	}
	arsort( $ids ); // posts matching more words first.
	$ordered = array_slice( array_keys( $ids ), 0, 9 );
	return new WP_Query( array( 'post__in' => $ordered, 'orderby' => 'post__in', 'post_type' => 'post', 'posts_per_page' => 9, 'no_found_rows' => true ) );
}

/**
 * Did-you-mean + related category chips (template prints the H1/count).
 *
 * @param int $found Found posts.
 * @return void
 */
function studentup_smart_search_chips( $found = 0 ) {
	$s   = get_search_query();
	$dym = studentup_search_did_you_mean( $s );
	if ( $dym && empty( $found ) ) {
		echo '<p class="su-srch-dym">' . esc_html__( 'Did you mean', 'studentup' ) . ' <a href="' . esc_url( $dym['url'] ) . '">' . esc_html( $dym['name'] ) . '</a>?</p>';
	}
	$cats = studentup_search_related_cats( $s );
	if ( $cats ) {
		echo '<nav class="su-subcats su-srch-cats" aria-label="' . esc_attr__( 'Related sections', 'studentup' ) . '">';
		foreach ( $cats as $c ) {
			echo '<a href="' . esc_url( get_category_link( $c ) ) . '">' . esc_html( $c->name ) . '</a>';
		}
		echo '</nav>';
	}
}

/**
 * Render the no-results recovery: closest matches (any word) + latest.
 *
 * @return void
 */
function studentup_smart_search_empty() {
	$s  = get_search_query();
	$fb = studentup_search_fallback_query( $s );
	if ( $fb && $fb->have_posts() ) {
		echo '<div class="sectionhead"><div><h2>' . esc_html__( 'Closest matches', 'studentup' ) . '</h2></div></div>';
		echo '<div class="newsgrid">';
		$i = 0;
		while ( $fb->have_posts() ) {
			$fb->the_post();
			studentup_card( $i++ );
		}
		echo '</div>';
		wp_reset_postdata();
		return;
	}
	$latest = new WP_Query( array( 'post_type' => 'post', 'posts_per_page' => 6, 'no_found_rows' => true, 'ignore_sticky_posts' => true ) );
	if ( $latest->have_posts() ) {
		echo '<div class="sectionhead"><div><h2>' . esc_html__( 'Latest on StudentUp', 'studentup' ) . '</h2></div></div>';
		echo '<div class="newsgrid">';
		$i = 0;
		while ( $latest->have_posts() ) {
			$latest->the_post();
			studentup_card( $i++ );
		}
		echo '</div>';
		wp_reset_postdata();
	}
}
