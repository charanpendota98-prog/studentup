<?php
/**
 * v1.9.122 — qualification landing page (/jobs/degree/ …). See inc/qual-pages.php.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
$su_qslug = studentup_qual_page_slug();
get_header();
?>
<main id="main">
	<div class="wrap">
		<div class="su-layout">
			<div class="su-main">
		<div class="crumbs"><?php echo wp_kses_post( studentup_breadcrumbs() ); ?></div>
		<div class="sectionhead">
			<div>
				<h1><?php echo esc_html( studentup_qual_page_h1( $su_qslug ) ); ?></h1>
			</div>
			<a class="su-viewall" href="<?php echo esc_url( function_exists( 'studentup_opportunity_board_url' ) ? studentup_opportunity_board_url() : home_url( '/' ) ); ?>">All jobs →</a>
		</div>
		<?php do_action( 'studentup_qual_links_row' ); ?>
		<div class="newsgrid" id="grid">
			<?php
			$su_i = 0;
			while ( have_posts() ) :
				the_post();
				if ( 4 === $su_i ) {
					studentup_ad( 'in-feed' );
				}
				studentup_card( $su_i );
				$su_i++;
			endwhile;
			?>
		</div>
		<?php studentup_ad( 'mid' ); ?>
		<nav class="sectionhead" aria-label="Pages"><div><?php echo wp_kses_post( paginate_links() ?? '' ); ?></div></nav>
			</div><!-- /.su-main -->
			<?php get_sidebar(); ?>
		</div><!-- /.su-layout -->
	</div>
</main>
<?php
get_footer();
