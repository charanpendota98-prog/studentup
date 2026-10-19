<?php
/**
 * v249 — DOUBTS / Q&A (prathi post kinda) — real backend tho.
 *
 * Owner: "inka chaala advanced ga". Ee feature nijam ga advanced enduko:
 *   · User-generated content = Google ki fresh content + long-tail keywords
 *     ("TSPSC group 2 lo BC-B ki age relaxation enta?" laanti real questions).
 *   · QAPage schema → rich result eligibility (answered questions matrame).
 *   · Return visits: question adigina student answer kosam malli vastadu.
 *   · Content gap radar: students em adugutunnaro adi next post topic.
 *
 * Nijam ga em build chesam (UI matrame kaadu):
 *   STORAGE    : WordPress comments table, comment_type = 'su_doubt'
 *                (backup, export, moderation anni WP tho vastayi).
 *   PERMISSION : public post; admin/editor matrame approve + answer.
 *   VALIDATION : length limits, sanitize, URL/link block (spam), honeypot,
 *                nonce, per-IP rate limit (60s), duplicate guard.
 *   MODERATION : default unapproved — admin approve chesaka matrame public.
 *                Answer leni question Google ki schema lo pampam.
 *   ERRORS     : prathi fail ki clear message + no-JS form kuda pani chestundi.
 *   PRIVACY    : email optional, public ga chupincham; IP hash matrame.
 *
 * @package StudentUp
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const STUDENTUP_DOUBT_TYPE = 'su_doubt';
const STUDENTUP_DOUBT_MAX  = 600;
const STUDENTUP_DOUBT_MIN  = 10;

/* ------------------------------------------------------------- 1. helpers */

/**
 * Feature ON unnaya? (filter tho off cheyyochu)
 */
function studentup_doubts_enabled() {
	return (bool) apply_filters( 'studentup_doubts_enabled', true );
}

/**
 * Asker identity — IP + UA hash matrame (personal data store cheyyam).
 */
function studentup_doubt_fingerprint() {
	$ip = isset( $_SERVER['REMOTE_ADDR'] ) ? (string) $_SERVER['REMOTE_ADDR'] : '';
	$ua = isset( $_SERVER['HTTP_USER_AGENT'] ) ? (string) $_SERVER['HTTP_USER_AGENT'] : '';
	return substr( wp_hash( $ip . '|' . $ua ), 0, 24 );
}

/**
 * Approved doubts for a post (answer unna/leni).
 *
 * @param int $post_id Post.
 * @return array<int, WP_Comment>
 */
function studentup_get_doubts( $post_id ) {
	$post_id = absint( $post_id );
	if ( ! $post_id ) {
		return array();
	}
	$items = get_comments(
		array(
			'post_id' => $post_id,
			'type'    => STUDENTUP_DOUBT_TYPE,
			'status'  => 'approve',
			'orderby' => 'comment_date_gmt',
			'order'   => 'ASC',
			'number'  => 50,
		)
	);
	return is_array( $items ) ? $items : array();
}

/**
 * Admin answer (comment meta lo).
 */
function studentup_doubt_answer( $comment_id ) {
	return (string) get_comment_meta( absint( $comment_id ), 'su_answer', true );
}

/* ------------------------------------------------------- 2. save + validate */

/**
 * Question save. Returns array( ok => bool, msg => string ).
 *
 * @param int    $post_id  Post id.
 * @param string $question Raw question.
 * @param string $name     Optional display name.
 * @param string $honeypot Hidden field — bot aithe nindutundi.
 * @return array
 */
