#!/usr/bin/env bash
# =============================================================================
#  StudentUp bot — ONE COMMAND installer
#
#  Ubuntu 22.04/24.04 VM (Oracle free tier / any VPS) lo ide okka command:
#      bash install-bot.sh
#
#  Idi chesedi:
#    1. python3 + venv + unzip + cron install (apt)
#    2. studentup-bot-cron.zip extract  (ee script pakkana undali)
#    3. .env ni adigi create (keys paste cheste chalu) — already unte keep
#    4. deploy-check + WordPress connection test
#    5. ONE dry-run draft (publish kaadu) — nijanga pani chestunda ani proof
#    6. crontab install (6:30 AM drafts · 7:00 AM quiz · approvals */5 min)
#
#  SAFE: AUTOMATION_DRAFT_ONLY=1 · AUTO_PUBLISH_DAILY=0 — bot eppudu direct
#  publish cheyyadu. Mee approval tarvata ne live.
#  Idempotent: malli run cheste em pagaladu, update matrame.
#
#  Non-interactive / CI (prompts skip, env vars nunchi values):
#      NONINTERACTIVE=1 SKIP_APT=1 SKIP_CRON=1 bash install-bot.sh
# =============================================================================
set -euo pipefail

BOT_DIR="${BOT_DIR:-$HOME/studentup-bot}"
ZIP="${ZIP:-studentup-bot-cron.zip}"
NONINTERACTIVE="${NONINTERACTIVE:-0}"
SKIP_APT="${SKIP_APT:-0}"
SKIP_CRON="${SKIP_CRON:-0}"
SKIP_PROOF="${SKIP_PROOF:-0}"
PY="$BOT_DIR/.venv/bin/python"

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '   \033[1;32m✔\033[0m %s\n' "$*"; }
warn() { printf '   \033[1;33m⚠\033[0m %s\n' "$*"; }
die()  { printf '\n\033[1;31m✘ %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- 1. packages
say "1/6  System packages"
APT_OK=0
if [ "$SKIP_APT" = "1" ]; then
  warn "SKIP_APT=1 — package install skip chesam"
elif ! command -v apt-get >/dev/null 2>&1; then
  warn "apt-get ledu (shared hosting?) — unna python3 tho continue"
else
  SUDO=""
  if [ "$(id -u)" != "0" ]; then
    command -v sudo >/dev/null 2>&1 && SUDO="sudo"
  fi
  export DEBIAN_FRONTEND=noninteractive
  if $SUDO apt-get update -qq \
     && $SUDO apt-get install -y -qq python3 python3-venv python3-pip unzip curl cron >/dev/null; then
    APT_OK=1
    ok "python3 · venv · unzip · cron ready"
  else
    warn "apt install fail ayyindi (network/permissions?) — unnavi tho continue"
  fi
fi
command -v python3 >/dev/null 2>&1 || die "python3 ledu — mundu install cheyandi: sudo apt install python3 python3-venv"
ok "python3 $(python3 -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])')"

# ----------------------------------------------------------------- 2. extract
say "2/6  Bot files"
[ -f "$ZIP" ] || die "$ZIP ee folder lo ledu. Repo nunchi download chesi ee script pakkana pettandi."
mkdir -p "$BOT_DIR"
if command -v unzip >/dev/null 2>&1; then
  unzip -qo "$ZIP" -d "$BOT_DIR"
else
  # unzip lekapothe python tho extract (apt fail ayyina pani chestundi)
  python3 -c 'import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$ZIP" "$BOT_DIR"
  ok "unzip ledu — python zipfile tho extract chesam"
fi
# zip lopala okka folder unte daanni paiki techu
if [ ! -f "$BOT_DIR/run.py" ]; then
  inner="$(dirname "$(find "$BOT_DIR" -maxdepth 3 -name run.py -type f | head -1 || true)")"
  [ -n "$inner" ] && [ "$inner" != "." ] || die "run.py dorakaledu — zip correct ga undo chudandi"
  cp -r "$inner"/. "$BOT_DIR"/
fi
[ -f "$BOT_DIR/run.py" ] || die "run.py inka dorakaledu — zip structure chudandi"
ok "extracted → $BOT_DIR"

# ------------------------------------------------------- 3. python environment
say "3/6  Python environment"
if [ ! -x "$PY" ]; then
  python3 -m venv "$BOT_DIR/.venv" || die "venv create kaledu — sudo apt install python3-venv"
fi
"$PY" -m pip install -q --upgrade pip
"$PY" -m pip install -q -r "$BOT_DIR/requirements.txt" \
  || die "pip install fail (internet? proxy?) — requirements.txt: $(tr '\n' ' ' < "$BOT_DIR/requirements.txt")"
ok "dependencies installed ($(wc -l < "$BOT_DIR/requirements.txt") packages)"

# --------------------------------------------------------------------- 4. env
say "4/6  Configuration (.env)"
ENVF="$BOT_DIR/.env"

# safe key=value writer — sed kaadu (value lo | & / unna pagaladu)
env_set() { # env_set KEY VALUE
  ENV_FILE="$ENVF" ENV_KEY="$1" ENV_VAL="$2" "$PY" - <<'PYEOF'
import os, pathlib
p = pathlib.Path(os.environ["ENV_FILE"])
key, val = os.environ["ENV_KEY"], os.environ["ENV_VAL"]
lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
out, done = [], False
for ln in lines:
    if ln.strip() == key or ln.strip().startswith(key + "="):
        out.append("%s=%s" % (key, val)); done = True
    else:
        out.append(ln)
if not done:
    out.append("%s=%s" % (key, val))
p.write_text("\n".join(out) + "\n", encoding="utf-8")
PYEOF
}

env_get() { # env_get KEY  -> value (ledu ante khalii)
  ENV_FILE="$ENVF" ENV_KEY="$1" "$PY" - <<'PYEOF'
import os, pathlib
p = pathlib.Path(os.environ["ENV_FILE"]); key = os.environ["ENV_KEY"]
if p.exists():
    for ln in p.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if s == key or s.startswith(key + "="):
            print(s.partition("=")[2].strip().strip('"').strip("'")); break
PYEOF
}

ask() { # ask VAR "prompt"
  local var="$1" prompt="$2" val=""
  [ "$NONINTERACTIVE" = "1" ] && return 0
  printf '   %s: ' "$prompt"
  read -r val || true
  [ -n "$val" ] || return 0
  env_set "$var" "$val"
}

if [ -f "$ENVF" ]; then
  ok ".env already undi — touch cheyyaledu (edit: nano $ENVF)"
else
  [ -f "$BOT_DIR/.env.example" ] || die ".env.example zip lo ledu — zip damage ayyinda?"
  cp "$BOT_DIR/.env.example" "$ENVF"
  echo "   (Enter koduthe skip — tarvata nano .env lo pettochu)"
  ask WP_SITE            "WordPress site URL [https://studentup.in]"
  ask WP_USERNAME        "WP username"
  ask WP_APP_PASSWORD    "WP Application Password (spaces tho)"
  ask GEMINI_API_KEY     "Gemini API key (aistudio.google.com/apikey)"
  ask GEMINI_API_KEYS    "Extra Gemini keys (comma separated, optional)"
  ask GROQ_API_KEY       "Groq API key (console.groq.com/keys, optional)"
  ask TELEGRAM_BOT_TOKEN "Telegram bot token (@BotFather, optional)"
  ask GOOGLE_CSE_API_KEY "Google CSE API key (live copy-check, optional)"
  ask GOOGLE_CSE_ID      "Google CSE ID (optional)"
  ok ".env create ayyindi"
fi

# safety defaults: draft only, eppudu auto-publish kaadu
env_set DEFAULT_POST_STATUS  draft
env_set AUTOMATION_DRAFT_ONLY 1
env_set AUTO_PUBLISH_DAILY   0
chmod 600 "$ENVF"
ok "draft-only mode locked (AUTOMATION_DRAFT_ONLY=1 · AUTO_PUBLISH_DAILY=0 · chmod 600)"

# .env parse cheyyagalada? (inline-comment type bugs ikkade pattabadatayi)
cd "$BOT_DIR"
mkdir -p log private output
"$PY" -c 'import autoblog.config' \
  || die ".env parse cheyyalekapotunnadi — paina error chusi .env ni sari cheyandi (nano $ENVF)"
ok ".env parse OK"
for t in ci/test_env_parser.py ci/test_cli_flags.py ci/test_shadowed_imports.py; do
  if [ -f "$BOT_DIR/$t" ]; then
    if "$PY" "$t" > "/tmp/su-$(basename "$t" .py).log" 2>&1; then
      ok "self-test $t passed"
    else
      warn "self-test $t FAIL — /tmp/su-$(basename "$t" .py).log chudandi:"
      sed 's/^/      /' "/tmp/su-$(basename "$t" .py).log" | tail -5
    fi
  fi
done

# ------------------------------------------------------------------- 5. checks
say "5/6  Health checks"
"$PY" run.py --deploy-check || warn "deploy-check lo warnings unnayi (paiki chudandi)"

WP_PASS="$(env_get WP_APP_PASSWORD)"
WP_USER="$(env_get WP_USERNAME)"
case "$WP_PASS" in
  ""|xxxx*|your_*) warn "WP app password inka pettaleedu — --check-wp skip";;
  *)
    if [ -z "$WP_USER" ]; then
      warn "WP_USERNAME khaali ga undi — --check-wp skip"
    else
      "$PY" run.py --check-wp || warn "WordPress connect kaledu — URL / username / application-password chudandi"
    fi;;
