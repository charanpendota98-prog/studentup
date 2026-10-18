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
				<p><?php esc_html_e( 'Jobs, scholarships, results and exam updates for students.', 'studentup' ); ?></p>
				<p><?php echo studentup_ui_icon( 'check', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Spotted a mistake? Tell us at', 'studentup' ); ?> <a href="mailto:<?php echo esc_attr( studentup_contact_email() ); ?>"><?php echo esc_html( studentup_contact_email() ); ?></a></p>
			</div>
			<div>
				<h3><?php esc_html_e( 'Categories', 'studentup' ); ?></h3>
				<ul>
					<?php
					foreach ( array_slice( studentup_most_used(), 0, 5 ) as $m ) :
						$term = studentup_used_term( $m['slug'] );   // v89: alias-aware
						if ( ! $term ) {
							continue;
						}
						?>
						<li><a href="<?php echo esc_url( get_category_link( $term ) ); ?>"><?php echo esc_html( studentup_nav_english() ? $m['label'] : translate( $m['label'], 'studentup' ) ); ?></a></li>
					<?php endforeach; ?>
				</ul>
			</div>
			<div>
				<h3><?php esc_html_e( 'Other links', 'studentup' ); ?></h3>
				<?php
				// v308 NEAT: menu unte menu mattrame; lekapote policy fallback list. Mundu rendu render ayyi
				// (About Us + About us, Privacy Policy + Privacy policy ...) prathi link 2 sarlu kanipinchedi.
				if ( has_nav_menu( 'footer' ) ) {
					wp_nav_menu( array( 'theme_location' => 'footer', 'container' => false, 'depth' => 1, 'fallback_cb' => false ) );
				} else {
					?>
				<ul>
					<?php
					$su_policy = array(
						'about'            => 'About us',
						'contact'          => 'Contact',
						'privacy'          => 'Privacy policy',
						'disclaimer'       => 'Disclaimer',
						'terms'            => 'Terms',
						'editorial-policy' => 'Editorial policy',
						'post-your-news'   => 'Post your news',
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
					<?php
				}
				?>
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
			</div>
		</div>
		<div class="footer-bottom">
			<span>© <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?> — <?php esc_html_e( 'All rights reserved.', 'studentup' ); ?></span>
			<?php // v283: owner — footer lo disclaimer sentence vaddu (Disclaimer page + policy links unnayi). ?>
		</div>
	</div>
</footer>

<?php $su_soc = studentup_social_links(); // v304 FIX: header.php lo define ayina $su_soc footer template scope lo undadu → rail hrefs khali ayyevi (live bug). ?>
<nav class="su-social" id="surail" aria-label="<?php esc_attr_e( 'Social media', 'studentup' ); ?>">
	<button type="button" class="su-close" id="suclose" aria-label="<?php esc_attr_e( 'Hide social icons', 'studentup' ); ?>"><?php echo studentup_ui_icon( 'close', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></button>
	<a class="su-soc su-socb-wa" href="<?php echo esc_url( $su_soc['whatsapp'] ); ?>" target="_blank" rel="noopener" aria-label="<?php echo esc_attr__( 'WhatsApp', 'studentup' ); ?>"><?php echo studentup_social_icon( 'whatsapp', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
	<a class="su-soc su-socb-tg" href="<?php echo esc_url( $su_soc['telegram'] ); ?>" target="_blank" rel="noopener" aria-label="<?php echo esc_attr__( 'Telegram', 'studentup' ); ?>"><?php echo studentup_social_icon( 'telegram', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
	<a class="su-soc su-socb-ig" href="<?php echo esc_url( $su_soc['instagram'] ); ?>" target="_blank" rel="noopener" aria-label="<?php echo esc_attr__( 'Instagram', 'studentup' ); ?>"><?php echo studentup_social_icon( 'instagram', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
	<a class="su-soc su-socb-yt" href="<?php echo esc_url( $su_soc['youtube'] ); ?>" target="_blank" rel="noopener" aria-label="<?php echo esc_attr__( 'YouTube', 'studentup' ); ?>"><?php echo studentup_social_icon( 'youtube', 19 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></a>
</nav>
<button type="button" class="su-tab" id="sutab" aria-label="<?php esc_attr_e( 'Show social icons', 'studentup' ); ?>">‹</button>

<?php
// v64: sticky bottom ad (option: StudentUp → Ads → Sticky bottom ad ON)
if ( studentup_opt( 'sticky_ad', '0' ) ) :
	?>
	<script>document.body.classList.add('su-has-stickyad');</script>
	<div class="su-stickyad" id="su-stickyad">
		<button type="button" class="su-sticky-close" aria-label="<?php echo esc_attr__( 'Close', 'studentup' ); ?>"><?php echo studentup_ui_icon( 'close', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></button>
		<?php studentup_ad( 'anchor' ); ?>
	</div>
<?php endif; ?>

<?php
// v72.1: Web-app install — native APK claim cheyyakunda, browser-provided install flow.
// Click: Android/Chrome lo install prompt, iPhone/desktop lo device-wise steps.
if ( studentup_opt( 'pwa', '1' ) && studentup_opt( 'install_prompt', '1' ) ) :
	?>
	<div class="su-installwrap" id="su-installwrap"><button type="button" class="installbtn su-install-cta" aria-controls="installhint" aria-expanded="false" id="installbtn"><?php echo studentup_ui_icon( 'download', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Download App', 'studentup' ); ?> <span class="ibadge"><?php echo esc_html__( 'WEB APP', 'studentup' ); ?></span></button><button type="button" class="su-installwrap-x" id="installbtn-x" aria-label="<?php esc_attr_e( 'Close', 'studentup' ); ?>">&#x2715;</button></div>
	<div class="installsheet" id="installhint" hidden role="dialog" aria-modal="true" aria-labelledby="isheet-title">
		<h3 id="isheet-title"><?php esc_html_e( 'Install StudentUp as a web app', 'studentup' ); ?></h3>
		<p class="isub"><?php esc_html_e( 'One-tap access · visited pages can stay available offline. No native APK download is required.', 'studentup' ); ?></p>
		<ol id="isteps">
			<li><b>Android (Chrome):</b> ⋮ Menu → <b><?php esc_html_e( 'Install app', 'studentup' ); ?></b> / <b><?php esc_html_e( 'Add to Home screen', 'studentup' ); ?></b></li>
			<li><b>iPhone (Safari):</b> <b>Share</b> → <b><?php echo esc_html__( 'Add to Home Screen', 'studentup' ); ?></b> → Add</li>
			<li><b><?php esc_html_e( 'Computer:', 'studentup' ); ?></b> <?php esc_html_e( 'click the install icon in the address bar', 'studentup' ); ?></li>
		</ol>
		<div class="irow">
			<button type="button" class="installok" id="installnow"><?php esc_html_e( 'Install now', 'studentup' ); ?></button>
			<button type="button" class="installclose" id="installclose"><?php esc_html_e( 'Later', 'studentup' ); ?></button>
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