function studentup_save_doubt( $post_id, $question, $name = '', $honeypot = '' ) {
	$post_id = absint( $post_id );

	if ( ! studentup_doubts_enabled() ) {
		return array( 'ok' => false, 'msg' => __( 'Questions are closed right now.', 'studentup' ) );
	}
	if ( '' !== trim( (string) $honeypot ) ) {
		// Bot — silent ga accept chesinattu chupinchi, save cheyyam.
		return array( 'ok' => true, 'msg' => __( 'Thanks! Your question is waiting for review.', 'studentup' ) );
	}
	if ( ! $post_id || 'publish' !== get_post_status( $post_id ) ) {
		return array( 'ok' => false, 'msg' => __( 'This page cannot take questions.', 'studentup' ) );
	}

	$question = wp_strip_all_tags( (string) $question );
	$question = trim( preg_replace( '/\s+/u', ' ', $question ) );
	$len      = function_exists( 'mb_strlen' ) ? mb_strlen( $question ) : strlen( $question );

	if ( $len < STUDENTUP_DOUBT_MIN ) {
		return array( 'ok' => false, 'msg' => __( 'Please write your question in a few more words.', 'studentup' ) );
	}
	if ( $len > STUDENTUP_DOUBT_MAX ) {
		return array( 'ok' => false, 'msg' => __( 'Please keep the question under 600 characters.', 'studentup' ) );
	}
	// Spam guard: links / emails / phone numbers vaddu.
	if ( preg_match( '#(https?://|www\.|@[a-z0-9.\-]+\.[a-z]{2,}|\b\d{10}\b)#i', $question ) ) {
		return array( 'ok' => false, 'msg' => __( 'Links, emails and phone numbers are not allowed in questions.', 'studentup' ) );
	}

	$fp = studentup_doubt_fingerprint();

	// Rate limit — 60s lo okkate question.
	$rl = 'su_doubt_rl_' . $fp;
	if ( get_transient( $rl ) ) {
		return array( 'ok' => false, 'msg' => __( 'Please wait a minute before asking again.', 'studentup' ) );
	}

	// Duplicate guard — same post lo same question malli vaddu.
	$existing = get_comments(
		array(
			'post_id' => $post_id,
			'type'    => STUDENTUP_DOUBT_TYPE,
			'status'  => 'all',
			'number'  => 100,
			'fields'  => 'all',
		)
	);
	if ( is_array( $existing ) ) {
		foreach ( $existing as $c ) {
			if ( isset( $c->comment_content )
				&& 0 === strcasecmp( trim( (string) $c->comment_content ), $question ) ) {
				return array( 'ok' => false, 'msg' => __( 'This question is already asked — the answer will appear here.', 'studentup' ) );
			}
		}
	}

	$name = sanitize_text_field( (string) $name );
	$name = '' === $name ? __( 'Student', 'studentup' ) : mb_substr( $name, 0, 40 );

	$id = wp_insert_comment(
		array(
			'comment_post_ID'  => $post_id,
			'comment_author'   => $name,
			'comment_content'  => $question,
			'comment_type'     => STUDENTUP_DOUBT_TYPE,
			'comment_approved' => 0, // moderation: admin approve chesaka matrame public
			'comment_agent'    => 'studentup-doubts',
			'comment_meta'     => array( 'su_fp' => $fp ),
		)
	);
	if ( ! $id ) {
		return array( 'ok' => false, 'msg' => __( 'Could not save the question. Please try again.', 'studentup' ) );
	}

	set_transient( $rl, 1, 60 );

	return array( 'ok' => true, 'msg' => __( 'Thanks! Your question is waiting for review — the answer will appear on this page.', 'studentup' ) );
}

/* ---------------------------------------------------------- 3. no-JS form */

/**
 * POST handler (JS lekunda kuda pani cheyyali).
 */
function studentup_doubt_post_handler() {
	if ( ! isset( $_POST['su_doubt_submit'] ) ) {
		return;
	}
	$post_id = isset( $_POST['su_doubt_post'] ) ? absint( $_POST['su_doubt_post'] ) : 0;
	$nonce   = isset( $_POST['su_doubt_nonce'] ) ? sanitize_text_field( wp_unslash( $_POST['su_doubt_nonce'] ) ) : '';
	if ( ! wp_verify_nonce( $nonce, 'su_doubt_' . $post_id ) ) {
		return;
	}
	$res = studentup_save_doubt(
		$post_id,
		isset( $_POST['su_doubt_q'] ) ? wp_unslash( $_POST['su_doubt_q'] ) : '',
		isset( $_POST['su_doubt_name'] ) ? wp_unslash( $_POST['su_doubt_name'] ) : '',
		isset( $_POST['su_doubt_hp'] ) ? wp_unslash( $_POST['su_doubt_hp'] ) : ''
	);
	$url = add_query_arg( 'su_doubt', $res['ok'] ? 'ok' : 'err', get_permalink( $post_id ) ) . '#su-doubts';
	wp_safe_redirect( $url );
	exit;
}
add_action( 'template_redirect', 'studentup_doubt_post_handler', 5 );

/* ------------------------------------------------------------- 4. REST API */

/**
 * REST: POST /studentup/v1/doubt — same validation, JSON answer.
 */
