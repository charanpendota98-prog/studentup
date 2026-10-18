# v360 — 100× deep audit plan (theme 1.9.146 + bot)

Method: real WordPress 6.7.1 rig (SQLite + Rank Math) + headless Chromium, 10 URLs × phone/laptop.
New dimensions this round: CSS/JS coverage, CLS/LCP, color contrast (WCAG AA), keyboard focus (real Tab
presses), landmarks/skip link, HTML nesting, schema required fields, 404 / empty search / pagination,
manifest/PWA meta, external-link rel. Bot: gate stress-tested with two deliberately bad articles.

## What is already right (verified, no change)
- Structure: 1 h1, no heading skips, landmarks (header/main/nav×5-7 all aria-labelled/footer), skip link
  target exists, 0 positive tabindex, 0 button-in-link, 0 block-in-p, 0 images without dims/alt, no eager
  images below fold, manifest + theme-color + apple-touch-icon, canonical self, noindex on search/404.
- Keyboard focus: 40 Tab presses on phone → every focused element has a visible outline (global
  `:focus-visible` rule works). The "43/80 no focus style" number from scripted `.focus()` was a false alarm.
- CLS 0.006–0.011 everywhere except desktop /daily-quiz/ (0.083 — still "good", see T6).
- Footer contrast flags were false positives (gradient background not read by the probe); real ratios ≥7:1.

## Theme defects found → fixes (T)
| # | Finding (evidence) | Fix |
|---|---|---|
| T1 | `--muted:#64748b` text on light panels = 4.4:1 (`small`, TIME, "/ 5", doubt hint); `.su-rb-time #94a3b8` 2.4:1; `.su-rb-label` 3.8:1; `.su-op-updated #718096` 4.0:1; mobile-menu social rows white-on-WhatsApp-green 2.0:1 | darken tokens (`--muted:#596577` ≈5.6:1), rb/op colours, darker brand backgrounds for `.su-msoc` rows |
| T2 | Schema: `Organization` node without `url`/`logo`; `NewsArticle`/`Article` without `image` when post has no featured image | add `url` + logo fallback (site icon → theme default OG image); image fallback to default OG image |
| T3 | Same anchor text, different targets ("పూర్తి వివరాలు →", "షేర్") on every card — screen-reader users hear identical links | `aria-label` = post title + action |
| T4 | Two `href="#"` links (`.su-msaved`, `.su-install-cta`) | `role="button"` on both + `aria-controls`; keep markup otherwise |
| T5 | 4 render-blocking sync scripts on home (`engage`, `status`, `menu`, `slider`) | WP `strategy => defer` where no inline-after script depends on them |
| T6 | Desktop /daily-quiz/ CLS 0.083 — stepper hides questions 2-5 after JS runs | CSS pre-hides non-active steps when JS is on (`html.js`) so no shift |
| T7 | CSS: 416 KB over 4 blocking files, 9–21 % used per page | measured only — async CSS failed on live (v296) and purging risks bot-generated post markup; reported, not changed |

## Bot defects found → fixes (B)
Stress article #2 (Tenglish title, English H2s, placeholders, dup sentences, hype, bad FAQ answers,
`15/01/2025`, English meta, wrong category) — these passed the gate and now fail:
| # | Slipped through | Fix |
|---|---|---|
| B1 | `[Insert … here]`, `XXXX`, `TBD`, `N/A`, `{{telegram_link}}`, "AI సహాయంతో రాయబడింది" | `no_dev_text` patterns + regex (critical) |
| B2 | Title "… Telugu lo – Complete Details Guide 2026" | `no_guide_suffix` adds `telugu lo`, `details guide`, `in telugu lo`, trailing `guide YYYY` |
| B3 | H2 "Eligibility Criteria", "How to Apply Online" (3+ English words, no Telugu) | new advisory `headings_telugu` |
| B4 | "త్వరపడండి!!", "!!!" hype | new `no_hype` (≥2 consecutive `!` or ≥4 `!` total) |
| B5 | FAQ answers "TBD." / "N/A" in `<h3>` FAQs | `faq_depth` now also reads HTML h3 → next `<p>` (≥6 words) |
| B6 | Meta description with no Telugu script | new `meta_telugu` |
| B7 | `dd/mm/yyyy` dates | new advisory `date_format` (prefer `15 జనవరి 2025`) |
| B8 | Title says Notification but category Results | new advisory `category_match` |
| B9 | Exact duplicate sentence inside article only lowered a score; filler openers ("ఈ ఆర్టికల్ లో మనం … తెలుసుకుందాం", "మీ స్నేహితులతో షేర్ చేయండి", "సందర్శిస్తూ ఉండండి") not in list | `content_quality.tidy()` deterministically removes 2nd+ exact duplicate sentences/paragraphs and whole-sentence filler (inline-tag-balance guarded); new filler patterns; new gate `no_filler` |

## Deliberately NOT done (owner rules / risk)
- No async/deferred CSS (owner-tested failure v296), no CSS purge (bot post markup lives outside the theme).
- No new home sections, ads, tickers, hints; no changes to the approved social rail / fixed elements.
- Standard English terms (Notification, Official Website, Eligibility…) stay English per owner's list.
