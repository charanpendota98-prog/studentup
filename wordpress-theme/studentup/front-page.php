<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<?php
/**
 * Front page — v191.2 MONEY EDITION (student-first, ad-optimised, Google-safe).
 *
 * Design law (v201 — demo (preview/worldclass) order ne ikkada):
 *   ticker → hero → Latest Notifications slider → most-searched →
 *   LEADERBOARD AD → breaking →
 *   filters → LATEST OPPORTUNITIES GRID (lead card + native in-feed ads) →
 *   jobs table → popular searches → MID AD → hot-10 + closing-week →
 *   personal picks → BELOW-CONTENT AD.
 *
 * Enduku itla:
 *  1) Content first — phone reader ki first job card 2 screens lopala kanipistundi
 *     (bounce ↓, session ↑).
 *  2) Ad slots content madhya lo unnayi (in-feed native) — viewability + CTR ↑,
 *     kaani ads content ni dominate cheyavu (AdSense policy safe).
 *  3) Calculator/widget wall TEESESAAM (user brief: "ee tools em avasaram ledu") —
 *     avi ippudu /tools/ page lo mattrame (page-tools.php).
 *
 * @package studentup
 */

get_header();

/*
 * v176 REAL FIX (live-install proof): /page/2/ kuda front-page.php ne vaadutundi.
 * Grid query paged-aware + numbered pagination + page 2+ lo widgets ledu.
 */
$su_paged = max( 1, (int) get_query_var( 'paged' ) );
$su_is_p2 = $su_paged > 1;
?>

<?php // v311: owner — trending ticker removed ("avasaram ledu"). ?>

<?php if ( ! $su_is_p2 ) : ?>
	<?php studentup_hero_premium(); // search + quick links (hero H1) ?>
	<?php /* v233: naukri-la scrolling category rail — hero ki ventane kinda */ ?>
	<?php studentup_latest_notifications(); // v201: “Latest Notifications” sliding track (preview ↔ live parity) ?>
<?php endif; ?>

<?php // v314 NEAT: "Most searched by students" removed on home — same 12 links as the category tiles just above (duplicate block). ?>

<?php // v311: owner — "Top 5 Trending Now" removed; Daily Quiz + Post your news band full width. ?>
<?php if ( ! $su_is_p2 ) : ?>
<div class="su-home-grid su-home-grid--solo">
	<div class="hg-q">
		<?php studentup_daily_quiz( array( 'id' => 'daily-quiz', 'heading' => 'Daily Quiz — 5 easy questions, share your score' ) ); ?>
		<?php if ( function_exists( 'studentup_postnews_cta' ) ) { studentup_postnews_cta(); } // v294: readers send stories/photos/district news → we approve → we post. ?>
	</div>
</div>
<?php endif; ?>

<?php
// v281: Closing Soon band — real last dates only (≤14 days), nearest first. Data lekapote render kaadu.
if ( ! $su_is_p2 && function_exists( 'studentup_opportunity_board_posts' ) && function_exists( 'studentup_slider_pill' ) ) :
	$su_closing = array();
	foreach ( studentup_opportunity_board_posts( 120 ) as $su_row ) {
		if ( null !== $su_row['days_left'] && $su_row['days_left'] >= 0 && $su_row['days_left'] <= 14 ) {
			$su_closing[] = $su_row;
		}
	}
	usort( $su_closing, static function ( $a, $b ) { return $a['days_left'] <=> $b['days_left']; } );
	$su_closing = array_slice( $su_closing, 0, 6 );
	if ( $su_closing ) :
	?>
