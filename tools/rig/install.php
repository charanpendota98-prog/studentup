<?php
// Rig installer: run twice (first = install, second = content). Idempotent.
define( 'WP_INSTALLING', true );
require '/wordpress/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/upgrade.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';
require_once ABSPATH . 'wp-admin/includes/taxonomy.php';
if ( ! is_blog_installed() ) {
	wp_install( 'StudentUp Rig', 'admin', 'admin@example.com', true, '', 'adminpass' );
	echo "installed\n";
	exit( 0 );
}
activate_plugin( 'seo-by-rank-math/rank-math.php' );
update_option( 'rank_math_registration_skip', 1 );
switch_theme( 'studentup' );
update_option( 'permalink_structure', '/%postname%/' );
update_option( 'timezone_string', 'Asia/Kolkata' );
$cats = array( 'jobs' => 'Jobs', 'results' => 'Results', 'admit-cards' => 'Admit Cards', 'current-affairs' => 'Current Affairs', 'daily-quiz' => 'Daily Quiz', 'software-jobs' => 'Software Jobs', 'walk-in-jobs' => 'Walk-in Jobs', 'internships' => 'Internships' );
$cid = array();
foreach ( $cats as $slug => $name ) { $t = get_term_by( 'slug', $slug, 'category' ); $cid[ $slug ] = $t ? (int) $t->term_id : (int) wp_create_category( $name ); if ( $t === false ) { wp_update_term( $cid[ $slug ], 'category', array( 'slug' => $slug ) ); } }
$body = '<h2>నోటిఫికేషన్ వివరాలు</h2><p>తెలంగాణ పబ్లిక్ సర్వీస్ కమిషన్ గ్రూప్-2 నోటిఫికేషన్ విడుదల చేసింది. మొత్తం 783 పోస్టులు. డిగ్రీ అర్హత ఉన్న అభ్యర్థులు దరఖాస్తు చేసుకోవచ్చు.</p><h2>ముఖ్యమైన తేదీలు</h2><ul><li>దరఖాస్తు ప్రారంభం: 2026-10-01</li><li>చివరి తేదీ: %LAST%</li></ul><h2>అర్హత</h2><p>ఏదైనా డిగ్రీ. వయస్సు 18–44 సంవత్సరాలు.</p><h2>ఎలా దరఖాస్తు చేయాలి</h2><p>అధికారిక వెబ్‌సైట్ tspsc.gov.in లో ఆన్‌లైన్‌లో దరఖాస్తు చేయండి.</p>';
$posts = array(
	array( 'TSPSC Group 2 Notification 2026 – 783 Posts', 'tspsc-group-2-notification-2026-783-posts', 'jobs', '+2 days', 'TSPSC' ),
	array( 'APPSC Group 1 Notification 2026 – 120 Posts', 'appsc-group-1-notification-2026', 'jobs', '+12 days', 'APPSC' ),
	array( 'SSC CGL 2026 Notification – 17000 Posts', 'ssc-cgl-2026-notification', 'jobs', '+25 days', 'SSC' ),
	array( 'RRB NTPC 2026 Notification', 'rrb-ntpc-2026-notification', 'jobs', '+40 days', 'RRB' ),
	array( 'TS Police Constable Results 2026', 'ts-police-constable-results-2026', 'results', '', 'TSLPRB' ),
	array( 'TS EAPCET 2026 Results Released', 'ts-eapcet-2026-results', 'results', '', 'JNTUH' ),
	array( 'SSC GD Admit Card 2026 Download', 'ssc-gd-admit-card-2026', 'admit-cards', '', 'SSC' ),
	array( 'Daily Current Affairs 18 October 2026', 'daily-current-affairs-18-october-2026', 'current-affairs', '', '' ),
	array( 'TCS NQT 2026 Software Jobs for Freshers', 'tcs-nqt-2026-software-jobs', 'software-jobs', '+15 days', 'TCS' ),
	array( 'Infosys Walk-in Drive Hyderabad 2026', 'infosys-walk-in-drive-hyderabad-2026', 'walk-in-jobs', '+5 days', 'Infosys' ),
	array( 'ISRO Internship 2026 for Degree Students', 'isro-internship-2026', 'internships', '+30 days', 'ISRO' ),
);
foreach ( $posts as $p ) {
	if ( get_page_by_path( $p[1], OBJECT, 'post' ) ) { continue; }
	$last = $p[3] ? gmdate( 'Y-m-d', strtotime( $p[3] ) ) : '';
	$id = wp_insert_post( array( 'post_title' => $p[0], 'post_name' => $p[1], 'post_status' => 'publish', 'post_type' => 'post', 'post_content' => str_replace( '%LAST%', $last ? $last : '—', $body ), 'post_category' => array( $cid[ $p[2] ] ), 'post_author' => 1 ) );
	if ( $last ) { update_post_meta( $id, 'studentup_last_date', $last ); update_post_meta( $id, 'studentup_apply_url', 'https://www.' . strtolower( $p[4] ) . '.gov.in/apply' ); update_post_meta( $id, 'studentup_qual', 'Degree' ); update_post_meta( $id, 'studentup_vacancies', '783' ); update_post_meta( $id, 'studentup_age_min', '18' ); update_post_meta( $id, 'studentup_age_max', '44' ); update_post_meta( $id, 'studentup_salary', '₹ 36,750 – 1,04,200' ); }
	if ( $p[4] ) { update_post_meta( $id, 'studentup_source_url', 'https://www.' . strtolower( $p[4] ) . '.gov.in/' ); update_post_meta( $id, 'studentup_org_url', 'https://www.' . strtolower( $p[4] ) . '.gov.in/' ); }
	if ( $p[2] === 'jobs' || $p[2] === 'software-jobs' || $p[2] === 'walk-in-jobs' || $p[2] === 'internships' ) { wp_set_object_terms( $id, 'TSPSC' === $p[4] ? 'tspsc' : strtolower( $p[4] ), 'post_tag', true ); }
}
foreach ( array( 'daily-quiz' => 'Daily Quiz', 'latest-jobs' => 'Latest Jobs', 'post-your-news' => 'Post Your News', 'about' => 'About', 'contact' => 'Contact', 'privacy-policy' => 'Privacy Policy', 'corrections' => 'Corrections', 'exam-calendar' => 'Exam Calendar', 'internet-center' => 'Internet Center', 'compare' => 'Compare', 'saved' => 'Saved', 'quiz' => 'Quiz', 'thank-you' => 'Thank You', 'success-stories' => 'Success Stories' ) as $slug => $title ) {
	if ( get_page_by_path( $slug ) ) { continue; }
	wp_insert_post( array( 'post_title' => $title, 'post_name' => $slug, 'post_status' => 'publish', 'post_type' => 'page', 'post_content' => '<p>' . $title . ' పేజీ.</p>', 'post_author' => 1 ) );
}
$hw = get_page_by_path( 'hello-world', OBJECT, 'post' ); if ( $hw ) { wp_delete_post( $hw->ID, true ); }
flush_rewrite_rules( false );
echo "content ok\n";
