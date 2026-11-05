#!/usr/bin/env bash
# Runs inside a terminal on the desktop: the research job, then the report in Mousepad.
# Usage: show.sh <log file> <question>
HOME_DIR=/data/agents/gpt-researcher
LOG="$1"; shift
cd "$HOME_DIR" && . ./.env
export ANONYMIZED_TELEMETRY=false PYTHONUNBUFFERED=1
echo "\$ gpt-researcher \"$*\""
.venv/bin/python run.py "$@" 2>&1 | tee "$LOG"
REPORT=$(grep -o '=== REPORT === .*' "$LOG" | tail -n 1 | cut -d' ' -f4-)
if [ -n "$REPORT" ]; then
  mousepad "$REPORT" >/dev/null 2>&1 &
  sleep 3
  for WIN in $(xdotool search --onlyvisible --class mousepad 2>/dev/null); do
    xdotool windowmove "$WIN" 0 0 windowsize "$WIN" 1280 770 2>/dev/null
  done
fi
echo "MARITIME_RUN_EXIT" >> "$LOG"
sleep 600
