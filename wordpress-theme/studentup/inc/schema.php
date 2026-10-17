<?php
/**
 * v64: JSON-LD schema — Organization + WebSite (SearchAction) + BreadcrumbList.
 *
 * Post-level Article/JobPosting/FAQ schema bot nunchi vasthundi (autoblog/seo.py);
 * site identity schema (ee file) WordPress nunchi — Google ki "ee site evaru" ani.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * wp_head lo schema (admin/feed lo vaddu).
 */
function studentup_schema_head() {
	if ( is_admin() || is_feed() || ! studentup_opt( 'schema', '1' ) ) {
		return;
	}
	// v1.9.124: Rank Math active → it already emits Organization(#organization)
	// + WebSite(#website). A second Organization/WebSite pair from the theme was
	// a duplicate-entity signal; our extra facts (sameAs, contactPoint, founder,
	// inLanguage) are merged INTO Rank Math's graph instead (studentup_rm_jsonld).
	if ( class_exists( 'RankMath' ) ) {
		return;
	}
	$home  = home_url( '/' );
	$name  = get_bloginfo( 'name' );
	$desc  = get_bloginfo( 'description' );
	$logo  = has_custom_logo() ? wp_get_attachment_image_url( get_theme_mod( 'custom_logo' ), 'full' ) : '';
	$socials = array_values( studentup_social_links() );

	$org = array(
		'@type' => 'Organization',
		'@id'   => $home . '#org',
		'name'  => $name,
		'url'   => $home,
	);
	if ( $logo ) {
		$org['logo'] = array( '@type' => 'ImageObject', 'url' => $logo );
	}
	if ( $socials ) {
		$org['sameAs'] = $socials;
	}
	if ( $desc ) {
		$org['description'] = $desc;
	}
	// v195 (E-E-A-T): publisher identity ki nijamaina founder + review contact.
	$org['founder'] = array( '@id' => $home . '#founder' );
	if ( function_exists( 'studentup_contact_email' ) ) {
		$mail = studentup_contact_email();
		if ( $mail ) {
			$org['contactPoint'] = array(
				array(
					'@type'       => 'ContactPoint',
					'contactType' => 'editorial',
					'email'       => $mail,
					'availableLanguage' => array( 'te', 'en' ),
				),
			);
		}
	}
	$site = array(
		'@type'           => 'WebSite',
		'@id'             => $home . '#website',
		'url'             => $home,
		'name'            => $name,
		'publisher'       => array( '@id' => $home . '#org' ),
		'inLanguage'      => 'te-IN',
		'potentialAction' => array(
			'@type'       => 'SearchAction',
			'target'      => array(
				'@type'       => 'EntryPoint',
				'urlTemplate' => $home . '?s={search_term_string}',
			),
			'query-input' => 'required name=search_term_string',
		),
	);
	$graph = array( $org, $site );

	if ( is_singular() ) {
		$graph[] = array(
			'@type'           => 'BreadcrumbList',
			'@id'             => get_permalink() . '#breadcrumb',
			'itemListElement' => studentup_breadcrumb_items(),
		);
	}
	echo '<script type="application/ld+json">'
		. wp_json_encode( array( '@context' => 'https://schema.org', '@graph' => $graph ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES )
		. '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_schema_head', 5 );

/**
 * Breadcrumb items (Rank Math breadcrumb unte adi vadhu — duplicate avvali).
 */
function studentup_breadcrumb_items() {
	$items = array(
		array( '@type' => 'ListItem', 'position' => 1, 'name' => 'Home', 'item' => home_url( '/' ) ),
	);
	if ( is_singular( 'post' ) ) {
		$cats = get_the_category();
		if ( $cats ) {
			$items[] = array(
				'@type'    => 'ListItem',
				'position' => 2,
				'name'     => $cats[0]->name,
				'item'     => get_category_link( $cats[0] ),
			);
		}
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => count( $items ) + 1,
			'name'     => get_the_title(),
			'item'     => get_permalink(),
		);
	}
	return $items;
}

/**
 * NewsArticle schema for single posts (Google News / Discover eligibility).
 *
 * v141: only emitted when nothing else already describes the article — if Rank
 * Math (or another SEO plugin) is active it owns the Article graph and a second
 * one would be a duplicate. The bot's in-content Article/FAQ schema is also
 * detected, so a post never carries two competing article nodes.
 *
 * @return void
 */
