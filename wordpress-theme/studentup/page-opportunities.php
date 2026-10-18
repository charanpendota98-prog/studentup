<?php
/**
 * Live active opportunities board — deadline-aware and section-wise.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
get_header();
$sections = studentup_opportunity_sections();
$rows     = studentup_opportunity_board_posts();
$groups   = array_fill_keys( array_keys( $sections ), array() );
foreach ( $rows as $row ) {
	if ( isset( $groups[ $row['section'] ] ) && count( $groups[ $row['section'] ] ) < 12 ) {
		$groups[ $row['section'] ][] = $row;
	}
}
$total = count( $rows );
?>
<main id="main" class="su-op-board-page" data-su-opportunities data-su-op-total="<?php echo esc_attr( $total ); ?>">
	<div class="wrap">
		<nav class="su-breadcrumbs" aria-label="<?php echo esc_attr__( 'Breadcrumb', 'studentup' ); ?>">
			<a href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Home', 'studentup' ); ?></a><span aria-hidden="true">›</span><span><?php esc_html_e( 'Latest active opportunities', 'studentup' ); ?></span>
		</nav>
		<section class="su-op-hero" aria-labelledby="su-op-title">
			<div>
				<p class="su-op-kicker">STUDENTUP · <?php esc_html_e( 'LIVE LIST', 'studentup' ); ?></p>
				<h1 id="su-op-title"><?php esc_html_e( 'Latest Jobs & Student Opportunities', 'studentup' ); ?></h1>
				<p><?php esc_html_e( 'TS, AP, Central, software, private, walk-in, job mela, scholarship, results and hall-ticket updates in one clean list.', 'studentup' ); ?></p>
			</div>
			<div class="su-op-count"><strong><?php echo esc_html( number_format_i18n( $total ) ); ?></strong><span><?php esc_html_e( 'active updates', 'studentup' ); ?></span></div>
		</section>
		<?php do_action( 'studentup_qual_links_row' ); // v1.9.122: /jobs/<qualification>/ landing pages ?>
		<?php do_action( 'studentup_org_links_row' ); // v1.9.123: /org/<organisation>/ ?>
		<div class="su-op-notice" role="note">
			<?php echo studentup_ui_icon( 'check', 15 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php echo wp_kses( __( 'This list updates from published StudentUp posts. Verified last dates are shown, expired notices are hidden automatically, and an unavailable date is shown as <strong>Not announced</strong> — never guessed.', 'studentup' ), array( 'strong' => array() ) ); ?>
		</div>
		<section class="su-op-filters" aria-labelledby="su-op-filter-title">
			<div class="su-op-filter-heading">
				<h2 id="su-op-filter-title"><?php esc_html_e( 'Find the right opportunity', 'studentup' ); ?></h2>
				<span data-su-op-results aria-live="polite"><?php echo esc_html( number_format_i18n( $total ) . ' ' . __( 'active updates', 'studentup' ) ); ?></span>
			</div>
			<div class="su-op-filter-grid">
				<label><span><?php esc_html_e( 'Search title', 'studentup' ); ?></span><input type="search" data-su-op-search placeholder="<?php esc_attr_e( 'Try SSC, software, scholarship…', 'studentup' ); ?>" autocomplete="off" /></label>
				<label><span><?php esc_html_e( 'Category', 'studentup' ); ?></span><select data-su-op-section-filter><option value=""><?php esc_html_e( 'All categories', 'studentup' ); ?></option><?php foreach ( $sections as $key => $section ) : ?><option value="<?php echo esc_attr( $key ); ?>"><?php echo esc_html( $section['label'] ); ?></option><?php endforeach; ?></select></label>
				<label><span><?php esc_html_e( 'Qualification', 'studentup' ); ?></span><select data-su-op-qualification><option value=""><?php esc_html_e( 'Any qualification', 'studentup' ); ?></option><option value="10th">10th</option><option value="inter">Inter / 10+2</option><option value="iti">ITI / Diploma</option><option value="degree">Degree</option><option value="pg">PG</option></select></label>
				<label><span><?php esc_html_e( 'Deadline', 'studentup' ); ?></span><select data-su-op-deadline><option value=""><?php esc_html_e( 'Any deadline', 'studentup' ); ?></option><option value="7"><?php esc_html_e( 'Closing in 7 days', 'studentup' ); ?></option><option value="30"><?php esc_html_e( 'Closing in 30 days', 'studentup' ); ?></option><option value="unknown"><?php esc_html_e( 'Date not announced', 'studentup' ); ?></option></select></label>
			</div>
		</section>
		<div class="su-op-no-results" data-su-op-no-results hidden><?php esc_html_e( 'No matching active opportunities found. Try another keyword or category.', 'studentup' ); ?></div>
		<div class="su-op-jump" aria-label="<?php echo esc_attr__( 'Opportunity sections', 'studentup' ); ?>">
			<?php foreach ( $sections as $key => $section ) : ?>
				<?php if ( empty( $groups[ $key ] ) ) { continue; } ?>
				<a href="#su-<?php echo esc_attr( $key ); ?>"><?php echo studentup_ui_icon( $section['icon'], 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php echo esc_html( $section['label'] ); ?></a>
			<?php endforeach; ?>
		</div>
		<?php foreach ( $sections as $key => $section ) : ?>
			<?php if ( empty( $groups[ $key ] ) ) { continue; } ?>
			<section class="su-op-section" id="su-<?php echo esc_attr( $key ); ?>" aria-labelledby="su-<?php echo esc_attr( $key ); ?>-title">
				<div class="su-op-section-head">
					<h2 id="su-<?php echo esc_attr( $key ); ?>-title"><span class="su-sec-ico" aria-hidden="true"><?php echo studentup_ui_icon( $section['icon'], 18 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span> <?php echo esc_html( $section['label'] ); ?></h2>
					<a href="<?php echo esc_url( home_url( '/?s=' . rawurlencode( $section['label'] ) ) ); ?>"><?php esc_html_e( 'See all', 'studentup' ); ?> →</a>
				</div>
				<div class="su-op-list">
					<?php foreach ( $groups[ $key ] as $row ) : ?>
						<?php studentup_opportunity_render_card( $row ); ?>
					<?php endforeach; ?>
				</div>
			</section>
		<?php endforeach; ?>
		<?php if ( ! $total ) : ?>
			<div class="su-op-empty"><?php esc_html_e( 'No active verified opportunities are available right now. Please check again after the next update.', 'studentup' ); ?></div>
		<?php endif; ?>
		<p class="su-op-footnote"><?php esc_html_e( 'Last-date information is taken from the reviewed article. Always open the article and verify the official notification before applying.', 'studentup' ); ?></p>
	</div>
</main>
<?php get_footer(); ?>
