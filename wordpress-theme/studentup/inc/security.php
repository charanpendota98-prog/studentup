<?php
/**
 * v67: SECURITY HARDENING — top-theme level hardening (shared hosting safe).
 *
 * Enti chestundi:
 *  · Security headers (clickjacking · MIME sniffing · referrer · permissions)
 *  · WordPress version geneator meta theeseyadam (fingerprinting)
 *  · XML-RPC / pingback off (bot REST API vaadutundi — XML-RPC avasaram ledu)
 *  · ?author=N enumeration block (user names leak avvavu)
 *  · Emoji scripts theeseyadam (perf: 2 requests + inline CSS)
 *  · Attachment pages → parent post ki redirect (thin page index avvavu)
 *  · Comment flood guard (link count limit — spam)
 *
 * CSP add cheyyaledu: AdSense/analytics inline scripts tho conflict avutundi — adi
 * hosting/WAF level lo cheyyali (docs lo chusandi). Option: StudentUp → Advanced →
 * Security hardening OFF (emergency lo mattrame).
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Hardening ON aa? (default ON — emergency lo admin nunchi OFF cheyyochu)
 *
 * @return bool
 */
function studentup_security_on() {
	return '0' !== (string) studentup_opt( 'security_hardening', '1' );
}

/**
 * Security headers (front-end + admin, cheap — hosting lo mod_headers lekapoyina pani chestundi).
 */
function studentup_security_headers() {
	if ( is_admin() || ! studentup_security_on() ) {
		return;
	}
	if ( headers_sent() ) {
		return;
	}
	header( 'X-Content-Type-Options: nosniff' );
	header( 'X-Frame-Options: SAMEORIGIN' );
	header( 'Referrer-Policy: strict-origin-when-cross-origin' );
	header( 'Permissions-Policy: geolocation=(), microphone=(), camera=()' );
	header( 'Cross-Origin-Opener-Policy: same-origin-allow-popups' );
	// v81 (§76): HSTS — HTTPS live + SSL confirm ayyaka owner ON cheyali
	// (default OFF: HTTP staging lo ON chesthe site lock avtundi).
	// 1.9.174: CSP in REPORT-ONLY mode — never blocks anything (AdSense / GA4 /
	// YouTube keep working), browsers just report what WOULD break. Owner reads
	// the report in WP → Settings → StudentUp CSP log, then flips enforce later.
	// Option csp_report_only = '1' (default) | '0' off.
	if ( '0' !== (string) studentup_opt( 'csp_report_only', '1' ) ) {
		$report = esc_url_raw( rest_url( 'studentup/v1/csp-report' ) );
		header( "Content-Security-Policy-Report-Only: default-src 'self' https: data: blob:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' https: data: blob:; font-src 'self' https: data:; connect-src 'self' https:; frame-src https:; object-src 'none'; base-uri 'self'; form-action 'self' https://docs.google.com https://wa.me https://t.me; report-uri " . $report );
	}
	if ( '1' === (string) studentup_opt( 'hsts_enforce', '0' ) && is_ssl() ) {
		header( 'Strict-Transport-Security: max-age=31536000; includeSubDomains' );
	}
}
add_action( 'send_headers', 'studentup_security_headers' );

/**
 * WP version meta + emoji scripts theeseyadam (fingerprint + perf).
 */
function studentup_clean_head() {
	if ( ! studentup_security_on() ) {
		return;
	}
	remove_action( 'wp_head', 'wp_generator' );
	remove_action( 'wp_head', 'wp_shortlink_wp_head' );
	remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
	remove_action( 'wp_print_styles', 'print_emoji_styles' );
	remove_action( 'admin_print_scripts', 'print_emoji_detection_script' );
	remove_action( 'admin_print_styles', 'print_emoji_styles' );
}
add_action( 'init', 'studentup_clean_head' );

/**
 * XML-RPC off (REST API tho bot pani chestundi — XML-RPC attack surface thagginchadam).
 *
 * @param bool $enabled XML-RPC enabled.
 * @return bool
 */
function studentup_disable_xmlrpc( $enabled ) {
	return studentup_security_on() ? false : $enabled;
}
add_filter( 'xmlrpc_enabled', 'studentup_disable_xmlrpc' );

/**
 * ?author=N enumeration block — usernames leak avvakunda home ki pampadam.
 */
function studentup_block_author_enum() {
	if ( ! studentup_security_on() || is_admin() || is_user_logged_in() ) {
		return;
	}
	if ( isset( $_GET['author'] ) && ! is_author() ) { // phpcs:ignore WordPress.Security.NonceVerification
		wp_safe_redirect( home_url( '/' ), 301 );
		exit;
	}
	if ( isset( $_GET['author'] ) && preg_match( '/^\d+$/', (string) wp_unslash( $_GET['author'] ) ) ) { // phpcs:ignore WordPress.Security.NonceVerification
		wp_safe_redirect( home_url( '/' ), 301 );
		exit;
	}
}
add_action( 'template_redirect', 'studentup_block_author_enum' );

