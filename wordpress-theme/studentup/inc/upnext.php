<?php
/**
 * v96: UP NEXT — session-depth engine (real page navigation).
 *
 * Owner brief: "plan the ad refresh — not automation; the reader should move
 * to another page and come back."
 *
 * Why it is built THIS way (important):
 *   Refreshing an ad without a user action (timer / JS reload) is INVALID
 *   TRAFFIC under AdSense policy and risks the account. So this module uses
 *   no timers at all. Instead every article ends with an "Up Next" list (and
 *   on mobile a sticky next-article bar). When the reader taps it that is a
 *   REAL new pageview: new page = new ad request = a legitimate refresh.
 *
 * Real effects:
 *   · more pages/session  → more impressions/session (RPM up)
 *   · longer dwell time + internal links → "useful site" signal for Google
 *   · lower bounce rate → better for Discover / News surfacing
 *
 * Implementation notes:
 *   · Next post = a fresh post in the same category, else the newest on the
 *     site. PHP always returns a deterministic candidate so the block works
 *     with JavaScript disabled; the JS layer only hides already-seen links.
 *   · Zero external requests, zero tracking scripts, no timers.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Up Next candidates — newest posts in the same category, else site latest.
 *
 * @param int $limit How many posts are needed.
 * @return WP_Post[]
 */
/**
 * v1.9.170: two headlines about the SAME notification (bot duplicates such as
 * "APPSC Group 2 Notification 2026: 686 పోస్టులు" vs "APPSC Group 2 Notification
 * 2026 686 పోస్టులు Official వివరాలు") must never sit next to each other.
 *
 * @param string $a Title.
 * @param string $b Title.
 * @return bool
 */
function studentup_same_topic( $a, $b ) {
	$tok = static function ( $t ) {
		$t = strtolower( wp_strip_all_tags( (string) $t ) );
		$t = preg_replace( '/[^\p{L}\p{N}]+/u', ' ', $t );
		$w = array_filter( explode( ' ', $t ), static function ( $x ) {
			return mb_strlen( $x ) > 1 && ! in_array( $x, array( 'official', 'వివరాలు', 'పోస్టులు', 'notification', 'recruitment', 'apply', 'online', 'latest', 'new', 'posts', 'vacancies', 'vacancy', 'the', 'and', 'for' ), true );
		} );
		return array_values( array_unique( $w ) );
	};
	$x = $tok( $a );
	$y = $tok( $b );
	if ( count( $x ) < 2 || count( $y ) < 2 ) {
		return false;
	}
	$shared = count( array_intersect( $x, $y ) );
	return $shared / min( count( $x ), count( $y ) ) >= 0.8;
}

/**
 * v1.9.170: ids already rendered by Up-next on this page — the "ఇవి కూడా చూడండి"
 * grid skips them (live: both lists showed the same 3 posts).
 *
 * @return int[]
 */
function studentup_upnext_shown_ids() {
	return isset( $GLOBALS['studentup_upnext_ids'] ) && is_array( $GLOBALS['studentup_upnext_ids'] ) ? $GLOBALS['studentup_upnext_ids'] : array();
}

