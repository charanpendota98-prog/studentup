<?php
/**
 * v1.9.134 — /today/ date-wise updates page. See inc/today.php.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
get_header();
?>
<main id="main">
	<div class="wrap">
		<div class="su-layout">
			<div class="su-main">
		<div class="crumbs"><?php echo wp_kses_post( studentup_breadcrumbs() ); ?></div>
		<div class="sectionhead">
			<div>
				<h1><?php echo esc_html( studentup_today_h1() ); ?></h1>
				<p><?php echo esc_html( sprintf( __( 'Updates from the last %d days. Older posts are in each section.', 'studentup' ), STUDENTUP_TODAY_DAYS ) ); ?></p>
			</div>
			<a class="su-viewall" href="<?php echo esc_url( function_exists( 'studentup_opportunity_board_url' ) ? studentup_opportunity_board_url() : home_url( '/' ) ); ?>"><?php esc_html_e( 'All deadlines', 'studentup' ); ?> &rarr;</a>
		</div>
		<?php studentup_today_list(); ?>
		<?php studentup_ad( 'mid' ); ?>
			</div><!-- /.su-main -->
			<?php get_sidebar(); ?>
		</div><!-- /.su-layout -->
	</div>
<?php if ( function_exists( 'studentup_sectionwise_elsewhere' ) ) { echo '<div class="wrap">'; studentup_sectionwise_elsewhere(); echo '</div>'; } ?>
</main>
<?php
get_footer();
