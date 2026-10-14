<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<?php
/**
 * Category / tag / date archive — student card grid + ads.
 *
 * @package studentup
 */

get_header();
?>
<main id="main">
	<div class="wrap">
		<div class="su-layout">
			<div class="su-main">
		<div class="crumbs"><?php echo wp_kses_post( studentup_breadcrumbs() ); ?></div>
		<div class="sectionhead">
			<div>
				<h1>
					<?php
					if ( is_category() || is_tag() ) {
						// v178: alias group primary term — deterministic archive H1.
						$su_arch_obj = get_queried_object();
						if ( function_exists( 'studentup_alias_primary_term' ) ) {
							$su_arch_obj = studentup_alias_primary_term( $su_arch_obj );
						}
						echo esc_html( $su_arch_obj instanceof WP_Term ? $su_arch_obj->name : get_the_archive_title() );
					} elseif ( is_day() ) {
						// v303: date pages = "today's govt job updates" landing (clean H1, no "Day:" prefix).
						echo esc_html( sprintf( __( 'Updates — %s', 'studentup' ), get_the_date( 'j M Y' ) ) );
					} else {
						the_archive_title();
					}
					?>
				</h1>
				<?php if ( ! is_day() ) : ?>
				<p><?php echo esc_html( wp_strip_all_tags( get_the_archive_description() ) ); ?></p>
				<?php endif; ?>
			</div>
			<?php if ( is_day() ) : ?>
				<a class="su-viewall" href="<?php echo esc_url( home_url( '/' ) ); ?>">← Latest</a>
			<?php endif; ?>
		</div>
		<?php
		// v303: day archive — prev/next day nav (only days that really have posts).
		if ( is_day() ) {
			$su_day_ts = strtotime( get_the_date( 'Y-m-d' ) );
			$su_prev   = get_posts( array( 'posts_per_page' => 1, 'fields' => 'ids', 'post_status' => 'publish', 'date_query' => array( array( 'before' => gmdate( 'Y-m-d 00:00:00', $su_day_ts ) ) ) ) );
			$su_next   = get_posts( array( 'posts_per_page' => 1, 'fields' => 'ids', 'post_status' => 'publish', 'order' => 'ASC', 'date_query' => array( array( 'after' => gmdate( 'Y-m-d 23:59:59', $su_day_ts ) ) ) ) );
			if ( $su_prev || $su_next ) {
				echo '<nav class="su-daynav" aria-label="' . esc_attr__( 'Other days', 'studentup' ) . '">';
				if ( $su_prev ) {
					$su_pd = get_the_date( 'U', $su_prev[0] );
					echo '<a href="' . esc_url( get_day_link( (int) gmdate( 'Y', $su_pd ), (int) gmdate( 'm', $su_pd ), (int) gmdate( 'd', $su_pd ) ) ) . '">← ' . esc_html( get_the_date( 'j M', $su_prev[0] ) ) . '</a>';
				}
				if ( $su_next ) {
					$su_nd = get_the_date( 'U', $su_next[0] );
					echo '<a class="is-next" href="' . esc_url( get_day_link( (int) gmdate( 'Y', $su_nd ), (int) gmdate( 'm', $su_nd ), (int) gmdate( 'd', $su_nd ) ) ) . '">' . esc_html( get_the_date( 'j M', $su_next[0] ) ) . ' →</a>';
				}
				echo '</nav>';
			}
		}
		?>
		<?php
		// v80 (P16): subcategory chips — category landing rich (child cats + counts).
		if ( is_category() && function_exists( 'studentup_subcat_chips' ) ) {
			$su_chips_obj = get_queried_object();
			if ( function_exists( 'studentup_alias_primary_term' ) ) {
				$su_chips_obj = studentup_alias_primary_term( $su_chips_obj );
			}
			studentup_subcat_chips( $su_chips_obj instanceof WP_Term ? (int) $su_chips_obj->term_id : get_queried_object_id() );
		}
		?>
		<?php
		// v295: Breaking News section — Telangana / Andhra Pradesh → alphabetical districts.
		if ( is_category() && function_exists( 'studentup_breaking_section_nav' ) ) {
			studentup_breaking_section_nav();
		}
		?>
		<?php
		if ( function_exists( 'studentup_qual_bar' ) ) {
			studentup_qual_bar();          // v72: qualification filter on archives/categories too
			studentup_qual_active_note();
			studentup_hidden_note();
		}
		?>
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
		<nav class="sectionhead" aria-label="Pages"><div><?php echo wp_kses_post( paginate_links() ?? '' ); // v173 REAL FIX: single page unte paginate_links() NULL → wp_kses_post(null) PHP 8.1+ fatal ?></div></nav>
			</div><!-- /.su-main -->
			<?php get_sidebar(); ?>
		</div><!-- /.su-layout -->
	</div>
</main>
<?php
get_footer();
