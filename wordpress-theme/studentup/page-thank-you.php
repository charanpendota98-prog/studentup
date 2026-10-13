<?php
/**
 * Template Name: Thank You
 *
 * v227 (#31) — lead confirm page. noindex (inc/trust.php) + GA4 generate_lead
 * event automatic ga fire avutundi.
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<main class="wrap su-thanks" id="content">
	<article <?php post_class( 'card su-thanks-card' ); ?>>
		<div class="su-thanks-tick" aria-hidden="true">✓</div>
		<h1><?php echo esc_html( get_the_title() ); ?></h1>
		<?php
		$line = function_exists( 'studentup_response_time_shortcode' )
			? studentup_response_time_shortcode() : '';
		if ( $line ) {
			echo wp_kses_post( $line );
		}
		while ( have_posts() ) :
			the_post();
			?>
			<div class="article-content"><?php the_content(); ?></div>
			<?php
		endwhile;
		?>
		<p class="su-thanks-next">
			<a class="bluebtn" href="<?php echo esc_url( home_url( '/' ) ); ?>">Back to home</a>
			<a class="su-cta" href="<?php echo esc_url( home_url( '/daily-quiz/' ) ); ?>">Try today&rsquo;s quiz</a>
		</p>
	</article>
</main>
<?php
get_footer();