esac

if [ "$SKIP_PROOF" = "1" ]; then
  warn "SKIP_PROOF=1 — proof run skip chesam"
else
  say "5b/6  Proof run — ONE draft (publish kaadu)"
  GKEY="$(env_get GEMINI_API_KEY)"
  case "$GKEY" in
    ""|your_*|key2_*)
      warn "Gemini key ledu — offline proof (--dry-run --mock) run chestunnam"
      "$PY" run.py --dry-run --mock || warn "dry-run --mock fail — paina error chudandi";;
    *)
      "$PY" run.py --dry-run || warn "dry-run fail — paina error chudandi (key/quota?)"
      warn "Real proof kavali ante: $PY run.py --dry-run  (Gemini key tho)";;
  esac
fi

# -------------------------------------------------------------------- 6. cron
say "6/6  Cron"
CRON_MARK="# studentup-bot"
if [ "$SKIP_CRON" = "1" ]; then
  warn "SKIP_CRON=1 — crontab ni touch cheyyaledu"
elif ! command -v crontab >/dev/null 2>&1; then
  warn "crontab command ledu — sudo apt install cron (leda systemd timer: deploy/install-vps.sh)"
elif crontab -l 2>/dev/null | grep -q "$CRON_MARK"; then
  ok "cron already installed (change: crontab -e)"
