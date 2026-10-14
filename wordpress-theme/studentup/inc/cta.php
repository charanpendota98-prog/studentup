<?php
/**
 * v71: Students Internet Center + WhatsApp/Telegram join blocks.
 *
 * Why here: the homepage and every post end with a practical next step for the
 * student. Both blocks read the same theme options as the social rail, so the
 * owner changes a number once (StudentUp -> Settings) and everything follows.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Students Internet Center — apply from home: call, WhatsApp documents, get the PDF.
 */
function studentup_cta_internet_center() {
	$soc   = studentup_social_links();
	$phone = studentup_call_number( studentup_opt( 'social_whatsapp', '' ) );
	$tel   = $phone ? 'tel:+91' . $phone : '';
	$mail  = studentup_contact_email();
	?>
	<section class="su-ic su-ic-v2" aria-labelledby="su-ic-title">
		<div class="su-ic-top">
			<span class="su-ic-logo" aria-hidden="true"><?php echo studentup_ui_icon( 'laptop', 22 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
			<div class="su-ic-titles">
				<h2 id="su-ic-title"><?php esc_html_e( 'Students Internet Center', 'studentup' ); ?> <span class="su-ic-badge"><?php esc_html_e( 'TS &amp; AP', 'studentup' ); ?></span></h2>
				<p class="su-ic-sub su-ic-te"><?php esc_html_e( 'విద్యార్థుల ఇంటర్నెట్ సెంటర్', 'studentup' ); ?></p>
			</div>
			<span class="su-ic-live"><span class="su-ic-dot" aria-hidden="true"></span><?php esc_html_e( 'Open today', 'studentup' ); ?></span>
		</div>

		<div class="su-ic-body su-ic-te">
			<p class="su-ic-lead"><?php esc_html_e( 'మీరు jobs apply చేసుకోవటం కోసం ఎక్కడికీ వెళ్లవలసిన అవసరం లేదు. కేవలం మాకు call చేసి, సంబంధించిన documents పంపిస్తే చాలు — అతి తక్కువ ఖర్చులో apply చేసి, filled application PDF మీకు send చేయటం జరుగుతుంది.', 'studentup' ); ?></p>
			<p class="su-ic-lead2"><?php esc_html_e( 'PDF తో పాటు — study materials, previous papers, మరియు preparation group లో add చేయటం కూడా జరుగుతుంది.', 'studentup' ); ?></p>
		</div>

		<ul class="su-ic-perks su-ic-te">
			<li><?php echo studentup_ui_icon( 'doc', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Application PDF', 'studentup' ); ?></li>
			<li><?php echo studentup_ui_icon( 'book', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Materials &amp; previous papers', 'studentup' ); ?></li>
			<li><?php echo studentup_ui_icon( 'person', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Preparation group', 'studentup' ); ?></li>
			<li><?php echo studentup_ui_icon( 'wallet', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'అతి తక్కువ charge', 'studentup' ); ?></li>
		</ul>

		<div class="su-ic-actions">
			<a class="su-wa-box" href="<?php echo esc_url( $soc['whatsapp'] ); ?>" target="_blank" rel="noopener">
				<span class="su-wa-ico" aria-hidden="true"><?php echo studentup_social_icon( 'whatsapp', 20 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
				<span class="su-wa-txt">
					<b><?php esc_html_e( 'WhatsApp లో documents పంపండి', 'studentup' ); ?></b>
					<small><?php esc_html_e( 'Tap చేస్తే మా WhatsApp open అవుతుంది — వెంటనే reply', 'studentup' ); ?></small>
				</span>
			</a>
			<?php if ( $tel ) : ?>
				<a class="su-ic-alt" href="<?php echo esc_attr( $tel ); ?>"><?php echo studentup_social_icon( 'call', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Call now', 'studentup' ); ?></a>
			<?php endif; ?>
			<?php if ( $mail ) : ?>
				<a class="su-ic-alt" href="mailto:<?php echo esc_attr( $mail ); ?>"><?php echo studentup_social_icon( 'email', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Email', 'studentup' ); ?></a>
			<?php endif; ?>
		</div>

		<p class="su-ic-foot su-ic-te"><?php esc_html_e( 'గమనిక: ఇది మా service — official application fee వేరు. Documents మీ అనుమతితోనే వాడతాం.', 'studentup' ); ?></p>
	</section>
	<?php
}

/**
 * Join channel block — WhatsApp + Telegram (replaces the old newsletter form).
 */
function studentup_cta_join() {
	$soc = studentup_social_links();
	?>
	<section class="su-join" aria-labelledby="su-join-title">
		<div class="su-join-copy">
			<h2 id="su-join-title"><?php esc_html_e( 'Every job, exam date and result — first on your phone', 'studentup' ); ?></h2>
			<?php /* v308: 2 hint lines teesesam — heading + 2 buttons chalu (hint-text rule). */ ?>
		</div>
		<div class="su-join-cta">
			<a class="su-join-wa" href="<?php echo esc_url( $soc['whatsapp'] ); ?>" target="_blank" rel="noopener"><?php echo studentup_social_icon( 'whatsapp', 16 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'WhatsApp updates', 'studentup' ); ?></a>
			<a class="su-join-tg" href="<?php echo esc_url( $soc['telegram'] ); ?>" target="_blank" rel="noopener"><?php echo studentup_social_icon( 'telegram', 16 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Telegram channel', 'studentup' ); ?></a>
		</div>
	</section>
	<?php
}

/**
 * Both blocks, printed right above the footer on every page.
 */
function studentup_cta_section() {
	studentup_cta_internet_center();

	/* v215 DEDUPE: single post bottom lo mundu **4 WhatsApp CTAs** vachevi —
	   community card (WA+TG) · status card (WA share) · share row (WA/TG/X) ·
	   ee join block (WA+TG) malli. Top-blogger sites okasari matrame adugutaru.
	   Article pages lo community card already undi kabatti ikkada join block
	   skip — home/archive/page lo mamulu ga vastundi. */
	if ( is_singular( 'post' ) && function_exists( 'studentup_opt' )
		&& studentup_opt( 'community_pulse', '1' ) ) {
		return;
	}
	studentup_cta_join();
}

/**
 * v79: compact mid-article join strip (Telegram + WhatsApp).
 *
 * DELIBERATE markup rules: div/span/strong/a ONLY — no <p> (ad injector
 * counts </p> for position) and no <h2> (TOC scans headings). Same social
 * options as rail/footer — owner changes once, everywhere follows.
 */
function studentup_cta_join_inline() {
	$soc = studentup_social_links();
	?>
	<div class="su-join-inline" role="complementary" aria-label="<?php esc_attr_e( 'Join our channels', 'studentup' ); ?>">
		<span class="su-join-inline-txt"><strong><?php echo studentup_ui_icon( 'bell', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Free job alerts on your phone', 'studentup' ); ?></strong>
			<span><?php esc_html_e( 'Jobs · results · hall tickets — first on WhatsApp / Telegram.', 'studentup' ); ?></span></span>
		<span class="su-join-inline-btns">
			<a class="su-join-wa" href="<?php echo esc_url( $soc['whatsapp'] ); ?>" target="_blank" rel="noopener"><?php echo studentup_social_icon( 'whatsapp', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Join WhatsApp', 'studentup' ); ?></a>
			<a class="su-join-tg" href="<?php echo esc_url( $soc['telegram'] ); ?>" target="_blank" rel="noopener"><?php echo studentup_social_icon( 'telegram', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Join Telegram', 'studentup' ); ?></a>
		</span>
	</div>
	<?php
}

/**
 * v79: inject the strip after the 2nd paragraph of single posts.
 * Priority 12 = before the in-article ad (20); the strip has no </p>
 * so the ad still lands after the 3rd ORIGINAL paragraph.
 */
function studentup_inject_join_cta( $content ) {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() || is_feed() ) {
		return $content;
	}
	if ( '0' === (string) studentup_opt( 'join_cta_inline', '1' ) ) {
		return $content;
	}
	if ( false !== strpos( $content, 'su-join-inline' ) ) {
		return $content;   // already inject ayyindi (double render ledu)
	}
	/*
	 * v96 DEDUPE: bot (autoblog `monetize.insert_join_strip`) kuda article
	 * madhyalo `.su-join-strip` ni HTML lopala pedutundi — adi content lo
	 * unte theme inkoka strip render cheyyakudadu (okate page lo rendu join
	 * boxes = spammy look + AdSense "value" review lo minus).
	 */
	if ( false !== strpos( $content, 'su-join-strip' ) ) {
		return $content;
	}
	$parts = explode( '</p>', $content, 3 );
	if ( count( $parts ) < 3 ) {
		return $content;   // 2 paragraphs kanna takkuva → strip vaddu
	}
	ob_start();
	studentup_cta_join_inline();
	$strip = trim( (string) ob_get_clean() );
	if ( '' === $strip ) {
		return $content;
	}
	return $parts[0] . '</p>' . $parts[1] . '</p>'
		. '<!--su-join-inline-->' . $strip . $parts[2];
}
add_filter( 'the_content', 'studentup_inject_join_cta', 12 );