function studentup_newsarticle_schema() {
	if ( is_admin() || is_feed() || ! is_singular( 'post' ) ) {
		return;
	}
	if ( ! studentup_opt( 'news_schema', '1' ) ) {
		return;
	}
	if ( class_exists( 'RankMath' ) || defined( 'WPSEO_VERSION' ) || defined( 'SEOPRESS_VERSION' ) ) {
		return; // SEO plugin already emits the article graph.
	}
	$post_id = get_the_ID();
	$content = (string) get_post_field( 'post_content', $post_id );
	if ( false !== strpos( $content, '"@type": "Article"' ) || false !== strpos( $content, '"@type":"Article"' ) ) {
		return; // bot already shipped the Article node inside the content
	}
	$image = get_the_post_thumbnail_url( $post_id, 'full' );
	$data  = array(
		'@context'         => 'https://schema.org',
		'@type'            => 'NewsArticle',
		'@id'              => get_permalink( $post_id ) . '#newsarticle',
		'headline'         => wp_trim_words( get_the_title( $post_id ), 20, '' ),
		'description'      => wp_strip_all_tags( get_the_excerpt( $post_id ) ),
		'datePublished'    => get_the_date( DATE_W3C, $post_id ),
		'dateModified'     => get_the_modified_date( DATE_W3C, $post_id ),
		'inLanguage'       => get_bloginfo( 'language' ),
		'mainEntityOfPage' => get_permalink( $post_id ),
		'author'           => array(
			'@type' => 'Person',
			'name'  => get_the_author_meta( 'display_name', (int) get_post_field( 'post_author', $post_id ) ),
			'url'   => get_author_posts_url( (int) get_post_field( 'post_author', $post_id ) ),
		),
		'publisher'        => array( '@id' => home_url( '/' ) . '#org' ),
	);
	if ( $image ) {
		$data['image'] = array( $image );
	}
	// v1.9.119: one article node — entities merged here (was a 2nd Article node).
	if ( function_exists( 'studentup_ai_entities_for_post' ) ) {
		$data = array_merge( $data, studentup_ai_entities_for_post( get_the_ID() ) );
	}
	$data = apply_filters( 'studentup_newsarticle_schema', $data );
	echo '<script type="application/ld+json">'
		. wp_json_encode( $data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES )
		. '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_newsarticle_schema', 7 );

/**
 * v243 — hreflang / language annotation (master-checklist item 163).
 *
 * StudentUp content Telugu + English rendu kalisi untundi, kaani okkate URL —
 * anduke "fake" translation URLs raayakudadu (adi Google ki tappu signal).
 * Ikkada honest ga: self-referencing hreflang + x-default matrame, mariyu
 * site locale nunchi correct BCP-47 tag (te-IN / en-IN).
 *
 * Singular posts/pages + home meeda matrame — archives lo avasaram ledu.
 */
function studentup_hreflang_tags() {
	if ( is_admin() || is_feed() || is_404() || is_search() ) {
		return;
	}
	if ( ! ( is_singular() || is_front_page() || is_home() ) ) {
		return;
	}

	$url = is_singular() ? get_permalink() : home_url( '/' );
	if ( ! $url ) {
		return;
	}

	$locale = (string) get_locale();                 // e.g. te_IN / en_US
	$tag    = str_replace( '_', '-', $locale );
	if ( '' === $tag ) {
		$tag = 'te-IN';
	}
	/* v1.9.116: content is Telugu even when WP locale is en_US — hreflang must say so. */
	if ( 0 === strpos( strtolower( $tag ), 'en' ) ) {
		$tag = function_exists( 'studentup_content_lang_tag' ) ? studentup_content_lang_tag() : 'te-IN';
	}

	printf(
		'<link rel="alternate" hreflang="%1$s" href="%2$s" />' . "\n",
		esc_attr( strtolower( $tag ) ),
		esc_url( $url )
	);
	printf(
		'<link rel="alternate" hreflang="x-default" href="%1$s" />' . "\n",
		esc_url( $url )
	);
}
add_action( 'wp_head', 'studentup_hreflang_tags', 6 );


