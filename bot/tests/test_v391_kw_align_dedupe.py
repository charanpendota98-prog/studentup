"""v391: keyword/title alignment, acronym casing, topic duplicates, title entities."""
import os

os.environ.setdefault("WP_URL", "https://studentup.in")
os.environ.setdefault("WP_USER", "x")
os.environ.setdefault("WP_APP_PASSWORD", "x")
os.environ.setdefault("GEMINI_API_KEY", "x")

from autoblog import kw_align, rm100, pipeline  # noqa: E402
from autoblog.dedupe_posts import group_duplicates  # noqa: E402


def test_query_keyword_is_derived_from_title_not_prepended():
    a = {"focus_keyword": "ap pg medical fees",
         "title": "AP PG Medical Admissions 2026: కన్వీనర్ కోటా నోటిఫికేషన్"}
    rep = kw_align.align(a)
    assert rep["changed"]
    assert a["focus_keyword"] == "AP PG Medical Admissions 2026"
    assert a["secondary_keywords"][0] == "ap pg medical fees"


def test_fix_title_never_doubles_entity():
    a = {"focus_keyword": "dic state coordinator salary",
         "title": "DIC State Coordinator Recruitment 2026: 12 పోస్టులు"}
    rm100.fix_title(a)
    assert not a["title"].lower().startswith("dic state coordinator salary")
    assert a["title"].count("DIC") == 1
    assert a["focus_keyword"].lower() in a["title"].lower()


def test_pretty_kw_acronyms():
    assert kw_align.pretty_kw("ap nmms scholarship online registration 2026") == \
        "AP NMMS Scholarship Online Registration 2026"
    assert kw_align.pretty_kw("upsc 2026 upcoming vacancy") == "UPSC 2026 Upcoming Vacancy"


def test_unrelated_keyword_falls_back_to_cased_prefix():
    a = {"focus_keyword": "tspsc group 4 hall ticket", "title": "APPSC Group 2 Notification 2026 686 పోస్టులు"}
    kw_align.align(a)
    assert a["focus_keyword"] == "TSPSC Group 4 Hall Ticket"


def test_same_topic_detection():
    assert kw_align.same_topic("AP DSC 2026 Notification 2,721 Teacher Vacancies",
                               "AP DSC Notification 2026: 2,721 పోస్టుల వివరాలు")
    assert kw_align.same_topic("APPSC Group 2 Notification 2026 686 పోస్టులు Official",
                               "APPSC Group 2 Notification 2026: 686 పోస్టులు Latest")
    assert not kw_align.same_topic("APPSC Group 1 Notification 2026: 166 పోస్టులు",
                                   "APPSC Group 2 Notification 2026: 686 పోస్టులు")
    assert not kw_align.same_topic("AP DSC 2026 Notification 2,721 Teacher Posts",
                                   "AP DSC 2026 Special Education Notification 350 పోస్టులు")
    assert not kw_align.same_topic("Telangana ePASS 2026 స్కాలర్‌షిప్స్ దరఖాస్తు విధానం",
                                   "NMMS Scholarship 2026 దరఖాస్తు విధానం మరియు పూర్తి వివరాలు")


def test_group_duplicates_keeps_singletons_out():
    def P(i, t, w):
        return {"id": i, "title": {"raw": t}, "content": {"raw": " ".join(["x"] * w)}, "date": f"2026-10-2{i}", "link": f"l{i}"}
    posts = [P(1, "AP DSC 2026 Notification 2,721 Posts", 500), P(2, "AP DSC Notification 2026 2,721 పోస్టులు", 700),
             P(3, "RRB NTPC 2026 1688 పోస్టులు", 400), P(4, "ICMR Young Professional 2026 Recruitment", 450)]
    groups = group_duplicates(posts)
    assert len(groups) == 1 and {r["id"] for r in groups[0]} == {1, 2}


def test_title_double_escaped_entities_cleaned():
    assert pipeline.clean_title_text("APSLPRB APP 2026 Prelims Key &amp;#8211; అభ్యంతరాలు") == \
        "APSLPRB APP 2026 Prelims Key – అభ్యంతరాలు"


def test_admissions_story_not_filed_under_jobs():
    a = {"title": "AP PG Medical Admissions 2026: కన్వీనర్ కోటా కౌన్సెలింగ్", "category": "Central Govt Jobs",
         "content_html": "<p>కౌన్సెలింగ్ షెడ్యూల్</p>"}
    pipeline.reconcile_category(a)
    assert a["category"] == "Online Education"


def test_vacancy_breakdown_numbers_are_not_verbatim():
    from autoblog import validator
    src = ["<p>మొత్తం 2 750 పోస్టులు సీనియర్ క్లర్క్ 1200 పోస్టులు జూనియర్ అసిస్టెంట్ 371 పోస్టులు టైపిస్ట్ 180 పోస్టులు వార్డ్ ఆఫీసర్ 999 పోస్టులు డ్రైవర్ 45 పోస్టులు అని ప్రకటించారు.</p>"]
    art = "<p>వివరాలు: మొత్తం 2 750 పోస్టులు సీనియర్ క్లర్క్ 1200 పోస్టులు జూనియర్ అసిస్టెంట్ 371 పోస్టులు టైపిస్ట్ 180 పోస్టులు వార్డ్ ఆఫీసర్ 999 పోస్టులు డ్రైవర్ 45 పోస్టులు ఉన్నాయి.</p>"
    assert validator.verbatim_overlaps(art, src, min_free=0) == []