function studentup_doubts_rest() {
	register_rest_route(
		'studentup/v1',
		'/doubt',
		array(
			'methods'             => 'POST',
			'permission_callback' => '__return_true', // public, kaani rate-limited + moderated
			'args'                => array(
				'post_id'  => array( 'required' => true, 'sanitize_callback' => 'absint' ),
				'question' => array( 'required' => true ),
			),
			'callback'            => function ( $req ) {
				$res = studentup_save_doubt(
					(int) $req->get_param( 'post_id' ),
					(string) $req->get_param( 'question' ),
					(string) $req->get_param( 'name' ),
					(string) $req->get_param( 'hp' )
				);
				return new WP_REST_Response(
					array( 'ok' => (bool) $res['ok'], 'message' => $res['msg'] ),
					$res['ok'] ? 200 : 400
				);
			},
		)
	);
}
add_action( 'rest_api_init', 'studentup_doubts_rest' );

/* --------------------------------------------------------------- 5. render */

/**
 * Q&A block — article kinda.
 */
function studentup_doubts_block( $content ) {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query()
		|| ! studentup_doubts_enabled() ) {
		return $content;
	}
	$post_id = get_the_ID();
	$items   = studentup_get_doubts( $post_id );

	$notice = '';
	if ( isset( $_GET['su_doubt'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Recommended
		$ok     = 'ok' === sanitize_key( wp_unslash( $_GET['su_doubt'] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
		$notice = '<p class="su-doubt-note ' . ( $ok ? 'ok' : 'err' ) . '" role="status">'
			. esc_html( $ok
				? __( 'Thanks! Your question is waiting for review.', 'studentup' )
				: __( 'Could not save that question. Please check and try again.', 'studentup' ) )
			. '</p>';
	}

	$list = '';
	foreach ( $items as $c ) {
		$answer = studentup_doubt_answer( $c->comment_ID );
		$list  .= '<div class="su-doubt">'
			. '<p class="su-doubt-q"><b>Q:</b> ' . esc_html( $c->comment_content ) . '</p>'
			. ( '' !== $answer
				? '<p class="su-doubt-a"><b>A:</b> ' . esc_html( $answer ) . '</p>'
				: '<p class="su-doubt-pending">' . esc_html__( 'Answer coming soon — our editor is verifying it.', 'studentup' ) . '</p>' )
			. '</div>';
	}
	if ( '' === $list ) {
		$list = '<p class="su-doubt-empty">'
			. esc_html__( 'No questions yet. Ask the first one — we answer with the official source.', 'studentup' )
			. '</p>';
	}

	$form = '<form class="su-doubt-form" method="post" action="">'
		. wp_nonce_field( 'su_doubt_' . $post_id, 'su_doubt_nonce', true, false )
		. '<input type="hidden" name="su_doubt_post" value="' . esc_attr( $post_id ) . '" />'
		. '<label class="su-doubt-label" for="su-doubt-q-' . esc_attr( $post_id ) . '">'
		. esc_html__( 'Your question (Telugu or English)', 'studentup' ) . '</label>'
		. '<textarea id="su-doubt-q-' . esc_attr( $post_id ) . '" name="su_doubt_q" rows="3" maxlength="600" required '
		. 'placeholder="' . esc_attr__( 'Example: BC-B category ki age relaxation enta?', 'studentup' ) . '"></textarea>'
		. '<input type="text" name="su_doubt_name" maxlength="40" aria-label="' . esc_attr__( 'Your name (optional)', 'studentup' ) . '" placeholder="'
		. esc_attr__( 'Your name (optional)', 'studentup' ) . '" />'
		// honeypot — screen readers ki kuda hidden, bots matrame nimputayi
		. '<input type="text" name="su_doubt_hp" value="" tabindex="-1" autocomplete="off" aria-hidden="true" class="su-doubt-hp" />'
		. '<button type="submit" name="su_doubt_submit" value="1" class="su-doubt-btn">'
		. esc_html__( 'Ask question', 'studentup' ) . '</button>'
		. '</form>';

	return $content
		. '<section class="su-doubts" id="su-doubts" aria-labelledby="su-doubts-title">'
		. '<h2 id="su-doubts-title">' . esc_html__( 'Doubts & Answers', 'studentup' ) . '</h2>'
		. $notice . $list . $form . '</section>';
}
// v1.9.119: render AFTER Important Links (template action) instead of inside
// the_content — reader sees official links first, then community doubts.
add_action( 'studentup_after_important_links', function () {
	if ( ! is_singular( 'post' ) || ! studentup_doubts_enabled() ) {
		return;
	}
	echo studentup_doubts_block( '' ); // phpcs:ignore WordPress.Security.EscapeOutput -- block builds escaped HTML (single.php loop lo call avutundi)
} );

/* --------------------------------------------------------------- 6. schema */

/**
 * QAPage schema — ANSWERED questions matrame (Google guideline).
 */
function studentup_doubts_schema() {
	if ( is_admin() || is_feed() || ! is_singular( 'post' ) || ! studentup_doubts_enabled() ) {
		return;
	}
	$items = studentup_get_doubts( get_the_ID() );
	$qs    = array();
	foreach ( $items as $c ) {
		$a = studentup_doubt_answer( $c->comment_ID );
		if ( '' === $a ) {
			continue; // answer leni question schema lo vaddu
		}
		$qs[] = array(
			'@type'          => 'Question',
			'name'           => wp_strip_all_tags( $c->comment_content ),
			'answerCount'    => 1,
			'acceptedAnswer' => array(
				'@type' => 'Answer',
				'text'  => wp_strip_all_tags( $a ),
			),
		);
	}
	if ( ! $qs ) {
		return;
	}
	$data = array(
		'@context'   => 'https://schema.org',
		'@type'      => 'QAPage',
		'mainEntity' => count( $qs ) === 1 ? $qs[0] : $qs,
	);
	echo '<script type="application/ld+json">'
		. wp_json_encode( $data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES )
		. '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_doubts_schema', 10 );

/* ---------------------------------------------------------------- 7. admin */

/**
 * Admin: answer box prathi doubt ki (comment edit screen).
 */
function studentup_doubt_admin_field( $comment ) {
	if ( ! isset( $comment->comment_type ) || STUDENTUP_DOUBT_TYPE !== $comment->comment_type ) {
		return;
	}
	$val = studentup_doubt_answer( $comment->comment_ID );
	wp_nonce_field( 'su_doubt_answer', 'su_doubt_answer_nonce', false );
	echo '<table class="form-table"><tr>'
		. '<th><label for="su_answer">' . esc_html__( 'StudentUp answer (public)', 'studentup' ) . '</label></th>'
		. '<td><textarea id="su_answer" name="su_answer" rows="4" class="large-text">'
		. esc_textarea( $val ) . '</textarea>'
		. '<p class="description">'
		. esc_html__( 'Answer with the official source. Only answered questions go into QAPage schema.', 'studentup' )
		. '</p></td></tr></table>';
}
add_action( 'add_meta_boxes_comment', function () {
	add_meta_box(
		'su-doubt-answer',
		__( 'StudentUp — Doubt answer', 'studentup' ),
		'studentup_doubt_admin_field',
		'comment',
		'normal',
		'high'
	);
} );

/**
 * Admin save — capability + nonce check.
 */
function studentup_doubt_admin_save( $comment_id ) {
	if ( ! current_user_can( 'moderate_comments' ) ) {
		return;
	}
	$nonce = isset( $_POST['su_doubt_answer_nonce'] )
		? sanitize_text_field( wp_unslash( $_POST['su_doubt_answer_nonce'] ) ) : '';
	if ( ! wp_verify_nonce( $nonce, 'su_doubt_answer' ) ) {
		return;
	}
	$answer = isset( $_POST['su_answer'] ) ? wp_strip_all_tags( wp_unslash( $_POST['su_answer'] ) ) : '';
	$answer = mb_substr( trim( $answer ), 0, 1200 );
	if ( '' === $answer ) {
		delete_comment_meta( $comment_id, 'su_answer' );
		return;
	}
	update_comment_meta( $comment_id, 'su_answer', $answer );
}
add_action( 'edit_comment', 'studentup_doubt_admin_save' );

/**
 * Doubts ni normal comment counts lo kalupakudadu.
 */
function studentup_doubts_exclude( $clauses ) {
	if ( is_admin() ) {
		return $clauses;
	}
	global $wpdb;
	$clauses['where'] .= $wpdb->prepare( ' AND comment_type != %s', STUDENTUP_DOUBT_TYPE );
	return $clauses;
}
add_filter( 'comments_clauses', 'studentup_doubts_exclude' );