/**
 * Attachment pages → parent post (thin content index avvakunda, AdSense quality safe).
 */
function studentup_attachment_redirect() {
	if ( ! studentup_security_on() || ! is_attachment() ) {
		return;
	}
	$parent = get_post_parent();
	if ( $parent ) {
		wp_safe_redirect( get_permalink( $parent ), 301 );
		exit;
	}
	wp_safe_redirect( home_url( '/' ), 301 );
	exit;
}
add_action( 'template_redirect', 'studentup_attachment_redirect' );

/**
 * Comment link-flood guard (spam comment moderation load thagginchadam).
 *
 * @param array $comment_data Comment data.
 * @return array
 */
function studentup_comment_flood_guard( $comment_data ) {
	if ( isset( $comment_data['comment_content'] ) ) {
		$links = preg_match_all( '#https?://#i', (string) $comment_data['comment_content'] );
		if ( $links > 3 ) {
			wp_die( esc_html__( 'No more than 3 links in one comment.', 'studentup' ),
				esc_html__( 'Comment rejected', 'studentup' ), 403 );
		}
	}
	return $comment_data;
}
add_filter( 'preprocess_comment', 'studentup_comment_flood_guard' );

/**
 * Admin: file editor off (hosting lo accidental code edits prevent) — option tho.
 */
function studentup_maybe_disable_file_edit() {
	if ( ! studentup_security_on() ) {
		return;
	}
	if ( ! defined( 'DISALLOW_FILE_EDIT' ) ) {
		define( 'DISALLOW_FILE_EDIT', true );
	}
}
add_action( 'admin_init', 'studentup_maybe_disable_file_edit' );

/**
 * 1.9.174: CSP report sink — keeps the last 40 unique violations in an option
 * (no PII, no cookies; directive + blocked host only). 2 KB cap, IP rate limit.
 */
add_action( 'rest_api_init', function () {
	register_rest_route( 'studentup/v1', '/csp-report', array(
		'methods'             => 'POST',
		'permission_callback' => '__return_true',
		'callback'            => 'studentup_csp_report_sink',
	) );
} );
function studentup_csp_report_sink( $request ) {
	$ip  = isset( $_SERVER['REMOTE_ADDR'] ) ? (string) $_SERVER['REMOTE_ADDR'] : '';
	$key = 'su_csp_' . md5( $ip );
	if ( (int) get_transient( $key ) >= 20 ) {
		return new WP_REST_Response( null, 429 );
	}
	set_transient( $key, (int) get_transient( $key ) + 1, 10 * MINUTE_IN_SECONDS );
	$raw = (string) $request->get_body();
	if ( strlen( $raw ) > 4096 ) {
		return new WP_REST_Response( null, 413 );
	}
	$data = json_decode( $raw, true );
	$r    = isset( $data['csp-report'] ) && is_array( $data['csp-report'] ) ? $data['csp-report'] : ( is_array( $data ) ? $data : array() );
	$dir  = sanitize_text_field( (string) ( $r['violated-directive'] ?? $r['effective-directive'] ?? '' ) );
	$host = wp_parse_url( (string) ( $r['blocked-uri'] ?? '' ), PHP_URL_HOST );
	$host = $host ? sanitize_text_field( $host ) : sanitize_text_field( substr( (string) ( $r['blocked-uri'] ?? '' ), 0, 40 ) );
	if ( '' === $dir ) {
		return new WP_REST_Response( null, 204 );
	}
	$log = get_option( 'studentup_csp_log', array() );
	if ( ! is_array( $log ) ) {
		$log = array();
	}
	$k = $dir . ' ← ' . $host;
	$log[ $k ] = array( 'n' => ( isset( $log[ $k ]['n'] ) ? (int) $log[ $k ]['n'] + 1 : 1 ), 'last' => current_time( 'mysql' ) );
	if ( count( $log ) > 40 ) {
		uasort( $log, function ( $a, $b ) { return strcmp( $b['last'], $a['last'] ); } );
		$log = array_slice( $log, 0, 40, true );
	}
	update_option( 'studentup_csp_log', $log, false );
	return new WP_REST_Response( null, 204 );
}
add_action( 'admin_notices', function () {
	if ( ! current_user_can( 'manage_options' ) || ! isset( $_GET['su_csp'] ) ) {
		return;
	}
	$log = get_option( 'studentup_csp_log', array() );
	echo '<div class="notice notice-info"><p><strong>CSP report-only log</strong> (' . count( (array) $log ) . ')</p><ol>';
	foreach ( (array) $log as $k => $v ) {
		echo '<li>' . esc_html( $k ) . ' × ' . (int) $v['n'] . ' · ' . esc_html( $v['last'] ) . '</li>';
	}
	echo '</ol></div>';
} );