<section class="su-closing" aria-label="<?php esc_attr_e( 'Closing soon', 'studentup' ); ?>">
	<div class="wrap">
		<div class="sectionhead"><h2><?php esc_html_e( 'Closing Soon', 'studentup' ); ?></h2>
			<a class="su-viewall" href="<?php echo esc_url( function_exists( 'studentup_opportunity_board_url' ) ? studentup_opportunity_board_url() : home_url( '/opportunities/' ) ); ?>"><?php esc_html_e( 'All deadlines', 'studentup' ); ?> &rarr;</a></div>
		<ul class="su-closing-list">
		<?php foreach ( $su_closing as $su_row ) : ?>
			<li><?php echo studentup_slider_pill( $su_row['id'] ); // phpcs:ignore WordPress.Security.EscapeOutput ?>
				<a href="<?php echo esc_url( $su_row['link'] ); ?>" data-su-ev="closing_click"><?php echo esc_html( $su_row['title'] ); ?></a>
				<span class="su-closing-date"><?php echo esc_html( date_i18n( 'D, j M', strtotime( $su_row['last_date'] ) ) ); ?></span></li>
		<?php endforeach; ?>
		</ul>
	</div>
</section>
	<?php endif; ?>
<?php endif; ?>

<?php if ( ! $su_is_p2 ) : ?>
	<div class="wrap"><?php studentup_ad( 'leaderboard' ); // slot 1 — highest paying, content ki mundu okkate ?></div>
<?php endif; ?>

<?php if ( $su_is_p2 ) : ?>
	<?php /* Page 1 lo H1 = hero title (premium.php). Pagination pages ki mattrame ikkada H1. */ ?>
	<section class="hero hero-slim" aria-label="Page title">
		<h1 class="screen-reader-text">
			<?php
			printf(
				/* translators: %d: page number. */
				esc_html__( 'Latest student updates — page %d', 'studentup' ),
				(int) $su_paged
			);
			?>
		</h1>
	</section>
<?php endif; ?>

