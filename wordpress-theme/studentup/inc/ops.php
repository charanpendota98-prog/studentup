<?php
/**
 * v1.9.148 — operations hardening (ARCHITECTURE_REVIEW_v361 §2 S3, §1 contract).
 *
 *  1. `studentup_bot` role: drafts-only (edit_posts + upload_files + read, NO
 *     publish_posts). The bot's Application Password should belong to a user
 *     with this role, so even a leaked key can never publish or delete.
 *  2. Admin notice (manage_options only, dismissible) when a user that owns an
 *     Application Password can publish — i.e. the bot still runs as an editor /
 *     administrator.
 *  3. Contract version exposed on GET /studentup/v1/theme-info so the bot can
 *     refuse to post when the theme it writes HTML for has drifted.
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

define( 'STUDENTUP_CONTRACT', 3 );

/**
 * Register / refresh the drafts-only bot role.
 */
function studentup_ops_bot_role() {
	$caps = array(
		'read'                => true,
		'edit_posts'          => true,
		'delete_posts'        => false,
		'publish_posts'       => false,
		'upload_files'        => true,
		'edit_published_posts' => false,
		'delete_published_posts' => false,
	);
	$role = get_role( 'studentup_bot' );
	if ( ! $role ) {
		add_role( 'studentup_bot', 'StudentUp Bot (drafts only)', $caps );
		return;
	}
	foreach ( $caps as $cap => $grant ) {
		if ( $grant && ! $role->has_cap( $cap ) ) {
			$role->add_cap( $cap );
		} elseif ( ! $grant && $role->has_cap( $cap ) ) {
			$role->remove_cap( $cap );
		}
	}
}
add_action( 'after_switch_theme', 'studentup_ops_bot_role' );
add_action( 'admin_init', 'studentup_ops_bot_role_once' );

function studentup_ops_bot_role_once() {
	if ( get_option( 'su_bot_role_v' ) !== (string) STUDENTUP_CONTRACT ) {
		studentup_ops_bot_role();
		update_option( 'su_bot_role_v', (string) STUDENTUP_CONTRACT, false );
	}
}

/**
 * Users that own an Application Password AND can publish — the bot should not.
 *
 * @return array<int,string> user_login list.
 */
function studentup_ops_overprivileged_bots() {
	if ( ! class_exists( 'WP_Application_Passwords' ) ) {
		return array();
	}
	$cached = get_transient( 'su_ops_overpriv' );
	if ( is_array( $cached ) ) {
		return $cached;
	}
	$out   = array();
	$users = get_users( array( 'fields' => array( 'ID', 'user_login' ), 'number' => 200 ) );
	foreach ( $users as $u ) {
		$pw = WP_Application_Passwords::get_user_application_passwords( $u->ID );
		if ( empty( $pw ) ) {
			continue;
		}
		if ( user_can( $u->ID, 'publish_posts' ) ) {
			$out[] = $u->user_login;
		}
	}
	set_transient( 'su_ops_overpriv', $out, 6 * HOUR_IN_SECONDS );
	return $out;
}

function studentup_ops_notice() {
	if ( ! current_user_can( 'manage_options' ) || get_user_meta( get_current_user_id(), 'su_ops_notice_off', true ) ) {
		return;
	}
	$bad = studentup_ops_overprivileged_bots();
	if ( ! $bad ) {
		return;
	}
	$url = wp_nonce_url( add_query_arg( 'su_ops_dismiss', '1' ), 'su_ops_dismiss' );
	echo '<div class="notice notice-warning"><p><strong>StudentUp భద్రత:</strong> Application Password ఉన్న ఈ యూజర్లు పోస్ట్ publish చేయగలరు — <code>' . esc_html( implode( ', ', $bad ) ) . '</code>. బాట్ కోసం <em>StudentUp Bot (drafts only)</em> రోల్ ఉన్న కొత్త యూజర్ సృష్టించి, దాని Application Password ని <code>.env</code> లో పెట్టండి. <a href="' . esc_url( $url ) . '">ఈ నోటీసు మూసివేయి</a></p></div>';
}
add_action( 'admin_notices', 'studentup_ops_notice' );

function studentup_ops_dismiss() {
	if ( isset( $_GET['su_ops_dismiss'] ) && current_user_can( 'manage_options' ) && check_admin_referer( 'su_ops_dismiss' ) ) {
		update_user_meta( get_current_user_id(), 'su_ops_notice_off', 1 );
		wp_safe_redirect( remove_query_arg( array( 'su_ops_dismiss', '_wpnonce' ) ) );
		exit;
	}
}
add_action( 'admin_init', 'studentup_ops_dismiss' );

/* Clear the privilege cache whenever app passwords or roles change. */
foreach ( array( 'wp_create_application_password', 'wp_delete_application_password', 'set_user_role', 'add_user_role', 'remove_user_role' ) as $hook ) {
	add_action( $hook, function () { delete_transient( 'su_ops_overpriv' ); } );
}
