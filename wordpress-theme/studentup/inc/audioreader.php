<?php
/**
 * Text-to-Speech Web Audio Article Reader.
 *
 * Provides in-browser speech synthesis for article headlines and key summary details.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Render Audio Article Reader Bar.
 *
 * @return void
 */
function studentup_audio_reader() {
	if ( ! is_singular( 'post' ) || ! studentup_opt( 'audio_reader', '1' ) ) {
		return;
	}

	$post_id   = get_the_ID();
	$title     = get_the_title( $post_id );
	$vacancies = get_post_meta( $post_id, 'studentup_vacancies', true );
	$last_date = get_post_meta( $post_id, 'studentup_last_date', true );

	// Audio summary script for speech synthesis
	$speech_parts = array( $title );
	if ( $vacancies ) {
		$speech_parts[] = 'Total vacancies ' . $vacancies . '.';
	}
	if ( $last_date ) {
		$ld_ts          = preg_match( '/^\d{4}-\d{2}-\d{2}$/', $last_date ) ? strtotime( $last_date . ' 12:00:00' ) : false;   // v304: TTS "2026-11-05" kaadu — "5 November 2026"
		$speech_parts[] = 'Last date to apply is ' . ( $ld_ts ? wp_date( 'j F Y', $ld_ts ) : $last_date ) . '.';
	}
	$speech_parts[] = 'Read the full notification details below.';
	$speech_text = implode( ' ', $speech_parts );

	?>
	<div class="su-audio-reader-box" id="su-audio-box" data-speech="<?php echo esc_attr( $speech_text ); ?>" aria-label="<?php esc_attr_e( 'Audio Article Reader', 'studentup' ); ?>">
		<div class="su-audio-left">
			<button type="button" id="su-audio-btn" class="su-audio-btn">
				<span class="su-audio-icon" id="su-audio-icon"><?php echo studentup_ui_icon( 'speaker', 16 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
				<span class="su-audio-label" id="su-audio-label"><?php esc_html_e( 'Listen to Article', 'studentup' ); ?></span>
			</button>
			<div class="su-audio-waves" id="su-audio-waves" aria-hidden="true" style="display:none;">
				<span class="su-wave-bar"></span>
				<span class="su-wave-bar"></span>
				<span class="su-wave-bar"></span>
				<span class="su-wave-bar"></span>
			</div>
		</div>
		<div class="su-audio-controls" id="su-audio-controls" style="display:none;">
			<button type="button" id="su-audio-stop" class="su-audio-ctrl-btn" aria-label="<?php esc_attr_e( 'Stop audio', 'studentup' ); ?>"><?php echo studentup_ui_icon( 'close', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> Stop</button>
			<span class="su-audio-speed" id="su-audio-speed-btn" role="button" tabindex="0" title="Change speed">1.0x</span>
		</div>
	</div>
	<?php
}
