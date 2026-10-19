<?php
/**
 * v1.9.133 — Telugu UI chrome (owner rule: site language is Telugu; English
 * only for standard terms — Apply Online, Results, Hall Ticket, PDF …).
 *
 * All theme strings go through the 'studentup' text domain, so one gettext
 * map localises headings, buttons, empty-states and labels without touching
 * ninety template files. Admin option `ui_telugu` ('1' default) switches it
 * off for an English site.
 *
 * @package studentup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * English → Telugu map (visible chrome only; keep placeholders intact).
 *
 * @return array<string,string>
 */
function studentup_ui_te_map() {
	static $map = null;
	if ( null !== $map ) {
		return $map;
	}
	$map = array(
		'TS Police' => 'TS పోలీస్',
		'AP Jobs' => 'AP ఉద్యోగాలు',
		'Telangana Jobs' => 'తెలంగాణ ఉద్యోగాలు',
		'Andhra Pradesh News' => 'ఆంధ్రప్రదేశ్ వార్తలు',
		'Telangana News' => 'తెలంగాణ వార్తలు',
		'Social' => 'సోషల్',
		'Explore' => 'అన్వేషించండి',
		'About StudentUp' => 'StudentUp గురించి',
		'Advertise' => 'ప్రకటనలు',
		'Contact' => 'సంప్రదించండి',
		'Corrections Log' => 'సవరణల లాగ్',
		'District News' => 'జిల్లా వార్తలు',
		'Editorial Team' => 'ఎడిటోరియల్ టీమ్',
		'Govt Schemes' => 'ప్రభుత్వ పథకాలు',
		'Minority & overseas' => 'మైనారిటీ & విదేశీ',
		'Post-matric (Inter · Degree)' => 'పోస్ట్-మెట్రిక్ (ఇంటర్ · డిగ్రీ)',
		'Pre-matric (Class 9–10)' => 'ప్రీ-మెట్రిక్ (9–10 తరగతులు)',
		'Previous Quizzes' => 'మునుపటి క్విజ్‌లు',
		'Scholarships 2026 hub' => 'స్కాలర్‌షిప్‌లు 2026 హబ్',
		'Terms of Use' => 'వినియోగ నిబంధనలు',
		'Walk-in Interviews' => 'వాక్-ఇన్ ఇంటర్వ్యూలు',
		'Verified source feed · fresh items only' => 'ధృవీకరించిన మూలాలు · తాజా అంశాలు మాత్రమే',
		'WEB APP' => 'వెబ్ యాప్',
		'Add to Home Screen' => 'హోమ్ స్క్రీన్‌కు జోడించండి',
		'Reviewed by' => 'సమీక్షించినవారు',
		'Was this update helpful?' => 'ఈ అప్‌డేట్ ఉపయోగపడిందా?',
		'Yes, clear' => 'అవును, స్పష్టంగా ఉంది',
		'Something is missing' => 'ఏదో తక్కువగా ఉంది',
		'Latest updates at a glance' => 'తాజా అప్‌డేట్లు ఒక్క చూపులో',
		'Official source' => 'అధికారిక మూలం',
		'Scholarships open now' => 'ఇప్పుడు తెరిచి ఉన్న స్కాలర్‌షిప్‌లు',
		'Get every update as a notification' => 'ప్రతి అప్‌డేట్ నోటిఫికేషన్‌గా పొందండి',
		'Turn on alerts' => 'అలర్ట్‌లు ఆన్ చేయండి',
		'StudentUp App' => 'StudentUp యాప్',
		'Key Highlights' => 'ముఖ్యాంశాలు',
		'Instant Job Alerts & Exam Updates' => 'తక్షణ ఉద్యోగ అలర్ట్‌లు & పరీక్ష అప్‌డేట్లు',
		'Join WhatsApp Channel' => 'WhatsApp ఛానల్‌లో చేరండి',
		'Join Telegram Group' => 'Telegram గ్రూప్‌లో చేరండి',
		'All India' => 'ఆల్ ఇండియా',
		'Your age' => 'మీ వయసు',
		'Closing soon first' => 'త్వరలో ముగిసేవి ముందు',
		'Newest first' => 'కొత్తవి ముందు',
		'Popular searches' => 'ఎక్కువగా వెతికేవి',
		'Trending & Related Notifications' => 'ట్రెండింగ్ & సంబంధిత నోటిఫికేషన్లు',
		'Clear history' => 'హిస్టరీ క్లియర్',
		'Yes, alert cheyandi' => 'అవును, అలర్ట్ చేయండి',
		'No thanks' => 'వద్దు',
		'Guides verified from official sources' => 'అధికారిక మూలాల నుంచి ధృవీకరించిన గైడ్‌లు',
		'Read details' => 'వివరాలు చదవండి',
		// v1.9.144 category / menu / qualification / month names.
		'TS Government Jobs' => 'TS ప్రభుత్వ ఉద్యోగాలు',
		'AP Government Jobs' => 'AP ప్రభుత్వ ఉద్యోగాలు',
		'Central Govt Jobs' => 'కేంద్ర ఉద్యోగాలు',
		'Central Government Jobs' => 'కేంద్ర ప్రభుత్వ ఉద్యోగాలు',
		'Admit Cards' => 'అడ్మిట్ కార్డులు',
		'Admit Card' => 'అడ్మిట్ కార్డ్',
		'Admissions' => 'అడ్మిషన్లు',
		'Bank Jobs' => 'బ్యాంక్ ఉద్యోగాలు',
		'Railway Jobs' => 'రైల్వే ఉద్యోగాలు',
		'Police Jobs' => 'పోలీస్ ఉద్యోగాలు',
		'Teaching Jobs' => 'టీచింగ్ ఉద్యోగాలు',
		'Defence Jobs' => 'డిఫెన్స్ ఉద్యోగాలు',
		'Answer Keys' => 'ఆన్సర్ కీలు',
		'Answer Key' => 'ఆన్సర్ కీ',
		'Syllabus' => 'సిలబస్',
		'Study Material' => 'స్టడీ మెటీరియల్',
		'Uncategorized' => 'ఇతరాలు',
		'Education News' => 'విద్యా వార్తలు',
		'About Us' => 'మా గురించి',
		'Contact Us' => 'సంప్రదించండి',
		'Privacy Policy' => 'ప్రైవసీ పాలసీ',
		'Disclaimer' => 'డిస్‌క్లెయిమర్',
		'Terms and Conditions' => 'నియమాలు & షరతులు',
		'Terms & Conditions' => 'నియమాలు & షరతులు',
		'Editorial Policy' => 'ఎడిటోరియల్ పాలసీ',
		'Corrections & Updates' => 'సవరణలు & అప్‌డేట్లు',
		'Daily Quiz & Polls' => 'డైలీ క్విజ్ & పోల్స్',
		'Post Your News' => 'మీ వార్త పంపండి',
		'Exam & Application Calendar' => 'పరీక్ష & దరఖాస్తు క్యాలెండర్',
		'Thank You' => 'ధన్యవాదాలు',
		'Exam Calendar' => 'పరీక్షల క్యాలెండర్',
		'Internet Center' => 'ఇంటర్నెట్ సెంటర్',
		'SSC · 10th' => '10వ తరగతి',
		'Inter (10+2)' => 'ఇంటర్ (10+2)',
		'Diploma' => 'డిప్లొమా',
		'Degree' => 'డిగ్రీ',
		'PG' => 'పీజీ',
		'%s Jobs' => '%s ఉద్యోగాలు',
		'yrs' => 'ఏళ్లు',
		'January' => 'జనవరి',
		'February' => 'ఫిబ్రవరి',
		'March' => 'మార్చి',
		'April' => 'ఏప్రిల్',
		'May' => 'మే',
		'June' => 'జూన్',
		'July' => 'జూలై',
		'August' => 'ఆగస్టు',
		'September' => 'సెప్టెంబర్',
		'October' => 'అక్టోబర్',
		'November' => 'నవంబర్',
		'December' => 'డిసెంబర్',
		'Jan' => 'జన',
		'Feb' => 'ఫిబ్ర',
		'Mar' => 'మార్చి',
		'Apr' => 'ఏప్రి',
		'Jun' => 'జూన్',
		'Jul' => 'జూలై',
		'Aug' => 'ఆగ',
		'Sep' => 'సెప్',
		'Oct' => 'అక్టో',
		'Nov' => 'నవం',
		'Dec' => 'డిసెం',
		// v1.9.143 aria-labels / placeholders.
		'Pages' => 'పేజీలు',
		'Close' => 'మూసివేయి',
		'Breadcrumb' => 'బ్రెడ్‌క్రంబ్',
		'Updates by organisation' => 'సంస్థల వారీగా అప్‌డేట్లు',
		'Quick search' => 'త్వరిత శోధన',
		'Page title' => 'పేజీ శీర్షిక',
		'Jobs by qualification' => 'అర్హత వారీగా ఉద్యోగాలు',
		'YouTube' => 'YouTube',
		'WhatsApp' => 'WhatsApp',
		'WhatsApp Status Card Generator' => 'WhatsApp స్టేటస్ కార్డ్ జనరేటర్',
		'Trending today' => 'ఈరోజు ట్రెండింగ్',
		'Trending and High-Intent Recommendations' => 'మీకు సరిపోయే సిఫార్సులు',
		'Top hot jobs today' => 'ఈరోజు టాప్ ఉద్యోగాలు',
		'Telegram' => 'Telegram',
		'Tags' => 'ట్యాగ్‌లు',
		'Subcategories' => 'ఉప విభాగాలు',
		'StudentUp section' => 'StudentUp విభాగం',
		'StudentUp search and quick links' => 'StudentUp శోధన & త్వరిత లింకులు',
		'Student reviews' => 'విద్యార్థుల అభిప్రాయాలు',
		'Sponsored college partner content' => 'కళాశాల భాగస్వామి సమాచారం',
		'Site menu' => 'సైట్ మెనూ',
		'Search' => 'శోధించు',
		'Search this site' => 'ఈ సైట్‌లో శోధించండి',
		'Search results' => 'శోధన ఫలితాలు',
		'Scholarships' => 'స్కాలర్‌షిప్‌లు',
		'Salary calculator' => 'జీతం కాలిక్యులేటర్',
		'Reset font size' => 'అక్షర పరిమాణం సాధారణం',
		'Reading options' => 'చదివే ఎంపికలు',
		'Quick story cards' => 'త్వరిత స్టోరీ కార్డులు',
		'Quick navigation' => 'త్వరిత నావిగేషన్',
		'Previous card' => 'మునుపటి కార్డ్',
		'Post pages' => 'పోస్ట్ పేజీలు',
		'Picked for you' => 'మీ కోసం ఎంపిక',
		'Our team' => 'మా బృందం',
		'Our location' => 'మా చిరునామా',
		'Opportunity sections' => 'అవకాశాల విభాగాలు',
		'Next card' => 'తర్వాతి కార్డ్',
		'More posts' => 'మరిన్ని పోస్టులు',
		'Menu' => 'మెనూ',
		'Latest jobs — scrolling list' => 'తాజా ఉద్యోగాలు — జాబితా',
		'Latest by section' => 'విభాగాల వారీగా తాజావి',
		'Join Student Community' => 'విద్యార్థి కమ్యూనిటీలో చేరండి',
		'Job calendar' => 'ఉద్యోగ క్యాలెండర్',
		'Instant job alerts' => 'తక్షణ ఉద్యోగ అలర్ట్‌లు',
		'Instagram' => 'Instagram',
		'Increase font size' => 'అక్షరాలు పెద్దవి',
		'Font size controls' => 'అక్షర పరిమాణం',
		'Featured Media Unit' => 'ఫీచర్డ్ మీడియా',
		'Explore by Category' => 'విభాగాల వారీగా చూడండి',
		'Decrease font size' => 'అక్షరాలు చిన్నవి',
		'Dark mode' => 'డార్క్ మోడ్',
		'Compare notifications' => 'నోటిఫికేషన్లు పోల్చండి',
		'Close menu' => 'మెనూ మూసివేయి',
		'Case studies' => 'విజయ గాథలు',
		'Author' => 'రచయిత',
		'About the Author' => 'రచయిత గురించి',
		'AI job match and eligibility checker' => 'ఉద్యోగ అర్హత చెకర్',
		'Small text' => 'చిన్న అక్షరాలు',
		'Normal text' => 'సాధారణ అక్షరాలు',
		'Large text' => 'పెద్ద అక్షరాలు',
		'Search jobs, exams, results, scholarships…' => 'ఉద్యోగాలు, పరీక్షలు, ఫలితాలు, స్కాలర్‌షిప్‌లు వెతకండి…',
		'Search jobs, results, scholarships… (Esc to close)' => 'ఉద్యోగాలు, ఫలితాలు, స్కాలర్‌షిప్‌లు… (Esc మూసివేయి)',
		// Mega menu descriptions (v1.9.133).
		'Telangana & Andhra Pradesh' => 'తెలంగాణ & ఆంధ్రప్రదేశ్',
		'Central & private' => 'కేంద్ర & ప్రైవేట్',
		'Updates' => 'అప్‌డేట్స్',
		'Practice' => 'ప్రాక్టీస్',
		'Find money' => 'ఆర్థిక సాయం',
		'By level' => 'స్థాయి వారీగా',
		'Schemes & local' => 'పథకాలు & స్థానికం',
		'Site' => 'సైట్',
		'Policies' => 'విధానాలు',
		'Only notices with live dates — no expired lists.' => 'గడువు ఉన్న నోటిఫికేషన్లు మాత్రమే — ముగిసినవి ఉండవు.',
		'Open the board' => 'బోర్డు తెరవండి',
		'Exam calendar 2026' => 'పరీక్షల క్యాలెండర్ 2026',
		'Add every confirmed last date to your phone in one tap.' => 'నిర్ధారిత చివరి తేదీలన్నీ ఒక్క ట్యాప్‌తో మీ ఫోన్‌లోకి.',
		'Open calendar' => 'క్యాలెండర్ తెరవండి',
		'Free Internet Center' => 'ఫ్రీ ఇంటర్నెట్ సెంటర్',
		'Form filling at a fixed, published price — what we do and never do.' => 'నిర్ణీత ధరకే ఫారం ఫిల్లింగ్ — మేము ఏమి చేస్తాం, ఏమి చేయం.',
		'See the price list' => 'ధరల జాబితా చూడండి',
		'Telegram channel' => 'టెలిగ్రామ్ ఛానల్',
		'Job alerts reach you first — no spam, leave anytime.' => 'జాబ్ అలర్ట్స్ మీకే ముందుగా — స్పామ్ లేదు, ఎప్పుడైనా వదిలేయవచ్చు.',
		'Join channel' => 'ఛానల్‌లో చేరండి',
		'Recommended' => 'సిఫార్సు',
		'TSPSC · Police · Gurukul' => 'TSPSC · పోలీస్ · గురుకుల',
		'APPSC · Police · DSC · Secretariat' => 'APPSC · పోలీస్ · DSC · సచివాలయం',
		'10th · Inter · Degree · PG' => '10th · Inter · Degree · PG',
		'SSC · UPSC · Railways · Banks' => 'SSC · UPSC · రైల్వే · బ్యాంకులు',
		'Off-campus · fresher drives' => 'ఆఫ్-క్యాంపస్ · ఫ్రెషర్ డ్రైవ్స్',
		'IT · developer · support' => 'IT · డెవలపర్ · సపోర్ట్',
		'This week drives · venues' => 'ఈ వారం డ్రైవ్స్ · వేదికలు',
		'Stipend · remote · college' => 'స్టైపెండ్ · రిమోట్ · కాలేజీ',
		'Board · competitive · keys' => 'బోర్డు · పోటీ పరీక్షలు · కీలు',
		'Admit card · instructions' => 'అడ్మిట్ కార్డ్ · సూచనలు',
		'Confirmed last dates + .ics' => 'నిర్ధారిత చివరి తేదీలు',
		'Fresh questions every day' => 'ప్రతిరోజూ కొత్త ప్రశ్నలు',
		'Daily GK for exams' => 'పరీక్షల కోసం రోజువారీ GK',
		'Answer keys after every exam' => 'ప్రతి పరీక్ష తర్వాత Answer Keys',
		'NSP · ePASS · state schemes' => 'NSP · ePASS · రాష్ట్ర పథకాలు',
		'Amounts, eligibility, last dates' => 'మొత్తాలు, అర్హత, చివరి తేదీలు',
		'Verified journeys · lessons' => 'నిజమైన ప్రయాణాలు · పాఠాలు',
		'School-level schemes' => 'పాఠశాల స్థాయి పథకాలు',
		'The biggest State schemes' => 'ప్రధాన రాష్ట్ర పథకాలు',
		'NSP minority + abroad aid' => 'NSP మైనారిటీ + విదేశీ విద్య సాయం',
		'Rythu Bharosa · pensions · ration · housing' => 'రైతు భరోసా · పెన్షన్లు · రేషన్ · ఇళ్లు',
		'TS & AP districts · holidays · alerts' => 'TS & AP జిల్లాలు · సెలవులు · అలర్ట్స్',
		'Last 7 days + explanations' => 'గత 7 రోజులు + వివరణలు',
		'Who writes and verifies' => 'ఎవరు రాస్తారు, ఎవరు ధృవీకరిస్తారు',
		'Standards + sources' => 'ప్రమాణాలు + ఆధారాలు',
		'Public fixes · 48h SLA' => 'బహిరంగ సవరణలు · 48 గంటల్లో',
		'Corrections · suggestions' => 'సవరణలు · సూచనలు',
		'Sponsorship slots' => 'స్పాన్సర్‌షిప్ అవకాశాలు',
		'What we store (very little)' => 'మేము ఏమి నిల్వ చేస్తాం (చాలా తక్కువ)',
		'Rules for using the site' => 'సైట్ వినియోగ నియమాలు',
		'Not a government website' => 'ఇది ప్రభుత్వ వెబ్‌సైట్ కాదు',
		'How we verify every update' => 'ప్రతి అప్‌డేట్‌ను ఎలా ధృవీకరిస్తాం',
		'Latest active jobs' => 'తాజా యాక్టివ్ ఉద్యోగాలు',
		'Instant alerts' => 'తక్షణ అలర్ట్స్',
		'Browse everything' => 'అన్నీ చూడండి',
		'Most searched by students' => 'విద్యార్థులు ఎక్కువగా వెతికేవి',
		'Main menu' => 'ప్రధాన మెనూ',
		'Skip to content' => 'కంటెంట్‌కు వెళ్లండి',
		// /today/ page (v1.9.134).
		'All' => 'అన్నీ',
		'Timed mock tests · instant rank' => 'టైమ్‌డ్ మాక్ టెస్టులు · వెంటనే ర్యాంక్',
		'Date-wise updates' => 'తేదీల వారీగా అప్‌డేట్స్',
		'Recently viewed' => 'మీరు ఇటీవల చూసినవి',
		'Filter by section' => 'విభాగం వారీగా ఫిల్టర్',
		'Sunday' => 'ఆదివారం',
		'Monday' => 'సోమవారం',
		'Tuesday' => 'మంగళవారం',
		'Wednesday' => 'బుధవారం',
		'Thursday' => 'గురువారం',
		'Friday' => 'శుక్రవారం',
		'Saturday' => 'శనివారం',
		'Today’s updates — jobs, results, hall tickets' => 'ఈరోజు అప్‌డేట్స్ — ఉద్యోగాలు, రిజల్ట్స్, హాల్ టికెట్లు',
		'Today’s updates (%s) — latest jobs, results, hall tickets' => 'ఈరోజు అప్‌డేట్స్ (%s) — ఉద్యోగాలు, Results, Hall Tickets',
		'%1$d updates from the last %2$d days, grouped by date: notifications, last dates, results, hall tickets — Telugu. Updated every day.' => 'గత %2$d రోజుల్లో %1$d అప్‌డేట్స్, తేదీల వారీగా: నోటిఫికేషన్లు, చివరి తేదీలు, Results, Hall Tickets — తెలుగులో. ప్రతిరోజూ అప్‌డేట్.',
		'Today’s updates'                         => 'ఈరోజు అప్‌డేట్స్',
		'Today'                                   => 'ఈరోజు',
		'Yesterday'                               => 'నిన్న',
		'Last day today'                          => 'ఈరోజే చివరి రోజు',
		'Date-wise · every morning'               => 'తేదీల వారీగా · ప్రతి ఉదయం',
		'Older updates'                           => 'పాత అప్‌డేట్స్',
		'Updates from the last %d days. Older posts are in each section.' => 'గత %d రోజుల అప్‌డేట్స్. పాతవి ఆయా విభాగాల్లో ఉన్నాయి.',
		// v1.9.139 QA pass — opportunities board, install sheet, polls, footer.
		'Download App' => 'యాప్ డౌన్‌లోడ్',
		'Install StudentUp as a web app' => 'StudentUp ని వెబ్ యాప్‌గా ఇన్‌స్టాల్ చేయండి',
		'One-tap access · visited pages can stay available offline. No native APK download is required.' => 'ఒక్క ట్యాప్‌లో యాక్సెస్ · చూసిన పేజీలు ఆఫ్‌లైన్‌లోనూ ఉంటాయి. APK డౌన్‌లోడ్ అవసరం లేదు.',
		'Install app' => 'యాప్ ఇన్‌స్టాల్',
		'Add to Home screen' => 'హోమ్ స్క్రీన్‌కు యాడ్',
		'Computer:' => 'కంప్యూటర్:',
		'click the install icon in the address bar' => 'అడ్రస్ బార్‌లో ఇన్‌స్టాల్ ఐకాన్ నొక్కండి',
		'Later' => 'తర్వాత',
		'All rights reserved.' => 'సర్వ హక్కులు రక్షితం.',
		'navigate' => 'కదలండి',
		'open' => 'తెరవండి',
		'%d min read' => '%d నిమి. చదవడానికి',
		'Latest active opportunities' => 'తాజా యాక్టివ్ అవకాశాలు',
		'LIVE LIST' => 'లైవ్ లిస్ట్',
		'Latest Jobs & Student Opportunities' => 'తాజా ఉద్యోగాలు & విద్యార్థి అవకాశాలు',
		'TS, AP, Central, software, private, walk-in, job mela, scholarship, results and hall-ticket updates in one clean list.' => 'TS, AP, కేంద్ర, సాఫ్ట్‌వేర్, ప్రైవేట్, వాక్-ఇన్, జాబ్ మేళా, స్కాలర్‌షిప్, Results, Hall Ticket అప్‌డేట్స్ — ఒకే నీట్ లిస్ట్‌లో.',
		'active updates' => 'యాక్టివ్ అప్‌డేట్స్',
		'active update' => 'యాక్టివ్ అప్‌డేట్',
		'Find the right opportunity' => 'మీకు సరిపోయే అవకాశం వెతకండి',
		'Search title' => 'టైటిల్ వెతకండి',
		'Try SSC, software, scholarship…' => 'TSPSC, సాఫ్ట్‌వేర్, స్కాలర్‌షిప్…',
		'Category' => 'విభాగం',
		'All categories' => 'అన్ని విభాగాలు',
		'Any deadline' => 'ఏ తేదీ అయినా',
		'Closing in 30 days' => '30 రోజుల్లో ముగుస్తున్నవి',
		'Date not announced' => 'తేదీ ప్రకటించలేదు',
		'Search and filters run in your browser. Open the article and confirm the official notification before applying.' => 'సెర్చ్, ఫిల్టర్లు మీ బ్రౌజర్‌లోనే పనిచేస్తాయి. దరఖాస్తు చేసే ముందు ఆర్టికల్ తెరిచి official notification సరిచూడండి.',
		'No matching active opportunities found. Try another keyword or category.' => 'సరిపోయే యాక్టివ్ అవకాశాలు లేవు. వేరే పదం లేదా విభాగం ప్రయత్నించండి.',
		'No active verified opportunities are available right now. Please check again after the next update.' => 'ప్రస్తుతం యాక్టివ్ అవకాశాలు లేవు. తదుపరి అప్‌డేట్ తర్వాత మళ్లీ చూడండి.',
		'Last-date information is taken from the reviewed article. Always open the article and verify the official notification before applying.' => 'చివరి తేదీ సమాచారం సమీక్షించిన ఆర్టికల్ నుంచి తీసుకున్నది. దరఖాస్తు చేసే ముందు అధికారిక నోటిఫికేషన్ తప్పక సరిచూడండి.',
		'This list updates from published StudentUp posts. Verified last dates are shown, expired notices are hidden automatically, and an unavailable date is shown as <strong>Not announced</strong> — never guessed.' => 'ఈ లిస్ట్ StudentUp లో ప్రచురించిన పోస్టుల నుంచి అప్‌డేట్ అవుతుంది. ధృవీకరించిన చివరి తేదీలే చూపిస్తాం, గడువు ముగిసినవి ఆటోమేటిక్‌గా దాచబడతాయి, తేదీ లేకపోతే <strong>ప్రకటించలేదు</strong> అని చూపిస్తాం — ఊహించం.',
		'Not announced' => 'ప్రకటించలేదు',
		'Updated' => 'అప్‌డేట్',
		'Source checked' => 'సోర్స్ సరిచూశాం',
		'Details' => 'వివరాలు',
		'Official Apply' => 'Official Apply',
		'Which update do you want first on WhatsApp?' => 'WhatsApp లో ముందుగా ఏ అప్‌డేట్ కావాలి?',
		'New job notifications' => 'కొత్త జాబ్ నోటిఫికేషన్లు',
		'Exam date changes' => 'పరీక్ష తేదీ మార్పులు',
		'Results & hall tickets' => 'Results & Hall Tickets',
		'Scholarship deadlines' => 'స్కాలర్‌షిప్ చివరి తేదీలు',
		'Which exam are you preparing for right now?' => 'ఇప్పుడు మీరు ఏ పరీక్షకు సిద్ధమవుతున్నారు?',
		'Banking (IBPS / RRB)' => 'బ్యాంకింగ్ (IBPS / RRB)',
		'What stops you from applying to a government job?' => 'ప్రభుత్వ ఉద్యోగానికి దరఖాస్తు చేయకుండా మిమ్మల్ని ఏది ఆపుతోంది?',
		'Fee / documents cost' => 'ఫీజు / డాక్యుమెంట్ల ఖర్చు',
		'Not sure I am eligible' => 'అర్హత ఉందో లేదో తెలియదు',
		'Form filling is confusing' => 'ఫారం నింపడం గందరగోళం',
		'I miss the last date' => 'చివరి తేదీ మిస్ అవుతున్నాను',
		'Where do you read StudentUp mostly?' => 'StudentUp ఎక్కువగా ఎక్కడ చదువుతారు?',
		'Phone' => 'ఫోన్',
		'Laptop' => 'ల్యాప్‌టాప్',
		'College computer' => 'కాలేజీ కంప్యూటర్',
		'Internet center' => 'ఇంటర్నెట్ సెంటర్',
		'Which free tool should be built next?' => 'తర్వాత ఏ ఫ్రీ టూల్ కావాలి?',
		'Resume builder' => 'రెజ్యూమ్ బిల్డర్',
		'Exam date planner' => 'పరీక్ష తేదీల ప్లానర్',
		'Cut-off predictor' => 'కట్-ఆఫ్ ప్రిడిక్టర్',
		'Study timetable' => 'స్టడీ టైమ్‌టేబుల్',
		'Do you want a Telugu version of every article?' => 'ప్రతి ఆర్టికల్ తెలుగులో కావాలా?',
		'Yes — Telugu first' => 'అవును — తెలుగు ముందు',
		'English is fine' => 'ఇంగ్లీష్ సరిపోతుంది',
		'Both side by side' => 'రెండూ పక్కపక్కనే',
		'Only for exams' => 'పరీక్షలకు మాత్రమే',
		'How many notifications per day is OK for you?' => 'రోజుకు ఎన్ని నోటిఫికేషన్లు సరిపోతాయి?',
		'Only urgent (max 2)' => 'అత్యవసరమైనవే (గరిష్ఠం 2)',
		'3–5 updates' => '3–5 అప్‌డేట్స్',
		'One morning list' => 'ఉదయం ఒకే లిస్ట్',
		'No alerts, I check myself' => 'అలర్ట్స్ వద్దు, నేనే చూసుకుంటా',
		'Fresh questions every day (IST)' => 'ప్రతిరోజూ కొత్త ప్రశ్నలు (IST)',
		'Dates unna active notices only' => 'తేదీలు ఉన్న యాక్టివ్ నోటీసులే',
		'Today\'s 5 questions' => 'ఈరోజు 5 ప్రశ్నలు',
		'Compare Jobs' => 'ఉద్యోగాలు పోల్చండి',
		'Compare up to 3 posts' => '3 పోస్టుల వరకు పోల్చండి',
		'WhatsApp · Telegram channel' => 'WhatsApp · Telegram ఛానల్',
		'Age Calculator' => 'వయస్సు కాలిక్యులేటర్',
		'Check age eligibility with reservation relaxation' => 'రిజర్వేషన్ సడలింపుతో వయో అర్హత చూడండి',
		'Fee Calculator' => 'Fee కాలిక్యులేటర్',
		'Calculate application & exam fee' => 'దరఖాస్తు & పరీక్ష fee లెక్కించండి',
		'Syllabus Tracker' => 'సిలబస్ ట్రాకర్',
		'Track your exam study progress' => 'మీ పరీక్ష ప్రిపరేషన్ ట్రాక్ చేయండి',
		'Salary Calculator' => 'జీతం కాలిక్యులేటర్',
		'7th Pay Commission in-hand pay' => '7వ వేతన సంఘం in-hand జీతం',
		'Materials & previous papers' => 'మెటీరియల్స్ & పాత పేపర్లు',
		'Previous papers & keys' => 'పాత పేపర్లు & కీలు',
		'Application PDF' => 'దరఖాస్తు PDF',
		'Preparation group' => 'ప్రిపరేషన్ గ్రూప్',
		'Daily Quiz — 5 easy questions, share your score' => 'డైలీ క్విజ్ — 5 సులభ ప్రశ్నలు, మీ స్కోర్ షేర్ చేయండి',
		'%s articles' => '%s ఆర్టికల్స్',
		'Author website / profile' => 'రచయిత వెబ్‌సైట్ / ప్రొఫైల్',
		'Reasoning & Aptitude basics (SSC / RRB / Banking / TSPSC / APPSC)' => 'రీజనింగ్ & ఆప్టిట్యూడ్ బేసిక్స్ (SSC / RRB / Banking / TSPSC / APPSC)',
		'Constitution of India' => 'భారత రాజ్యాంగం',
		'Union Budget / Finance Ministry' => 'కేంద్ర బడ్జెట్ / ఆర్థిక మంత్రిత్వ శాఖ',
		'Telangana State Archaeology' => 'తెలంగాణ రాష్ట్ర పురావస్తు శాఖ',
		'Verified Exam Paper' => 'ధృవీకరించిన పరీక్ష పేపర్',
		'AP Irrigation Dept' => 'AP నీటిపారుదల శాఖ',
		'Ministry of Finance' => 'ఆర్థిక మంత్రిత్వ శాఖ',
		'NCERT Biology' => 'NCERT జీవశాస్త్రం',
		'National Tiger Conservation Authority' => 'జాతీయ పులుల సంరక్షణ ప్రాధికార సంస్థ',
		'Quantitative Aptitude / Banking' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్ / బ్యాంకింగ్',
		'Quantitative Aptitude / Ratios' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్ / నిష్పత్తులు',
		'Quantitative Aptitude / Time & Work' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్ / కాలం-పని',
		'Quantitative Aptitude' => 'క్వాంటిటేటివ్ ఆప్టిట్యూడ్',
		'SSC CGL / Quantitative Aptitude' => 'SSC CGL / క్వాంటిటేటివ్ ఆప్టిట్యూడ్',
		'TSPSC / TS Exams Current Affairs' => 'TSPSC / TS పరీక్షల కరెంట్ అఫైర్స్',
		'Telangana History / TSPSC' => 'తెలంగాణ చరిత్ర / TSPSC',
		// v1.9.141 full-surface sweep (secondary templates, workspace, saved, doubts, corrections, internet-center).
		'Published articles: %d' => 'ప్రచురించిన ఆర్టికల్స్: %d',
		'The StudentUp editorial team — honest articles for Telangana & Andhra Pradesh students, based on official sources.' => 'StudentUp ఎడిటోరియల్ టీమ్ — తెలంగాణ & ఆంధ్రప్రదేశ్ విద్యార్థుల కోసం అధికారిక మూలాల ఆధారంగా నిజాయితీగా రాసే ఆర్టికల్స్.',
		'%s comment' => '%s వ్యాఖ్య',
		'Older comments' => 'పాత వ్యాఖ్యలు',
		'Newer comments' => 'కొత్త వ్యాఖ్యలు',
		'Reply to %s' => '%s కు సమాధానం',
		'Social media' => 'సోషల్ మీడియా',
		'Advertisement' => 'ప్రకటన',
		'Apply actions' => 'దరఖాస్తు చర్యలు',
		'How every update is verified' => 'ప్రతి అప్‌డేట్‌ను ఎలా ధృవీకరిస్తాం',
		'We start from the official notification or the department website only.' => 'అధికారిక నోటిఫికేషన్ లేదా శాఖ వెబ్‌సైట్ నుంచే మొదలుపెడతాం.',
		'Dates, fees, vacancies and eligibility go into the post exactly as published — nothing is estimated.' => 'తేదీలు, ఫీజులు, ఖాళీలు, అర్హత — ప్రచురించినట్లే పోస్టులో ఉంటాయి; ఏదీ అంచనా వేయం.',
		'A reader correction is published publicly with the updated date.' => 'పాఠకుల సవరణను అప్‌డేట్ తేదీతో బహిరంగంగా ప్రచురిస్తాం.',
		'%d dated notification is open right now.' => 'ప్రస్తుతం %d తేదీ ఉన్న నోటిఫికేషన్ ఓపెన్‌లో ఉంది.',
		'No last dates are confirmed yet. Dates appear here only after the official notification is published - we never estimate a deadline.' => 'ఇంకా చివరి తేదీలు ధృవీకరించలేదు. అధికారిక నోటిఫికేషన్ వచ్చాకే తేదీలు ఇక్కడ కనిపిస్తాయి — గడువును మేము ఎప్పుడూ అంచనా వేయం.',
		'%d day left' => '%d రోజు మిగిలింది',
		'TS &amp; AP' => 'TS &amp; AP',
		'This page cannot take questions.' => 'ఈ పేజీలో ప్రశ్నలు స్వీకరించడం లేదు.',
		'Student' => 'విద్యార్థి',
		'Could not save the question. Please try again.' => 'ప్రశ్న సేవ్ కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.',
		'Could not save that question. Please check and try again.' => 'ఆ ప్రశ్న సేవ్ కాలేదు. దయచేసి సరిచూసి మళ్లీ ప్రయత్నించండి.',
		'Example: BC-B category ki age relaxation enta?' => 'ఉదాహరణ: BC-B కేటగిరీకి వయో సడలింపు ఎంత?',
		'StudentUp answer (public)' => 'StudentUp సమాధానం (పబ్లిక్)',
		'Answer with the official source. Only answered questions go into QAPage schema.' => 'అధికారిక మూలంతో సమాధానం ఇవ్వండి. సమాధానం ఉన్న ప్రశ్నలే QAPage schema లోకి వెళ్తాయి.',
		'StudentUp — Doubt answer' => 'StudentUp — సందేహానికి సమాధానం',
		'latest updates on the home page' => 'హోమ్ పేజీలో తాజా అప్‌డేట్లు',
		'Apply Online' => 'ఆన్‌లైన్‌లో దరఖాస్తు',
		'Official source registered; check the notice before applying.' => 'అధికారిక మూలం నమోదైంది; దరఖాస్తుకు ముందు నోటీసు చూడండి.',
		'Set your qualification and state once. The list is built on this device - no login, nothing sent to a server.' => 'మీ అర్హత, రాష్ట్రం ఒక్కసారి సెట్ చేయండి. జాబితా ఈ పరికరంలోనే తయారవుతుంది — లాగిన్ లేదు, సర్వర్‌కు ఏమీ పంపం.',
		'Build my list' => 'నా జాబితా తయారుచేయి',
		'Reset my choices' => 'నా ఎంపికలు రీసెట్',
		'Downloads a calendar file with an alarm one day before.' => 'ఒక రోజు ముందు అలారంతో క్యాలెండర్ ఫైల్ డౌన్‌లోడ్ అవుతుంది.',
		'Breaking news by state and district' => 'రాష్ట్రం, జిల్లా వారీగా బ్రేకింగ్ న్యూస్',
		'Search Telangana / Andhra news…' => 'తెలంగాణ / ఆంధ్ర వార్తలు వెతకండి…',
		'Search %s news…' => '%s వార్తలు వెతకండి…',
		'No district with that name — press Search to look inside the news.' => 'ఆ పేరుతో జిల్లా లేదు — వార్తల్లో వెతకడానికి Search నొక్కండి.',
		'StudentUp live stats' => 'StudentUp లైవ్ గణాంకాలు',
		'All tools' => 'అన్ని టూల్స్',
		'Money' => 'డబ్బు',
		'Career' => 'కెరీర్',
		'Search cheyandi leda tab tap cheyandi — okka sari lo okka tool, screen clean ga untundi.' => 'వెతకండి లేదా ట్యాబ్ నొక్కండి — ఒకసారి ఒక టూల్, స్క్రీన్ క్లీన్‌గా ఉంటుంది.',
		'Search tools' => 'టూల్స్ వెతకండి',
		'Search a tool — salary, age, fee, resume…' => 'టూల్ వెతకండి — జీతం, వయస్సు, ఫీజు, రెజ్యూమ్…',
		'Clear search' => 'వెతుకులాట క్లియర్',
		'Filter tools by category' => 'కేటగిరీ వారీగా టూల్స్',
		'Ee peru tho tool ledu:' => 'ఈ పేరుతో టూల్ లేదు:',
		'Try “salary”, “age” leda “resume”.' => '“salary”, “age” లేదా “resume” ప్రయత్నించండి.',
		'Next tool' => 'తర్వాతి టూల్',
		'Back to tools' => 'టూల్స్‌కు వెనక్కి',
		'Category shortcuts' => 'కేటగిరీ షార్ట్‌కట్‌లు',
		'Close install banner' => 'ఇన్‌స్టాల్ బ్యానర్ మూసివేయి',
		'Saved job reminders' => 'సేవ్ చేసిన ఉద్యోగ రిమైండర్లు',
		'Remind me in the browser too' => 'బ్రౌజర్‌లో కూడా గుర్తు చేయి',
		'Open the saved page' => 'సేవ్ చేసినవి పేజీ తెరువు',
		'Storage is not available in this browser (private mode?) — saving is off.' => 'ఈ బ్రౌజర్‌లో స్టోరేజ్ అందుబాటులో లేదు (ప్రైవేట్ మోడ్?) — సేవ్ ఆఫ్‌లో ఉంది.',
		'Remove all saved posts?' => 'సేవ్ చేసిన పోస్టులన్నీ తొలగించాలా?',
		'All saved posts removed.' => 'సేవ్ చేసిన పోస్టులన్నీ తొలగించాం.',
		'Applied' => 'దరఖాస్తు చేశాను',
		'Interview' => 'ఇంటర్వ్యూ',
		'Application status — tap to change' => 'దరఖాస్తు స్థితి — మార్చడానికి నొక్కండి',
		'No more than 3 links in one comment.' => 'ఒక వ్యాఖ్యలో 3 లింకులకు మించి వద్దు.',
		'Comment rejected' => 'వ్యాఖ్య తిరస్కరించబడింది',
		'Latest Jobs Sliding Track' => 'తాజా ఉద్యోగాల స్లైడర్',
		'Scrolling latest jobs carousel' => 'తాజా ఉద్యోగాల స్క్రోలింగ్ కరోసెల్',
		'Choose slide' => 'స్లైడ్ ఎంచుకోండి',
		'Go to slide %d' => 'స్లైడ్ %d కు వెళ్లు',
		'Close compare panel' => 'పోలిక ప్యానెల్ మూసివేయి',
		'Reminder file downloaded. Add it to your calendar.' => 'రిమైండర్ ఫైల్ డౌన్‌లోడ్ అయింది. మీ క్యాలెండర్‌లో చేర్చండి.',
		'Profile is stored in this browser only — no account, nothing sent to the server.' => 'ప్రొఫైల్ ఈ బ్రౌజర్‌లోనే ఉంటుంది — ఖాతా లేదు, సర్వర్‌కు ఏమీ పంపం.',
		'Set your qualification above — matching jobs appear here instantly.' => 'పైన మీ అర్హత సెట్ చేయండి — సరిపోయే ఉద్యోగాలు వెంటనే ఇక్కడ కనిపిస్తాయి.',
		'Save jobs from any card — your pipeline builds here automatically.' => 'ఏ కార్డ్ నుంచైనా ఉద్యోగాలు సేవ్ చేయండి — మీ పైప్‌లైన్ ఇక్కడ ఆటోమేటిక్‌గా తయారవుతుంది.',
		'Saved jobs with deadlines will show up here, most urgent first.' => 'గడువు ఉన్న సేవ్ చేసిన ఉద్యోగాలు ఇక్కడ కనిపిస్తాయి — అత్యవసరమైనవి ముందు.',
		'Open saved panel' => 'సేవ్ ప్యానెల్ తెరువు',
		'Age & eligibility calculator' => 'వయస్సు & అర్హత కాలిక్యులేటర్',
		'Fee & concession calculator' => 'ఫీజు & రాయితీ కాలిక్యులేటర్',
		'Exam score calculator' => 'పరీక్ష స్కోర్ కాలిక్యులేటర్',
		'Syllabus tracker' => 'సిలబస్ ట్రాకర్',
		'In-hand salary calculator' => 'in-hand జీతం కాలిక్యులేటర్',
		'My workspace' => 'నా వర్క్‌స్పేస్',
		'My Workspace' => 'నా వర్క్‌స్పేస్',
		'Set your profile once — eligible jobs, deadlines and your application status, all in one place.' => 'ప్రొఫైల్ ఒక్కసారి సెట్ చేయండి — అర్హత ఉన్న ఉద్యోగాలు, గడువులు, మీ దరఖాస్తు స్థితి అన్నీ ఒకే చోట.',
		'1 · Your profile' => '1 · మీ ప్రొఫైల్',
		'2 · Application pipeline' => '2 · దరఖాస్తు పైప్‌లైన్',
		'3 · Jobs matched for you' => '3 · మీకు సరిపోయే ఉద్యోగాలు',
		'4 · Deadline radar' => '4 · గడువు రాడార్',
		'Every correction we make is listed here with what changed and when. If you find a mistake, write to us with the page link and we will publish the fix on this page as well.' => 'మేము చేసే ప్రతి సవరణ — ఏం మారింది, ఎప్పుడు — ఇక్కడ జాబితాగా ఉంటుంది. తప్పు కనిపిస్తే పేజీ లింక్‌తో మాకు రాయండి; సవరణను ఈ పేజీలోనూ ప్రచురిస్తాం.',
		'No corrections have been needed so far. When one happens, it will be listed here with the date - we do not silently edit published facts.' => 'ఇప్పటివరకు సవరణలు అవసరం రాలేదు. వచ్చినప్పుడు తేదీతో ఇక్కడ జాబితా చేస్తాం — ప్రచురించిన వాస్తవాలను నిశ్శబ్దంగా మార్చం.',
		'How to report a mistake' => 'తప్పును ఎలా తెలియజేయాలి',
		'Copy the page link (or the headline) that looks wrong.' => 'తప్పుగా అనిపించిన పేజీ లింక్ (లేదా హెడ్‌లైన్) కాపీ చేయండి.',
		'Tell us what the official notification says instead - a screenshot or the official link helps most.' => 'అధికారిక నోటిఫికేషన్ ఏం చెబుతోందో తెలియజేయండి — స్క్రీన్‌షాట్ లేదా అధికారిక లింక్ ఎక్కువగా సహాయపడుతుంది.',
		'Send it to %s. Verified corrections are published within 48 hours.' => '%s కు పంపండి. ధృవీకరించిన సవరణలు 48 గంటల్లో ప్రచురిస్తాం.',
		'Send it to us on WhatsApp or Telegram. Verified corrections are published within 48 hours.' => 'WhatsApp లేదా Telegram లో మాకు పంపండి. ధృవీకరించిన సవరణలు 48 గంటల్లో ప్రచురిస్తాం.',
		'Exam &amp; application calendar 2026' => 'పరీక్షలు &amp; దరఖాస్తుల క్యాలెండర్ 2026',
		'Every last date we have confirmed from an official notification, in one list - sorted by month, with the closing-soon ones first.' => 'అధికారిక నోటిఫికేషన్ నుంచి ధృవీకరించిన ప్రతి చివరి తేదీ ఒకే జాబితాలో — నెల వారీగా, త్వరలో ముగిసేవి ముందు.',
		'Separate offline service · Telangana & Andhra Pradesh · run by the same team that publishes this website' => 'ప్రత్యేక ఆఫ్‌లైన్ సేవ · తెలంగాణ & ఆంధ్రప్రదేశ్ · ఈ వెబ్‌సైట్ నడిపే టీమే నిర్వహిస్తుంది',
		'This is optional.' => 'ఇది ఐచ్ఛికం.',
		'Reading this website, getting job alerts and using every tool here is free. You never need this service to use StudentUp.' => 'ఈ వెబ్‌సైట్ చదవడం, ఉద్యోగ అలర్ట్‌లు పొందడం, ఇక్కడి ప్రతి టూల్ వాడటం ఉచితం. StudentUp వాడటానికి ఈ సేవ ఎప్పుడూ అవసరం లేదు.',
		'Price list (2026)' => 'ధరల జాబితా (2026)',
		'Service' => 'సేవ',
		'What you get' => 'మీకు ఏం లభిస్తుంది',
		'Our service charge' => 'మా సేవా రుసుము',
		'Single application form' => 'ఒక్క దరఖాస్తు ఫారం',
		'One online form filled, checked and returned as a PDF' => 'ఒక ఆన్‌లైన్ ఫారం నింపి, సరిచూసి PDF గా ఇస్తాం',
		'Form + photo &amp; signature formatting' => 'ఫారం + ఫోటో &amp; సంతకం ఫార్మాటింగ్',
		'Form filling plus resizing/renaming of your photo and signature to the official size' => 'ఫారం నింపడంతో పాటు మీ ఫోటో, సంతకాన్ని అధికారిక సైజుకు రీసైజ్/రీనేమ్ చేయడం',
		'Application + document pack' => 'దరఖాస్తు + డాక్యుమెంట్ ప్యాక్',
		'Form, photo/signature work and a single PDF pack of the documents the notification asks for' => 'ఫారం, ఫోటో/సంతకం పని, నోటిఫికేషన్ అడిగిన డాక్యుమెంట్ల ఒకే PDF ప్యాక్',
		'Government application fee, exam fee or any official payment is separate and is never collected by us - you pay the department directly on the official portal.' => 'ప్రభుత్వ దరఖాస్తు ఫీజు, పరీక్ష ఫీజు లేదా ఏ అధికారిక చెల్లింపైనా వేరు — మేము వసూలు చేయం; మీరు అధికారిక పోర్టల్‌లో శాఖకు నేరుగా చెల్లిస్తారు.',
		'Prices are shown here permanently and do not change based on who calls.' => 'ధరలు ఇక్కడ శాశ్వతంగా ఉంటాయి — ఎవరు కాల్ చేసినా మారవు.',
		'What we never do' => 'మేము ఎప్పుడూ చేయనివి',
		'We never promise a job, a rank, a seat or a selection - no one can.' => 'ఉద్యోగం, ర్యాంక్, సీటు లేదా సెలెక్షన్ హామీ ఎప్పుడూ ఇవ్వం — ఎవరూ ఇవ్వలేరు.',
		'We never ask for Aadhaar, PAN, bank details, OTPs or passwords.' => 'ఆధార్, PAN, బ్యాంక్ వివరాలు, OTP లేదా పాస్‌వర్డ్‌లు ఎప్పుడూ అడగం.',
		'We never fill a form with guessed details. If a document is missing, we tell you instead of inventing it.' => 'ఊహించిన వివరాలతో ఫారం ఎప్పుడూ నింపం. డాక్యుమెంట్ లేకపోతే కల్పించకుండా మీకు చెబుతాం.',
		'How it works' => 'ఇది ఎలా పనిచేస్తుంది',
		'Send the job or scholarship name on WhatsApp, and ask for the price before paying.' => 'ఉద్యోగం లేదా స్కాలర్‌షిప్ పేరు WhatsApp లో పంపండి; చెల్లించే ముందు ధర అడగండి.',
		'Send only the documents the notification asks for.' => 'నోటిఫికేషన్ అడిగిన డాక్యుమెంట్లు మాత్రమే పంపండి.',
		'We fill the form, share a draft PDF with you, and submit only after you approve it.' => 'మేము ఫారం నింపి డ్రాఫ్ట్ PDF మీకు పంపుతాం; మీరు ఆమోదించాకే సబ్మిట్ చేస్తాం.',
		'Turnaround: typically the same day, at most 24 hours on working days.' => 'సమయం: సాధారణంగా అదే రోజు; పనిదినాల్లో గరిష్ఠంగా 24 గంటలు.',
		'Cancellation and refund' => 'రద్దు మరియు రీఫండ్',
		'If we cannot submit your application, the service charge is returned in full. If you cancel before we start filling, nothing is charged. Government fees paid on the official portal are between you and the department.' => 'మీ దరఖాస్తు సబ్మిట్ చేయలేకపోతే సేవా రుసుము పూర్తిగా తిరిగి ఇస్తాం. నింపడం మొదలుపెట్టక ముందే రద్దు చేస్తే ఏమీ వసూలు చేయం. అధికారిక పోర్టల్‌లో చెల్లించిన ప్రభుత్వ ఫీజులు మీకు, శాఖకు మధ్య విషయం.',
		'Contact the center' => 'సెంటర్‌ను సంప్రదించండి',
		'WhatsApp the center' => 'సెంటర్‌కు WhatsApp చేయండి',
		'This service is a private offline service. It is not connected to any government department, and paying us gives you no advantage in any selection process.' => 'ఇది ప్రైవేట్ ఆఫ్‌లైన్ సేవ. ఏ ప్రభుత్వ శాఖతోనూ సంబంధం లేదు; మాకు చెల్లించడం వల్ల ఏ ఎంపిక ప్రక్రియలోనూ ప్రయోజనం ఉండదు.',
		'You send' => 'మీరు పంపండి',
		'We verify' => 'మేము ధృవీకరిస్తాం',
		'Send it to us' => 'మాకు పంపండి',
		'Open form' => 'ఫారం తెరువు',
		'Post your news form' => 'మీ వార్త పంపే ఫారం',
		'Send public proof (result, offer letter, official link). Never send Aadhaar, PAN, bank, OTP or passwords.' => 'పబ్లిక్ ఆధారం పంపండి (ఫలితం, ఆఫర్ లెటర్, అధికారిక లింక్). ఆధార్, PAN, బ్యాంక్, OTP లేదా పాస్‌వర్డ్‌లు ఎప్పుడూ పంపకండి.',
		'Recent poll results' => 'ఇటీవలి పోల్ ఫలితాలు',
		'How readers voted this week' => 'ఈ వారం పాఠకులు ఎలా ఓటేశారు',
		'Today\'s Telangana jobs →' => 'ఈరోజు తెలంగాణ ఉద్యోగాలు →',
		'Salaries, age limits, fees, scores, admit cards, resumes and syllabus — official rules batti calculate cheyandi.' => 'జీతాలు, వయో పరిమితులు, ఫీజులు, స్కోర్లు, అడ్మిట్ కార్డులు, రెజ్యూమ్‌లు, సిలబస్ — అధికారిక నిబంధనల ప్రకారం లెక్కించండి.',
		'%d result' => '%d ఫలితం',
		'Sidebar' => 'సైడ్‌బార్',
		'%d dated notifications are open right now.' => 'ప్రస్తుతం %d తేదీ ఉన్న నోటిఫికేషన్లు ఓపెన్‌లో ఉన్నాయి.',
		'%s comments' => '%s వ్యాఖ్యలు',
		'%d results' => '%d ఫలితాలు',
		'Page not found' => 'పేజీ దొరకలేదు',
		'The link may have changed — search below or go to the home page.' => 'లింక్ మారి ఉండవచ్చు — కింద వెతకండి లేదా హోమ్ పేజీకి వెళ్లండి.',
		'Go to home →' => 'హోమ్‌కు వెళ్లండి →',
		'Popular categories' => 'ప్రముఖ విభాగాలు',
		'Back to home' => 'హోమ్‌కు వెనక్కి',
		'Try today’s quiz' => 'ఈరోజు క్విజ్ ఆడండి',
		'updates' => 'అప్‌డేట్లు',
		'Soon' => 'త్వరలో',
		'No posts in this section yet — coming soon.' => 'ఈ విభాగంలో ఇంకా పోస్టులు లేవు — త్వరలో.',
		'Searching…' => 'వెతుకుతోంది…',
		'No posts found — press Enter to see the full search page' => 'పోస్టులు దొరకలేదు — పూర్తి సెర్చ్ పేజీ కోసం Enter నొక్కండి',
		'See all' => 'అన్నీ చూడండి',
		'See all results' => 'అన్ని ఫలితాలు చూడండి',
		'Deadline passed' => 'గడువు ముగిసింది',
		'Closes tomorrow' => 'రేపు ముగుస్తుంది',
		'Deadline is close — check now' => 'గడువు దగ్గరలో ఉంది — ఇప్పుడే చూడండి',
		'Anyone with this qualification can apply' => 'ఈ అర్హత ఉన్న ఎవరైనా దరఖాస్తు చేయవచ్చు',
		'Audio Article Reader' => 'ఆడియో ఆర్టికల్ రీడర్',
		'Listen to audio summary' => 'ఆడియో సారాంశం వినండి',
		'Stop audio' => 'ఆడియో ఆపు',
		// Home / sections.
		'Jobs, scholarships, results and exam updates for students.' => 'విద్యార్థుల కోసం ఉద్యోగాలు, స్కాలర్‌షిప్‌లు, రిజల్ట్స్, పరీక్షల అప్‌డేట్స్.',
		'Spotted a mistake? Tell us at'           => 'తప్పు కనిపించిందా? ఇక్కడ తెలపండి:',
		'Install now'                             => 'ఇప్పుడే ఇన్‌స్టాల్ చేయండి',
		'All active sections'                     => 'అన్ని యాక్టివ్ విభాగాలు',
		'Nothing for this filter — open the "All" tab and try again.' => 'ఈ ఫిల్టర్‌కు పోస్టులు లేవు — "అన్నీ" ట్యాబ్ తెరిచి చూడండి.',
		'Listen to Article'                       => 'ఆర్టికల్ వినండి',
		'Text Size:'                              => 'అక్షర పరిమాణం:',
		'One-tap install · new job alerts direct ga' => 'ఒక్క ట్యాప్ ఇన్‌స్టాల్ · కొత్త జాబ్ అలర్ట్స్ నేరుగా',
		'Your qualification:'                     => 'మీ అర్హత:',
		'All qualifications'                      => 'అన్ని అర్హతలు',
		'Closing in 7 days'                       => '7 రోజుల్లో ముగుస్తున్నవి',
		'Browse by qualification'                 => 'అర్హత వారీగా చూడండి',
		'More practice questions'                 => 'మరిన్ని ప్రాక్టీస్ ప్రశ్నలు',
		'Latest Notifications'                    => 'తాజా నోటిఫికేషన్లు',
		'Latest Jobs'                             => 'తాజా ఉద్యోగాలు',
		'Latest opportunities'                    => 'తాజా అవకాశాలు',
		'Latest opportunities — page %d'          => 'తాజా అవకాశాలు — పేజీ %d',
		'Latest student updates — page %d'        => 'తాజా అప్‌డేట్స్ — పేజీ %d',
		'Latest updates'                          => 'తాజా అప్‌డేట్స్',
		'Latest update'                           => 'తాజా అప్‌డేట్',
		'Latest on StudentUp'                     => 'StudentUp లో తాజా',
		'Closing Soon'                            => 'త్వరలో ముగుస్తున్నవి',
		'Closing soon'                            => 'త్వరలో ముగుస్తున్నవి',
		'Closing this week'                       => 'ఈ వారం ముగుస్తున్నవి',
		'Closing in 3 days'                       => '3 రోజుల్లో ముగుస్తున్నవి',
		'All deadlines'                           => 'అన్ని చివరి తేదీలు',
		'All sections'                            => 'అన్ని విభాగాలు',
		'Explore by Category'                     => 'విభాగాల వారీగా చూడండి',
		'Full details & Apply'                    => 'పూర్తి వివరాలు & Apply',
		'Full details'                            => 'పూర్తి వివరాలు',
		'Full details and official apply link'    => 'పూర్తి వివరాలు + Official Apply link',
		'View details'                            => 'వివరాలు చూడండి',
		'Read more'                               => 'పూర్తి వివరాలు',
		'Read next'                               => 'తర్వాత చదవండి',
		'Up next'                                 => 'తర్వాత',
		'Up next — read this too'                 => 'తర్వాత చదవండి — ఇవి కూడా',
		'Recent articles'                         => 'తాజా ఆర్టికల్స్',
		'Related sections'                        => 'సంబంధిత విభాగాలు',
		'%s updates' => '%s అప్‌డేట్స్',
		'More updates:'                           => 'మరిన్ని అప్‌డేట్స్:',
		'More %s'                                 => 'మరిన్ని %s',
		'More'                                    => 'మరిన్ని',
		'Updates today'                           => 'ఈరోజు అప్‌డేట్స్',
		'Updates — %s'                            => 'అప్‌డేట్స్ — %s',
		'%d update posted today'                  => 'ఈరోజు %d అప్‌డేట్',
		'%d updates posted today'                 => 'ఈరోజు %d అప్‌డేట్స్',
		'New notifications are added every day.'  => 'ప్రతిరోజూ కొత్త నోటిఫికేషన్లు జోడిస్తాం.',
		'New notifications are added every day. Meanwhile:' => 'ప్రతిరోజూ కొత్త నోటిఫికేషన్లు జోడిస్తాం. ఈలోగా:',
		'No matching posts yet — relax the filters or check back after the next update.' => 'ఈ ఫిల్టర్‌కు పోస్టులు లేవు — ఫిల్టర్ మార్చండి లేదా తర్వాత అప్‌డేట్ తర్వాత చూడండి.',
		'Government Jobs, Results & Notifications' => 'ప్రభుత్వ ఉద్యోగాలు, Results & నోటిఫికేషన్లు',
		'Search StudentUp'                        => 'StudentUp లో వెతకండి',
		'Search StudentUp — jobs, hall tickets, results…' => 'ఉద్యోగం, హాల్ టికెట్, రిజల్ట్ వెతకండి…',
		'Search'                                  => 'వెతకండి',
		'Press / to search'                       => 'వెతకడానికి / నొక్కండి',
		'Results for “%s”'                        => '“%s” కోసం ఫలితాలు',
		'Did you mean'                            => 'మీ ఉద్దేశం ఇదేనా',
		'No exact match.'                         => 'సరిగ్గా సరిపోయే ఫలితం లేదు.',
		'Closest matches'                         => 'దగ్గరి ఫలితాలు',
		'Suggestions'                             => 'సూచనలు',
		'Page %d'                                 => 'పేజీ %d',
		'Pages'                                   => 'పేజీలు',
		'Posts'                                   => 'పోస్టులు',
		'posts'                                   => 'పోస్టులు',
		'%s Posts'                                => '%s పోస్టులు',
		'Home'                                    => 'హోమ్',
		'Jobs'                                    => 'ఉద్యోగాలు',
		'Scholarships'                            => 'స్కాలర్‌షిప్‌లు',
		'Scholarship'                             => 'స్కాలర్‌షిప్',
		'Scholarship'                             => 'స్కాలర్‌షిప్',
		'Alerts'                                  => 'అలర్ట్స్',
		'News'                                    => 'వార్తలు',
		'Exams'                                   => 'పరీక్షలు',
		'Categories'                              => 'విభాగాలు',
		'Other links'                             => 'ఇతర లింకులు',
		'Exams & More'                            => 'పరీక్షలు & మరిన్ని',
		'Upcoming Exams'                          => 'రాబోయే పరీక్షలు',
		// Deadlines.
		'%d days left'                            => '%d రోజులు మిగిలాయి',
		'Only %d days left'                       => 'ఇంకా %d రోజులే',
		'1 day left'                              => '1 రోజు మిగిలింది',
		'days left'                               => 'రోజులు మిగిలాయి',
		'%s Day Left'                             => '%s రోజు మిగిలింది',
		'%s Days Left'                            => '%s రోజులు మిగిలాయి',
		'Last date'                               => 'చివరి తేదీ',
		'Last date:'                              => 'చివరి తేదీ:',
		'Last date today'                         => 'ఈరోజే చివరి తేదీ',
		'Last day today'                          => 'ఈరోజే చివరి రోజు',
		'Last day'                                => 'చివరి రోజు',
		'Last date over'                          => 'చివరి తేదీ ముగిసింది',
		'Closes today'                            => 'ఈరోజే ముగుస్తుంది',
		'Closed'                                  => 'ముగిసింది',
		'Application window closed'               => 'దరఖాస్తు గడువు ముగిసింది',
		'Apply today - last date tomorrow'        => 'ఈరోజే దరఖాస్తు చేయండి — రేపే చివరి తేదీ',
		'Deadline'                                => 'చివరి తేదీ',
		'Deadlines'                               => 'చివరి తేదీలు',
		'Key details'                             => 'ముఖ్య వివరాలు',
		'Vacancies'                               => 'ఖాళీలు',
		'Qualification'                           => 'అర్హత',
		'Eligibility'                             => 'అర్హత',
		'Age'                                     => 'వయస్సు',
		'Age limit'                               => 'వయోపరిమితి',
		'Fee'                                     => 'ఫీజు',
		'Salary'                                  => 'జీతం',
		'Pay'                                     => 'జీతం',
		'Result'                                  => 'Result',
		'State'                                   => 'రాష్ట్రం',
		'Telangana'                               => 'తెలంగాణ',
		'Andhra Pradesh'                          => 'ఆంధ్రప్రదేశ్',
		'Central'                                 => 'కేంద్రం',
		'All states'                              => 'అన్ని రాష్ట్రాలు',
		'Any qualification'                       => 'ఏ అర్హత అయినా',
		'NEW'                                     => 'కొత్త',
		'New'                                     => 'కొత్త',
		'LIVE'                                    => 'LIVE',
		// Post page.
		'Share this with your friends'            => 'మీ స్నేహితులకు షేర్ చేయండి',
		'Share'                                   => 'షేర్',
		'Share on WhatsApp'                       => 'WhatsApp లో షేర్ చేయండి',
		'Copy link'                               => 'లింక్ కాపీ',
		'Save'                                    => 'సేవ్',
		'Saved'                                   => 'సేవ్ అయింది',
		'Saved posts'                             => 'సేవ్ చేసిన పోస్టులు',
		'Save this post for later'                => 'తర్వాత చదవడానికి సేవ్ చేయండి',
		'Remove this post from saved'             => 'సేవ్ నుంచి తీసేయండి',
		'Removed from saved'                      => 'సేవ్ నుంచి తీసేశాం',
		'Post saved — open the Saved panel any time to read it later.' => 'సేవ్ అయింది — Saved ప్యానెల్ లో ఎప్పుడైనా చదవండి.',
		'No saved posts yet. Tap Save on any card to keep it here.' => 'ఇంకా సేవ్ చేసిన పోస్టులు లేవు. ఏ కార్డ్ లోనైనా సేవ్ నొక్కండి.',
		'No saved posts yet. Open any post and tap Save.' => 'ఇంకా సేవ్ చేసిన పోస్టులు లేవు. ఏ పోస్ట్ లోనైనా సేవ్ నొక్కండి.',
		'No saved posts yet. Open any post and tap the Save button.' => 'ఇంకా సేవ్ చేసిన పోస్టులు లేవు. ఏ పోస్ట్ లోనైనా సేవ్ బటన్ నొక్కండి.',
		'View saved here'                         => 'సేవ్ చేసినవి ఇక్కడ చూడండి',
		'Clear all'                               => 'అన్నీ తీసేయండి',
		'Clear'                                   => 'క్లియర్',
		'Compare'                                 => 'పోల్చండి',
		'Compare posts'                           => 'పోస్టులను పోల్చండి',
		'Compare up to three posts.'              => 'గరిష్ఠంగా 3 పోస్టులు పోల్చవచ్చు.',
		'Add this post to compare'                => 'పోల్చడానికి జోడించండి',
		'Added'                                   => 'జోడించారు',
		'Open comparison'                         => 'పోలిక చూడండి',
		'Select at least two posts to compare.'   => 'పోల్చడానికి కనీసం 2 పోస్టులు ఎంచుకోండి.',
		'Important Links'                         => 'ముఖ్యమైన లింకులు',
		'Apply Online (Official)'                 => 'అధికారిక అప్లై లింక్',
		'Apply online'                            => 'అప్లై చేయండి',
		'Download Hall Ticket'                    => 'హాల్ టికెట్ డౌన్‌లోడ్',
		'View Result'                             => 'రిజల్ట్ చూడండి',
		'Open Official Portal'                    => 'అధికారిక పోర్టల్ తెరవండి',
		'Official Website'                        => 'అధికారిక వెబ్‌సైట్',
		'Official Notification'                   => 'అధికారిక నోటిఫికేషన్',
		'Official Notification (PDF)'             => 'అధికారిక నోటిఫికేషన్ (PDF)',
		'Click Here'                              => 'తెరవండి',
		'Apply Now'                               => 'దరఖాస్తు చేయండి',
		'Job alerts on Telegram'                  => 'Telegram లో జాబ్ అలర్ట్స్',
		'Doubts & Answers'                        => 'సందేహాలు & సమాధానాలు',
		'No questions yet. Ask the first one — we answer with the official source.' => 'ఇంకా ప్రశ్నలు లేవు. మొదటి ప్రశ్న మీరే అడగండి — official source ఆధారంగా సమాధానం ఇస్తాం.',
		'Your question (Telugu or English)'       => 'మీ ప్రశ్న (తెలుగు లేదా English)',
		'Your name (optional)'                    => 'మీ పేరు (ఐచ్ఛికం)',
		'Ask question'                            => 'ప్రశ్న పంపండి',
		'Reviewed before publishing. No links, emails or phone numbers.' => 'ప్రచురణకు ముందు పరిశీలిస్తాం. లింకులు, ఈమెయిల్, ఫోన్ నంబర్లు వద్దు.',
		'Thanks! Your question is waiting for review — the answer will appear on this page.' => 'ధన్యవాదాలు! మీ ప్రశ్న పరిశీలనలో ఉంది — సమాధానం ఈ పేజీలో కనిపిస్తుంది.',
		'Thanks! Your question is waiting for review.' => 'ధన్యవాదాలు! మీ ప్రశ్న పరిశీలనలో ఉంది.',
		'This question is already asked — the answer will appear here.' => 'ఈ ప్రశ్న ఇప్పటికే అడిగారు — సమాధానం ఇక్కడ కనిపిస్తుంది.',
		'Answer coming soon — our editor is verifying it.' => 'సమాధానం త్వరలో — మా ఎడిటర్ ధృవీకరిస్తున్నారు.',
		'Please write your question in a few more words.' => 'ప్రశ్నను ఇంకొన్ని పదాల్లో రాయండి.',
		'Please keep the question under 600 characters.' => 'ప్రశ్న 600 అక్షరాల లోపు ఉండాలి.',
		'Links, emails and phone numbers are not allowed in questions.' => 'ప్రశ్నలో లింకులు, ఈమెయిల్, ఫోన్ నంబర్లు అనుమతించం.',
		'Please wait a minute before asking again.' => 'మళ్లీ అడగడానికి ఒక నిమిషం ఆగండి.',
		'Questions are closed right now.'         => 'ప్రస్తుతం ప్రశ్నలు స్వీకరించడం లేదు.',
		'Write your comment'                      => 'మీ కామెంట్ రాయండి',
		'Post comment'                            => 'కామెంట్ పంపండి',
		'Comment'                                 => 'కామెంట్',
		'Comments are closed.'                    => 'కామెంట్లు మూసివేయబడ్డాయి.',
		'Updated on'                              => 'అప్‌డేట్ చేసినది',
		'Updated:'                                => 'అప్‌డేట్:',
		'Sources verified:'                       => 'ధృవీకరించిన మూలాలు:',
		'Save this notification as PDF'           => 'ఈ నోటిఫికేషన్‌ను PDF గా సేవ్ చేయండి',
		'Uses your browser print dialog - choose "Save as PDF".' => 'బ్రౌజర్ ప్రింట్ విండోలో "Save as PDF" ఎంచుకోండి.',
		'Print / PDF'                             => 'ప్రింట్ / PDF',
		'Print or save this article as PDF'       => 'ఈ ఆర్టికల్‌ను ప్రింట్ చేయండి లేదా PDF గా సేవ్ చేయండి',
		'Add last date to my calendar'            => 'చివరి తేదీని నా క్యాలెండర్‌కు జోడించు',
		'Recently read'                           => 'ఇటీవల చదివినవి',
		'Recommended'                             => 'సిఫార్సు',
		'Eligible for you'                        => 'మీకు అర్హత ఉన్నవి',
		'Eligible by age'                         => 'వయస్సు ప్రకారం అర్హత',
		'Partly eligible — check details'         => 'పాక్షిక అర్హత — వివరాలు చూడండి',
		// Quiz.
		'Daily quiz'                              => 'డైలీ క్విజ్',
		'Restart' => 'మళ్లీ మొదలు',
		'Check answers' => 'సమాధానాలు చూడండి',
		'Share my score' => 'నా స్కోర్ షేర్ చేయండి',
		'Previous' => 'వెనుకకు',
		'Next question' => 'తర్వాత ప్రశ్న',
		'See result' => 'ఫలితం చూడండి',
		'Jump to question' => 'ప్రశ్నకు వెళ్లండి',
		'Question %1$d of %2$d' => 'ప్రశ్న %1$d / %2$d',
		'Your 5 today'                            => 'ఈరోజు మీ 5 ప్రశ్నలు',
		'Table of contents' => 'విషయ సూచిక',
		'This article was checked against official sources and written in simple language. If you spot a mistake, %s — we correct it within 24 hours. Always confirm deadlines and numbers in the official notification.' => 'ఈ ఆర్టికల్‌ను అధికారిక మూలాలతో సరిచూసి, సులభమైన భాషలో రాశాం. తప్పు కనిపిస్తే %s కు తెలపండి — 24 గంటల్లో సరిదిద్దుతాం. చివరి తేదీలు, సంఖ్యలు అధికారిక నోటిఫికేషన్‌లో తప్పక నిర్ధారించుకోండి.',
		'Senior Education Editor · 5+ Years of Experience' => 'సీనియర్ ఎడ్యుకేషన్ ఎడిటర్ · 5+ సంవత్సరాల అనుభవం',
		'Charan Pendota is a senior content editor and digital career researcher with 5+ years of experience in Telugu job notifications, exam patterns, and career guidance. At StudentUp, he leads the fact-checking desk, ensuring 100% source-verified information for Telangana and Andhra Pradesh students.' => 'చరణ్ పెండోట తెలుగు ఉద్యోగ నోటిఫికేషన్లు, పరీక్షా విధానాలు, కెరీర్ గైడెన్స్‌లో 5+ సంవత్సరాల అనుభవం ఉన్న సీనియర్ కంటెంట్ ఎడిటర్. StudentUp లో ఫ్యాక్ట్-చెక్ డెస్క్‌ను నడిపిస్తూ, తెలంగాణ, ఆంధ్రప్రదేశ్ విద్యార్థులకు అధికారిక మూలాల ఆధారంగా సమాచారం అందిస్తారు.',
		'Reviewed:' => 'సమీక్షించినది:',
		'Contact Email' => 'ఈమెయిల్',
		'Editorial policy' => 'ఎడిటోరియల్ పాలసీ',
		'Report mistakes' => 'తప్పులు తెలపండి',
		'Channel' => 'ఛానల్',
		'TS Govt Jobs' => 'TS ప్రభుత్వ ఉద్యోగాలు',
		'AP Govt Jobs' => 'AP ప్రభుత్వ ఉద్యోగాలు',
		'Central Jobs' => 'కేంద్ర ఉద్యోగాలు',
		'Software Jobs' => 'సాఫ్ట్‌వేర్ జాబ్స్',
		'Private Jobs' => 'ప్రైవేట్ జాబ్స్',
		'Hall Tickets' => 'హాల్ టికెట్స్',
		'Results' => 'రిజల్ట్స్',
		'Walk-in Jobs' => 'వాక్-ఇన్ జాబ్స్',
		'Internships' => 'ఇంటర్న్‌షిప్స్',
		'Success Stories' => 'సక్సెస్ స్టోరీస్',
		'Current Affairs' => 'కరెంట్ అఫైర్స్',
		'Daily Quiz' => 'డైలీ క్విజ్',
		'Live Exams' => 'లైవ్ ఎగ్జామ్స్',
		'Search job / exam / result…' => 'ఉద్యోగం / పరీక్ష / రిజల్ట్ వెతకండి…',
		'Why:'                                    => 'ఎందుకంటే:',
		'Reader poll'                             => 'రీడర్ పోల్',
		'READER POLL'                             => 'రీడర్ పోల్',
		'DAILY QUIZ'                              => 'డైలీ క్విజ్',
		'Vote'                                    => 'ఓటు వేయండి',
		'Thanks — your vote is counted.'          => 'ధన్యవాదాలు — మీ ఓటు నమోదైంది.',
		'Be the first to vote — results show as soon as people answer.' => 'మొదటి ఓటు మీదే — సమాధానాలు రాగానే ఫలితాలు కనిపిస్తాయి.',
		'%s readers voted — tap an option to see live results.' => '%s మంది ఓటు వేశారు — ఫలితాల కోసం ఒక ఆప్షన్ నొక్కండి.',
		'Strong — keep this streak alive tomorrow.' => 'అద్భుతం — రేపు కూడా ఈ స్ట్రీక్ కొనసాగించండి.',
		'Decent start. Read the "why" lines once and retry.' => 'మంచి ప్రారంభం. "ఎందుకంటే" వివరణలు చదివి మళ్లీ ప్రయత్నించండి.',
		'No problem — practice is the point. Try again tomorrow.' => 'పర్వాలేదు — ప్రాక్టీసే ముఖ్యం. రేపు మళ్లీ ప్రయత్నించండి.',
		'Other days'                              => 'ఇతర రోజులు',
		'Daily current affairs →'                 => 'డైలీ కరెంట్ అఫైర్స్ →',
		// Post your news.
		'Post your news'                          => 'మీ వార్త పంపండి',
		'Success story'                           => 'సక్సెస్ స్టోరీ',
		'Photo / Video'                           => 'ఫోటో / వీడియో',
		'District update'                         => 'జిల్లా అప్‌డేట్',
		'Send now'                                => 'ఇప్పుడే పంపండి',
		'We post with your name'                  => 'మీ పేరుతో పోస్ట్ చేస్తాం',
		'We review every submission. Approved stories are posted by the StudentUp team with your name (or anonymous, if you ask).' => 'ప్రతి సబ్మిషన్ పరిశీలిస్తాం. ఆమోదించిన కథనాలు మీ పేరుతో (కోరితే పేరు లేకుండా) StudentUp టీమ్ పోస్ట్ చేస్తుంది.',
		'Approved stories'                        => 'ఆమోదించిన కథనాలు',
		'All stories →'                           => 'అన్ని కథనాలు →',
		// Join / alerts / footer.
		'Every job, exam date and result — first on your phone' => 'ప్రతి ఉద్యోగం, పరీక్ష తేదీ, రిజల్ట్ — ముందుగా మీ ఫోన్‌లో',
		'Free job alerts on your phone'           => 'మీ ఫోన్‌లో ఉచిత జాబ్ అలర్ట్స్',
		'Jobs · results · hall tickets — first on WhatsApp / Telegram.' => 'Jobs · Results · Hall Tickets — ముందుగా WhatsApp / Telegram లో.',
		'Join WhatsApp'                           => 'WhatsApp లో జాయిన్',
		'Join Telegram'                           => 'Telegram లో జాయిన్',
		'Join our Telegram channel'               => 'మా Telegram ఛానల్‌లో జాయిన్ అవ్వండి',
		'Join our channels'                       => 'మా ఛానల్స్‌లో జాయిన్ అవ్వండి',
		'WhatsApp updates'                        => 'WhatsApp అప్‌డేట్స్',
		'Telegram channel'                        => 'Telegram ఛానల్',
		'Live job alerts'                         => 'లైవ్ జాబ్ అలర్ట్స్',
		'Daily updates free ga — join avvandi.'   => 'రోజూ ఉచిత అప్‌డేట్స్ — జాయిన్ అవ్వండి.',
		'Follow us'                               => 'మమ్మల్ని ఫాలో అవ్వండి',
		'Corrections'                             => 'సవరణలు',
		'Corrections &amp; updates'               => 'సవరణలు &amp; అప్‌డేట్స్',
		'Install'                                 => 'ఇన్‌స్టాల్',
		'Close'                                   => 'మూసివేయి',
		'Dismiss'                                 => 'తీసేయి',
		'Hide social icons'                       => 'సోషల్ ఐకాన్లు దాచు',
		'Show social icons'                       => 'సోషల్ ఐకాన్లు చూపు',
		'Swipe sideways for more'                 => 'మరిన్నింటికి పక్కకు స్వైప్ చేయండి',
		'Scroll left'                             => 'ఎడమకు',
		'Scroll right'                            => 'కుడికి',
		'Slide Left'                              => 'ఎడమకు',
		'Slide Right'                             => 'కుడికి',
		// Archive / tools misc.
		'Active jobs board'                       => 'యాక్టివ్ జాబ్స్ బోర్డ్',
		'Government job & exam last dates'        => 'ప్రభుత్వ ఉద్యోగ & పరీక్షల చివరి తేదీలు',
		'Last dates from the official notifications' => 'Official నోటిఫికేషన్ల ప్రకారం చివరి తేదీలు',
		'Every last date from official notifications — never guessed.' => 'ప్రతి చివరి తేదీ official నోటిఫికేషన్ నుంచే — ఊహించినవి కావు.',
		'No confirmed date is available for this post.' => 'ఈ పోస్ట్‌కు ధృవీకరించిన తేదీ లేదు.',
		'Quick tools'                             => 'క్విక్ టూల్స్',
		'Student tools'                           => 'విద్యార్థి టూల్స్',
		'Free tools for students'                 => 'విద్యార్థులకు ఉచిత టూల్స్',
		'Breaking News'                           => 'బ్రేకింగ్ న్యూస్',
		'Open Breaking News'                      => 'బ్రేకింగ్ న్యూస్ చూడండి',
		'District-wise news'                      => 'జిల్లాల వారీగా వార్తలు',
		'Telangana · Andhra Pradesh district news' => 'తెలంగాణ · ఆంధ్రప్రదేశ్ జిల్లా వార్తలు',
		'Latest story'                            => 'తాజా కథనం',
		'Students Internet Center'                => 'స్టూడెంట్స్ ఇంటర్నెట్ సెంటర్',
		'Open today'                              => 'ఈరోజు తెరిచి ఉంది',
		'Call now'                                => 'కాల్ చేయండి',
		'Call'                                    => 'కాల్',
		'Email'                                   => 'ఈమెయిల్',
		'Read our editorial policy'               => 'మా ఎడిటోరియల్ పాలసీ చదవండి',
		'Every post links the official source so you can check it yourself.' => 'ప్రతి పోస్ట్ అధికారిక మూలానికి లింక్ ఇస్తుంది — మీరే సరిచూసుకోవచ్చు.',
	);
	return $map;
}

