<?php
/**
 * Template Name: Post Your News
 *
 * v294 — reader submissions page (slug: post-your-news).
 *  · 3 what-to-send tiles (success story · photo/video · district update)
 *  · Google Form embed when configured (Settings → Verified Success Story Google Form URL)
 *  · WhatsApp / Telegram send buttons (always real)
 *  · Approved stories grid (published success-stories posts) — motivational wall;
 *    lekapote render kaadu.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

$su_form   = function_exists( 'studentup_postnews_form_url' ) ? studentup_postnews_form_url() : '';
$su_embed  = $su_form && function_exists( 'studentup_postnews_embed_url' ) ? studentup_postnews_embed_url( $su_form ) : '';
$su_soc    = function_exists( 'studentup_social_links' ) ? studentup_social_links() : array();
$su_wa_txt = rawurlencode( 'Hi StudentUp, I want to post my news: ' );
$su_wa     = ! empty( $su_soc['whatsapp'] ) ? $su_soc['whatsapp'] . '?text=' . $su_wa_txt : '';
$su_tg     = ! empty( $su_soc['telegram'] ) ? $su_soc['telegram'] : '';
$su_mail   = function_exists( 'studentup_opt' ) ? sanitize_email( studentup_opt( 'contact_email', get_option( 'admin_email' ) ) ) : '';
$su_wall   = function_exists( 'studentup_postnews_approved' ) ? studentup_postnews_approved( 12 ) : array();
?>
<main id="main" class="wrap su-postnews-page">
	<?php
	while ( have_posts() ) :
		the_post();
		?>
		<nav class="crumbs" aria-label="Breadcrumb">
			<a href="<?php echo esc_url( home_url( '/' ) ); ?>">Home</a> › <?php the_title(); ?>
		</nav>
		<h1 class="su-pn-title"><?php the_title(); ?></h1>

		<div class="su-pn-tiles" role="list">
			<div class="su-pn-tile" role="listitem"><span class="su-pn-tic" aria-hidden="true"><?php echo studentup_ui_icon( 'trophy', 24 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span><b><?php esc_html_e( 'Success story', 'studentup' ); ?></b></div>
			<div class="su-pn-tile" role="listitem"><span class="su-pn-tic" aria-hidden="true"><?php echo studentup_ui_icon( 'upload', 24 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span><b><?php esc_html_e( 'Photo / Video', 'studentup' ); ?></b></div>
			<div class="su-pn-tile" role="listitem"><span class="su-pn-tic" aria-hidden="true"><?php echo studentup_ui_icon( 'pin', 24 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span><b><?php esc_html_e( 'District update', 'studentup' ); ?></b></div>
		</div>

		<?php if ( trim( (string) get_the_content() ) !== '' ) : ?>
			<div class="su-pn-intro"><?php the_content(); ?></div>
		<?php endif; ?>

		<ol class="su-pn-steps" aria-label="<?php esc_attr_e( 'How it works', 'studentup' ); ?>">
			<li><b>1</b><span><?php esc_html_e( 'You send', 'studentup' ); ?></span></li>
			<li><b>2</b><span><?php esc_html_e( 'We verify', 'studentup' ); ?></span></li>
			<li><b>3</b><span><?php esc_html_e( 'We post with your name', 'studentup' ); ?></span></li>
		</ol>

		<section class="su-pn-send" aria-labelledby="su-pn-send-h">
			<h2 id="su-pn-send-h"><?php esc_html_e( 'Send it to us', 'studentup' ); ?></h2>
			<div class="su-pn-btns">
				<?php if ( $su_wa ) : ?>
					<a class="su-pn-btn su-pn-wa" href="<?php echo esc_url( $su_wa ); ?>" target="_blank" rel="noopener" data-su-ev="postnews_whatsapp"><?php echo studentup_social_icon( 'whatsapp', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'WhatsApp', 'studentup' ); ?></a>
				<?php endif; ?>
				<?php if ( $su_tg ) : ?>
					<a class="su-pn-btn su-pn-tg" href="<?php echo esc_url( $su_tg ); ?>" target="_blank" rel="noopener" data-su-ev="postnews_telegram"><?php echo studentup_social_icon( 'telegram', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Telegram', 'studentup' ); ?></a>
				<?php endif; ?>
				<?php if ( $su_mail ) : ?>
					<a class="su-pn-btn su-pn-mail" href="<?php echo esc_url( 'mailto:' . $su_mail . '?subject=' . rawurlencode( 'Post my news - StudentUp' ) ); ?>" data-su-ev="postnews_email"><?php echo studentup_ui_icon( 'doc', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Email', 'studentup' ); ?></a>
				<?php endif; ?>
				<?php if ( $su_form ) : ?>
					<a class="su-pn-btn su-pn-form" href="<?php echo esc_url( $su_form ); ?>" target="_blank" rel="noopener noreferrer" data-su-ev="postnews_form"><?php echo studentup_ui_icon( 'external', 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Open form', 'studentup' ); ?></a>
				<?php endif; ?>
			</div>
			<?php if ( $su_embed ) : ?>
				<div class="su-pn-embed">
					<iframe src="<?php echo esc_url( $su_embed ); ?>" title="<?php esc_attr_e( 'Post your news form', 'studentup' ); ?>" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
				</div>
			<?php endif; ?>
			<ul class="su-pn-rules">
				<li><?php esc_html_e( 'We review every submission. Approved stories are posted by the StudentUp team with your name (or anonymous, if you ask).', 'studentup' ); ?></li>
				<li><?php esc_html_e( 'Send public proof (result, offer letter, official link). Never send Aadhaar, PAN, bank, OTP or passwords.', 'studentup' ); ?></li>
			</ul>
		</section>

		<?php if ( $su_wall ) : ?>
			<section class="su-pn-wall" aria-labelledby="su-pn-wall-h">
				<div class="su-pn-wall-head">
					<h2 id="su-pn-wall-h"><?php esc_html_e( 'Approved stories', 'studentup' ); ?></h2>
					<?php
					$su_ss = function_exists( 'studentup_used_term' ) ? studentup_used_term( 'success-stories' ) : null;
					if ( $su_ss ) :
						?>
						<a class="su-viewall" href="<?php echo esc_url( get_category_link( $su_ss ) ); ?>"><?php esc_html_e( 'All stories →', 'studentup' ); ?></a>
					<?php endif; ?>
				</div>
				<?php
				$su_feat = array_shift( $su_wall );
				if ( $su_feat ) :
					$su_fx = wp_trim_words( wp_strip_all_tags( get_the_excerpt( $su_feat ) ), 28 );
					?>
					<a class="su-pn-feat" href="<?php echo esc_url( get_permalink( $su_feat ) ); ?>">
						<?php if ( has_post_thumbnail( $su_feat ) ) : ?>
							<span class="su-pn-feat-img"><?php echo get_the_post_thumbnail( $su_feat, 'large', array( 'loading' => 'eager', 'alt' => esc_attr( get_the_title( $su_feat ) ) ) ); ?></span>
						<?php endif; ?>
						<span class="su-pn-feat-body">
							<span class="su-pn-feat-k"><?php esc_html_e( 'Latest story', 'studentup' ); ?></span>
							<b><?php echo esc_html( get_the_title( $su_feat ) ); ?></b>
							<?php if ( $su_fx ) : ?><em><?php echo esc_html( $su_fx ); ?></em><?php endif; ?>
							<time datetime="<?php echo esc_attr( get_the_date( 'c', $su_feat ) ); ?>"><?php echo esc_html( get_the_date( 'j M Y', $su_feat ) ); ?></time>
						</span>
					</a>
				<?php endif; ?>
				<div class="su-pn-grid">
					<?php foreach ( $su_wall as $su_p ) : ?>
						<a class="su-pn-card" href="<?php echo esc_url( get_permalink( $su_p ) ); ?>">
							<?php if ( has_post_thumbnail( $su_p ) ) : ?>
								<span class="su-pn-thumb"><?php echo get_the_post_thumbnail( $su_p, 'medium', array( 'loading' => 'lazy', 'alt' => esc_attr( get_the_title( $su_p ) ) ) ); ?></span>
							<?php else : ?>
								<span class="su-pn-thumb su-pn-thumb--ic" aria-hidden="true"><?php echo studentup_ui_icon( 'trophy', 30 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
							<?php endif; ?>
							<b><?php echo esc_html( get_the_title( $su_p ) ); ?></b>
							<time datetime="<?php echo esc_attr( get_the_date( 'c', $su_p ) ); ?>"><?php echo esc_html( get_the_date( 'j M Y', $su_p ) ); ?></time>
						</a>
					<?php endforeach; ?>
				</div>
			</section>
		<?php endif; ?>
	<?php endwhile; ?>
</main>
<?php
get_footer();
