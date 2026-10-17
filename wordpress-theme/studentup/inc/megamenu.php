<?php
/**
 * v197 ADVANCED MENU — mega panel data (desktop) + accordion groups (mobile).
 *
 * Enduku kotha module:
 *  · v93 lo menu ki plain dropdown vachindi (group + description). Kaani pedda
 *    site lo 25+ links okate column lo padithe scroll avutundi, reader ki
 *    "ekkada em undi" teliyadu. Ippudu prathi top-level item ki **columns**
 *    (mega panel) + highlighted feature card + mobile accordion.
 *  · Okkate data source — desktop mega, mobile accordion, footer shortcuts
 *    anni ike nunchi teesukuntayi (double maintenance ledu, drift ledu).
 *  · **404 eppudu ledu**: prathi link real term / real published page / real
 *    front-page anchor. Emaina missing aithe aa item silent ga drop avutundi
 *    (empty column drop, empty group → plain link).
 *
 * Telugu ledu (v73 invariant) — labels English.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Page URL by candidate slugs — first **published** page wins, else ''.
 *
 * @param string|string[] $slugs Candidate slugs (alias order).
 * @return string
 */
function studentup_mega_page_url( $slugs ) {
	foreach ( (array) $slugs as $slug ) {
		$page = get_page_by_path( $slug );
		if ( $page instanceof WP_Post && 'publish' === get_post_status( $page ) ) {
			return (string) get_permalink( $page );
		}
	}
	return '';
}

/**
 * Front-page anchor URL (section exists on front-page.php).
 *
 * @param string $anchor Anchor without '#'.
 * @return string
 */
function studentup_mega_home_url( $anchor = '' ) {
	return home_url( '/' ) . ( $anchor ? '#' . sanitize_title( $anchor ) : '' );
}

/**
 * One mega item (label + url + description + icon).
 *
 * @param string $label Label.
 * @param string $url   URL ('' = skip).
 * @param string $desc  Description.
 * @param string $icon  Icon key.
 * @return array<string,string>
 */
function studentup_mega_item( $label, $url, $desc, $icon = 'arrow' ) {
	// v1.9.133: descriptions pass through gettext so inc/lang-ui.php can show Telugu chrome.
	return array( 'label' => $label, 'url' => $url, 'desc' => ( '' !== $desc ? translate( $desc, 'studentup' ) : '' ), 'icon' => $icon );
}

/**
 * Mega menu definition — top-level items with columns + feature card.
 *
 * @return array<int,array<string,mixed>>
 */
