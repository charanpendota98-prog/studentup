<?php
/**
 * v197 DAILY QUIZ v2 — real quiz (v123 lo render avvatledu, ippudu FULL).
 *
 * Enduku rewrite:
 *  · v123 `studentup_daily_quiz()` **eppudu call avvaledu** — front page lo quiz
 *    ledu, preview lo `href="#quiz"` dead link. Ippudu front-page + /daily-quiz/
 *    page rendu chotla render avutundi.
 *  · Server-side HTML: prathi question + 4 options + explanation markup lo ne
 *    untayi → **JS lekapoyina quiz pani chestundi** (form submit → server score),
 *    Google ki crawlable text, reader ki instant paint (JS ki wait ledu).
 *  · JS (`studentup-engage.js`) unte: instant grading, streak, share, keyboard
 *    1–4. JS ledu aithe: radios + "Check answers" button → same result.
 *  · Quiz JSON-LD schema (valid `Quiz` + `Question`), honest — practice content,
 *    government exam claims ledu.
 *  · No personal data: score localStorage lo mattrame (server ki vote ledu).
 *
 * Telugu ledu (v73 invariant) — UI + questions English.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}


/**
 * v250 — IST day key (Asia/Kolkata), UTC kaadu.
 *
 * Mundu `gmdate('Y-m-d')` vadinam — adi UTC. Valla rendu bugs:
 *   1. Kotha quiz roju raatri 12:00 IST ki kaakunda udayam 5:30 IST ki
 *      marutundi (UTC midnight = 5:30 IST).
 *   2. Bot raatri 00:30 IST ki push chesthe adi "nenna" key lo padutundi.
 * Master checklist #136/#137 (IST timezone + midnight rollover) ki ide
 * correct fix. WordPress site timezone em unna, quiz eppudu IST meede.
 *
 * @param int $shift Day offset (yesterday = -1).
 * @return string Y-m-d (IST).
 */
function studentup_quiz_ist_date( $shift = 0 ) {
	$ts = time() + ( 5 * HOUR_IN_SECONDS ) + ( 30 * MINUTE_IN_SECONDS )
		+ ( (int) $shift * DAY_IN_SECONDS );
	return gmdate( 'Y-m-d', $ts );
}

/**
 * v250 — IST day number (rotation seed). Same day = same quiz, everyone ki.
 *
 * @param int $shift Day offset.
 * @return int
 */
function studentup_quiz_ist_daynum( $shift = 0 ) {
	$d = studentup_quiz_ist_date( $shift );
	return (int) gmdate( 'z', strtotime( $d . ' 00:00:00 UTC' ) )
		+ ( (int) substr( $d, 0, 4 ) * 366 );
}

/**
 * Question bank. Each: q, a[4], c (correct index), why, cat, src.
 *
 * `src` = official/verifiable source name (E-E-A-T: answer ki proof).
 *
 * @return array<int,array<string,mixed>>
 */
