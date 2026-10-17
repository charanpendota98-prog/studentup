<?php
/**
 * Interactive FAQ Accordion & FAQPage JSON-LD Rich Snippet Schema.
 *
 * Provides FAQPage schema for Google search rich snippets and interactive accordion.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Get standard FAQs for the current post.
 *
 * @param int $post_id Post ID.
 * @return array<int,array<string,string>>
 */
function studentup_get_post_faqs( $post_id = 0 ) {
	$post_id = $post_id ? $post_id : get_the_ID();
	if ( ! $post_id ) {
		return array();
	}

	$title     = get_the_title( $post_id );
	$vacancies = (string) get_post_meta( $post_id, 'studentup_vacancies', true );
	$last_date = (string) get_post_meta( $post_id, 'studentup_last_date', true );
	$qual      = (string) get_post_meta( $post_id, 'studentup_qual', true );
	$apply_url = (string) get_post_meta( $post_id, 'studentup_apply_url', true );
	$salary    = (string) get_post_meta( $post_id, 'studentup_salary', true );

	/*
	 * v175: context-aware FAQs. Puratham — hall-ticket download post meeda
	 * "last date to apply for X?" adigite wrong (apply cheyyaledu, download
	 * chestunnadu). studentup_apply_cta() kind prakaram questions maarutayi.
	 */
	$cta = function_exists( 'studentup_apply_cta' ) ? studentup_apply_cta( $post_id ) : array( 'label' => 'Apply online', 'kind' => 'job' );
	$kind = $cta['kind'];

	$faqs = array();
	$last_pretty = $last_date ? wp_date( 'd M Y', strtotime( $last_date . ' 12:00:00' ) ) : '';
	// v1.9.128: owner rule — site language is Telugu (standard terms stay English).
	// Every question/answer below is Telugu-script grammar, built ONLY from real meta.

	if ( 'hallticket' === $kind ) {
		if ( $last_date ) {
			$faqs[] = array(
				'q' => 'Hall Ticket download చేయడానికి చివరి తేదీ ఎప్పుడు?',
				'a' => 'Hall Ticket download link ' . esc_html( $last_pretty ) . ' వరకు అందుబాటులో ఉంటుంది. చివరి రోజు server load ఉంటుంది కాబట్టి ముందుగానే download చేసుకోండి.',
			);
		}
		if ( $apply_url ) {
			$faqs[] = array(
				'q' => 'Hall Ticket ఎక్కడ download చేయాలి?',
				'a' => 'Official portal నుంచి మాత్రమే download చేయండి. ఈ article లో ఇచ్చిన official link ఉపయోగించండి; third-party sites వద్దు.',
			);
		}
		$faqs[] = array(
			'q' => 'Hall Ticket download కి ఏ వివరాలు కావాలి?',
			'a' => 'సాధారణంగా Registration Number మరియు Date of Birth (లేదా Password) కావాలి. Application form copy దగ్గర ఉంచుకోండి.',
		);
		return $faqs;
	}

	if ( 'result' === $kind ) {
		if ( $apply_url ) {
			$faqs[] = array(
				'q' => 'Result ఎక్కడ check చేయాలి?',
				'a' => 'Official website లో మాత్రమే result check చేయండి. ఈ article లో ఇచ్చిన official result link ఉపయోగించండి.',
			);
		}
		if ( $last_date ) {
			$faqs[] = array(
				'q' => 'Result link ఎప్పటి వరకు పనిచేస్తుంది?',
				'a' => 'Result link ' . esc_html( $last_pretty ) . ' వరకు అందుబాటులో ఉంటుంది. Result copy ని భవిష్యత్తు అవసరాలకు save చేసుకోండి.',
			);
		}
		$faqs[] = array(
			'q' => 'Result చూసిన తర్వాత ఏం చేయాలి?',
			'a' => 'Qualify అయితే తదుపరి దశ (Interview / Document Verification) సూచనలను official website లో చూసి certificates సిద్ధంగా ఉంచుకోండి.',
		);
		return $faqs;
	}

	if ( $last_date ) {
		$faqs[] = array(
			'q' => esc_html( $title ) . ' కి Apply చేయడానికి చివరి తేదీ ఎప్పుడు?',
			'a' => 'Online application submit చేయడానికి చివరి తేదీ ' . esc_html( $last_pretty ) . '. అభ్యర్థులు ముందుగానే apply చేయడం మంచిది.',
		);
	}

	if ( $vacancies ) {
		$faqs[] = array(
			'q' => 'ఈ recruitment లో మొత్తం ఎన్ని vacancies ఉన్నాయి?',
			'a' => 'Official notification ప్రకారం మొత్తం ' . esc_html( $vacancies ) . ' posts భర్తీ చేస్తారు.',
		);
	}

	if ( $qual ) {
		$faqs[] = array(
			'q' => 'కనీస Qualification ఏమిటి?',
			'a' => 'అభ్యర్థులు గుర్తింపు పొందిన board / university నుంచి ' . esc_html( studentup_qual_pretty( $qual ) ) . ' లేదా సమానమైన అర్హత కలిగి ఉండాలి.',
		);
	}

	if ( $salary ) {
		$faqs[] = array(
			'q' => 'ఈ post కి నెల జీతం (Salary) ఎంత?',
			'a' => 'Government pay rules ప్రకారం సుమారు నెల జీతం ' . esc_html( $salary ) . '.',
		);
	}

	$faqs[] = array(
		'q' => 'ఈ recruitment కి Online Apply ఎలా చేయాలి?',
		'a' => 'అర్హత ఉన్న అభ్యర్థులు official recruitment portal లో online application నింపి, అవసరమైన certificates upload చేసి, చివరి తేదీ లోపు submit చేయాలి.',
	);

	return $faqs;
}