else
  { crontab -l 2>/dev/null || true
    echo "$CRON_MARK — drafts only, human approval"
    echo "30 6 * * * cd $BOT_DIR && $PY run.py --daily >> $BOT_DIR/log/daily.log 2>&1"
    echo "0 7 * * * cd $BOT_DIR && $PY run.py --daily-quiz >> $BOT_DIR/log/quiz.log 2>&1"
    echo "10 7 * * * cd $BOT_DIR && $PY run.py --guardian >> $BOT_DIR/log/guardian.log 2>&1"
    echo "*/5 * * * * cd $BOT_DIR && $PY run.py --approval-poll >> $BOT_DIR/log/approval.log 2>&1"
    echo "0 3 * * 0 cd $BOT_DIR && $PY run.py --site-audit >> $BOT_DIR/log/audit.log 2>&1"
    echo "45 3 * * 0 cd $BOT_DIR && $PY run.py --orphans >> $BOT_DIR/log/links.log 2>&1"
    echo "0 3 1 * * tail -c 500000 $BOT_DIR/log/cron.log > /tmp/su-cron.log && mv /tmp/su-cron.log $BOT_DIR/log/cron.log"
  } | crontab -
  ok "cron installed — 6:30 drafts · 7:00 quiz · 7:10 guardian · approvals */5 min"
fi

cat <<EOF

=============================================================================
  ✅ BOT READY — $BOT_DIR

  Ippudu cheyyalsinavi:
    1. WP Admin → Posts → Drafts lo vachina draft chadavandi
       (dates / fee / apply link correct a?)
    2. Correct unte publish. 5 drafts ila verify chesaka ne cron ni nammandi.
    3. Logs:  tail -f $BOT_DIR/log/daily.log

  Useful:
    $PY run.py --status          # ee roju plan + stats
    $PY run.py --ai-status       # ye AI providers/keys live lo unnayo
    $PY run.py --radar           # ee roju ye notifications vachayi
    $PY run.py --force           # ventane okka post (draft ga)
    $PY run.py --daily-quiz      # quiz draft
    $PY run.py --adsense-ready   # AdSense apply cheyyocha?
    $PY run.py --deploy-check    # readiness re-check
    nano $ENVF                   # keys marchadaniki

  ⚠️  Bot eppudu direct publish cheyyadu (AUTOMATION_DRAFT_ONLY=1).
      Nammakam vachaka .env lo AUTO_PUBLISH_DAILY=1 pettandi.
=============================================================================
EOF