function studentup_quiz_bank() {
	$bank = array(
		// v1.9.140 — bank fully Telugu (owner rule: content Telugu, standard terms English).
		// v282 — owner: easy reasoning / aptitude / competitive-style questions (status-share game).
		array( 'q' => 'సంఖ్యా శ్రేణి: 2, 4, 8, 16, ?', 'a' => array( '24', '30', '32', '34' ), 'c' => 2, 'why' => 'ప్రతి సంఖ్య రెట్టింపు అవుతుంది: 16 × 2 = 32.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'సంఖ్యా శ్రేణి: 5, 10, 15, 20, ?', 'a' => array( '22', '25', '30', '35' ), 'c' => 1, 'why' => 'ప్రతిసారి 5 కలపాలి: 20 + 5 = 25.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'భిన్నమైనది ఏది? (Odd One Out)', 'a' => array( 'ఆపిల్', 'అరటి', 'క్యారెట్', 'మామిడి' ), 'c' => 2, 'why' => 'క్యారెట్ కూరగాయ; మిగిలినవి పండ్లు.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'భిన్నమైనది ఏది? (Odd One Out)', 'a' => array( 'త్రిభుజం', 'చతురస్రం', 'వృత్తం', 'దీర్ఘచతురస్రం' ), 'c' => 2, 'why' => 'వృత్తానికి సరళ భుజాలు ఉండవు; మిగిలినవి బహుభుజులు.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'కోడింగ్-డీకోడింగ్: CAT = 3-1-20 అయితే, DOG = ?', 'a' => array( '4-15-7', '4-14-7', '3-15-7', '4-15-8' ), 'c' => 0, 'why' => 'అక్షరాల వరుస సంఖ్యలు: D=4, O=15, G=7.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'కోడింగ్-డీకోడింగ్: APPLE ను BQQMF అని రాస్తే, MANGO ను ఎలా రాస్తారు?', 'a' => array( 'NBOHP', 'NBOGP', 'LZMFN', 'NBOHQ' ), 'c' => 0, 'why' => 'ప్రతి అక్షరం +1 ముందుకు: M→N, A→B, N→O, G→H, O→P.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'దిశా జ్ఞానం: రవి ఉత్తరం వైపు చూస్తూ కుడివైపు, మళ్లీ కుడివైపు తిరిగాడు. ఇప్పుడు అతను ఏ దిశలో ఉన్నాడు?', 'a' => array( 'తూర్పు', 'పడమర', 'దక్షిణం', 'ఉత్తరం' ), 'c' => 2, 'why' => 'ఉత్తరం → కుడి = తూర్పు → మళ్లీ కుడి = దక్షిణం.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'దిశా జ్ఞానం: తూర్పు వైపు చూస్తూ ఎడమవైపు తిరిగితే, ఇప్పుడు ఏ దిశ?', 'a' => array( 'ఉత్తరం', 'దక్షిణం', 'పడమర', 'తూర్పు' ), 'c' => 0, 'why' => 'తూర్పు వైపు చూస్తూ ఎడమకు తిరిగితే ఉత్తరం వస్తుంది.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'రక్త సంబంధం: ఫోటో చూపిస్తూ సీత అంది, “ఈమె మా అమ్మకు ఒక్కగానొక్క కూతురు.” ఫోటోలో ఉన్నది ఎవరు?', 'a' => array( 'సీత సోదరి', 'సీతనే', 'సీత అత్త', 'సీత కూతురు' ), 'c' => 1, 'why' => 'అమ్మకు ఒక్కగానొక్క కూతురు = సీతనే.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'రక్త సంబంధం: మీ నాన్న సోదరుడు మీకు ఏమవుతాడు?', 'a' => array( 'కజిన్', 'బాబాయి/పెదనాన్న', 'మేనల్లుడు', 'తాత' ), 'c' => 1, 'why' => 'నాన్న సోదరుడు = బాబాయి లేదా పెదనాన్న.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'ర్యాంకింగ్: 20 మంది విద్యార్థుల వరుసలో అనిల్ ఎడమ నుంచి 5వ వాడు. కుడి నుంచి అతని స్థానం?', 'a' => array( '14వ', '15వ', '16వ', '17వ' ), 'c' => 2, 'why' => 'కుడి నుంచి స్థానం = 20 − 5 + 1 = 16వ.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'సాదృశ్యం: పెన్ను : రాయడం :: కత్తి : ?', 'a' => array( 'కోయడం', 'పదునైన', 'ఉక్కు', 'వంటగది' ), 'c' => 0, 'why' => 'పెన్ను రాయడానికి; కత్తి కోయడానికి.', 'cat' => 'Reasoning', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'శాతం: 200 లో 25% = ?', 'a' => array( '25', '40', '50', '75' ), 'c' => 2, 'why' => '25% = 1/4 → 200 ÷ 4 = 50.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'శాతం: 450 లో 10% = ?', 'a' => array( '40', '45', '50', '54' ), 'c' => 1, 'why' => '10% = 10 తో భాగించాలి → 45.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'సగటు: 10, 20, 30 ల సగటు ఎంత?', 'a' => array( '15', '20', '25', '30' ), 'c' => 1, 'why' => '(10 + 20 + 30) ÷ 3 = 20.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'గడియారం: గంటల ముల్లు 1 గంటలో ఎన్ని డిగ్రీలు తిరుగుతుంది?', 'a' => array( '15°', '30°', '45°', '60°' ), 'c' => 1, 'why' => '360° ÷ 12 = గంటకు 30°.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'సాధారణ వడ్డీ: రూ.1,000 కి సంవత్సరానికి 10% చొప్పున 2 సంవత్సరాలకు వడ్డీ ఎంత?', 'a' => array( 'రూ.100', 'రూ.200', 'రూ.210', 'రూ.120' ), 'c' => 1, 'why' => 'SI = 1000 × 10 × 2 ÷ 100 = రూ.200.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'నిష్పత్తి: 100 ను 3 : 2 నిష్పత్తిలో పంచితే పెద్ద భాగం ఎంత?', 'a' => array( '40', '50', '60', '70' ), 'c' => 2, 'why' => '100 లో 3/5 = 60.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'వేగం: ఒక బస్సు 120 km ను 2 గంటల్లో ప్రయాణిస్తే దాని వేగం?', 'a' => array( '50 km/h', '60 km/h', '70 km/h', '80 km/h' ), 'c' => 1, 'why' => 'వేగం = 120 ÷ 2 = 60 km/h.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'లాభ-నష్టం: రూ.80 కి కొని రూ.100 కి అమ్మితే లాభ శాతం?', 'a' => array( '20%', '25%', '30%', '40%' ), 'c' => 1, 'why' => '80 పై లాభం 20 = 20/80 × 100 = 25%.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'క.సా.గు (LCM): 4 మరియు 6 ల క.సా.గు ఎంత?', 'a' => array( '8', '10', '12', '24' ), 'c' => 2, 'why' => '4 గుణిజాలు: 4, 8, 12…; 6 గుణిజాలు: 6, 12… → 12.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'వర్గాలు: 15 × 15 = ?', 'a' => array( '200', '215', '225', '235' ), 'c' => 2, 'why' => '15² = 225 (ట్రిక్: 1×2 = 2, తర్వాత 25 → 225).', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'కాలం-పని: A ఒక పనిని 10 రోజుల్లో చేస్తాడు. 1 రోజులో చేసే పని = ?', 'a' => array( '1/5', '1/10', '1/20', '10' ), 'c' => 1, 'why' => 'ఒక రోజు పని = మొత్తం పనిలో 1/10.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'వయస్సు: రాము సీత కంటే 5 సంవత్సరాలు పెద్ద. సీత వయస్సు 20 అయితే రాము వయస్సు?', 'a' => array( '15', '20', '25', '30' ), 'c' => 2, 'why' => '20 + 5 = 25.', 'cat' => 'Aptitude', 'src' => 'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)', 'exam' => 'all', 'easy' => true ),
		array( 'q' => 'తెలంగాణ పరీక్షలు: TS EAMCET ను ఇప్పుడు ఏ ప్రవేశ పరీక్ష పేరుతో నిర్వహిస్తున్నారు?', 'a' => array( 'TS EAPCET', 'TS ECET', 'TS PGECET', 'TS ICET' ), 'c' => 0, 'why' => 'TS EAMCET పేరు TS EAPCET (Engineering, Agriculture & Pharmacy CET) గా మారింది; JNTUH నిర్వహిస్తుంది.', 'cat' => 'Telangana GK', 'src' => 'TSPSC / TS Exams Current Affairs', 'exam' => 'tspsc,all' ),
		array( 'q' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్: 240 m పొడవున్న రైలు ఒక టెలిగ్రాఫ్ స్తంభాన్ని 12 సెకన్లలో దాటితే రైలు వేగం (km/h) ఎంత?', 'a' => array( '60 km/h', '72 km/h', '54 km/h', '80 km/h' ), 'c' => 1, 'why' => 'వేగం = 240 m ÷ 12 s = 20 m/s. km/h లో: 20 × 18/5 = 72 km/h.', 'cat' => 'Aptitude', 'src' => 'SSC CGL / Quantitative Aptitude', 'exam' => 'ssc,rrb,banking' ),
		array( 'q' => 'లాజికల్ రీజనింగ్: PAPER ను QBQFS అని కోడ్ చేస్తే, అదే పద్ధతిలో OFFICE కోడ్ ఏమిటి?', 'a' => array( 'PGGIDF', 'PGGJDF', 'NFFHBD', 'QHHJEG' ), 'c' => 1, 'why' => 'ప్రతి అక్షరం +1 ముందుకు: O→P, F→G, F→G, I→J, C→D, E→F.', 'cat' => 'Reasoning', 'src' => 'Logical Reasoning / SSC CGL', 'exam' => 'ssc,rrb' ),
		array( 'q' => 'బ్యాంకింగ్ & ఆర్థిక వ్యవస్థ: వాణిజ్య బ్యాంకులకు స్వల్పకాలిక ద్రవ్యత అందించేందుకు RBI సర్దుబాటు చేసే పాలసీ రేటు ఏది?', 'a' => array( 'Reverse Repo Rate', 'Cash Reserve Ratio (CRR)', 'Repo Rate', 'Statutory Liquidity Ratio (SLR)' ), 'c' => 2, 'why' => 'రెపో రేటు = ప్రభుత్వ సెక్యూరిటీల హామీపై RBI వాణిజ్య బ్యాంకులకు స్వల్పకాలిక నిధులు ఇచ్చే వడ్డీ రేటు.', 'cat' => 'Banking', 'src' => 'rbi.org.in', 'exam' => 'banking' ),
		array( 'q' => 'భారత రాజ్యాంగం: ప్రాథమిక హక్కుల అమలు కోసం పౌరుడు నేరుగా సుప్రీంకోర్టును ఏ ఆర్టికల్ కింద ఆశ్రయించవచ్చు?', 'a' => array( 'Article 32', 'Article 226', 'Article 131', 'Article 143' ), 'c' => 0, 'why' => 'ఆర్టికల్ 32 రాజ్యాంగ పరిహార హక్కును ఇస్తుంది; సుప్రీంకోర్టు రిట్లు జారీ చేయగలదు.', 'cat' => 'Polity', 'src' => 'Constitution of India', 'exam' => 'tspsc,appsc,ssc' ),
		array( 'q' => 'జనరల్ స్టడీస్: దేశవ్యాప్త వస్తు సేవల పన్ను (GST) ను ఏ రాజ్యాంగ సవరణ చట్టం తీసుకొచ్చింది?', 'a' => array( '100వ సవరణ చట్టం', '101వ సవరణ చట్టం', '102వ సవరణ చట్టం', '103వ సవరణ చట్టం' ), 'c' => 1, 'why' => '101వ రాజ్యాంగ సవరణ చట్టం, 2016 ద్వారా 1 జూలై 2017 నుంచి GST అమలులోకి వచ్చింది.', 'cat' => 'Economy', 'src' => 'Ministry of Finance', 'exam' => 'all' ),
		array( 'q' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్: 15 వస్తువుల కొన్న ధర 12 వస్తువుల అమ్మిన ధరకు సమానమైతే లాభ శాతం ఎంత?', 'a' => array( '20%', '25%', '30%', '16.66%' ), 'c' => 1, 'why' => 'లాభం = (15 − 12) ÷ 12 × 100 = 3/12 × 100 = 25%.', 'cat' => 'Aptitude', 'src' => 'Quantitative Aptitude / Banking', 'exam' => 'banking,ssc' ),
		array( 'q' => 'లాజికల్ రీజనింగ్: 35 మంది విద్యార్థుల వరుసలో రమేష్ ఎడమ నుంచి 12వ వాడు. కుడి నుంచి అతని స్థానం?', 'a' => array( '23వ', '24వ', '25వ', '22వ' ), 'c' => 1, 'why' => 'కుడి నుంచి స్థానం = (మొత్తం − ఎడమ స్థానం) + 1 = (35 − 12) + 1 = 24వ.', 'cat' => 'Reasoning', 'src' => 'Logical Reasoning / Ranking', 'exam' => 'ssc,rrb' ),
		array( 'q' => 'భారత రాజ్యాంగం: పార్టీ ఫిరాయింపు కారణంగా అనర్హత (ఫిరాయింపు నిరోధక చట్టం) నిబంధనలు ఏ షెడ్యూల్‌లో ఉన్నాయి?', 'a' => array( '8వ షెడ్యూల్', '9వ షెడ్యూల్', '10వ షెడ్యూల్', '11వ షెడ్యూల్' ), 'c' => 2, 'why' => '52వ రాజ్యాంగ సవరణ చట్టం, 1985 ద్వారా 10వ షెడ్యూల్ చేర్చారు.', 'cat' => 'Polity', 'src' => 'Constitution of India', 'exam' => 'tspsc,appsc,ssc' ),
		array( 'q' => 'తెలంగాణ చరిత్ర: UNESCO ప్రపంచ వారసత్వ స్థలమైన రామప్ప దేవాలయం (రుద్రేశ్వరాలయం) ఏ కాకతీయ రాజు కాలంలో నిర్మించారు?', 'a' => array( 'ప్రతాపరుద్రుడు', 'గణపతి దేవుడు', 'రాణి రుద్రమదేవి', 'రెండవ ప్రోలరాజు' ), 'c' => 1, 'why' => 'కాకతీయ రాజు గణపతి దేవుడి సేనాని రేచర్ల రుద్రుడు 1213 CE లో రామప్ప ఆలయాన్ని నిర్మించాడు.', 'cat' => 'Telangana', 'src' => 'Telangana State Archaeology', 'exam' => 'tspsc' ),
		array( 'q' => 'భారత ఆర్థిక వ్యవస్థ: భారతదేశంలో వినియోగదారుల ధరల సూచీ (CPI) ద్రవ్యోల్బణ గణాంకాలను ఏ సంస్థ విడుదల చేస్తుంది?', 'a' => array( 'RBI', 'NITI Aayog', 'National Statistical Office (NSO)', 'Department of Financial Services' ), 'c' => 2, 'why' => 'గణాంకాలు & కార్యక్రమ అమలు మంత్రిత్వ శాఖ (MoSPI) కింద ఉన్న NSO ప్రతి నెలా CPI గణాంకాలను విడుదల చేస్తుంది.', 'cat' => 'Economy', 'src' => 'mospi.gov.in', 'exam' => 'banking,ssc,appsc,tspsc' ),
		array( 'q' => 'జనరల్ సైన్స్: ISRO LVM3 (GSLV Mk-III) రాకెట్ క్రయోజెనిక్ పై దశలో వాడే ప్రధాన ఇంధన కలయిక ఏది?', 'a' => array( 'ఘన HTPB', 'ద్రవ UDMH + N2O4', 'ద్రవ హైడ్రోజన్ (LH2) + ద్రవ ఆక్సిజన్ (LOX)', 'కిరోసిన్ + ద్రవ ఆక్సిజన్' ), 'c' => 2, 'why' => 'C25 క్రయోజెనిక్ దశ −253°C వద్ద ద్రవ హైడ్రోజన్‌ను, −183°C వద్ద ద్రవ ఆక్సిజన్‌ను మండిస్తుంది.', 'cat' => 'Science', 'src' => 'isro.gov.in', 'exam' => 'rrb,tspsc,appsc,ssc' ),
		array( 'q' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్: ఒక మొత్తం సాధారణ వడ్డీతో 5 సంవత్సరాల్లో రెట్టింపు అయితే వార్షిక వడ్డీ రేటు ఎంత?', 'a' => array( '15%', '20%', '25%', '10%' ), 'c' => 1, 'why' => 'SI = P. P = (P × R × 5)/100 ⇒ R = 100/5 = సంవత్సరానికి 20%.', 'cat' => 'Aptitude', 'src' => 'Quantitative Aptitude', 'exam' => 'ssc,banking,rrb' ),
		array( 'q' => 'లాజికల్ రీజనింగ్: ఫోటో చూపిస్తూ ఒక మహిళ అంది: “ఇతను మా మామగారి ఒక్కగానొక్క కొడుకుకు ఒక్కగానొక్క కొడుకు.” ఫోటోలో ఉన్న వ్యక్తి ఆమెకు ఏమవుతాడు?', 'a' => array( 'భర్త', 'సోదరుడు', 'కొడుకు', 'మేనల్లుడు' ), 'c' => 2, 'why' => 'మామగారి ఒక్కగానొక్క కొడుకు = ఆమె భర్త. భర్త ఒక్కగానొక్క కొడుకు = ఆమె కొడుకు.', 'cat' => 'Reasoning', 'src' => 'Logical Reasoning / Blood Relations', 'exam' => 'ssc,banking,tspsc,appsc' ),
		array( 'q' => 'భారత రాజ్యాంగం: కేంద్ర ఖాతాలకు సంబంధించిన ఆడిట్ నివేదికలను CAG ఎవరికి సమర్పిస్తారు?', 'a' => array( 'ప్రధానమంత్రి', 'ఆర్థిక మంత్రి', 'భారత రాష్ట్రపతి', 'లోక్‌సభ స్పీకర్' ), 'c' => 2, 'why' => 'ఆర్టికల్ 151 ప్రకారం కేంద్ర ఖాతాల CAG నివేదికలు రాష్ట్రపతికి సమర్పిస్తారు; ఆయన వాటిని పార్లమెంటు ముందు ఉంచుతారు.', 'cat' => 'Polity', 'src' => 'Constitution of India', 'exam' => 'tspsc,appsc,ssc' ),
		array( 'q' => 'ఆంధ్రప్రదేశ్ & భూగోళశాస్త్రం: పోలవరం బహుళార్థ సాధక జాతీయ ప్రాజెక్టును ఏ నదిపై నిర్మిస్తున్నారు?', 'a' => array( 'కృష్ణా', 'గోదావరి', 'పెన్నా', 'వంశధార' ), 'c' => 1, 'why' => 'పోలవరం ఆనకట్టను గోదావరి నదిపై ఏలూరు/అల్లూరి సీతారామరాజు జిల్లాల్లో నిర్మిస్తున్నారు.', 'cat' => 'Andhra Pradesh', 'src' => 'AP Irrigation Dept', 'exam' => 'appsc' ),
		array( 'q' => 'బ్యాంకింగ్ అవగాహన: బ్యాంకింగ్‌లో ‘RTGS’ అంటే ఏమిటి?', 'a' => array( 'Real Time Gross Settlement', 'Rapid Transfer Government Scheme', 'Real Time General Settlement', 'Regional Treasury Guarantee System' ), 'c' => 0, 'why' => 'RTGS = Real Time Gross Settlement — ప్రతి ఆర్డర్‌ను విడిగా, నిరంతరంగా సెటిల్ చేసే నిధుల బదిలీ విధానం.', 'cat' => 'Banking', 'src' => 'rbi.org.in', 'exam' => 'banking' ),
		array( 'q' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్: A, B పైపులు ఒక ట్యాంకును వరుసగా 20, 30 నిమిషాల్లో నింపుతాయి. రెండూ కలిపి తెరిస్తే ఎంత సమయం పడుతుంది?', 'a' => array( '10 నిమిషాలు', '12 నిమిషాలు', '15 నిమిషాలు', '18 నిమిషాలు' ), 'c' => 1, 'why' => '1/20 + 1/30 = (3+2)/60 = 5/60 = 1/12. కలిపి 12 నిమిషాలు.', 'cat' => 'Aptitude', 'src' => 'Quantitative Aptitude / Time & Work', 'exam' => 'ssc,rrb,banking' ),
		array( 'q' => 'భారత రాజ్యాంగం: ఆర్టికల్ 108 కింద పార్లమెంటు ఉభయ సభల సంయుక్త సమావేశానికి ఎవరు అధ్యక్షత వహిస్తారు?', 'a' => array( 'భారత రాష్ట్రపతి', 'భారత ఉపరాష్ట్రపతి', 'లోక్‌సభ స్పీకర్', 'ప్రధానమంత్రి' ), 'c' => 2, 'why' => 'ఆర్టికల్ 118(4) ప్రకారం సంయుక్త సమావేశానికి లోక్‌సభ స్పీకర్ అధ్యక్షత వహిస్తారు.', 'cat' => 'Polity', 'src' => 'Constitution of India', 'exam' => 'tspsc,appsc,ssc' ),
		array( 'q' => 'తెలంగాణ ఉద్యమం: ఆంధ్రప్రదేశ్ ఏర్పాటుకు ముందు చారిత్రక ‘పెద్దమనుషుల ఒప్పందం’ ఏ సంవత్సరంలో జరిగింది?', 'a' => array( '1952', '1956', '1969', '1948' ), 'c' => 1, 'why' => 'పెద్దమనుషుల ఒప్పందం 20 ఫిబ్రవరి 1956 న న్యూఢిల్లీలో జరిగింది; తెలంగాణ ప్రాంతానికి రక్షణలు కల్పించింది.', 'cat' => 'Telangana', 'src' => 'Telangana History / TSPSC', 'exam' => 'tspsc' ),
		array( 'q' => 'జనరల్ సైన్స్: రసాయనికంగా ఆస్కార్బిక్ ఆమ్లం అని పిలిచే, కొల్లాజెన్ తయారీ మరియు ఇనుము శోషణలో కీలకమైన విటమిన్ ఏది?', 'a' => array( 'Vitamin A', 'Vitamin B12', 'Vitamin C', 'Vitamin D' ), 'c' => 2, 'why' => 'ఆస్కార్బిక్ ఆమ్లం = విటమిన్ C. దీని తీవ్ర లోపం వల్ల స్కర్వీ వస్తుంది.', 'cat' => 'Science', 'src' => 'NCERT Biology', 'exam' => 'rrb,ssc,tspsc,appsc' ),
		array( 'q' => 'లాజికల్ రీజనింగ్: శ్రేణిలో తప్పిపోయిన సంఖ్య: 3, 7, 15, 31, 63, ?', 'a' => array( '125', '127', '129', '131' ), 'c' => 1, 'why' => 'సూత్రం: ×2 + 1. 3×2+1=7, 7×2+1=15, 15×2+1=31, 31×2+1=63, 63×2+1=127.', 'cat' => 'Reasoning', 'src' => 'Logical Reasoning / Number Series', 'exam' => 'ssc,banking,rrb' ),
		array( 'q' => 'భారత ఆర్థిక వ్యవస్థ: DICGC ఒక్కో డిపాజిటర్‌కు ఒక్కో బ్యాంకులో గరిష్ఠంగా ఎంత బీమా రక్షణ ఇస్తుంది?', 'a' => array( 'రూ.1,00,000', 'రూ.2,00,000', 'రూ.5,00,000', 'రూ.10,00,000' ), 'c' => 2, 'why' => 'DICGC (RBI అనుబంధ సంస్థ) వాణిజ్య, సహకార బ్యాంకుల్లో ఒక్కో డిపాజిటర్‌కు అసలు + వడ్డీ కలిపి రూ.5 లక్షల వరకు బీమా ఇస్తుంది.', 'cat' => 'Banking', 'src' => 'dicgc.org.in', 'exam' => 'banking' ),
		array( 'q' => 'భారత రాజ్యాంగం: ఓటు హక్కు వయస్సును 21 నుంచి 18 సంవత్సరాలకు తగ్గించిన రాజ్యాంగ సవరణ చట్టం ఏది?', 'a' => array( '42వ సవరణ చట్టం', '44వ సవరణ చట్టం', '61వ సవరణ చట్టం', '73వ సవరణ చట్టం' ), 'c' => 2, 'why' => '61వ రాజ్యాంగ సవరణ చట్టం, 1988 లోక్‌సభ, శాసనసభల ఓటు వయస్సును 21 నుంచి 18 కు తగ్గించింది.', 'cat' => 'Polity', 'src' => 'Constitution of India', 'exam' => 'tspsc,appsc,ssc' ),
		array( 'q' => 'కేంద్ర పథకాలు: అర్హులైన రైతు కుటుంబాలకు సంవత్సరానికి రూ.6,000 ను మూడు సమాన వాయిదాల్లో ఇచ్చే ప్రధాన పథకం ఏది?', 'a' => array( 'PM Fasal Bima Yojana', 'PM-KISAN Samman Nidhi', 'PM Krishi Sinchayee Yojana', 'PM Kisan Maandhan Yojana' ), 'c' => 1, 'why' => 'PM-KISAN కింద సంవత్సరానికి రూ.6,000 ను రూ.2,000 చొప్పున మూడు వాయిదాల్లో నేరుగా రైతుల బ్యాంకు ఖాతాల్లో జమ చేస్తారు.', 'cat' => 'Schemes', 'src' => 'pmkisan.gov.in', 'exam' => 'all' ),
		array( 'q' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్: A, B వయస్సుల నిష్పత్తి 3:4. నాలుగు సంవత్సరాల తర్వాత అది 4:5 అవుతుంది. A ప్రస్తుత వయస్సు?', 'a' => array( '12 సంవత్సరాలు', '16 సంవత్సరాలు', '18 సంవత్సరాలు', '20 సంవత్సరాలు' ), 'c' => 0, 'why' => '(3x + 4)/(4x + 4) = 4/5 ⇒ 15x + 20 = 16x + 16 ⇒ x = 4. A వయస్సు = 3 × 4 = 12 సంవత్సరాలు.', 'cat' => 'Aptitude', 'src' => 'Quantitative Aptitude / Ratios', 'exam' => 'ssc,banking,tspsc,appsc' ),
		array( 'q' => 'భూగోళశాస్త్రం & పర్యావరణం: విస్తీర్ణం ప్రకారం భారతదేశంలో అతి పెద్ద టైగర్ రిజర్వ్ అయిన నాగార్జునసాగర్-శ్రీశైలం టైగర్ రిజర్వ్ ఏ రాష్ట్రంలో ఉంది?', 'a' => array( 'తెలంగాణ & ఆంధ్రప్రదేశ్', 'మధ్యప్రదేశ్', 'కర్ణాటక', 'మహారాష్ట్ర' ), 'c' => 0, 'why' => 'నాగార్జునసాగర్-శ్రీశైలం టైగర్ రిజర్వ్ నల్లమల అడవుల్లో ఆంధ్రప్రదేశ్, తెలంగాణ రెండు రాష్ట్రాల్లో విస్తరించి ఉంది.', 'cat' => 'Geography', 'src' => 'National Tiger Conservation Authority', 'exam' => 'tspsc,appsc' ),
		array( 'q' => 'భారత రాజ్యాంగం: పార్లమెంటు సమావేశాల్లో లేనప్పుడు ఆర్డినెన్స్ జారీ చేసే అధికారాన్ని రాష్ట్రపతికి ఏ ఆర్టికల్ ఇస్తుంది?', 'a' => array( 'Article 110', 'Article 123', 'Article 213', 'Article 356' ), 'c' => 1, 'why' => 'ఆర్టికల్ 123 — ఏదైనా సభ సమావేశంలో లేనప్పుడు రాష్ట్రపతి ఆర్డినెన్స్ జారీ చేయవచ్చు. గవర్నర్లకు ఆర్టికల్ 213.', 'cat' => 'Polity', 'src' => 'Constitution of India', 'exam' => 'tspsc,appsc,ssc' ),
		array( 'q' => 'ఆర్థిక వ్యవస్థ: ద్రవ్య లోటు (Fiscal Deficit) నుంచి వడ్డీ చెల్లింపులను తీసివేస్తే వచ్చే లోటు ఏది?', 'a' => array( 'రెవెన్యూ లోటు', 'ద్రవ్యీకృత లోటు', 'ప్రాథమిక లోటు', 'ప్రభావవంతమైన రెవెన్యూ లోటు' ), 'c' => 2, 'why' => 'ప్రాథమిక లోటు = ద్రవ్య లోటు − వడ్డీ చెల్లింపులు.', 'cat' => 'Economy', 'src' => 'Union Budget / Finance Ministry', 'exam' => 'banking,ssc,appsc,tspsc' ),
		array( 'q' => 'లాజికల్ రీజనింగ్: ఆగ్నేయం ఉత్తరం అయితే, ఈశాన్యం పడమర అయితే (అదే క్రమంలో), పడమర ఏమవుతుంది?', 'a' => array( 'ఈశాన్యం', 'ఆగ్నేయం', 'వాయవ్యం', 'నైరుతి' ), 'c' => 1, 'why' => 'ప్రతి దిశ సవ్యదిశలో 135° తిరిగింది. పడమర 135° సవ్యదిశలో తిరిగితే ఆగ్నేయం.', 'cat' => 'Reasoning', 'src' => 'Logical Reasoning / Directions', 'exam' => 'ssc,rrb,banking' ),
		array( 'q' => 'రక్షణ & సాంకేతికత: బ్రహ్మోస్ సూపర్‌సోనిక్ క్రూయిజ్ క్షిపణి భారత్‌తో పాటు ఏ దేశ సంయుక్త ప్రాజెక్టు?', 'a' => array( 'అమెరికా', 'ఫ్రాన్స్', 'రష్యా', 'ఇజ్రాయెల్' ), 'c' => 2, 'why' => 'బ్రహ్మోస్‌ను భారత DRDO, రష్యా NPOM సంయుక్త సంస్థ బ్రహ్మోస్ ఏరోస్పేస్ అభివృద్ధి చేసింది.', 'cat' => 'Defence', 'src' => 'drdo.gov.in', 'exam' => 'rrb,tspsc,appsc,ssc' ),
	);

	// Check if external bot ingested questions for today
	$daily_store = get_option( 'studentup_daily_quiz_store', array() );
	$today_key   = studentup_quiz_ist_date(); // v250: IST, UTC kaadu
	if ( is_array( $daily_store ) && ! empty( $daily_store[ $today_key ] ) && is_array( $daily_store[ $today_key ] ) ) {
		$bank = array_merge( $daily_store[ $today_key ], $bank );
	}

	/**
	 * Filter: add your own questions (site owner / coaching partner).
	 *
	 * @param array<int,array<string,mixed>> $bank Question bank.
	 */
	return apply_filters( 'studentup_quiz_bank', $bank );
}

/**
 * Register REST API route for external bot quiz intake.
 */
function studentup_quiz_register_rest_routes() {
	register_rest_route(
		'studentup/v1',
		'/quiz-intake',
		array(
			'methods'             => 'POST',
			'permission_callback' => 'studentup_quiz_rest_permission',
			'callback'            => 'studentup_quiz_rest_intake',
		)
	);
}
add_action( 'rest_api_init', 'studentup_quiz_register_rest_routes' );

/**
 * REST API permission callback for quiz intake.
 *
 * @param WP_REST_Request $request Request.
 * @return bool|WP_Error
 */
function studentup_quiz_rest_permission( $request ) {
	if ( current_user_can( 'edit_posts' ) ) {
		return true;
	}
	$key = $request->get_header( 'x-studentup-key' );
	if ( ! empty( $key ) ) {
		$expected = get_option( 'studentup_quiz_api_key' );
		if ( empty( $expected ) && defined( 'AUTH_KEY' ) ) {
			$expected = substr( hash( 'sha256', AUTH_KEY ), 0, 32 );
		}
		if ( ! empty( $expected ) && hash_equals( (string) $expected, (string) $key ) ) {
			return true;
		}
	}
	return new WP_Error( 'rest_forbidden', 'Unauthorized quiz intake access.', array( 'status' => 401 ) );
}

/**
 * REST API callback: accepts 20 daily questions from external bots.
 *
 * @param WP_REST_Request $request Request.
 * @return WP_REST_Response|WP_Error
 */
function studentup_quiz_rest_intake( $request ) {
	$params = $request->get_json_params();
	if ( empty( $params ) ) {
		$params = $request->get_body_params();
	}
	$raw_questions = array();
	if ( is_array( $params ) ) {
		if ( isset( $params['questions'] ) && is_array( $params['questions'] ) ) {
			$raw_questions = $params['questions'];
		} else {
			$raw_questions = $params;
		}
	}
	if ( empty( $raw_questions ) ) {
		return new WP_Error( 'invalid_data', 'No valid questions array found.', array( 'status' => 400 ) );
	}

	$normalized = array();
	foreach ( $raw_questions as $item ) {
		if ( ! is_array( $item ) ) {
			continue;
		}
		$q_text = sanitize_text_field( $item['q'] ?? ( $item['question'] ?? '' ) );
		// v1.9.140: bot bilingual push → Telugu line (`qt`) ni primary ga vaadu (owner: content Telugu).
		$q_te = sanitize_text_field( (string) ( $item['qt'] ?? '' ) );
		if ( '' !== $q_te && preg_match( '/[\x{0C00}-\x{0C7F}]/u', $q_te ) ) {
			$q_text = $q_te;
		}
		if ( empty( $q_text ) ) {
			continue;
		}
		$opts_raw = $item['a'] ?? ( $item['options'] ?? ( $item['choices'] ?? array() ) );
		if ( ! is_array( $opts_raw ) || count( $opts_raw ) < 2 ) {
			continue;
		}
		$opts = array();
		foreach ( array_slice( $opts_raw, 0, 4 ) as $opt_txt ) {
			$opts[] = sanitize_text_field( (string) $opt_txt );
		}
		while ( count( $opts ) < 4 ) {
			$opts[] = 'Option ' . chr( 65 + count( $opts ) );
		}

		$c_val = $item['c'] ?? ( $item['answer'] ?? ( $item['correct'] ?? 0 ) );
		$c_idx = 0;
		if ( is_numeric( $c_val ) ) {
			$c_idx = max( 0, min( 3, absint( $c_val ) ) );
		} elseif ( is_string( $c_val ) ) {
			$c_upper = strtoupper( trim( $c_val ) );
			if ( in_array( $c_upper, array( 'A', 'B', 'C', 'D' ), true ) ) {
				$c_idx = ord( $c_upper ) - ord( 'A' );
			}
		}

		$exam = sanitize_key( $item['exam'] ?? ( $item['target_exam'] ?? 'general' ) );
		if ( empty( $exam ) ) {
			$exam = 'general';
		}

		$normalized[] = array(
			'q'    => $q_text,
			'a'    => $opts,
			'c'    => $c_idx,
			'why'  => sanitize_text_field( $item['why'] ?? ( $item['explanation'] ?? 'Official answer verification.' ) ),
			'cat'  => sanitize_text_field( $item['cat'] ?? ( $item['category'] ?? 'General Studies' ) ),
			'src'  => sanitize_text_field( $item['src'] ?? ( $item['source'] ?? 'Verified Exam Paper' ) ),
			'exam' => $exam,
		);
	}

	if ( empty( $normalized ) ) {
		return new WP_Error( 'no_valid_questions', 'Failed to normalize questions.', array( 'status' => 422 ) );
	}

	$store = get_option( 'studentup_daily_quiz_store', array() );
	if ( ! is_array( $store ) ) {
		$store = array();
	}
	$today = studentup_quiz_ist_date(); // v250: IST day key
	$store[ $today ] = $normalized;
	update_option( 'studentup_daily_quiz_store', $store, false );

	return rest_ensure_response(
		array(
			'status'   => 'ok',
			'imported' => count( $normalized ),
			'day'      => $today,
		)
	);
}

/**
 * Today's questions — same for everyone, rotates daily (date seed).
 *
 * @param int $count How many questions (default 5).
 * @param int $shift Day offset (practice mode: yesterday = -1).
 * @return array<int,array<string,mixed>>
 */
function studentup_quiz_today( $count = 5, $shift = 0 ) {
	$bank = array_values( studentup_quiz_bank() );
	$n    = count( $bank );
	if ( ! $n ) {
		return array();
	}
	$count  = max( 1, min( 10, (int) $count ) );
	$shift  = (int) $shift;
	// v250: IST day seed — raatri 12:00 IST ki kotha quiz (UTC kaadu).
	$day    = studentup_quiz_ist_daynum( $shift );
	$out    = array();
	// v282: easy pool first (owner: easy reasoning/aptitude game), GK pool fills the rest.
	$easy = array_values( array_filter( $bank, static function ( $q ) { return ! empty( $q['easy'] ); } ) );
	$rest = array_values( array_filter( $bank, static function ( $q ) { return empty( $q['easy'] ); } ) );
	$ne   = count( $easy );
	$take = min( $count, $n );
	$want_easy = min( $take, max( 0, $take - 1 ), $ne ); // 4 easy + 1 GK (when both exist)
	if ( ! count( $rest ) ) {
		$want_easy = min( $take, $ne );
	}
	for ( $i = 0; $i < $want_easy; $i++ ) {
		$out[] = $easy[ ( $day * 5 + $i * 7 ) % $ne ];
	}
	$nr = count( $rest );
	for ( $i = count( $out ); $i < $take && $nr; $i++ ) {
		$out[] = $rest[ ( $day * 5 + $i * 7 ) % $nr ];
	}
	/**
	 * Filter: replace today's set (e.g. current-affairs questions from a post).
	 *
	 * @param array<int,array<string,mixed>> $out   Questions.
	 * @param int                            $shift Day offset.
	 */
	return apply_filters( 'studentup_quiz_today', $out, $shift );
}

/**
 * No-JS path: read + verify the quiz form (never fatal, never stores data).
 *
 * @return array<int,int> picked answers (question index => option index).
 */
function studentup_quiz_answers_from_post() {
	if ( empty( $_POST['su_quiz_nonce'] ) ) {
		return array();
	}
	$nonce = sanitize_text_field( wp_unslash( $_POST['su_quiz_nonce'] ) );
	if ( ! wp_verify_nonce( $nonce, 'su_quiz_submit' ) ) {
		return array();
	}
	$out = array();
	foreach ( studentup_quiz_today() as $i => $q ) {
		$key = 'suq_' . (int) $i;
		if ( isset( $_POST[ $key ] ) ) {
			$val = absint( wp_unslash( $_POST[ $key ] ) );
			if ( $val >= 0 && $val < count( (array) $q['a'] ) ) {
				$out[ $i ] = $val;
			}
		}
	}
	return $out;
}

/**
 * Quiz JSON-LD (valid Quiz + Question). Honest: practice content, no claims.
 *
 * @param array<int,array<string,mixed>> $qs Questions.
 * @return string
 */
function studentup_quiz_schema( $qs ) {
	if ( ! $qs ) {
		return '';
	}
	$items = array();
	foreach ( $qs as $q ) {
		$ans = array();
		foreach ( (array) $q['a'] as $ai => $txt ) {
			$ans[] = array(
				'@type'        => 'Answer',
				'text'         => (string) $txt,
				'position'     => $ai,
				'isCorrect'    => ( (int) $q['c'] === (int) $ai ),
				'comment'      => (string) $q['why'],
			);
		}
		$items[] = array(
			'@type'           => 'Question',
			'name'            => (string) $q['q'],
			'eduQuestionType' => 'Multiple choice',
			'suggestedAnswer' => $ans,
			'acceptedAnswer'  => array(
				'@type'    => 'Answer',
				'text'     => (string) $q['a'][ (int) $q['c'] ],
				'position' => (int) $q['c'],
			),
		);
	}
	$graph = array(
		'@context'      => 'https://schema.org',
		'@type'         => 'Quiz',
		'name'          => 'StudentUp Daily Quiz — ' . date_i18n( 'M j, Y' ),
		'about'         => 'Government exam practice questions for Telangana, Andhra Pradesh and Central exams',
		'inLanguage'    => 'te-IN',
		'educationalLevel' => 'Intermediate to graduate',
		'hasPart'       => $items,
	);
	return wp_json_encode( $graph, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES );
}

/**
 * Render the daily quiz (server-side, JS-enhanced).
 *
 * @param array<string,mixed> $args Args: count, shift, id, heading, kicker.
 * @return void
 */
function studentup_daily_quiz( $args = array() ) {
	if ( ! studentup_opt( 'daily_quiz', '1' ) ) {
		return;
	}
	$args = wp_parse_args(
		$args,
		array(
			'count'   => 5,
			'shift'   => 0,
			'id'      => 'daily-quiz',
			'heading' => '5 Easy Questions — Reasoning & Aptitude',
			'kicker'  => 'DAILY QUIZ',
		)
	);
	$qs = studentup_quiz_today( (int) $args['count'], (int) $args['shift'] );
	if ( ! $qs ) {
		return;
	}
	$picked   = studentup_quiz_answers_from_post();
	$answered = array() !== $picked;
	$score    = 0;
	foreach ( $qs as $i => $q ) {
		if ( $answered && isset( $picked[ $i ] ) && (int) $picked[ $i ] === (int) $q['c'] ) {
			$score++;
		}
	}
	$cat   = studentup_used_term( 'daily-quiz' );
	$more  = $cat ? get_category_link( $cat ) : studentup_mega_page_url( array( 'daily-quiz', 'quiz' ) );
	$pct   = $answered ? (int) round( ( $score / max( 1, count( $qs ) ) ) * 100 ) : 0;
	$line  = $answered
		? sprintf( 'You scored %1$d of %2$d (%3$d%%)', $score, count( $qs ), $pct )
		: '';
	$share = rawurlencode( 'I scored ' . $score . '/' . count( $qs ) . ' in today\'s StudentUp Daily Quiz. Practice free: ' . home_url( '/' ) );
	?>
	<?php
	// v286: share link = clean short URL studentup.in/quiz (studentup_quiz_short_redirect() → real quiz).
	$su_quiz_url = home_url( '/quiz' );
	?>
	<section class="su-quiz su-quiz-v2" id="<?php echo esc_attr( (string) $args['id'] ); ?>" data-su-quiz-url="<?php echo esc_url( $su_quiz_url ); ?>" aria-label="<?php esc_attr_e( 'Daily quiz', 'studentup' ); ?>">
		<div class="su-quiz-card">
			<div class="su-quiz-head">
				<div>
					<p class="su-quiz-kick"><?php echo esc_html( translate( (string) $args['kicker'], 'studentup' ) ); ?> · <?php echo esc_html( date_i18n( 'M j, Y' ) ); ?></p>
					<h2><?php echo esc_html( translate( (string) $args['heading'], 'studentup' ) ); ?></h2>
				</div>
				<div class="su-quiz-score" role="status" aria-live="polite">
					<b data-su-quiz-score><?php echo esc_html( (string) $score ); ?></b><span>/ <?php echo esc_html( (string) count( $qs ) ); ?></span>
				</div>
			</div>
			<div class="su-quiz-bar"><i data-su-quiz-bar style="width:<?php echo esc_attr( (string) ( $answered ? $pct : 0 ) ); ?>%"></i></div>

			<div class="su-q-jump" data-su-quiz-jump role="group" aria-label="<?php esc_attr_e( 'Jump to question', 'studentup' ); ?>"></div>
			<form method="post" class="su-quiz-form" data-su-quiz-form>
				<?php wp_nonce_field( 'su_quiz_submit', 'su_quiz_nonce' ); ?>
				<input type="hidden" name="su_quiz_submitted" value="1">
				<?php foreach ( $qs as $i => $q ) : ?>
					<?php
					$was   = $answered ? (int) ( $picked[ $i ] ?? -1 ) : -1;
					$right = (int) $q['c'];
					?>
					<fieldset class="su-q" data-c="<?php echo esc_attr( (string) $right ); ?>" data-i="<?php echo esc_attr( (string) $i ); ?>" data-exam="<?php echo esc_attr( (string) ( $q['exam'] ?? 'all' ) ); ?>">
						<legend class="su-q-title"><span class="su-q-n"><?php echo esc_html( (string) ( $i + 1 ) ); ?></span> <?php echo esc_html( (string) $q['q'] ); ?></legend>
						<?php
						$su_short = true;
						foreach ( (array) $q['a'] as $su_t ) {
							if ( mb_strlen( (string) $su_t ) > 12 ) {
								$su_short = false;
							}
						}
						?>
						<div class="<?php echo esc_attr( $su_short ? 'su-q-opts is-short' : 'su-q-opts' ); ?>">
							<?php foreach ( (array) $q['a'] as $ai => $txt ) : ?>
								<?php
								$cls = 'su-opt';
								if ( $answered ) {
									if ( $ai === $right ) {
										$cls .= ' right';
									} elseif ( $ai === $was ) {
										$cls .= ' wrong';
									}
								}
								?>
								<label class="<?php echo esc_attr( $cls ); ?>">
									<input type="radio" name="suq_<?php echo esc_attr( (string) $i ); ?>" value="<?php echo esc_attr( (string) $ai ); ?>"<?php checked( $was, (int) $ai ); ?>>
									<span class="su-opt-key"><?php echo esc_html( chr( 65 + (int) $ai ) ); ?></span>
									<span class="su-opt-t"><?php echo esc_html( (string) $txt ); ?></span>
								</label>
							<?php endforeach; ?>
						</div>
						<p class="su-why" data-su-why<?php echo esc_attr( $answered ? '' : ' hidden' ); ?>>
							<strong><?php esc_html_e( 'Why:', 'studentup' ); ?></strong> <?php echo esc_html( (string) $q['why'] ); ?>
							<?php if ( ! empty( $q['src'] ) ) : ?>
								<em>· <?php echo esc_html( translate( (string) $q['src'], 'studentup' ) ); ?></em>
							<?php endif; ?>
						</p>
					</fieldset>
				<?php endforeach; ?>
				<div class="su-quiz-foot">
					<button type="submit" class="su-quiz-restart" data-su-quiz-check><?php echo studentup_ui_icon( 'check', 14 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Check answers', 'studentup' ); ?></button>
					<button type="button" class="su-quiz-restart su-quiz-prev" data-su-quiz-prev hidden>← <?php esc_html_e( 'Previous', 'studentup' ); ?></button>
					<button type="button" class="su-quiz-more su-quiz-next" data-su-quiz-next hidden><?php esc_html_e( 'Next question', 'studentup' ); ?> →</button>
					<button type="button" class="su-quiz-restart" data-su-quiz-restart hidden><?php echo studentup_ui_icon( 'refresh', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Restart', 'studentup' ); ?></button>
					<a class="su-quiz-more su-quiz-share" data-su-quiz-share rel="nofollow noopener" target="_blank"
						href="<?php echo esc_url( 'https://wa.me/?text=' . $share ); ?>" hidden><?php echo studentup_ui_icon( 'upload', 13 ); // phpcs:ignore WordPress.Security.EscapeOutput -- trusted SVG ?> <?php esc_html_e( 'Share my score', 'studentup' ); ?></a>
					<span class="su-quiz-streak" data-su-quiz-streak hidden></span>
					<?php if ( $more ) : ?>
						<a class="su-quiz-more" href="<?php echo esc_url( $more ); ?>"><?php esc_html_e( 'More practice questions', 'studentup' ); ?> →</a>
					<?php endif; ?>
				</div>
			</form>

			<?php if ( $answered ) : ?>
				<div class="su-quiz-done" role="status">
					<b><?php echo esc_html( $line ); ?></b>
					<p>
						<?php
						if ( $pct >= 80 ) {
							esc_html_e( 'Strong — keep this streak alive tomorrow.', 'studentup' );
						} elseif ( $pct >= 40 ) {
							esc_html_e( 'Decent start. Read the "why" lines once and retry.', 'studentup' );
						} else {
							esc_html_e( 'No problem — practice is the point. Try again tomorrow.', 'studentup' );
						}
						?>
					</p>
				</div>
			<?php endif; ?>
		</div>
		<?php
		$json = studentup_quiz_schema( $qs );
		if ( $json ) {
			printf( '<script type="application/ld+json">%s</script>', $json ); // phpcs:ignore WordPress.Security.EscapeOutput -- wp_json_encode output
		}
		?>
	</section>
	<?php
}

/**
 * Days in the current month that already had a quiz (practice-mode links).
 *
 * @param int $days How many past days to expose.
 * @return array<int,string> ISO date => label.
 */
function studentup_quiz_recent_days( $days = 7 ) {
	$out = array();
	for ( $i = 1; $i <= max( 1, (int) $days ); $i++ ) {
		// v250: IST dates — quiz rollover tho match avvali.
		$ts    = strtotime( studentup_quiz_ist_date( -$i ) . ' 00:00:00 UTC' );
		$out[] = gmdate( 'D, M j', $ts );
	}
	return $out;
}

/**
 * v286: `/quiz` short link (status / WhatsApp / Telegram shares) → real quiz.
 * Dedicated page (slug daily-quiz|quiz) unte akkadiki; lekapote home `#daily-quiz`.
 * `?ref=status` carry avutundi (GA4 lo source chudadaniki). parse_request lo
 * handle chestam kabatti rewrite flush avasaram ledu.
 *
 * @param WP $wp Current request.
 * @return void
 */
function studentup_quiz_short_redirect( $wp ) {
	$req = isset( $wp->request ) ? trim( (string) $wp->request, '/' ) : '';
	if ( 'quiz' !== $req && 'play' !== $req ) {
		return;
	}
	$ref = isset( $_GET['ref'] ) ? sanitize_key( wp_unslash( $_GET['ref'] ) ) : 'share'; // phpcs:ignore WordPress.Security.NonceVerification.Recommended -- read-only tracking param
	$dest = function_exists( 'studentup_mega_page_url' ) ? studentup_mega_page_url( array( 'daily-quiz' ) ) : '';
	if ( '' !== $dest ) {
		$dest = add_query_arg( 'ref', $ref, $dest );
	} else {
		$dest = add_query_arg( 'ref', $ref, home_url( '/' ) ) . '#daily-quiz';
	}
	wp_safe_redirect( $dest, 302 );
	exit;
}
add_action( 'parse_request', 'studentup_quiz_short_redirect' );

