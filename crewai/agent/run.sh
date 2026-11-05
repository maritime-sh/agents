#!/usr/bin/env bash
# Runs the crew on this Maritime Linux desktop. Runs inside the computer.
# A terminal opens on the desktop's screen (DISPLAY :1) and shows the run live,
# so you can watch it from the Maritime viewer.
set -uo pipefail
HOME_DIR=/data/agents/crewai
TASK="$*"
export CREWAI_TRACING_ENABLED=false CREWAI_DISABLE_TELEMETRY=true OTEL_SDK_DISABLED=true
export PYTHONUNBUFFERED=1 COLUMNS=100 TERM=xterm-256color HOME="$HOME_DIR/work"

VIEW="$HOME_DIR/terminal.log"
printf '$ python crew.py "%s"\n\n' "$TASK" > "$VIEW"
if [ -n "${DISPLAY:-}" ]; then
  pkill -f "xfce4-terminal --disable-server --title crewAI" 2>/dev/null || true
  xfce4-terminal --disable-server --title "crewAI" --geometry 104x30+40+30 --hide-menubar --hide-toolbar \
    --font "DejaVu Sans Mono 12" --color-bg "#ffffff" --color-text "#1f2328" \
    -x tail -n +1 -f "$VIEW" >/dev/null 2>&1 &
  sleep 2
fi

cd "$HOME_DIR/work"
"$HOME_DIR/.venv/bin/python" "$HOME_DIR/crew.py" "$TASK" 2>&1 | tee -a "$VIEW"
rc=${PIPESTATUS[0]}
if [ -f summary.md ]; then
  printf '\n$ cat summary.md\n' >> "$VIEW"; cat summary.md >> "$VIEW"
fi
exit "$rc"
