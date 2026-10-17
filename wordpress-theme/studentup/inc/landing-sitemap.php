<?php
/**
 * v1.9.124 — Rank Math sitemap provider for StudentUp landing routes.
 *
 * /latest-jobs/, /jobs/<qualification>/ (v1.9.122) and /org/<organisation>/
 * (v1.9.123) are virtual routes — no post/term object — so Rank Math's
 * sitemap (which replaces the core sitemap) never listed them, and the owner
 * would have had to add them by hand. This registers a proper provider via
 * `rank_math/sitemap/providers` → `landing-sitemap.xml` appears in
 * sitemap_index.xml automatically, only with routes that currently have posts.
 *
 * (Core sitemap providers in qual-pages.php / org-pages.php stay for installs
 * without Rank Math.)
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * All indexable landing URLs that have content right now.
 *
 * @return array list of array( 'loc' => url, 'mod' => W3C date )
 */
function studentup_landing_urls() {
	$mod  = get_lastpostmodified( 'gmt' );
	$mod  = $mod ? gmdate( DATE_W3C, strtotime( $mod ) ) : gmdate( DATE_W3C );
	$urls = array();
	if ( function_exists( 'studentup_opportunity_board_url' ) ) {
		$urls[] = array( 'loc' => studentup_opportunity_board_url(), 'mod' => $mod );
	}
	if ( function_exists( 'studentup_qual_terms' ) && function_exists( 'studentup_qual_count' ) && function_exists( 'studentup_qual_page_url' ) ) {
		foreach ( studentup_qual_terms() as $slug => $label ) {
			if ( studentup_qual_count( $slug ) > 0 ) {
				$urls[] = array( 'loc' => studentup_qual_page_url( $slug ), 'mod' => $mod );
			}
		}
	}
	if ( function_exists( 'studentup_org_pages_active' ) && function_exists( 'studentup_org_page_url' ) ) {
		foreach ( studentup_org_pages_active() as $slug => $n ) {
			$urls[] = array( 'loc' => studentup_org_page_url( $slug ), 'mod' => $mod );
		}
	}
	return $urls;
}

add_filter( 'rank_math/sitemap/providers', function ( $providers ) {
	if ( ! interface_exists( '\RankMath\Sitemap\Providers\Provider' ) || ! class_exists( '\RankMath\Sitemap\Router' ) ) {
		return $providers;
	}
	if ( ! class_exists( 'StudentUp_Landing_Sitemap_Provider' ) ) {
		class StudentUp_Landing_Sitemap_Provider implements \RankMath\Sitemap\Providers\Provider {
			public function handles_type( $type ) {
				return 'landing' === $type;
			}
			public function get_index_links( $max_entries ) {
				$urls = studentup_landing_urls();
				if ( empty( $urls ) ) {
					return array();
				}
				return array(
					array(
						'loc'     => \RankMath\Sitemap\Router::get_base_url( 'landing-sitemap.xml' ),
						'lastmod' => $urls[0]['mod'],
					),
				);
			}
			public function get_sitemap_links( $type, $max_entries, $current_page ) {
				return studentup_landing_urls();
			}
		}
	}
	$providers[] = new StudentUp_Landing_Sitemap_Provider();
	return $providers;
} );