/**
 * gettext filter — 'studentup' domain only.
 */
/**
 * 1.9.150 — NAVIGATION IN ENGLISH (owner, v364): category tiles, header/mega
 * menu, phone drawer, bottom nav, hero links and category names stay English;
 * article content and section UI stay Telugu. Option `nav_english` (default ON).
 */
function studentup_nav_english() {
	static $on = null;
	if ( null === $on ) {
		$on = ! is_admin() && function_exists( 'studentup_opt' ) && (bool) studentup_opt( 'nav_english', '1' );
	}
	return $on;
}

/** Strings that belong to navigation chrome (kept English when nav_english is ON). */
function studentup_nav_strings() {
	static $set = null;
	if ( null === $set ) {
		$set = array_fill_keys( array(
			'Home', 'Jobs', 'Scholarship', 'Scholarships', 'Alerts', 'Search', 'Menu', 'Main menu', 'Close menu',
			'Explore by Category', 'All sections', 'Breaking News', 'Latest Jobs', 'Today’s updates',
			'TS Govt Jobs', 'AP Govt Jobs', 'Central Jobs', 'Central Govt Jobs', 'Software Jobs', 'Private Jobs',
			'Hall Tickets', 'Results', 'Daily Quiz', 'Live Exams', 'Walk-in Jobs', 'Internships', 'Success Stories',
			'Current Affairs', 'Admissions', 'Telangana Jobs', 'AP Jobs', 'Telangana News', 'Andhra Pradesh News',
			'Exam Calendar', 'Compare Jobs', 'Saved', 'Post Your News', 'About', 'Contact', 'Privacy Policy',
			'Daily Quiz & Polls', 'Corrections & Updates', 'Exam & Application Calendar', 'Download App', 'All', 'WEB APP', 'Follow us', 'Exams & More', 'Upcoming Exams', 'Govt Schemes', 'Install', 'StudentUp App', 'New', 'NEW', 'Categories', 'Other links', 'About us', 'About Us', 'Contact', 'Contact Us', 'Privacy policy', 'Disclaimer', 'Terms', 'Terms & Conditions', 'Editorial policy', 'Editorial Policy', 'Post your news', 'Corrections', 'Sitemap',
		), true );
	}
	return $set;
}

