<?php
/**
 * Sidebar — widget area + sticky ad (desktop lo viewability ekkuva → RPM ekkuva).
 *
 * Widgets lekapote asalu markup render avvadu (layout break avvadu).
 * Registered widget areas: `sidebar-1` (main) — `inc/template.php` lo chusandi.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// v1.9.168: widget area renders ONLY when the owner turns it on — leftover widgets from a
// previous theme (Blocksy search block, lorem-ipsum testimonial, empty 'Posts') were showing live.
$su_has_widgets = is_active_sidebar( 'sidebar-1' ) && '1' === (string) studentup_opt( 'sidebar_widgets', '0' );
// v308: ad code lekapote (AdSense approval mundu) empty wrapper render kaadu.
$su_has_ad = function_exists( 'studentup_ad_available' ) ? studentup_ad_available( 'sidebar' ) : studentup_ads_allowed( 'sidebar' );
// v1.9.132: widgets/ads lekapoina desktop sidebar khali ga undadu — real-data
// sidecards (latest updates · closing soon · organisations). Phone lo hidden
// (same lists main column lo already untayi).
$su_auto = function_exists( 'studentup_sidebar_auto_cards' ) ? studentup_sidebar_auto_cards() : '';
if ( ! $su_has_widgets && ! $su_has_ad && '' === $su_auto ) {
	return;
}
?>
<aside class="su-sidebar<?php echo ( ! $su_has_widgets && ! $su_has_ad ) ? ' su-side-auto' : ''; ?>" aria-label="<?php esc_attr_e( 'Sidebar', 'studentup' ); ?>">
	<?php if ( $su_has_ad ) : ?>
		<div class="su-sidebar-ad"><?php studentup_ad( 'sidebar' ); ?></div>
	<?php endif; ?>

	<?php
	if ( $su_has_widgets ) {
		dynamic_sidebar( 'sidebar-1' );
	}
	echo $su_auto; // phpcs:ignore WordPress.Security.EscapeOutput -- built with esc_* in studentup_sidebar_auto_cards()
	?>
</aside>