function studentup_mega_groups() {
	$home = home_url( '/' );

	$cat = static function ( $slug ) {
		$term = studentup_used_term( $slug );
		return $term ? (string) get_category_link( $term ) : '';
	};
	$page = 'studentup_mega_page_url';
	$hub  = 'studentup_hub_url';

	$groups = array();

	/* ---------------------------------------------------------------- JOBS */
	$jobs_cols = array(
		array(
			'title' => 'Telangana & Andhra Pradesh',
			'items' => array(
				studentup_mega_item( 'TS Government Jobs', $cat( 'ts-jobs' ), 'TSPSC · Police · Gurukul', 'bank' ),
				studentup_mega_item( 'AP Government Jobs', $cat( 'ap-jobs' ), 'APPSC · Police · DSC · Secretariat', 'bank' ),
				studentup_mega_item( 'Jobs by qualification', studentup_mega_home_url( 'qualsplit' ), '10th · Inter · Degree · PG', 'school' ),
			),
		),
		array(
			'title' => 'Central & private',
			'items' => array(
				studentup_mega_item( 'Central Govt Jobs', $cat( 'central-jobs' ), 'SSC · UPSC · Railways · Banks', 'flag' ),
				studentup_mega_item( 'Private Jobs', $cat( 'private-jobs' ), 'Off-campus · fresher drives', 'building' ),
				studentup_mega_item( 'Software Jobs', $cat( 'software-jobs' ), 'IT · developer · support', 'laptop' ),
				studentup_mega_item( 'Walk-in Interviews', $cat( 'walkin-jobs' ), 'This week drives · venues', 'walk' ),
				studentup_mega_item( 'Internships', $cat( 'internships' ), 'Stipend · remote · college', 'work' ),
			),
		),
	);
	$groups[] = array(
		'label'   => 'Jobs',
		'icon'    => 'bank',
		'url'     => studentup_opportunity_board_url(),
		'cols'    => $jobs_cols,
		'feature' => array(
			'title' => 'Latest active jobs',
			'desc'  => 'Only notices with live dates — no expired lists.',
			'url'   => studentup_opportunity_board_url(),
			'cta'   => 'Open the board',
		),
	);

	/* --------------------------------------------------------------- EXAMS */
	$exam_cols = array(
		array(
			'title' => 'Updates',
			'items' => array(
				studentup_mega_item( 'Results', $cat( 'results' ), 'Board · competitive · keys', 'doc' ),
				studentup_mega_item( 'Hall Tickets', $cat( 'hall-tickets' ), 'Admit card · instructions', 'ticket' ),
				studentup_mega_item( 'Exam Calendar', $page( array( 'exam-calendar' ) ), 'Confirmed last dates + .ics', 'calendar' ),
			),
		),
		array(
			'title' => 'Practice',
			'items' => array(
				studentup_mega_item( 'Daily Quiz & Polls', $page( array( 'daily-quiz', 'quiz' ) ), 'Fresh questions every day', 'chart' ),
				studentup_mega_item( 'Current Affairs', $cat( 'current-affairs' ), 'Daily GK for exams', 'news' ),
				studentup_mega_item( 'Previous papers & keys', $cat( 'results' ), 'Answer keys after every exam', 'key' ),
			),
		),
	);
	$groups[] = array(
		'label'   => 'Exams',
		'icon'    => 'board',
		'url'     => $cat( 'results' ),
		'cols'    => $exam_cols,
		'feature' => array(
			'title' => 'Exam calendar 2026',
			'desc'  => 'Add every confirmed last date to your phone in one tap.',
			'url'   => $page( array( 'exam-calendar' ) ),
			'cta'   => 'Open calendar',
		),
	);

	/* -------------------------------------------------------- SCHOLARSHIPS */
	$schol_cols = array(
		array(
			'title' => 'Find money',
			'items' => array(
				studentup_mega_item( 'Scholarships', $cat( 'scholarships' ), 'NSP · ePASS · state schemes', 'school' ),
				studentup_mega_item( 'Scholarships 2026 hub', $hub( 'scholarships-hub' ), 'Amounts, eligibility, last dates', 'doc' ),
				studentup_mega_item( 'Success Stories', $cat( 'success-stories' ), 'Verified journeys · lessons', 'trophy' ),
			),
		),
		array(
			'title' => 'By level',
			'items' => array(
				studentup_mega_item( 'Pre-matric (Class 9–10)', $hub( 'scholarships-hub' ), 'School-level schemes', 'book' ),
				studentup_mega_item( 'Post-matric (Inter · Degree)', $hub( 'scholarships-hub' ), 'The biggest State schemes', 'school' ),
				studentup_mega_item( 'Minority & overseas', $hub( 'scholarships-hub' ), 'NSP minority + abroad aid', 'flag' ),
			),
		),
		// v221: welfare schemes + TS/AP district news — bot ee rendu
		// categories ni auto-classify chesi fill chestundi.
		array(
			'title' => 'Schemes & local',
			'items' => array(
				studentup_mega_item( 'Govt Schemes', $cat( 'govt-schemes' ), 'Rythu Bharosa · pensions · ration · housing', 'shield' ),
				studentup_mega_item( 'District News', $cat( 'district-news' ), 'TS & AP districts · holidays · alerts', 'pin' ),
			),
		),
	);
	$groups[] = array(
		'label'   => 'Scholarships',
		'icon'    => 'school',
		'url'     => $cat( 'scholarships' ),
		'cols'    => $schol_cols,
		'feature' => array(
			'title' => 'Free Internet Center',
			'desc'  => 'Form filling at a fixed, published price — what we do and never do.',
			'url'   => $page( array( 'internet-center' ) ),
			'cta'   => 'See the price list',
		),
	);

	/* ----------------------------------------------------------------- TOOLS */
	/* v248 — TOOLS REMOVED (owner decision).
	 * Age/fee/salary calculators, resume maker, compare, saved — ivi space
	 * tinesayi, click value takkuva. Menu lo Tools column ne teesesam;
	 * daani badulu DAILY QUIZ (engagement + return visits) pedutunnam.
	 * Tools pages ni firstrun create cheyyadu (inc/firstrun.php v248).
	 */
	$quiz_url = $page( array( 'daily-quiz', 'quiz' ) );
	$groups[] = array(
		'label'   => 'Daily Quiz',
		'icon'    => 'chart',
		'url'     => $quiz_url,
		'cols'    => array(
			array(
				'title' => 'Practice',
				'items' => array(
					studentup_mega_item( "Today's Quiz", $quiz_url, 'Fresh questions every day (IST)', 'chart' ),
					studentup_mega_item( 'Current Affairs', $cat( 'current-affairs' ), 'Daily GK for exams', 'news' ),
					studentup_mega_item( 'Previous Quizzes', $quiz_url, 'Last 7 days + explanations', 'doc' ),
				),
			),
		),
		'feature' => array(
			'title' => 'Daily Quiz',
			'desc'  => 'Roju kotha questions · explanations tho · login avasaram ledu.',
			'url'   => $quiz_url,
			'cta'   => 'Start quiz',
		),
	);

	/* ------------------------------------------------------------------ INFO */
	$info_cols = array(
		array(
			'title' => 'Site',
			'items' => array(
				studentup_mega_item( 'About StudentUp', $page( array( 'about' ) ), 'Who writes and verifies', 'person' ),
				studentup_mega_item( 'Editorial Team', $page( array( 'editorial-team' ) ), 'Standards + sources', 'shield' ),
				studentup_mega_item( 'Corrections Log', $page( array( 'corrections' ) ), 'Public fixes · 48h SLA', 'refresh' ),
				studentup_mega_item( 'Contact', $page( array( 'contact', 'contact-us' ) ), 'Corrections · suggestions', 'phone' ),
				studentup_mega_item( 'Advertise', $page( array( 'advertise' ) ), 'Sponsorship slots', 'tag' ),
			),
		),
		array(
			'title' => 'Policies',
			'items' => array(
				studentup_mega_item( 'Privacy Policy', $page( array( 'privacy-policy', 'privacy' ) ), 'What we store (very little)', 'shield' ),
				studentup_mega_item( 'Terms of Use', $page( array( 'terms-conditions', 'terms' ) ), 'Rules for using the site', 'doc' ),
				studentup_mega_item( 'Disclaimer', $page( array( 'disclaimer' ) ), 'Not a government website', 'alert' ),
				studentup_mega_item( 'Editorial Policy', $page( array( 'editorial-policy' ) ), 'How we verify every update', 'check' ),
			),
		),
	);
	$groups[] = array(
		'label'   => 'More',
		'icon'    => 'help',
		'url'     => $page( array( 'about' ) ),
		'cols'    => $info_cols,
		'feature' => array(
			'title' => 'Telegram channel',
			'desc'  => 'Job alerts reach you first — no spam, leave anytime.',
			'url'   => function_exists( 'studentup_tg_channel_url' ) ? studentup_tg_channel_url() : '',
			'cta'   => 'Join channel',
		),
	);

	/**
	 * Filter: change/extend the mega menu without touching the theme.
	 *
	 * @param array<int,array<string,mixed>> $groups Mega groups.
	 */
	return apply_filters( 'studentup_mega_groups', $groups );
}