function studentup_upnext_posts( $limit = 3 ) {
	$limit = max( 1, (int) $limit );
	if ( ! is_singular( 'post' ) ) {
		return array();
	}
	$id   = (int) get_the_ID();
	$cats = wp_get_post_categories( $id );
	$args = array(
		'posts_per_page'      => $limit + 3,
		'post__not_in'        => array( $id ),
		'ignore_sticky_posts' => true,
		'no_found_rows'       => true,
		'post_status'         => 'publish',
		'orderby'             => 'date',
		'order'               => 'DESC',
	);
	$posts = array();
	if ( $cats ) {
		$same = get_posts( array_merge( $args, array( 'category__in' => $cats ) ) );
		$posts = is_array( $same ) ? $same : array();
	}
	if ( count( $posts ) < $limit ) {
		$skip  = array_merge( array( $id ), wp_list_pluck( $posts, 'ID' ) );
		$more  = get_posts(
			array_merge(
				$args,
				array(
					'post__not_in'   => $skip,
					'posts_per_page' => $limit - count( $posts ),
				)
			)
		);
		if ( is_array( $more ) ) {
			$posts = array_merge( $posts, $more );
		}
	}
	// v1.9.170: drop same-notification duplicates (vs this post and vs each other).
	$cur  = get_the_title( $id );
	$keep = array();
	foreach ( $posts as $p ) {
		if ( studentup_same_topic( $cur, $p->post_title ) ) {
			continue;
		}
		$dup = false;
		foreach ( $keep as $k ) {
			if ( studentup_same_topic( $k->post_title, $p->post_title ) ) {
				$dup = true;
				break;
			}
		}
		if ( ! $dup ) {
			$keep[] = $p;
		}
		if ( count( $keep ) >= $limit ) {
			break;
		}
	}
	$GLOBALS['studentup_upnext_ids'] = array_unique( array_merge( studentup_upnext_shown_ids(), wp_list_pluck( $keep, 'ID' ) ) ); // phpcs:ignore WordPress.WP.GlobalVariablesOverride.Prohibited
	return $keep;
}

/**
 * "Up Next" card list under the article (real links — never an auto redirect).
 */
function studentup_upnext_block() {
	if ( '0' === (string) studentup_opt( 'upnext', '1' ) ) {
		return;
	}
	$posts = studentup_upnext_posts( 3 );
	if ( ! $posts ) {
		return;
	}
	?>
	<section class="su-upnext" aria-labelledby="su-upnext-title" data-su-upnext>
		<h2 id="su-upnext-title" class="su-upnext-title"><?php esc_html_e( 'Up next — read this too', 'studentup' ); ?></h2>
		<ol class="su-upnext-list">
			<?php foreach ( $posts as $index => $p ) : ?>
				<li class="su-upnext-item">
					<a href="<?php echo esc_url( get_permalink( $p ) ); ?>" data-su-upnext-link="<?php echo (int) $index; ?>">
						<?php if ( has_post_thumbnail( $p ) ) : ?>
							<span class="su-upnext-thumb">
								<?php
								// Core builds and escapes the <img> tag itself.
								echo wp_kses_post( get_the_post_thumbnail( $p, 'studentup-card', array( 'loading' => 'lazy', 'alt' => '' ) ) );
								?>
							</span>
						<?php endif; ?>
						<span class="su-upnext-copy">
							<span class="su-upnext-head"><?php echo esc_html( wp_strip_all_tags( get_the_title( $p ) ) ); ?></span>
							<span class="su-upnext-meta"><?php echo esc_html( get_the_date( '', $p ) ); ?> · <?php echo esc_html( studentup_reading_time( $p->ID ) ); ?></span>
						</span>
					</a>
				</li>
			<?php endforeach; ?>
		</ol>
	</section>
	<?php
}

/**
 * Mobile sticky "next article" bar — one tap to the next pageview.
 *
 * This is NOT the sticky ad (that is a separate option); it is a content
 * link. The theme CSS keeps it clear of the sticky ad via z-index + offset.
 */
function studentup_upnext_bar() {
	if ( ! is_singular( 'post' ) ) {
		return;
	}
	if ( '0' === (string) studentup_opt( 'upnext_bar', '1' ) ) {
		return;
	}
	$posts = studentup_upnext_posts( 1 );
	if ( ! $posts ) {
		return;
	}
	$p = $posts[0];
	?>
	<div class="su-nextbar" data-su-nextbar hidden>
		<a class="su-nextbar-link" href="<?php echo esc_url( get_permalink( $p ) ); ?>">
			<span class="su-nextbar-kicker"><?php esc_html_e( 'Read next', 'studentup' ); ?></span>
			<span class="su-nextbar-title"><?php echo esc_html( wp_trim_words( wp_strip_all_tags( get_the_title( $p ) ), 9, '…' ) ); ?></span>
		</a>
		<button type="button" class="su-nextbar-close" data-su-nextbar-close aria-label="<?php esc_attr_e( 'Close', 'studentup' ); ?>">×</button>
	</div>
	<?php
}
add_action( 'wp_footer', 'studentup_upnext_bar', 20 );
