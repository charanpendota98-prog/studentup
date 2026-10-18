<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<?php
/**
 * Single post — article layout: meta, content, ads, share, related, trust note.
 *
 * @package studentup
 */

get_header();
?>
<div class="su-progress" aria-hidden="true"><span id="su-progress-bar"></span></div>
<main id="main">
	<div class="wrap">
		<div class="su-layout">
			<div class="su-main">
		<?php
		while ( have_posts() ) :
			the_post();
			?>
			<div class="crumbs"><?php echo wp_kses_post( studentup_breadcrumbs() ); ?></div>
			<article <?php post_class( 'article' ); ?> data-id="<?php echo (int) get_the_ID(); ?>">
				<div class="article-head">
					<h1><?php the_title(); ?></h1>
					<div class="article-meta">
						<span class="su-am su-am-date"><?php echo studentup_ui_icon( 'calendar', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php echo esc_html( get_the_date() ); ?></span>
						<?php echo wp_kses_post( studentup_last_updated() ); ?>
						<?php // studentup_reading_time() intentionally not shown on article pages. ?>
						<?php $su_cats = get_the_category(); ?>
						<?php if ( $su_cats ) : ?>
							<span class="su-am su-am-cat"><?php echo studentup_ui_icon( 'tag', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php echo esc_html( $su_cats[0]->name ); ?></span>
						<?php endif; ?>
						<?php
						if ( function_exists( 'studentup_qual_labels' ) ) {
							$su_q = studentup_qual_labels( get_the_ID(), 3 );
							if ( $su_q ) {
								echo '<span class="su-am su-am-qual">' . studentup_ui_icon( 'check', 14 ) . ' ' . esc_html( implode( ' · ', $su_q ) ) . '</span>'; // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG
							}
							$su_badge = studentup_last_date_badge( get_the_ID() );
							if ( $su_badge ) {
								echo '<span>' . wp_kses_post( $su_badge ) . '</span>';
							}
						}
						?>
					</div>
					<?php // Byline is intentionally omitted from the article header; schema retains publisher/author data. ?>
				</div>

				<?php if ( function_exists( 'studentup_reader_toolbar' ) ) : ?>
					<?php studentup_reader_toolbar(); ?>
				<?php endif; ?>

				<?php if ( function_exists( 'studentup_audio_reader' ) ) : ?>
					<?php studentup_audio_reader(); ?>
				<?php endif; ?>

				<?php if ( has_post_thumbnail() ) : ?>
					<figure class="su-featured-hero">
						<?php the_post_thumbnail( 'studentup-discover', array(
							'loading'       => 'eager',
							'fetchpriority' => 'high',
							'decoding'      => 'async',
							'alt'           => esc_attr( get_the_title() ),
						) ); ?>
					</figure>
				<?php endif; ?>

				<?php
				// v213 owner feedback: "Save · Compare · Print/PDF ivi kuda ravoddu" —
				// article head lo ee 3 utility buttons row teesesam (phone lo
				// headline kinda clutter ga kanipinchedi). Saved rail + compare page
				// inka pani chestunnayi; print browser menu lo undi.
				?>
				<?php if ( function_exists( 'studentup_source_verification_notice' ) ) : ?>
					<?php echo wp_kses_post( studentup_source_verification_notice( get_the_ID() ) ); ?>
				<?php endif; ?>

				<?php echo function_exists( 'studentup_expired_notice' ) ? wp_kses_post( studentup_expired_notice() ) : ''; ?>

				<?php
				if ( function_exists( 'studentup_sponsor_partner_box' ) ) {
					studentup_sponsor_partner_box();
				}
				?>

				<?php studentup_keyfacts_box(); // v158 ?>
				<?php studentup_ad( 'mid' ); // v1.9.117 Clean Reader: facts first, then the ad ?>
				<?php
				if ( function_exists( 'studentup_age_calculator_block' ) ) {
					studentup_age_calculator_block();
				}
				?>
				<?php
				if ( function_exists( 'studentup_fee_calculator_block' ) ) {
					studentup_fee_calculator_block();
				}
				?>
				<?php
				if ( function_exists( 'studentup_video_ad_slot' ) ) {
					studentup_video_ad_slot();
				}
				?>
				<div class="article-content" id="su-details"><?php the_content(); ?></div>   <?php // v175: id — apply bar "Full details" ghost button anchor (puratham anchor ledu → click emi cheyaledu). ?>
				<?php
				if ( function_exists( 'studentup_important_links_box' ) ) {
					studentup_important_links_box(); // v292: Apply · Notification · Official site · More · Telegram (real data only)
				}
				do_action( 'studentup_after_important_links' ); // v1.9.119: Doubts & Answers lands here
				?>
				<?php
				if ( function_exists( 'studentup_faq_box' ) ) {
					studentup_faq_box();
				}
				?>
				<?php
				// v215 READING ORDER (top-blogger standard): content → share → tags
				// → internal links (recirculation) → community CTA → status card.
				// Mundu CTA stack (community + status + join) content ki reader
				// share/tags ki mundE vachedi — "clumsy" feel + Google ki kuda
				// content-after-content signal weak. Ippudu reader modata article
				// mugistadu → share → related reading → appudu okka CTA.
				?>

				<?php /* v1.9.117 CLEAN READER: quick-summary (dup of Key facts), updated-stamp (dup of meta row),
				   smart-recirculation + community-pulse + status-card + helpful-box (CTA stack) removed from
				   the post template — owner rule: article → links → FAQ → tags → author → ONE related grid → ONE box. */ ?>
				<?php /* v307: second share row removed — studentup_share_bar() (content filter) already renders WhatsApp/Telegram/Copy. */ ?>

				<?php if ( has_tag() ) : ?>
					<div class="su-tags" aria-label="Tags"><?php echo studentup_ui_icon( 'tag', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php the_tags( '', ' · ', '' ); ?></div>
				<?php endif; ?>

				<?php studentup_author_box(); ?>

				<?php studentup_trust_note(); ?>

				<nav class="post-nav" aria-label="More posts">
					<span class="post-nav-prev"><?php previous_post_link( '%link', '← %title' ); ?></span>
					<span class="post-nav-next"><?php next_post_link( '%link', '%title →' ); ?></span>
				</nav>
			</article>

			<?php
			// v96: Up Next — reader tap = NIJAMAINA kotha pageview (policy-safe
			// ad refresh). Ad ki MUNDU pedatunnam: content link modata, ad tarvata.
			if ( function_exists( 'studentup_upnext_block' ) ) {
				studentup_upnext_block();
			}
			?>

			<?php studentup_ad( 'below-content' ); ?>
			<?php
			if ( comments_open() || get_comments_number() ) {
				comments_template();
			}
			?>

			<?php
			$su_rel  = get_the_category();
			$su_cat  = $su_rel ? wp_list_pluck( $su_rel, 'term_id' ) : array();
			$su_tags = wp_get_post_tags( get_the_ID(), array( 'fields' => 'ids' ) );
			// v210: related posts ALWAYS chupinchali — old code `tags && category`
			// strict-gate valla tags leni bot posts ki empty section vachedi.
			// Ippudu 3-step relevance: (1) tag+category exact, (2) tag-only
			// cross-category same-topic, (3) same-category latest fill — 4 cards
			// (phone lo 2x2 neat grid). Ids-only light queries, count vaddu.
			$su_picks = array();
			if ( $su_cat && $su_tags ) {
				$su_picks = get_posts(
					array(
						'fields'              => 'ids',
						'posts_per_page'      => 4,
						'category__in'        => $su_cat,
						'tag__in'             => $su_tags,
						'post__not_in'        => array( get_the_ID() ),
						'ignore_sticky_posts' => true,
						'no_found_rows'       => true, // v69 perf: count query vaddu
					)
				);
			}
			if ( count( $su_picks ) < 4 && $su_tags ) {
				$su_picks = array_merge(
					$su_picks,
					get_posts(
						array(
							'fields'              => 'ids',
							'posts_per_page'      => 4 - count( $su_picks ),
							'tag__in'             => $su_tags,
							'post__not_in'        => array_merge( array( get_the_ID() ), $su_picks ),
							'ignore_sticky_posts' => true,
							'no_found_rows'       => true,
						)
					)
				);
			}
			if ( count( $su_picks ) < 4 && $su_cat ) {
				$su_picks = array_merge(
					$su_picks,
					get_posts(
						array(
							'fields'              => 'ids',
							'posts_per_page'      => 4 - count( $su_picks ),
							'category__in'        => $su_cat,
							'post__not_in'        => array_merge( array( get_the_ID() ), $su_picks ),
							'ignore_sticky_posts' => true,
							'no_found_rows'       => true,
						)
					)
				);
			}
			if ( ! $su_picks ) {
				// Category kuda leni rare post — ikkada kuda empty section
				// vaddu; site-lo latest updates tho fill.
				$su_picks = get_posts(
					array(
						'fields'              => 'ids',
						'posts_per_page'      => 4,
						'post__not_in'        => array( get_the_ID() ),
						'ignore_sticky_posts' => true,
						'no_found_rows'       => true,
					)
				);
			}
			echo '<aside id="su-recent" class="su-recent" hidden data-l="' . esc_attr__( 'Recently viewed', 'studentup' ) . '"></aside>'; // v1.9.135: device-local, JS fills only when ≥2 items
			if ( $su_picks ) {
				echo '<div class="sectionhead"><div><h2>ఇవి కూడా చూడండి</h2></div></div><div class="newsgrid">';
				$su_i = 0;
				foreach ( $su_picks as $su_pid ) {
					$su_pick = get_post( $su_pid );
					if ( ! $su_pick ) {
						continue;
					}
					$GLOBALS['post'] = $su_pick; // phpcs:ignore WordPress.WP.GlobalVariablesOverride.Prohibited
					setup_postdata( $su_pick );
					studentup_card( $su_i );
					$su_i++;
				}
				echo '</div>';
				wp_reset_postdata();
			}
			?>
			<?php
			// v216 REVENUE: related posts (editorial) TARVATA multiplex
			// "related content" ad grid — in-article tarvata highest RPM unit.
			// Slot set cheyyakapothe emi render avvadu.
			if ( function_exists( 'studentup_ad_multiplex' ) ) {
				studentup_ad_multiplex();
			}
			?>
		<?php endwhile; ?>
			</div><!-- /.su-main -->
			<?php get_sidebar(); // v191.5: article sidebar (300x250) — highest viewability ?>
		</div><!-- /.su-layout -->
	</div>
</main>
<?php
studentup_calendar_button();
studentup_pdf_button();
studentup_up_next();

get_footer();
