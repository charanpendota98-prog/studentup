<?php
/**
 * v229 — MAIN MENU (phone drawer top block).
 *
 * Owner report (screenshot tho): phone menu lo modati ga 4 breaking-news
 * headlines, taruvata khaali boxes kanipinchayi — "Home, TS govt jobs, AP govt
 * jobs, central jobs, walkin jobs, software jobs, private jobs, hall tickets,
 * results, breaking news, daily quiz ilaaga anni neat ga undali".
 *
 * Anduke drawer open cheyyagane **modati block ee 11 destinations** —
 * icon + label + chinna hint, 44px tap target, scroll avvakunda.
 * Breaking headlines ippudu deeni kindaki velthayi.
 *
 * Rule (v227 golden rule laage): category lekapote aa row ni render
 * cheyyakudadu — khaali page ki link ivvadam kante lekapovadam better.
 * Home / Breaking News / Daily Quiz eppudu untayi (avi category meeda
 * aadhaarapadavu).
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

/**
 * Drawer main-menu rows: label, icon, hint + destination.
 *
 * @return array<int,array<string,string>> Rows with a resolved `url`.
 */
function studentup_mobile_main_rows() {
	$quiz = function_exists( 'studentup_mega_page_url' )
		? studentup_mega_page_url( array( 'daily-quiz', 'quiz' ) )
		: '';

	$rows = array(
		array(
			'slug' => '',
			'url'  => home_url( '/' ),
			'icon' => 'home',
			'lab'  => 'Home',
			'hint' => '',
		),
		array( 'slug' => 'ts-jobs', 'icon' => 'bank', 'lab' => 'TS Govt Jobs', 'hint' => '' ),
		array( 'slug' => 'ap-jobs', 'icon' => 'bank', 'lab' => 'AP Govt Jobs', 'hint' => '' ),
		array( 'slug' => 'central', 'icon' => 'flag', 'lab' => 'Central Jobs', 'hint' => '' ),
		array( 'slug' => 'walkin', 'icon' => 'walk', 'lab' => 'Walk-in Jobs', 'hint' => '' ),
		array( 'slug' => 'software', 'icon' => 'laptop', 'lab' => 'Software Jobs', 'hint' => '' ),
		array( 'slug' => 'private', 'icon' => 'building', 'lab' => 'Private Jobs', 'hint' => '' ),
		array( 'slug' => 'hall-tickets', 'icon' => 'ticket', 'lab' => 'Hall Tickets', 'hint' => '' ),
		array( 'slug' => 'results', 'icon' => 'doc', 'lab' => 'Results', 'hint' => '' ),
		array(
			'slug' => '',
			'url'  => studentup_opportunity_board_url(),
			'icon' => 'bolt',
			'lab'  => 'Breaking News',
			'hint' => '',
			'cls'  => 'su-mmain-brk',
		),
		array(
			'slug' => '',
			'url'  => $quiz ? $quiz : home_url( '/#daily-quiz' ),
			'icon' => 'chart',
			'lab'  => 'Daily Quiz',
			'hint' => '',
		),
	);

	$out = array();
	foreach ( $rows as $row ) {
		if ( ! empty( $row['slug'] ) ) {
			$term = studentup_used_term( $row['slug'] );
			if ( ! $term ) {
				continue;   // category ledu → khaali archive ki link vaddu.
			}
			$row['url'] = get_category_link( $term );
		}
		$out[] = $row;
	}
	return $out;
}

/**
 * Render the drawer main menu.
 */
function studentup_mobile_main_menu() {
	$rows = studentup_mobile_main_rows();
	if ( ! $rows ) {
		return;
	}
	echo '<div class="mlabel">' . esc_html__( 'Main menu', 'studentup' ) . '</div>';
	echo '<nav class="su-mmain" aria-label="Main menu">';
	foreach ( $rows as $row ) {
		printf(
			'<a class="su-mmain-a %1$s" href="%2$s">%3$s<span class="su-mmain-t">%4$s%5$s</span>%6$s</a>',
			esc_attr( isset( $row['cls'] ) ? $row['cls'] : '' ),
			esc_url( $row['url'] ),
			studentup_ui_icon( $row['icon'], 18 ), // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG.
			esc_html( $row['lab'] ),
			'' , // v268: hints owner ki avasaram ledu — eppudu render cheyyamu
			studentup_ui_icon( 'chevron', 14 ) // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG.
		);
	}
	echo '</nav>';
}