function studentup_ui_gettext( $translation, $text, $domain ) {
	if ( 'studentup' !== $domain || is_admin() ) {
		return $translation;
	}
	if ( ! function_exists( 'studentup_opt' ) || ! studentup_opt( 'ui_telugu', '1' ) ) {
		return $translation;
	}
	if ( studentup_nav_english() && isset( studentup_nav_strings()[ $text ] ) ) {
		return $text;
	}
	$map = studentup_ui_te_map();
	return isset( $map[ $text ] ) ? $map[ $text ] : $translation;
}
add_filter( 'gettext', 'studentup_ui_gettext', 10, 3 );

/**
 * ngettext filter — plural forms (days left, posts, updates today).
 */
function studentup_ui_ngettext( $translation, $single, $plural, $number, $domain ) {
	if ( 'studentup' !== $domain || is_admin() ) {
		return $translation;
	}
	if ( ! function_exists( 'studentup_opt' ) || ! studentup_opt( 'ui_telugu', '1' ) ) {
		return $translation;
	}
	$map = studentup_ui_te_map();
	$key = ( 1 === (int) $number ) ? $single : $plural;
	return isset( $map[ $key ] ) ? $map[ $key ] : $translation;
}
add_filter( 'ngettext', 'studentup_ui_ngettext', 10, 5 );