<main id="main">
	<div class="wrap">
		<?php /* v202 FIX: owner feedback — separate "Breaking News / Verified source
		feed" block (and its empty-state message) not needed on home; the hero's
		"Breaking News" link + Most-searched tile already cover this. */ ?>

		<div class="sectionhead" id="jobs">
			<div>
				<h2>
					<?php
					if ( $su_is_p2 ) {
						printf(
							/* translators: %d: page number. */
							esc_html__( 'Latest opportunities — page %d', 'studentup' ),
							(int) $su_paged
						);
					} else {
						esc_html_e( 'Latest opportunities', 'studentup' );
					}
					?>
				</h2>
				<?php /* v203 FIX: owner feedback — "Filter by qualification — Telangana ·
				Andhra Pradesh · Central" caption tiseyyabadindi; actual filter chips/qual-bar
				(ikkade kinda, studentup_qual_bar()) already same thing chupistunnai — text
				redundant + phone lo extra vertical space waste chesedi. */ ?>
			</div>
			<?php if ( $su_is_p2 ) : ?>
				<a class="su-viewall" href="<?php echo esc_url( home_url( '/' ) ); ?>">← Newest updates</a>
			<?php else : ?>
				<a class="su-viewall" href="<?php echo esc_url( studentup_opportunity_board_url() ); ?>">All active sections →</a>
			<?php endif; ?>
		</div>

		<?php
		studentup_qual_bar();
		studentup_qual_active_note();
		studentup_hidden_note();
		// v302: "N posted today" → day archive (real count, 10-min cache; 0 aithe render kaadu).
		if ( ! $su_is_p2 ) {
			$su_today_n = get_transient( 'su_today_count' );
			if ( false === $su_today_n ) {
				$su_tq = new WP_Query(
					array(
						'post_type'      => 'post',
						'post_status'    => 'publish',
						'posts_per_page' => 1,
						'fields'         => 'ids',
						'date_query'     => array( array( 'after' => 'today', 'inclusive' => true ) ),
					)
				);
				$su_today_n = (int) $su_tq->found_posts;
				set_transient( 'su_today_count', $su_today_n, 10 * MINUTE_IN_SECONDS );
			}
			if ( $su_today_n > 0 ) {
				$su_day_url = get_day_link( (int) current_time( 'Y' ), (int) current_time( 'm' ), (int) current_time( 'd' ) );
				echo '<a class="su-today" href="' . esc_url( $su_day_url ) . '"><span class="su-today-dot" aria-hidden="true"></span><b>'
					. esc_html( sprintf( _n( '%d update posted today', '%d updates posted today', $su_today_n, 'studentup' ), $su_today_n ) )
					. '</b><i aria-hidden="true">→</i></a>';
			}
		}
		?>

		<?php
		/* v207 FIX: owner feedback — "Latest opportunities" heading kinda unna
		category filter chips row (All · TS Jobs · AP Jobs · Central · Results ·
		Hall Tickets · Scholarships) "ivvi delete cheyu — vaddu" annaru (phone lo
		space waste, clumsy ga kanipistundi). Real filtering already server-side
		qualification bar (studentup_qual_bar just paifana) + category pages lo
		untundi — ee client-side row duplicate & extra vertical space matrame.
		JS lo chip click wiring + #cat- hash handler kuda clean chesamu;
		applyFilter() expired-hide + deadline badges + qual dropdown kosam
		alage untundi. */ ?>

		<div class="newsgrid" id="grid">
			<?php
			$su_q = new WP_Query(
				studentup_qual_query_args(
					array(
						'post_type'           => 'post',
						'posts_per_page'      => 12,
						'paged'               => $su_paged,
						'ignore_sticky_posts' => false,
						'no_found_rows'       => false,
					)
				)
			);
			$su_i = 0;
			if ( $su_q->have_posts() ) :
				while ( $su_q->have_posts() ) :
					$su_q->the_post();
					// v191.2: native in-feed slots 3rd + 8th card tarvata (viewability max,
					// density cap + policy checks studentup_ad() lo ne untayi).
					if ( 3 === $su_i || 8 === $su_i ) {
						studentup_ad( 'in-feed' );
					}
					studentup_card( $su_i );
					$su_i++;
				endwhile;
			else :
				?>
			<p class="nores" style="display:block">No posts yet — the bot will publish the first update soon.</p>
			<?php endif; ?>
		</div>
		<p class="nores" id="nores">Nothing for this filter — open the "All" tab and try again.</p>

		<nav class="sectionhead" aria-label="Post pages">
			<div>
				<?php
				$su_total = (int) $su_q->max_num_pages;
				if ( $su_total > 1 ) {
					echo wp_kses_post(
						paginate_links(
							array(
								'total'     => $su_total,
								'current'   => $su_paged,
								'prev_text' => '← Newer',
								'next_text' => 'Older →',
							)
						) ?? ''
					);
				}
				?>
			</div>
		</nav>

		<?php if ( ! $su_is_p2 ) : ?>
			<?php
			// v308 NEAT: home lo okate posts list 4 sarlu repeat ayyedi (grid → "at a glance" table →
			// "Top 10 hot jobs" → "Closing this week") + categories 3 sarlu (tiles → Most searched →
			// "Popular searches") + qualification picker 2 sarlu ("Your qualification" bar → "Your 5 today").
			// Owner: "agam aga kakunda, neat ga" → duplicates teesesam; grid + Closing Soon band + Top 5 untayi.
			// Functions (studentup_jobs_table / popular_searches / hot_jobs / closing_week / personal_picks) inka unnayi.
			studentup_ad( 'mid' );           // slot 2
			// v277: daily quiz paiki move ayyindi (su-home-grid band — top5 pakkana,
			// laptop lo side-by-side; phone lo top5 kindha). Ikkada inkundi render kaadu.
			// v203 FIX: owner feedback — "Reader Poll" block ("Which update do you want
			// first on WhatsApp?") tiseyyabadindi; avasaram ledu ani cheppāru, inkā home
			// page ni long ga chesedi (phone lo especially). Function (studentup_daily_poll)
			// ippudu kuda undi, ikkada call cheyadam ledu antе.
			studentup_ad( 'below-content' ); // slot 3 — finish chesina reader ki
			?>
		<?php endif; ?>
		<?php
		// v310: "Browse by qualification" lives INSIDE main (was wp_footer → rendered below the site footer).
		if ( function_exists( 'studentup_qual_directory' ) ) {
			studentup_qual_directory();
		}
		?>
	</div>
</main>

<?php
wp_reset_postdata();
get_footer();
