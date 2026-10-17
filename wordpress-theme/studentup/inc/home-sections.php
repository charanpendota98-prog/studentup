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
function studentup_home_sectionwise( $exclude = 0, $heading = '' ) {
	if ( is_paged() || ( ! $exclude && ! is_front_page() && ! is_archive() && ! is_search() && ! is_404() && ! is_page() ) ) {
		return;
	}
	$exclude = (int) $exclude;
	$slugs = array( 'results', 'hall-tickets', 'scholarships', 'admissions', 'ts-govt-jobs', 'ap-govt-jobs', 'central-govt-jobs' );
	$cols  = array();
	foreach ( $slugs as $slug ) {
		$term = function_exists( 'studentup_used_term' ) ? studentup_used_term( $slug ) : get_category_by_slug( $slug );
		if ( ! $term || (int) $term->count < 2 || (int) $term->term_id === $exclude ) {
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
		<div class="qsplit-head"><h2><?php echo esc_html( $heading ? $heading : 'విభాగాల వారీగా తాజా అప్‌డేట్స్' ); ?></h2></div>
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

/**
 * Archive / search / 404 / landing pages: same section lists, current
 * section excluded — every list page links out to the rest of the site.
 */
function studentup_sectionwise_elsewhere() {
	if ( is_front_page() || is_singular( 'post' ) ) {
		return;
	}
	$cur = 0;
	if ( is_category() ) {
		$qo  = get_queried_object();
		$cur = $qo ? (int) $qo->term_id : 0;
	}
	studentup_home_sectionwise( $cur ? $cur : -1, 'ఇతర విభాగాల్లో తాజా అప్‌డేట్స్' );
}

/**
 * v1.9.132 — sidebar auto cards (desktop): latest updates · closing soon ·
 * organisations. Real data only; empty string when nothing to show.
 *
 * @return string
 */
function studentup_sidebar_auto_cards() {
	if ( is_admin() || is_front_page() ) {
		return '';
	}
	$cur = is_singular() ? (int) get_queried_object_id() : 0;
	$out = '';
	// 1) Latest updates (8 titles; current post excluded; breaking excluded).
	$args = array(
		'post_type'           => 'post',
		'post_status'         => 'publish',
		'posts_per_page'      => 9,
		'ignore_sticky_posts' => true,
		'no_found_rows'       => true,
	);
	if ( function_exists( 'studentup_breaking_term' ) ) {
		$bt = studentup_breaking_term();
		if ( $bt ) {
			$args['category__not_in'] = array( (int) $bt->term_id );
		}
	}
	$q     = new WP_Query( $args );
	$items = '';
	$n     = 0;
	foreach ( $q->posts as $p ) {
		if ( (int) $p->ID === $cur || $n >= 8 ) {
			continue;
		}
		$n++;
		$items .= '<li><a href="' . esc_url( get_permalink( $p ) ) . '">' . esc_html( wp_strip_all_tags( get_the_title( $p ) ) ) . '</a>'
			. '<time datetime="' . esc_attr( get_the_date( 'c', $p ) ) . '">' . esc_html( get_the_date( 'd M', $p ) ) . '</time></li>';
	}
	wp_reset_postdata();
	if ( $n >= 3 ) {
		$out .= '<section class="sidecard su-side-latest"><h3>లేటెస్ట్ అప్‌డేట్స్</h3><ul>' . $items . '</ul>'
			. '<a class="su-secwise-more" href="' . esc_url( function_exists( 'studentup_opportunity_board_url' ) ? studentup_opportunity_board_url() : home_url( '/' ) ) . '">అన్నీ చూడండి →</a></section>';
	}
	// 2) Closing soon — only posts with a REAL future last date (≤ 15 days).
	if ( function_exists( 'studentup_opportunity_board_posts' ) ) {
		$rows = array();
		foreach ( studentup_opportunity_board_posts( 120 ) as $r ) {
			if ( (int) $r['id'] === $cur || ! $r['last_date'] || null === $r['days_left'] || $r['days_left'] < 0 || $r['days_left'] > 15 ) {
				continue;
			}
			$rows[] = $r;
		}
		if ( count( $rows ) >= 2 ) {
			usort( $rows, function ( $a, $b ) {
				return $a['days_left'] <=> $b['days_left'];
			} );
			$li = '';
			foreach ( array_slice( $rows, 0, 6 ) as $r ) {
				$d   = (int) $r['days_left'];
				$lbl = 0 === $d ? 'ఈరోజే చివరి తేదీ' : $d . ' రోజులు మిగిలాయి';
				$li .= '<li><a href="' . esc_url( $r['link'] ) . '">' . esc_html( wp_strip_all_tags( $r['title'] ) ) . '</a><b class="su-side-days' . ( $d <= 3 ? ' is-hot' : '' ) . '">' . esc_html( $lbl ) . '</b></li>';
			}
			$out .= '<section class="sidecard su-side-closing"><h3>త్వరలో ముగుస్తున్నవి</h3><ul>' . $li . '</ul></section>';
		}
	}
	// 3) Organisations with posts.
	if ( function_exists( 'studentup_org_pages_links' ) ) {
		$links = studentup_org_pages_links( function_exists( 'studentup_org_page_slug' ) ? studentup_org_page_slug() : '' );
		if ( '' !== $links ) {
			$out .= '<section class="sidecard su-side-orgs"><h3>సంస్థల వారీగా</h3>' . $links . '</section>';
		}
	}
	return $out;
}
