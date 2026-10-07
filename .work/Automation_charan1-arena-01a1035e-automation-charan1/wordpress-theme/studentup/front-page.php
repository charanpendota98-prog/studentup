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

<?php studentup_latest_ticker(); // v201 demo order: ticker → hero → slider ?>

<?php if ( ! $su_is_p2 ) : ?>
	<?php studentup_hero_premium(); // search + quick links (hero H1) ?>
	<?php studentup_latest_notifications(); // v201: “Latest Notifications” sliding track (preview ↔ live parity) ?>
<?php endif; ?>

<?php if ( ! $su_is_p2 ) : ?>
<section class="usedwrap" aria-label="Most searched by students">
	<div class="wrap">
		<div class="usedhead">
			<b>Most searched by students</b>
			<?php /* v203 FIX: owner feedback — "One tap to the sections TS & AP students
			open most" caption tiseyyabadindi; heading + cards themselves already clear,
			extra line phone lo vertical space tinestundi. */ ?>
		</div>
		<div class="usedgrid">
			<a class="su-used-breaking" href="<?php echo esc_url( home_url( '/#jobs' ) ); ?>" aria-label="Breaking News - Live Flash Updates">
				<span class="ui ui--breaking" aria-hidden="true"><?php echo studentup_ui_icon( 'bolt', 20 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
				<div class="su-ub-body">
					<div class="su-ub-top">
						<span class="su-ub-tag"><span class="su-pulse-dot"></span> LIVE FLASH</span>
						<b>Breaking News</b>
					</div>
					<small><?php esc_html_e( 'Latest notifications · hall tickets & exam alerts', 'studentup' ); ?></small>
				</div>
				<em class="ucount ucount--brk"><?php esc_html_e( 'Flash Updates →', 'studentup' ); ?></em>
			</a>
			<?php
			foreach ( studentup_most_used() as $i => $m ) :
				$term = studentup_used_term( $m['slug'] );
				if ( ! $term ) {
					continue;
				}
				$hot = ( $i < 3 ) ? ' hot' : '';
				?>
				<a class="usedcard<?php echo esc_attr( $hot ); ?>" href="<?php echo esc_url( get_category_link( $term ) ); ?>">
					<span class="ui" aria-hidden="true"><?php echo studentup_ui_icon( $m['icon'], 22 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?></span>
					<div><b><?php echo esc_html( $m['label'] ); ?></b><small><?php echo esc_html( $m['hint'] ); ?></small></div>
				<?php
				// v199: nijamaina category count (WP term count — extra query ledu).
				// Count 0 aithe emi chupinchamu — fake number ledu, stray dash ledu.
				$su_n = (int) $term->count;
				if ( $su_n > 0 ) :
					?>
					<em class="ucount"><?php echo esc_html( sprintf( /* translators: %s: number of updates. */ __( '%s updates', 'studentup' ), number_format_i18n( $su_n ) ) ); ?></em>
				<?php endif; ?>
				</a>
				<?php endforeach; ?>
		</div>
	</div>
</section>
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
			studentup_jobs_table( 8 );       // v202: short + scannable — Google ki rich, reader ki fast
			studentup_popular_searches();    // internal links (SEO + session depth)
			studentup_ad( 'mid' );           // slot 2 — content madhya lo
			studentup_hot_jobs( 10 );        // TOP 10 HOT JOBS TODAY (return visits)
			studentup_closing_week( 7 );     // urgency (last dates) — real meta mattrame
			studentup_personal_picks();      // local-only personalised top 5
			// v197: engagement block — real daily quiz + reader poll (v123 quiz
			// eppudu render avvaledu; ippudu server-rendered, JS-enhanced).
			studentup_daily_quiz( array( 'id' => 'daily-quiz', 'heading' => 'Daily quiz — 5 questions, 2 minutes' ) );
			// v203 FIX: owner feedback — "Reader Poll" block ("Which update do you want
			// first on WhatsApp?") tiseyyabadindi; avasaram ledu ani cheppāru, inkā home
			// page ni long ga chesedi (phone lo especially). Function (studentup_daily_poll)
			// ippudu kuda undi, ikkada call cheyadam ledu antе.
			studentup_ad( 'below-content' ); // slot 3 — finish chesina reader ki
			?>
		<?php endif; ?>
	</div>
</main>

<?php
wp_reset_postdata();
get_footer();