/**
 * Core WordPress strings that leak into the front end (comment form etc.).
 */
function studentup_ui_core_gettext( $translation, $text, $domain ) {
	if ( 'default' !== $domain || is_admin() ) {
		return $translation;
	}
	if ( ! function_exists( 'studentup_opt' ) || ! studentup_opt( 'ui_telugu', '1' ) ) {
		return $translation;
	}
	static $core = array(
		'Leave a Reply'       => 'మీ కామెంట్ రాయండి',
		'Post Comment'        => 'కామెంట్ పంపండి',
		'Cancel reply'        => 'రద్దు చేయండి',
		'Name'                => 'పేరు',
		'Website'             => 'వెబ్‌సైట్',
		'Save my name, email, and website in this browser for the next time I comment.' => 'తదుపరి కామెంట్ కోసం నా పేరు, ఈమెయిల్ ఈ బ్రౌజర్‌లో సేవ్ చేయండి.',
		'Older posts'         => 'పాత పోస్టులు',
		'Newer posts'         => 'కొత్త పోస్టులు',
		'Search for:'         => 'వెతకండి:',
		'Nothing Found'       => 'ఏమీ దొరకలేదు',
		'Skip to content'     => 'కంటెంట్‌కు వెళ్లండి',
	);
	return isset( $core[ $text ] ) ? $core[ $text ] : $translation;
}
add_filter( 'gettext', 'studentup_ui_core_gettext', 10, 3 );

