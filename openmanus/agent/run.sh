#!/usr/bin/env bash
# Runs one OpenManus task on this Maritime Linux desktop. Runs inside the computer.
# OpenManus drives a Chromium window on the desktop's screen (DISPLAY :1), and a
# terminal beside it shows the agent's steps, so you can watch both from the
# Maritime viewer and take over at any moment.
set -uo pipefail
HOME_DIR=/data/agents/openmanus
PORT=9222
LOG="$HOME_DIR/last-run.log"
: > "$LOG"

# A dedicated Chromium with remote debugging on, visible on the desktop. Its profile
# lives in /data, so logins survive sleep and restarts.
if ! curl -fs "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  /usr/bin/chromium --remote-debugging-port=${PORT} --user-data-dir="$HOME_DIR/profile" \
    --no-first-run --no-default-browser-check --password-store=basic \
    --window-position=0,0 --window-size=800,760 about:blank >/dev/null 2>&1 &
  for _ in $(seq 1 30); do curl -fs "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1 && break; sleep 1; done
fi

# The agent's steps in a terminal next to the browser (log prefixes and token counts left out).
if [ -n "${DISPLAY:-}" ]; then
  pkill -f "xfce4-terminal --disable-server --title OpenManus" 2>/dev/null || true
  printf '$ python run_manus.py "%s"\n\n' "$*" > "$HOME_DIR/terminal.log"
  xfce4-terminal --disable-server --title "OpenManus" --geometry 56x38+805+0 --hide-menubar --hide-toolbar \
    --font "DejaVu Sans Mono 10" --color-bg "#ffffff" --color-text "#1f2328" \
    -x bash -c "tail -n +1 -f '$HOME_DIR/terminal.log' & tail -n +1 -f '$LOG' | grep --line-buffered -v 'Token usage' \
      | sed -u -E 's/^[0-9-]+ [0-9:.]+ \| [A-Z]+ +\| [^ ]+ - //' \
      | perl -CS -pe 'BEGIN{\$|=1} s/[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{FE0F}]\s?//g'" >/dev/null 2>&1 &
  sleep 2
fi

export BU_CDP_URL="http://127.0.0.1:${PORT}"
export PYTHONUNBUFFERED=1 ANONYMIZED_TELEMETRY=false BROWSER_USE_TELEMETRY=false
"$HOME_DIR/.venv/bin/python" "$HOME_DIR/run_manus.py" "$@" 2>&1 | tee -a "$LOG"
exit "${PIPESTATUS[0]}"