/**
 * Clean a mega group — drop empty columns/items, drop the group if nothing left.
 *
 * @param array<string,mixed> $g Group.
 * @return array<string,mixed>|null
 */
function studentup_mega_clean( $g ) {
	if ( empty( $g['cols'] ) || ! is_array( $g['cols'] ) ) {
		return null;
	}
	$cols = array();
	foreach ( $g['cols'] as $col ) {
		$items = array();
		foreach ( (array) ( $col['items'] ?? array() ) as $it ) {
			if ( empty( $it['label'] ) || empty( $it['url'] ) ) {
				continue; // missing term/page → 404 ledu
			}
			$items[] = $it;
		}
		if ( $items ) {
			$cols[] = array( 'title' => (string) ( $col['title'] ?? '' ), 'items' => $items );
		}
	}
	if ( ! $cols ) {
		return null;
	}
	$g['cols'] = $cols;
	if ( empty( $g['url'] ) ) {
		$g['url'] = $cols[0]['items'][0]['url'];
	}
	if ( empty( $g['feature']['url'] ) ) {
		$g['feature'] = array();
	}
	return $g;
}

/**
 * Cleaned mega menu, ready to render.
 *
 * @return array<int,array<string,mixed>>
 */
function studentup_mega_ready() {
	$out = array();
	foreach ( studentup_mega_groups() as $g ) {
		$clean = studentup_mega_clean( $g );
		if ( $clean ) {
			$out[] = $clean;
		}
	}
	return $out;
}

/**
 * Mobile accordion groups (header.php panel) — same data, flat shape.
 *
 * @return array<int,array<string,mixed>>
 */
function studentup_mega_mobile_groups() {
	$out = array();
	foreach ( studentup_mega_ready() as $g ) {
		$items = array();
		foreach ( $g['cols'] as $col ) {
			foreach ( $col['items'] as $it ) {
				$items[] = $it;
			}
		}
		if ( $items ) {
			$out[] = array(
				'label' => $g['label'],
				'icon'  => $g['icon'] ?? 'arrow',
				'items' => $items,
			);
		}
	}
	/** Filter: mobile accordion groups. */
	return apply_filters( 'studentup_mega_mobile_groups', $out );
}

