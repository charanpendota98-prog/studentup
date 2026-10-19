<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<?php
/**
 * Author archive — E-E-A-T friendly (bio · article count · website · verified note).
 *
 * Google ki "ee vyasam evaru rasinaru?" ane prashna ki idi jawabu: author bio,
 * published articles, external profile links, editorial policy link.
 *
 * @package studentup
 */

get_header();

$su_author = get_queried_object();
$su_id     = $su_author instanceof WP_User ? (int) $su_author->ID : (int) get_the_author_meta( 'ID' );
$su_name   = $su_author instanceof WP_User ? $su_author->display_name : get_the_author_meta( 'display_name', $su_id );
$su_bio    = $su_author instanceof WP_User ? $su_author->description : get_the_author_meta( 'description', $su_id );
// 1.9.157: one editorial identity everywhere — same name/bio/avatar/role as the post author box
// (options author_name/author_bio/author_avatar_url). No gravatar (third-party request, often broken).
$su_opt_name = function_exists( 'studentup_opt' ) ? (string) studentup_opt( 'author_name', 'Charan Pendota' ) : '';
$su_opt_bio  = function_exists( 'studentup_opt' ) ? (string) studentup_opt( 'author_bio', '' ) : '';
$su_opt_av   = function_exists( 'studentup_opt' ) ? (string) studentup_opt( 'author_avatar_url', '' ) : '';
$su_role     = function_exists( 'studentup_opt' ) ? (string) studentup_opt( 'author_experience', __( 'Senior Education Editor · 5+ Years of Experience', 'studentup' ) ) : '';
$su_name     = $su_opt_name ?: ( $su_name ?: 'Charan Pendota' );
$su_bio      = $su_opt_bio ?: ( $su_bio ?: __( 'Charan Pendota is a senior content editor and digital career researcher with 5+ years of experience in Telugu job notifications, exam patterns, and career guidance. At StudentUp, he leads the fact-checking desk, ensuring 100% source-verified information for Telangana and Andhra Pradesh students.', 'studentup' ) );
$su_initials = mb_strtoupper( mb_substr( $su_name, 0, 1 ) . ( preg_match( '/\s(\S)/u', $su_name, $su_m ) ? $su_m[1] : '' ) );
$su_url    = $su_author instanceof WP_User ? $su_author->user_url : get_the_author_meta( 'user_url', $su_id );
$su_count  = $su_id ? (int) count_user_posts( $su_id, 'post', true ) : 0;
?>
<main id="main">
	<div class="wrap">
		<div class="su-layout">
			<div class="su-main">
		<div class="crumbs"><?php echo wp_kses_post( studentup_breadcrumbs() ); ?></div>

		<section class="article authortop" aria-labelledby="author-title">
			<div class="authorwrap">
				<?php
				if ( $su_opt_av && wp_http_validate_url( $su_opt_av ) ) {
					echo '<img class="author-avatar" src="' . esc_url( $su_opt_av ) . '" alt="' . esc_attr( $su_name ) . '" width="96" height="96" loading="lazy" decoding="async">';
				} else {
					echo '<div class="author-avatar su-ab-placeholder" aria-hidden="true"><span>' . esc_html( $su_initials ) . '</span></div>';
				}
				?>
				<div class="authorbody">
					<h1 id="author-title" class="entry-title">
						<?php
						printf(
							/* translators: %s: author display name */
							esc_html__( '%s articles', 'studentup' ),
							esc_html( $su_name )
						);
						?>
					</h1>
					<?php if ( $su_role ) : ?><p class="authormeta su-author-role"><?php echo esc_html( $su_role ); ?></p><?php endif; ?>
					<p class="authormeta">
						<?php
						printf(
							/* translators: %d: number of published posts */
							esc_html__( 'Published articles: %d', 'studentup' ),
							(int) $su_count
						);
						?>
					</p>
					<?php if ( $su_bio ) : ?>
						<div class="authorbio"><?php echo wp_kses_post( wpautop( $su_bio ) ); ?></div>
					<?php else : ?>
						<p class="authorbio">
							<?php esc_html_e( 'The StudentUp editorial team — honest articles for Telangana & Andhra Pradesh students, based on official sources.', 'studentup' ); ?>
						</p>
					<?php endif; ?>
					<?php if ( $su_url ) : ?>
						<p class="authormeta">
							<a href="<?php echo esc_url( $su_url ); ?>" rel="me noopener" target="_blank">
								<?php esc_html_e( 'Author website / profile', 'studentup' ); ?>
							</a>
						</p>
					<?php endif; ?>
					<p class="authormeta">
						<a href="<?php echo esc_url( home_url( '/editorial-policy/' ) ); ?>">
							<?php esc_html_e( 'Read our editorial policy', 'studentup' ); ?>
						</a>
					</p>
				</div>
			</div>
		</section>

		<div class="sectionhead">
			<div><h2><?php esc_html_e( 'Recent articles', 'studentup' ); ?></h2></div>
		</div>
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
		<nav class="sectionhead" aria-label="<?php esc_attr_e( 'Pages', 'studentup' ); ?>">
			<div><?php echo wp_kses_post( paginate_links() ?? '' ); // v173 REAL FIX: single page unte paginate_links() NULL → wp_kses_post(null) PHP 8.1+ fatal ?></div>
		</nav>
			</div><!-- /.su-main -->
			<?php get_sidebar(); ?>
		</div><!-- /.su-layout -->
	</div>
</main>
<?php
get_footer();
