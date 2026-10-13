<?php
/**
 * v226 — MEASUREMENT + LEAD TRACKING (launch checklist #6, #7, #8, #19).
 *
 * Idi enduku:
 *   `ga4_id` option theme lo undedi, kaani GA4 tag **asalu emit avvaledu** —
 *   kevalam preconnect hint matrame undedi. Ante Analytics eppudu pani
 *   cheyyaledu. Ikkada aa bug fix + lead events + Clarity + LocalBusiness.
 *
 * Privacy: consent.php lo Consent Mode v2 default 'denied' (EEA/UK) already
 * set ayyindi — GA4 adi gauravistundi. Ikkada extra cookie emi pettatledu.
 *
 * @package StudentUp
 */

defined( 'ABSPATH' ) || exit;

/**
 * GA4 tag (#6) — ga4_id option unte matrame. Lekapote okka byte kooda ledu.
 */
function studentup_ga4_tag() {
	$id = (string) studentup_opt( 'ga4_id', '' );
	if ( '' === $id || is_admin() ) {
		return;
	}
	// G-XXXXXXXXXX format matrame (injection impossible).
	if ( ! preg_match( '/^G-[A-Z0-9]{4,20}$/i', $id ) ) {
		return;
	}
	printf(
		'<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>' . "\n",
		esc_attr( rawurlencode( $id ) )
	);
	// dataLayer + gtag() consent.php lo already define ayyayi (priority 1).
	$js = "window.dataLayer=window.dataLayer||[];"
		. "if(typeof gtag!=='function'){function gtag(){dataLayer.push(arguments);}}"
		. "gtag('js',new Date());"
		. "gtag('config','" . esc_js( $id ) . "',{anonymize_ip:true});";
	echo '<script>' . $js . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput
}
add_action( 'wp_head', 'studentup_ga4_tag', 3 );

/**
 * Microsoft Clarity (#8) — heatmaps + session recordings. Free.
 */
function studentup_clarity_tag() {
	$id = (string) studentup_opt( 'clarity_id', '' );
	if ( '' === $id || is_admin() ) {
		return;
	}
	if ( ! preg_match( '/^[a-z0-9]{6,20}$/i', $id ) ) {
		return;
	}
	$js = "(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};"
		. "t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;"
		. "y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})"
		. "(window,document,'clarity','script','" . esc_js( $id ) . "');";
	echo '<script>' . $js . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput
}
add_action( 'wp_head', 'studentup_clarity_tag', 4 );

/**
 * Lead events (#7) — ae action money istundo ade track cheyali.
 *
 * Page views goal kaadu. WhatsApp tap · Call tap · Email tap · form submit —
 * ivi track ayite ae page nijamga enquiries istundo telustundi.
 * GA4 unna lekapoyina crash kaadu (typeof guard).
 */
function studentup_lead_events() {
	if ( is_admin() ) {
		return;
	}
	$ga4     = (string) studentup_opt( 'ga4_id', '' );
	$clarity = (string) studentup_opt( 'clarity_id', '' );
	if ( '' === $ga4 && '' === $clarity ) {
		return; // edi lekapote script emit cheyyaddu (speed first).
	}
	$js = <<<'JS'
(function(){
 var sent={};
 function fire(name,label){
  var key=name+'|'+label;
  if(sent[key])return; sent[key]=1;
  try{ if(typeof gtag==='function'){ gtag('event',name,{event_category:'lead',event_label:label,value:1}); } }catch(e){}
  try{ if(typeof clarity==='function'){ clarity('set','lead',name); } }catch(e){}
 }
 document.addEventListener('click',function(ev){
  var a=ev.target&&ev.target.closest?ev.target.closest('a,button'):null;
  if(!a)return;
  var href=(a.getAttribute('href')||'').toLowerCase();
  var label=(a.textContent||'').trim().slice(0,60)||location.pathname;
  if(href.indexOf('tel:')===0){ fire('call_click',label); return; }
  if(href.indexOf('mailto:')===0){ fire('email_click',label); return; }
  if(href.indexOf('wa.me')>-1||href.indexOf('whatsapp')>-1){ fire('whatsapp_click',label); return; }
  if(href.indexOf('t.me')>-1||href.indexOf('telegram')>-1){ fire('telegram_click',label); return; }
  if(a.hasAttribute('data-su-ev')){ fire(a.getAttribute('data-su-ev'),(a.getAttribute('data-su-kind')||'')+' '+label); } // v292 generic
  if(a.matches('[data-su-apply],.su-apply,.applybtn')){ fire('apply_click',label); }
 },{passive:true});
 document.addEventListener('submit',function(ev){
  var f=ev.target; if(!f||f.tagName!=='FORM')return;
  if(f.matches('[role="search"],.search-form,.su-searchform')){ fire('site_search',location.pathname); return; }
  fire('form_submit',(f.getAttribute('name')||f.className||'form').slice(0,60));
 },true);
 // scroll depth 75% = nijamga chadivaru (ad viewability + engagement signal)
 var deep=false;
 addEventListener('scroll',function(){
  if(deep)return;
  var h=document.documentElement;
  if((h.scrollTop+innerHeight)/h.scrollHeight>0.75){ deep=true; fire('read_75',location.pathname); }
 },{passive:true});
})();
JS;
	wp_register_script( 'studentup-lead', '', array(), STUDENTUP_VERSION, true );
	wp_enqueue_script( 'studentup-lead' );
	wp_add_inline_script( 'studentup-lead', $js );
}
add_action( 'wp_enqueue_scripts', 'studentup_lead_events', 30 );

/**
 * LocalBusiness schema (#19) — Students Internet Center nijamaina local
 * business. Address/phone option lo unte matrame emit (fake data ledu).
 */
function studentup_localbusiness_schema() {
	if ( ! is_front_page() && ! is_page_template( 'page-internet-center.php' ) ) {
		return;
	}
	$phone = (string) studentup_opt( 'ic_phone', '' );
	$addr  = (string) studentup_opt( 'ic_address', '' );
	$name  = (string) studentup_opt( 'ic_name', '' );
	if ( '' === $phone && '' === $addr ) {
		return; // data ledu → schema ledu. Google ki abaddham cheppaddu.
	}
	$data = array(
		'@context' => 'https://schema.org',
		'@type'    => 'LocalBusiness',
		'name'     => $name ? $name : get_bloginfo( 'name' ),
		'url'      => home_url( '/' ),
	);
	if ( $phone ) {
		$data['telephone'] = $phone;
	}
	if ( $addr ) {
		$data['address'] = array(
			'@type'           => 'PostalAddress',
			'streetAddress'   => $addr,
			'addressCountry'  => 'IN',
		);
		$city = (string) studentup_opt( 'ic_city', '' );
		if ( $city ) {
			$data['address']['addressLocality'] = $city;
		}
	}
	$hours = (string) studentup_opt( 'ic_hours', '' );
	if ( $hours ) {
		$data['openingHours'] = $hours;
	}
	$logo = (string) studentup_opt( 'ic_logo', '' );
	if ( $logo ) {
		$data['image'] = $logo;
	}
	$json = wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
	if ( is_string( $json ) ) {
		echo '<script type="application/ld+json">' . $json . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput
	}
}
add_action( 'wp_head', 'studentup_localbusiness_schema', 20 );
