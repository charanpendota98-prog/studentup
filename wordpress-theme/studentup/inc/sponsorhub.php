<?php
/**
 * High-RPM Contextual Sponsor Hub & Verified Study Partner Box.
 *
 * Provides dedicated learning partners and preparation material recommendations.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Render Contextual Sponsor & Study Partner Box.
 *
 * @return void
 */
function studentup_sponsor_partner_box() {
	if ( ! is_singular( 'post' ) || ! studentup_opt( 'sponsor_hub', '1' ) ) {
		return;
	}
	/*
	 * v291 (trust + AdSense policy): real partner (Settings → Featured partner ad:
	 * name/title/link) configure chesthe ne render. Mundu hardcoded "SPONSORED ·
	 * Free Study Kit" box prathi post lo vachedi — sponsor lekunda "Sponsored"
	 * label = misleading → reader trust + approval risk. Data lekapote render kaadu.
	 */
	$partner = studentup_featured_partner_ad();
	if ( ! $partner ) {
		return;
	}
	?>
	<section class="su-sponsor-box" aria-label="<?php esc_attr_e( 'Sponsored partner', 'studentup' ); ?>">
		<div class="su-sponsor-kicker"><?php echo esc_html( 'SPONSORED' . ( $partner['name'] ? ' · ' . $partner['name'] : '' ) ); ?></div>
		<div class="su-sponsor-card">
			<?php if ( $partner['image'] ) : ?>
				<img class="su-sponsor-img" src="<?php echo esc_url( $partner['image'] ); ?>" alt="<?php echo esc_attr( $partner['name'] ? $partner['name'] : '' ); ?>" loading="lazy" decoding="async" width="56" height="56">
			<?php else : ?>
				<div class="su-sponsor-icon" aria-hidden="true"><?php echo studentup_ui_icon( 'school', 24 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></div>
			<?php endif; ?>
			<div class="su-sponsor-info">
				<h3 class="su-sponsor-title"><?php echo esc_html( $partner['title'] ); ?></h3>
				<?php if ( $partner['description'] ) : ?>
					<p class="su-sponsor-desc"><?php echo esc_html( $partner['description'] ); ?></p>
				<?php endif; ?>
			</div>
			<div class="su-sponsor-action">
				<a href="<?php echo esc_url( $partner['link'] ); ?>" target="_blank" rel="sponsored nofollow noopener" class="su-sponsor-btn" data-su-ev="partner_click"><?php echo esc_html( $partner['cta'] ); ?></a>
			</div>
		</div>
	</section>
	<?php
}
