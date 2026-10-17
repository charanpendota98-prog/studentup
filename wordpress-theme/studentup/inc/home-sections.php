<?php
/**
 * v1.9.130 — Home: dense, scannable section lists (top Telugu education
 * portals pattern) + organisation directory. Real data only: a section or
 * organisation renders ONLY when it has published posts. No hint texts.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Section-wise latest headlines: Results · Hall Tickets · Scholarships ·
 * Admissions · TS/AP/Central jobs — 5 titles each, category link as head.
 * Breaking News never appears here (owner rule).
 */
function studentup_home_sectionwise() {
	if ( ! is_front_page() || is_paged() ) {
		return;
	}
	$slugs = array( 'results', 'hall-tickets', 'scholarships', 'admissions', 'ts-govt-jobs', 'ap-govt-jobs', 'central-govt-jobs' );
	$cols  = array();
	foreach ( $slugs as $slug ) {
		$term = function_exists( 'studentup_used_term' ) ? studentup_used_term( $slug ) : get_category_by_slug( $slug );
		if ( ! $term || (int) $term->count < 2 ) {
			continue;
		}
		$q = new WP_Query(
			array(
				'post_type'           => 'post',
				'post_status'         => 'publish',
				'posts_per_page'      => 5,
				'cat'                 => (int) $term->term_id,
				'ignore_sticky_posts' => true,
				'no_found_rows'       => true,
			)
		);
		if ( ! $q->have_posts() ) {
			continue;
		}
		$cols[] = array( 'term' => $term, 'posts' => $q->posts );
		if ( count( $cols ) >= 6 ) {
			break;
		}
	}
	wp_reset_postdata();
	if ( count( $cols ) < 2 ) {
		return;
	}
	?>
	<section class="su-secwise" aria-label="Latest by section">
		<div class="qsplit-head"><h2>విభాగాల వారీగా తాజా అప్‌డేట్స్</h2></div>
		<div class="su-secwise-grid">
			<?php foreach ( $cols as $c ) : ?>
				<div class="su-secwise-col">
					<a class="su-secwise-head" href="<?php echo esc_url( get_category_link( $c['term'] ) ); ?>"><?php echo esc_html( $c['term']->name ); ?></a>
					<ul>
						<?php foreach ( $c['posts'] as $p ) : ?>
							<li><a href="<?php echo esc_url( get_permalink( $p ) ); ?>"><?php echo esc_html( wp_strip_all_tags( get_the_title( $p ) ) ); ?></a>
								<time datetime="<?php echo esc_attr( get_the_date( 'c', $p ) ); ?>"><?php echo esc_html( get_the_date( 'd M', $p ) ); ?></time></li>
						<?php endforeach; ?>
					</ul>
					<a class="su-secwise-more" href="<?php echo esc_url( get_category_link( $c['term'] ) ); ?>">మరిన్ని →</a>
				</div>
			<?php endforeach; ?>
		</div>
	</section>
	<?php
}

/**
 * Organisation directory — chips for every organisation that has posts
 * (/org/<slug>/ landing pages, v332). Nothing renders without data.
 */
function studentup_home_orgdir() {
	if ( ! is_front_page() || is_paged() || ! function_exists( 'studentup_org_pages_links' ) ) {
		return;
	}
	$links = studentup_org_pages_links();
	if ( '' === $links ) {
		return;
	}
	?>
	<section class="su-orgdir" aria-label="Updates by organisation">
		<div class="qsplit-head"><h2>సంస్థల వారీగా (TSPSC · APPSC · SSC · RRB …)</h2></div>
		<?php echo wp_kses_post( $links ); ?>
	</section>
	<?php
}