/**
 * Render FAQ Accordion Box in Article.
 *
 * @return void
 */
function studentup_faq_box() {
	if ( ! is_singular( 'post' ) || ! studentup_opt( 'faq_schema', '1' ) ) {
		return;
	}

	$faqs = studentup_get_post_faqs();
	if ( empty( $faqs ) ) {
		return;
	}
	// v1.9.119: bot articles carry their own FAQ (h2 "Frequently Asked Questions" /
	// .su-faq) — a second generic FAQ box underneath was duplicate content.
	$raw = (string) get_post_field( 'post_content', get_the_ID() );
	if ( preg_match( '/<h2[^>]*>\s*(frequently asked questions|faq|తరచుగా అడిగే ప్రశ్నలు)/iu', $raw ) || false !== strpos( $raw, 'su-faq' ) || false !== strpos( $raw, '"FAQPage"' ) ) {
		return;
	}

	?>
	<section class="su-faq-section" id="faqs" aria-labelledby="su-faq-title">
		<div class="su-faq-head">
			<span class="su-faq-badge" aria-hidden="true"><?php echo studentup_ui_icon( 'help', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> FAQ</span>
			<h2 id="su-faq-title" class="su-faq-title">తరచుగా అడిగే ప్రశ్నలు (FAQ)</h2>
		</div>
		<div class="su-faq-list">
			<?php foreach ( $faqs as $i => $item ) : ?>
				<?php $open_attr = ( 0 === $i ) ? ' open' : ''; ?>
				<details class="su-faq-item"<?php echo esc_attr( $open_attr ); ?>>
					<summary class="su-faq-question">
						<span><?php echo esc_html( $item['q'] ); ?></span>
						<span class="su-faq-arrow" aria-hidden="true">▾</span>
					</summary>
					<div class="su-faq-answer">
						<p><?php echo esc_html( $item['a'] ); ?></p>
					</div>
				</details>
			<?php endforeach; ?>
		</div>
	</section>
	<?php
}

/**
 * Inject Google JSON-LD FAQPage Schema in wp_head.
 *
 * @return void
 */
function studentup_faq_schema() {
	if ( ! is_singular( 'post' ) || ! studentup_opt( 'faq_schema', '1' ) ) {
		return;
	}

	// v1.9.128: FAQ schema must match VISIBLE content (Google structured-data
	// policy). Bot/own-FAQ posts hide the theme box (see studentup_faq_box) and
	// usually ship their own FAQPage JSON-LD — emitting a second, invisible
	// English FAQPage here was a duplicate + mismatch. Same gate as the box.
	$raw = (string) get_post_field( 'post_content', get_the_ID() );
	if ( preg_match( '/<h2[^>]*>\s*(frequently asked questions|faq|తరచుగా అడిగే ప్రశ్నలు)/iu', $raw )
		|| false !== strpos( $raw, 'su-faq' ) || false !== strpos( $raw, '"FAQPage"' ) ) {
		return;
	}
	$faqs = studentup_get_post_faqs();
	if ( count( $faqs ) < 2 ) {
		return;
	}

	$elements = array();
	foreach ( $faqs as $item ) {
		$elements[] = array(
			'@type'          => 'Question',
			'name'           => $item['q'],
			'acceptedAnswer' => array(
				'@type' => 'Answer',
				'text'  => $item['a'],
			),
		);
	}

	$schema = array(
		'@context'   => 'https://schema.org',
		'@type'      => 'FAQPage',
		'mainEntity' => $elements,
	);

	echo '<script type="application/ld+json">'
		. wp_json_encode( $schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES )
		. '</script>' . "\n";
}
add_action( 'wp_head', 'studentup_faq_schema', 12 );