/**
 * v1.9.144 — Category/tag names and nav-menu titles are site data (English on
 * live), not gettext strings. Front-end display passes them through the same
 * map so cards, breadcrumbs, meta lines and footer menus read in Telugu.
 */
function studentup_ui_te_label( $text ) {
	if ( is_admin() || ! function_exists( 'studentup_opt' ) || ! studentup_opt( 'ui_telugu', '1' ) ) {
		return $text;
	}
	$map = studentup_ui_te_map();
	$key = trim( (string) $text );
	return isset( $map[ $key ] ) ? $map[ $key ] : $text;
}

function studentup_ui_te_term( $term ) {
	if ( is_admin() || ! ( $term instanceof WP_Term ) || studentup_nav_english() ) {
		return $term;
	}
	if ( in_array( $term->taxonomy, array( 'category', 'post_tag' ), true ) ) {
		$term->name = studentup_ui_te_label( $term->name );
	}
	return $term;
}
add_filter( 'get_term', 'studentup_ui_te_term', 20 );

function studentup_ui_te_menu_items( $items ) {
	if ( studentup_nav_english() ) {
		return $items;
	}
	if ( is_admin() || ! is_array( $items ) ) {
		return $items;
	}
	foreach ( $items as $it ) {
		if ( isset( $it->title ) ) {
			$it->title = studentup_ui_te_label( $it->title );
		}
	}
	return $items;
}
add_filter( 'wp_nav_menu_objects', 'studentup_ui_te_menu_items', 5 );
add_filter( 'wp_get_nav_menu_items', 'studentup_ui_te_menu_items', 5 );

