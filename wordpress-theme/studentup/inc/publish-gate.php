<?php
/**
 * v1.9.173: WordPress-side PUBLISH GATE.
 *
 * Why: every quality guard lived in the bot. On 22-Oct the owner bulk-published
 * 19 drafts from the Posts list and WordPress happily put 4× RRB NTPC, 3× AP DSC
 * and a "REVIEW:" draft live in one minute. The site itself must refuse that.
 *
 * Rules (publish → draft downgrade + admin notice; nothing is deleted):
 *   1. Title still starts with "REVIEW:"            → not reviewed yet.
 *   2. A PUBLISHED post about the same notification  → duplicate (same_topic ≥ 0.8).
 *   3. Title contains Hindi/Tamil/Kannada/Malayalam/Bengali/Urdu script → wrong feed.
 * Bot drafts are never touched (they arrive as draft). Only the publish
 * transition of post_type=post is gated. Admin can force: tick "Force publish
 * (skip StudentUp gate)" — stored as _su_force_publish for the audit log.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function studentup_publish_gate_reason( $post_id, $title ) {
	$title = trim( wp_strip_all_tags( (string) $title ) );
	if ( '' === $title ) {
		return '';
	}
	if ( 0 === stripos( $title, 'REVIEW:' ) ) {
		return 'title starts with "REVIEW:" — bot flagged it for a human look; remove the prefix only after checking the flag';
	}
	if ( preg_match( '/[\x{0900}-\x{0DFF}\x{0600}-\x{06FF}]/u', $title ) && ! preg_match( '/[\x{0C00}-\x{0C7F}]/u', $title ) ) {
		return 'title is in a non-Telugu Indic script (feed mix-up)';
	}
	if ( ! function_exists( 'studentup_same_topic' ) ) {
		return '';
	}
	$q = new WP_Query(
		array(
			'post_type'              => 'post',
			'post_status'            => 'publish',
			'posts_per_page'         => 60,
			'post__not_in'           => array( (int) $post_id ),
			'date_query'             => array( array( 'after' => '120 days ago' ) ),
			'fields'                 => 'ids',
			'no_found_rows'          => true,
			'update_post_meta_cache' => false,
			'update_post_term_cache' => false,
		)
	);
	foreach ( (array) $q->posts as $pid ) {
		$other = get_the_title( $pid );
		if ( studentup_same_topic( $title, $other ) ) {
			return sprintf( 'same notification is already live: <a href="%s">%s</a> (#%d) — update that post instead, or trash it first', esc_url( get_edit_post_link( $pid, 'raw' ) ), esc_html( $other ), $pid );
		}
	}
	return '';
}

/**
 * Filter runs for classic editor, quick edit, bulk edit AND the REST API (block
 * editor / bot) — wp_insert_post_data is the single choke point.
 */
function studentup_publish_gate( $data, $postarr ) {
	if ( 'post' !== ( $data['post_type'] ?? '' ) || 'publish' !== ( $data['post_status'] ?? '' ) ) {
		return $data;
	}
	$post_id = (int) ( $postarr['ID'] ?? 0 );
	if ( $post_id && 'publish' === get_post_status( $post_id ) ) {
		return $data; // already live — editing a published post is not gated.
	}
	$forced = ! empty( $postarr['su_force_publish'] )
		|| ( isset( $_POST['su_force_publish'], $_POST['su_force_publish_nonce'] ) // phpcs:ignore WordPress.Security.NonceVerification.Missing
			&& wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['su_force_publish_nonce'] ) ), 'su_force_publish' ) )
		|| ( $post_id && get_post_meta( $post_id, '_su_force_publish', true ) );
	if ( $forced && current_user_can( 'publish_posts' ) ) {
		return $data;
	}
	// 1.9.178 (audit F-9): WP-CLI no longer bypasses the gate silently. A CLI
	// operator who really needs it sets SU_FORCE_PUBLISH=1 (or su_force_publish).
	if ( defined( 'WP_CLI' ) && WP_CLI && getenv( 'SU_FORCE_PUBLISH' ) ) {
		return $data;
	}
	$reason = studentup_publish_gate_reason( $post_id, $data['post_title'] ?? '' );
	if ( '' === $reason ) {
		return $data;
	}
	$data['post_status'] = 'draft';
	if ( defined( 'WP_CLI' ) && WP_CLI && class_exists( 'WP_CLI' ) ) {
		WP_CLI::warning( 'StudentUp publish gate: kept as draft — ' . wp_strip_all_tags( $reason ) . ' (SU_FORCE_PUBLISH=1 to override)' );
	}
	$log   = (array) get_option( 'studentup_publish_gate_log', array() );
	$log[] = array( 't' => time(), 'id' => $post_id, 'title' => wp_strip_all_tags( (string) ( $data['post_title'] ?? '' ) ), 'reason' => wp_strip_all_tags( $reason ) );
	update_option( 'studentup_publish_gate_log', array_slice( $log, -50 ), false );
	set_transient( 'su_gate_notice_' . get_current_user_id(), array( 'title' => $data['post_title'] ?? '', 'reason' => $reason ), 120 );
	return $data;
}
add_filter( 'wp_insert_post_data', 'studentup_publish_gate', 5, 2 );

function studentup_publish_gate_notice() {
	$n = get_transient( 'su_gate_notice_' . get_current_user_id() );
	if ( ! $n ) {
		return;
	}
	delete_transient( 'su_gate_notice_' . get_current_user_id() );
	printf(
		'<div class="notice notice-error"><p><b>StudentUp publish gate:</b> “%s” was kept as <b>draft</b> — %s.</p></div>',
		esc_html( wp_strip_all_tags( (string) $n['title'] ) ),
		wp_kses( $n['reason'], array( 'a' => array( 'href' => array() ) ) )
	);
}
add_action( 'admin_notices', 'studentup_publish_gate_notice' );

/** Force checkbox in the Publish box (classic) — audit-logged. */
function studentup_publish_gate_force_box() {
	global $post;
	if ( ! $post || 'post' !== $post->post_type || 'publish' === $post->post_status || ! current_user_can( 'publish_posts' ) ) {
		return;
	}
	wp_nonce_field( 'su_force_publish', 'su_force_publish_nonce' );
	echo '<div class="misc-pub-section"><label><input type="checkbox" name="su_force_publish" value="1"> Force publish (skip StudentUp duplicate/REVIEW gate)</label></div>';
}
add_action( 'post_submitbox_misc_actions', 'studentup_publish_gate_force_box' );

function studentup_publish_gate_force_save( $post_id ) {
	if ( isset( $_POST['su_force_publish'], $_POST['su_force_publish_nonce'] )
		&& wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['su_force_publish_nonce'] ) ), 'su_force_publish' )
		&& current_user_can( 'publish_posts' ) ) {
		update_post_meta( $post_id, '_su_force_publish', time() );
	}
}
add_action( 'save_post_post', 'studentup_publish_gate_force_save', 1 );

/** Site Health / StudentUp status: last gate decisions (operators see why). */
function studentup_publish_gate_log() {
	return (array) get_option( 'studentup_publish_gate_log', array() );
}
