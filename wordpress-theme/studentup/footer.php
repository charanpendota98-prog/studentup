<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<?php
/**
 * Footer + fixed socials (right side, vertically centered).
 *
 * @package studentup
 */

?>
<?php studentup_cta_section(); ?>

<footer class="footer">
	<div class="wrap">
		<div class="footer-grid">
			<div>
				<h3><?php bloginfo( 'name' ); ?></h3>
				<p>Jobs, scholarships, results and exam updates for students.</p>
				<p><?php echo studentup_ui_icon( 'check', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> Spotted a mistake? Tell us at <a href="mailto:<?php echo esc_attr( studentup_contact_email() ); ?>"><?php echo esc_html( studentup_contact_email() ); ?></a></p>
			</div>
			<div>
				<h3>Categories</h3>
				<ul>
					<?php
					foreach ( array_slice( studentup_most_used(), 0, 5 ) as $m ) :
						$term = studentup_used_term( $m['slug'] );   // v89: alias-aware
						if ( ! $term ) {
							continue;
						}
						?>
						<li><a href="<?php echo esc_url( get_category_link( $term ) ); ?>"><?php echo esc_html( $m['label'] ); ?></a></li>
					<?php endforeach; ?>
				</ul>
			</div>
			<div>
				<h3>Other links</h3>
				<?php
				if ( has_nav_menu( 'footer' ) ) {
					wp_nav_menu( array( 'theme_location' => 'footer', 'container' => false, 'depth' => 1, 'fallback_cb' => false ) );
				}
				?>
				<ul>
					<li><a href="<?php echo esc_url( studentup_social_links()['telegram'] ); ?>" target="_blank" rel="noopener">Telegram channel</a></li>
					<li><a href="<?php echo esc_url( home_url( '/#qualsplit' ) ); ?>">Jobs by qualification</a></li>
					<?php
					/*
					 * v94: policy pages footer lo link avvali — readers + Google
					 * (AdSense reviewers kuda) prathi page nunchi reach avvali.
					 * Page publish kaakapote link render avvadu (404 ledu).
					 */
					$su_policy = array(
						'privacy'          => 'Privacy policy',
						'about'            => 'About us',
						'contact'          => 'Contact',
						'disclaimer'       => 'Disclaimer',
						'terms'            => 'Terms',
						'editorial-policy' => 'Editorial policy',
					);
					foreach ( $su_policy as $su_slug => $su_label ) :
						$su_page = get_page_by_path( $su_slug );
						if ( ! $su_page || 'publish' !== get_post_status( $su_page ) ) {
							continue;
						}
						?>
						<li><a href="<?php echo esc_url( get_permalink( $su_page ) ); ?>"><?php echo esc_html( $su_label ); ?></a></li>
					<?php endforeach; ?>
				</ul>
			</div>
			<div>
				<h3><?php esc_html_e( 'Follow us', 'studentup' ); ?></h3>
				<?php $su_ft = studentup_social_links(); ?>
				<div class="su-ft-soc">
					<a class="su-socb-wa" href="<?php echo esc_url( $su_ft['whatsapp'] ); ?>" target="_blank" rel="noopener" aria-label="<?php esc_attr_e( 'WhatsApp', 'studentup' ); ?>"><?php echo studentup_social_icon( 'whatsapp', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
					<a class="su-socb-tg" href="<?php echo esc_url( $su_ft['telegram'] ); ?>" target="_blank" rel="noopener" aria-label="<?php esc_attr_e( 'Telegram', 'studentup' ); ?>"><?php echo studentup_social_icon( 'telegram', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
					<a class="su-socb-ig" href="<?php echo esc_url( $su_ft['instagram'] ); ?>" target="_blank" rel="noopener" aria-label="<?php esc_attr_e( 'Instagram', 'studentup' ); ?>"><?php echo studentup_social_icon( 'instagram', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
					<a class="su-socb-yt" href="<?php echo esc_url( $su_ft['youtube'] ); ?>" target="_blank" rel="noopener" aria-label="<?php esc_attr_e( 'YouTube', 'studentup' ); ?>"><?php echo studentup_social_icon( 'youtube', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
				</div>
				<p><?php esc_html_e( 'Daily updates free ga — join avvandi.', 'studentup' ); ?></p>
			</div>
		</div>
		<div class="footer-bottom">
			<span>© <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?> — All rights reserved.</span>
			<?php // v283: owner — footer lo disclaimer sentence vaddu (Disclaimer page + policy links unnayi). ?>
			<?php studentup_tg_join_block( 'footer' ); // v91: Telegram join chip (private channel override supported) ?>
		</div>
	</div>
</footer>

<?php $su_soc = studentup_social_links(); // v304 FIX: header.php lo define ayina $su_soc footer template scope lo undadu → rail hrefs khali ayyevi (live bug). ?>
<nav class="su-social" id="surail" aria-label="<?php esc_attr_e( 'Social media', 'studentup' ); ?>">
	<button type="button" class="su-close" id="suclose" aria-label="<?php esc_attr_e( 'Hide social icons', 'studentup' ); ?>"><?php echo studentup_ui_icon( 'close', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></button>
	<a class="su-soc su-socb-wa" href="<?php echo esc_url( $su_soc['whatsapp'] ); ?>" target="_blank" rel="noopener" aria-label="WhatsApp"><?php echo studentup_social_icon( 'whatsapp', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
	<a class="su-soc su-socb-tg" href="<?php echo esc_url( $su_soc['telegram'] ); ?>" target="_blank" rel="noopener" aria-label="Telegram"><?php echo studentup_social_icon( 'telegram', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
	<a class="su-soc su-socb-ig" href="<?php echo esc_url( $su_soc['instagram'] ); ?>" target="_blank" rel="noopener" aria-label="Instagram"><?php echo studentup_social_icon( 'instagram', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
	<a class="su-soc su-socb-yt" href="<?php echo esc_url( $su_soc['youtube'] ); ?>" target="_blank" rel="noopener" aria-label="YouTube"><?php echo studentup_social_icon( 'youtube', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
</nav>
<button type="button" class="su-tab" id="sutab" aria-label="<?php esc_attr_e( 'Show social icons', 'studentup' ); ?>">‹</button>

<?php
// v64: sticky bottom ad (option: StudentUp → Ads → Sticky bottom ad ON)
if ( studentup_opt( 'sticky_ad', '0' ) ) :
	?>
	<script>document.body.classList.add('su-has-stickyad');</script>
	<div class="su-stickyad" id="su-stickyad">
		<button type="button" class="su-sticky-close" aria-label="Close"><?php echo studentup_ui_icon( 'close', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></button>
		<?php studentup_ad( 'anchor' ); ?>
	</div>
<?php endif; ?>

<?php
// v72.1: Web-app install — native APK claim cheyyakunda, browser-provided install flow.
// Click: Android/Chrome lo install prompt, iPhone/desktop lo device-wise steps.
if ( studentup_opt( 'pwa', '1' ) && studentup_opt( 'install_prompt', '1' ) ) :
	?>
	<button type="button" class="installbtn su-install-cta" aria-controls="installhint" aria-expanded="false" id="installbtn"><?php echo studentup_ui_icon( 'download', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> Download App <span class="ibadge">WEB APP</span></button>
	<div class="installsheet" id="installhint" hidden role="dialog" aria-modal="true" aria-labelledby="isheet-title">
		<h3 id="isheet-title">Install StudentUp as a web app</h3>
		<p class="isub">One-tap access · visited pages can stay available offline. No native APK download is required.</p>
		<ol id="isteps">
			<li><b>Android (Chrome):</b> ⋮ Menu → <b>Install app</b> / <b>Add to Home screen</b></li>
			<li><b>iPhone (Safari):</b> tap <b>Share</b> → <b>Add to Home Screen</b> → Add</li>
			<li><b>Computer:</b> click the install icon in the address bar</li>
		</ol>
		<div class="irow">
			<button type="button" class="installok" id="installnow">Install now</button>
			<button type="button" class="installclose" id="installclose">Later</button>
		</div>
	</div>
<?php endif; ?>

<?php
// v92: Saved rail + drawer (reader bookmarks). localStorage mattrame — server load ledu.
studentup_saved_panel();
?>

<?php wp_footer(); ?>
</body>
</html>