/**
 * Dates: "October 18, 2026" → "అక్టోబర్ 18, 2026" (month names only; numbers stay).
 */
function studentup_ui_te_date( $date, $format = '' ) {
	if ( '' === (string) $format ) {
		$format = (string) get_option( 'date_format', 'F j, Y' );
	}
	if ( is_admin() || ! is_string( $date ) || ! preg_match( '/[FM]/', (string) $format ) ) {
		return $date;
	}
	if ( ! function_exists( 'studentup_opt' ) || ! studentup_opt( 'ui_telugu', '1' ) ) {
		return $date;
	}
	$map = studentup_ui_te_map();
	return preg_replace_callback( '/\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/', function ( $m ) use ( $map ) {
		return isset( $map[ $m[1] ] ) ? $map[ $m[1] ] : $m[1];
	}, $date );
}
add_filter( 'get_the_date', 'studentup_ui_te_date', 10, 2 );
add_filter( 'get_the_modified_date', 'studentup_ui_te_date', 10, 2 );
add_filter( 'date_i18n', 'studentup_ui_te_date', 10, 2 );

/**
 * 1.9.149 — setup pages are created with English titles ("Daily Quiz & Polls",
 * "Post Your News"); the front end must show them in Telugu like every other
 * label. Pages only (posts keep their own titles), front end only.
 */