/* ------------------------------------------------------------------ v1.9.124
 * Rank Math graph bridge — one knowledge graph, theme facts merged in.
 * ------------------------------------------------------------------------ */

/**
 * @param array  $data   Rank Math json-ld entities (publisher, WebSite, WebPage, richSnippet…).
 * @param object $jsonld Rank Math JsonLD instance.
 * @return array
 */
function studentup_rm_jsonld( $data, $jsonld = null ) {
	if ( ! is_array( $data ) ) {
		return $data;
	}
	$home = home_url( '/' );
	// Publisher (Organization/Person): social sameAs + editorial contact + founder.
	if ( isset( $data['publisher'] ) && is_array( $data['publisher'] ) ) {
		$socials = function_exists( 'studentup_social_links' ) ? array_values( array_filter( (array) studentup_social_links(), function ( $u ) {
			return is_string( $u ) && 0 === strpos( $u, 'http' );
		} ) ) : array();
		if ( $socials ) {
			$have = isset( $data['publisher']['sameAs'] ) ? (array) $data['publisher']['sameAs'] : array();
			$data['publisher']['sameAs'] = array_values( array_unique( array_merge( $have, $socials ) ) );
		}
		if ( function_exists( 'studentup_contact_email' ) && studentup_contact_email() && empty( $data['publisher']['contactPoint'] ) ) {
			$data['publisher']['contactPoint'] = array(
				'@type'             => 'ContactPoint',
				'contactType'       => 'editorial',
				'email'             => studentup_contact_email(),
				'availableLanguage' => array( 'te', 'en' ),
			);
		}
		if ( isset( $data['publisher']['@type'] ) && 'Organization' === $data['publisher']['@type'] && empty( $data['publisher']['founder'] ) ) {
			$data['publisher']['founder'] = array( '@id' => $home . '#founder' );
		}
	}
	// Rank Math copies the WP locale (en-US) into inLanguage — content is Telugu.
	$lang = function_exists( 'studentup_content_lang_tag' ) ? studentup_content_lang_tag() : 'te-IN';
	if ( isset( $data['WebSite'] ) && is_array( $data['WebSite'] ) ) {
		$data['WebSite']['inLanguage'] = $lang;
	}
	if ( isset( $data['WebPage'] ) && is_array( $data['WebPage'] ) ) {
		$data['WebPage']['inLanguage'] = $lang;
		if ( is_singular( 'post' ) && empty( $data['WebPage']['speakable'] ) ) {
			$data['WebPage']['speakable'] = array(
				'@type'       => 'SpeakableSpecification',
				'cssSelector' => array( '.article-head h1', '.su-quick-summary' ),
			);
		}
	}
	// Article node (Rank Math key "richSnippet"): entities + language.
	if ( is_singular( 'post' ) ) {
		foreach ( $data as $key => $node ) {
			if ( ! is_array( $node ) || empty( $node['@type'] ) ) {
				continue;
			}
			$types = (array) $node['@type'];
			if ( ! array_intersect( $types, array( 'Article', 'NewsArticle', 'BlogPosting' ) ) ) {
				continue;
			}
			// Rank Math default = BlogPosting; a jobs/results/news site qualifies for
			// NewsArticle (Top Stories / Discover eligibility). Only the default is
			// upgraded — an owner-chosen Article type stays.
			if ( array( 'BlogPosting' ) === $types && studentup_opt( 'news_schema', '1' ) ) {
				$data[ $key ]['@type'] = 'NewsArticle';
			}
			$data[ $key ]['inLanguage'] = $lang;
			if ( function_exists( 'studentup_ai_entities_for_post' ) ) {
				foreach ( studentup_ai_entities_for_post( get_the_ID() ) as $k => $v ) {
					if ( empty( $node[ $k ] ) ) {
						$data[ $key ][ $k ] = $v;
					}
				}
			}
		}
	}
	// Any remaining inLanguage (images, FAQ, author…) → content language.
	array_walk_recursive( $data, function ( &$v, $k ) use ( $lang ) {
		if ( 'inLanguage' === $k && is_string( $v ) ) {
			$v = $lang;
		}
	} );
	return $data;
}
add_filter( 'rank_math/json_ld', 'studentup_rm_jsonld', 100, 2 ); // after Rank Math's connect_schema_entities (99)
