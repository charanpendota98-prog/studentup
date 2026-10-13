<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<?php
/**
 * Category / tag / date search results — same card grid.
 *
 * @package studentup
 */

// v181: on-site search demand — server-side log (JS lekunda kuda pani chestundi).
if ( function_exists( 'studentup_searchlog_page' ) && get_search_query() ) {
	studentup_searchlog_page( get_search_query(), (int) $GLOBALS['wp_query']->found_posts );
}

get_header();
?>
<main id="main">
	<div class="wrap">
		<div class="su-layout">
			<div class="su-main">
		<div class="crumbs"><?php echo wp_kses_post( studentup_breadcrumbs() ); ?></div>
		<?php $su_found = isset( $GLOBALS['wp_query']->found_posts ) ? (int) $GLOBALS['wp_query']->found_posts : 0; ?>
		<div class="sectionhead su-srch-head">
			<div>
				<h1><?php echo esc_html( sprintf( /* translators: %s: query */ __( 'Results for “%s”', 'studentup' ), get_search_query() ) ); ?></h1>
				<?php if ( $su_found ) : ?>
					<p><?php echo esc_html( sprintf( /* translators: %d: count */ _n( '%d result', '%d results', $su_found, 'studentup' ), $su_found ) ); ?></p>
				<?php endif; ?>
			</div>
		</div>
		<?php studentup_smart_search_chips( $su_found ); // v290: did-you-mean + related category chips. ?>
		<?php if ( ! have_posts() ) : ?>
			<div class="su-empty su-srch-empty">
				<p><?php esc_html_e( 'No exact match.', 'studentup' ); ?></p>
				<?php get_search_form(); ?>
			</div>
			<?php studentup_smart_search_empty(); // v290: closest matches (any-word) → latest (data unte matrame). ?>
		<?php endif; ?>
		<div class="newsgrid">
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
		<nav class="sectionhead" aria-label="Pages"><div><?php echo wp_kses_post( paginate_links() ?? '' ); // v173 REAL FIX: single page unte paginate_links() NULL → wp_kses_post(null) PHP 8.1+ fatal ?></div></nav>
			</div><!-- /.su-main -->
			<?php get_sidebar(); ?>
		</div><!-- /.su-layout -->
	</div>
</main>
<?php
get_footer();