function studentup_ui_te_page_title( $title, $post_id = 0 ) {
	if ( $post_id instanceof WP_Post ) {
		$post_id = $post_id->ID;
	}
	if ( studentup_nav_english() ) {
		return $title; // page titles are navigation (menus, footer, crumbs) → English.
	}
	if ( is_admin() || ! $post_id || 'page' !== get_post_type( $post_id ) ) {
		return $title;
	}
	return studentup_ui_te_label( $title );
}
add_filter( 'the_title', 'studentup_ui_te_page_title', 10, 2 );
add_filter( 'single_post_title', 'studentup_ui_te_page_title', 10, 2 );

/**
 * 1.9.153 — raw ISO dates inside post text ("2026-10-21") read like database
 * output. Render them as "21 అక్టోబర్ 2026" in text nodes only (never inside
 * tags/attributes, scripts, styles, code). Invalid dates are left untouched.
 */
function studentup_ui_te_iso_dates( $html ) {
	if ( is_admin() || ! is_string( $html ) || false === strpos( $html, '20' ) ) {
		return $html;
	}
	if ( ! function_exists( 'studentup_opt' ) || ! studentup_opt( 'ui_telugu', '1' ) ) {
		return $html;
	}
	$months = array( 'జనవరి', 'ఫిబ్రవరి', 'మార్చి', 'ఏప్రిల్', 'మే', 'జూన్', 'జులై', 'ఆగస్టు', 'సెప్టెంబర్', 'అక్టోబర్', 'నవంబర్', 'డిసెంబర్' );
	$parts  = preg_split( '/(<(?:script|style|code|pre|a)\b[^>]*>.*?<\/(?:script|style|code|pre|a)>|<[^>]+>)/is', $html, -1, PREG_SPLIT_DELIM_CAPTURE );
	foreach ( $parts as $i => $chunk ) {
		if ( '' === $chunk || '<' === $chunk[0] ) {
			continue;
		}
		$parts[ $i ] = preg_replace_callback( '/(?<![\d\/\-])(20\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(?![\d\/\-:])/', function ( $m ) use ( $months ) {
			if ( ! checkdate( (int) $m[2], (int) $m[3], (int) $m[1] ) ) {
				return $m[0];
			}
			return (int) $m[3] . ' ' . $months[ (int) $m[2] - 1 ] . ' ' . $m[1];
		}, $chunk );
	}
	return implode( '', $parts );
}
add_filter( 'the_content', 'studentup_ui_te_iso_dates', 11 );
