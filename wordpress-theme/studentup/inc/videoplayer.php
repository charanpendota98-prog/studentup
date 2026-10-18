<?php
/**
 * Smart High-CPM Video & Outstream Ad Container.
 *
 * Reserves a zero-CLS responsive video slot for media and outstream units.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Render Video / High-CPM Outstream Slot.
 *
 * @return void
 */
function studentup_video_ad_slot() {
	if ( ! is_singular( 'post' ) || ! studentup_opt( 'video_ad_enabled', '1' ) ) {
		return;
	}

	$slot_id = (string) get_option( 'studentup_adsense_slot_video', '' );
	$client  = studentup_adsense_client();


	if ( ! ( $client && $slot_id && studentup_consent_ok() ) ) {
		/* v213 owner feedback: "SPONSORED MEDIA ▶ Video Analysis … available
		   soon" placeholder = space waste. Real ad unit lekapothe ippudu
		   emi render avvadu (zero empty box, zero CLS). */
		return;
	}

	?>
	<div class="su-video-ad-container su-ad-reserved" style="min-height:200px" data-su-height="200" aria-label="<?php echo esc_attr__( 'Featured Media Unit', 'studentup' ); ?>">
		<aside class="su-video-ad-box">
			<div class="su-ad-kicker">SPONSORED MEDIA</div>
			<ins class="adsbygoogle"
				style="display:block"
				data-ad-client="<?php echo esc_attr( $client ); ?>"
				data-ad-slot="<?php echo esc_attr( $slot_id ); ?>"
				data-ad-format="auto"
				data-full-width-responsive="true"></ins>
			<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
		</aside>
	</div>
	<?php
}
