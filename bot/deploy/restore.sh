#!/usr/bin/env bash
# StudentUp restore drill (audit PR-4). Verifies a backup is restorable WITHOUT
# touching the live state.db, then (optionally) swaps it in.
#   ./deploy/restore.sh                 → dry run: integrity_check + row counts of newest backup
#   ./deploy/restore.sh --apply FILE    → stop bot, swap FILE into place, restart
set -euo pipefail
APP_DIR="${APP_DIR:-/opt/studentup}"
DEST="${DEST:-/var/backups/studentup}"
MODE="${1:-}"; FILE="${2:-}"
if [ -z "$FILE" ]; then FILE="$(ls -1t "$DEST"/state-*.db "$APP_DIR"/state.db.bak/state-*.db 2>/dev/null | head -1 || true)"; fi
[ -n "$FILE" ] && [ -f "$FILE" ] || { echo "no backup found in $DEST or $APP_DIR/state.db.bak"; exit 2; }
echo "backup: $FILE ($(du -h "$FILE" | cut -f1), $(date -r "$FILE" '+%F %R'))"
python3 - "$FILE" <<'PY'
import sqlite3, sys
db = sqlite3.connect(sys.argv[1])
ok = db.execute("PRAGMA integrity_check").fetchone()[0]
print("integrity:", ok)
for t in ("posts", "sources", "meta", "wp_terms"):
    try: print(f"  {t:9s} {db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} rows")
    except sqlite3.Error as e: print(f"  {t:9s} MISSING ({e})")
sys.exit(0 if ok == "ok" else 1)
PY
if [ "$MODE" = "--apply" ]; then
  systemctl stop studentup-bot.timer studentup-approval.service 2>/dev/null || true
  cp -a "$APP_DIR/state.db" "$APP_DIR/state.db.pre-restore-$(date +%Y%m%d-%H%M)"
  cp -a "$FILE" "$APP_DIR/state.db"; rm -f "$APP_DIR/state.db-wal" "$APP_DIR/state.db-shm"
  systemctl start studentup-bot.timer studentup-approval.service 2>/dev/null || true
  echo "restored → $APP_DIR/state.db (previous kept as .pre-restore-*)"
else
  echo "dry run only. To restore: $0 --apply $FILE"
fi
