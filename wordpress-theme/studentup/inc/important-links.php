<?php
/**
 * v292 IMPORTANT LINKS — the #1 click element on every top Indian job site
 * (Sarkari Result / FreeJobAlert style), done the StudentUp way: real data only.
 *
 * Rows (each renders ONLY when its data exists — never a placeholder):
 *   Apply Online        → studentup_apply_url  (hidden after last date)
 *   Official Notification → studentup_source_url (the PDF / page we verified)
 *   Official Website    → host of source/apply URL
 *   More <Category>     → category archive (internal recirculation)
 *   Job alerts on Telegram → channel (returning-visitor loop)
 * Sits right after the article body — the exact moment the reader decides.
 * GA4: data-su-ev="important_link" (measure.php delegates data-su-ev clicks).
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Render the Important Links box for the current post.
 *
 * @return void
 */
function studentup_important_links_box() {
	if ( ! is_singular( 'post' ) ) {
		return;
	}
	$pid     = get_the_ID();
	$apply   = esc_url_raw( (string) get_post_meta( $pid, 'studentup_apply_url', true ) );
	$source  = esc_url_raw( (string) get_post_meta( $pid, 'studentup_source_url', true ) );
	$last    = trim( (string) get_post_meta( $pid, 'studentup_last_date', true ) );
	$expired = function_exists( 'studentup_opportunity_is_expired' ) ? studentup_opportunity_is_expired( $last ) : false;
	if ( ! $apply && ! $source ) {
		return; // golden rule: data lekapote render kaadu.
	}
	$rows = array();
	if ( $apply && ! $expired ) {
		$rows[] = array( __( 'Apply Online', 'studentup' ), $apply, 'arrow', 'apply', true );
	}
	if ( $source ) {
		$is_pdf = (bool) preg_match( '/\.pdf(\?|$)/i', $source );
		$rows[] = array( $is_pdf ? __( 'Official Notification (PDF)', 'studentup' ) : __( 'Official Notification', 'studentup' ), $source, $is_pdf ? 'download' : 'news', 'notification', false );
	}
	$host_src = wp_parse_url( $source ? $source : $apply, PHP_URL_HOST );
	if ( $host_src ) {
		$scheme = wp_parse_url( $source ? $source : $apply, PHP_URL_SCHEME );
		$rows[] = array( __( 'Official Website', 'studentup' ) . ' · ' . preg_replace( '/^www\./', '', $host_src ), ( $scheme ? $scheme : 'https' ) . '://' . $host_src . '/', 'globe', 'official', false );
	}
	$cat = function_exists( 'studentup_card_cat' ) ? studentup_card_cat( $pid ) : null;
	if ( ! $cat ) {
		$cats = get_the_category( $pid );
		$cat  = $cats ? $cats[0] : null;
	}
	if ( $cat instanceof WP_Term ) {
		$rows[] = array( sprintf( /* translators: %s: category */ __( 'More %s', 'studentup' ), $cat->name ), get_category_link( $cat ), 'board', 'category', false );
	}
	$tg = ltrim( (string) ( function_exists( 'studentup_opt' ) ? studentup_opt( 'social_telegram', 'studentup_in' ) : 'studentup_in' ), '@' );
	if ( $tg ) {
		$rows[] = array( __( 'Job alerts on Telegram', 'studentup' ), 'https://t.me/' . rawurlencode( $tg ), 'bell', 'telegram', false );
	}
	if ( ! $rows ) {
		return;
	}
	?>
	<section class="su-implinks" aria-labelledby="su-implinks-h">
		<h2 id="su-implinks-h" class="su-implinks-h"><?php esc_html_e( 'Important Links', 'studentup' ); ?></h2>
		<ul class="su-implinks-list">
			<?php foreach ( $rows as $r ) : ?>
				<?php
				list( $label, $url, $icon, $kind, $primary ) = $r;
				$ext = (bool) preg_match( '#^https?://#i', $url ) && false === strpos( $url, (string) wp_parse_url( home_url(), PHP_URL_HOST ) );
				?>
				<li class="<?php echo esc_attr( $primary ? 'su-implinks-row is-primary' : 'su-implinks-row' ); ?>">
					<span class="su-implinks-lab"><?php echo function_exists( 'studentup_ui_icon' ) ? studentup_ui_icon( $icon, 16 ) : ''; // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?><?php echo esc_html( $label ); ?></span>
					<a class="su-implinks-btn" href="<?php echo esc_url( $url ); ?>" data-su-ev="important_link" data-su-kind="<?php echo esc_attr( $kind ); ?>"<?php if ( $ext ) : ?> target="_blank" rel="noopener nofollow"<?php endif; ?>>
						<?php echo esc_html( $primary ? __( 'Apply Now', 'studentup' ) : __( 'Click Here', 'studentup' ) ); ?>
					</a>
				</li>
			<?php endforeach; ?>
		</ul>
		<?php if ( $apply && $expired ) : ?>
			<p class="su-implinks-closed"><?php echo esc_html( __( 'Application window closed', 'studentup' ) . ( $last ? ' · ' . date_i18n( 'j M Y', strtotime( $last ) ) : '' ) ); ?></p>
		<?php endif; ?>
	</section>
	<?php
}