/**
 * Render the mega menu (desktop `primary` location).
 *
 * Markup deliberately keeps the v93 contract (`ul class="sub-menu"` +
 * `aria-haspopup="true"`) so old CSS/JS + audits keep working — columns and
 * icons are added *inside* the same list.
 *
 * @param array<int,array<string,mixed>> $groups Cleaned mega groups.
 * @param string                         $home   Home URL.
 * @return void
 */
function studentup_mega_render( $groups, $home ) {
	echo '<ul id="primary-menu" class="menu-primary su-has-mega">';
	printf(
		'<li class="menu-item%s"><a href="%s">%s</a></li>',
		( is_front_page() ? ' current-menu-item' : '' ),
		esc_url( $home ),
		esc_html__( 'Home', 'studentup' )
	);
	// v202: Breaking News item — Central Jobs laage click/hover tho open avutundi.
	if ( function_exists( 'studentup_breaking_nav_li' ) ) {
		echo studentup_breaking_nav_li(); // phpcs:ignore WordPress.Security.EscapeOutput -- escaped inside.
	}
	foreach ( $groups as $g ) {
		$key = sanitize_title( (string) $g['label'] );
		$ic  = isset( $g['icon'] ) ? (string) $g['icon'] : 'arrow';
		printf( '<li class="menu-item menu-item-has-children su-mega-li">' );
		// aria-expanded ni JS ne maintain chestundi (hover ki kuda keyboard samaana).
		printf(
			'<a href="%s" aria-haspopup="true" aria-expanded="false" aria-controls="su-mega-%s">%s<span class="su-mega-lb">%s</span></a>',
			esc_url( (string) $g['url'] ),
			esc_attr( $key ),
			studentup_ui_icon( $ic, 16 ), // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG
			esc_html( (string) $g['label'] )
		);
		printf(
			'<ul class="sub-menu" id="su-mega-%s" data-su-mega aria-label="%s">',
			esc_attr( $key ),
			esc_attr( (string) $g['label'] )
		);
		foreach ( $g['cols'] as $col ) {
			echo '<li class="su-mega-col menu-item" role="none">';
			if ( ! empty( $col['title'] ) ) {
				printf( '<p class="su-mega-title">%s</p>', esc_html( translate( (string) $col['title'], 'studentup' ) ) );
			}
			echo '<ul class="su-mega-list">';
			foreach ( $col['items'] as $it ) {
				printf(
					'<li class="menu-item" role="none"><a role="menuitem" href="%s"><span class="su-mega-ic">%s</span>'
					. '<span class="su-mega-t">%s<small>%s</small></span></a></li>',
					esc_url( (string) $it['url'] ),
					studentup_ui_icon( (string) $it['icon'], 18 ), // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG
					esc_html( (string) $it['label'] ),
					esc_html( (string) $it['desc'] )
				);
			}
			echo '</ul>';
			echo '</li>';
		}
		if ( ! empty( $g['feature'] ) ) {
			$f = $g['feature'];
			echo '<li class="su-mega-feat menu-item" role="none">';
			printf( '<span class="su-mega-eyebrow">%s</span>', esc_html__( 'Recommended', 'studentup' ) );
			printf( '<b>%s</b>', esc_html( translate( (string) $f['title'], 'studentup' ) ) );
			printf( '<small>%s</small>', esc_html( translate( (string) $f['desc'], 'studentup' ) ) );
			printf(
				'<a class="su-mega-cta" href="%s">%s%s</a>',
				esc_url( (string) $f['url'] ),
				esc_html( translate( (string) $f['cta'], 'studentup' ) ),
				studentup_ui_icon( 'arrow', 14 ) // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG
			);
			echo '</li>';
		}
		echo '</ul>';
		echo '</li>';
	}
	echo '</ul>';
}

/**
 * Compact link set for the mobile panel accordion (one group → items).
 *
 * @param array<string,mixed> $g      Mobile group.
 * @param bool                $is_new Open by default (first group).
 * @return void
 */
function studentup_mega_mobile_accordion( $g, $is_new = false ) {
	printf(
		'<details class="mgroup"%s><summary>%s<span>%s</span>%s</summary><div class="mgroup-body">',
		$is_new ? ' open' : '',
		studentup_ui_icon( (string) ( $g['icon'] ?? 'arrow' ), 16 ), // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG
		esc_html( (string) $g['label'] ),
		studentup_ui_icon( 'chevron', 14 ) // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG
	);
	foreach ( $g['items'] as $it ) {
		printf(
			'<a href="%s"><span class="mgroup-t">%s</span><small>%s</small></a>',
			esc_url( (string) $it['url'] ),
			esc_html( (string) $it['label'] ),
			esc_html( (string) $it['desc'] )
		);
	}
	echo '</div></details>';
}
