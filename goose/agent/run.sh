#!/usr/bin/env bash
# Runs one goose task on this Maritime Linux desktop. Runs inside the computer.
# A terminal opens on the desktop's screen (DISPLAY :1) and shows the run live,
# so you can watch it from the Maritime viewer.
#
#   bash run.sh "Find the Growth plan price on maritime.sh/pricing"
#
# Model: any OpenAI-compatible endpoint. OPENAI_API_KEY, optional OPENAI_BASE_URL
# (for example Maritime LLM, https://api.maritime.sh/api/llm/v1), GOOSE_MODEL
# (default gpt-5.4). Or set GOOSE_PROVIDER and that provider's key yourself.
set -uo pipefail
HOME_DIR=/data/agents/goose
TASK="$*"

export GOOSE_DISABLE_KEYRING=1 GOOSE_MODE=auto GOOSE_CLI_THEME=light
export GOOSE_PROVIDER="${GOOSE_PROVIDER:-openai}" GOOSE_MODEL="${GOOSE_MODEL:-gpt-5.4}"
export XDG_CONFIG_HOME="$HOME_DIR/config" XDG_DATA_HOME="$HOME_DIR/data" XDG_STATE_HOME="$HOME_DIR/state"
if [ -n "${OPENAI_BASE_URL:-}" ]; then
  # goose splits an OpenAI-compatible URL into a host and a path
  rest="${OPENAI_BASE_URL#*://}"
  export OPENAI_HOST="${OPENAI_BASE_URL%%://*}://${rest%%/*}"
  path="${rest#*/}"; [ "$path" = "$rest" ] && path=""
  export OPENAI_BASE_PATH="${path:+${path%/}/}chat/completions"
fi

# Show the run in a terminal on the desktop.
VIEW="$HOME_DIR/terminal.log"
printf '$ goose run --text "%s"\n\n' "$TASK" > "$VIEW"
if [ -n "${DISPLAY:-}" ]; then
  pkill -f "xfce4-terminal --disable-server --title goose" 2>/dev/null || true
  xfce4-terminal --disable-server --title "goose" --geometry 104x30+40+30 --hide-menubar --hide-toolbar \
    --font "DejaVu Sans Mono 12" --color-bg "#ffffff" --color-text "#1f2328" \
    -x tail -n +1 -f "$VIEW" >/dev/null 2>&1 &
  sleep 2
fi

cd "$HOME_DIR/work"
# Leaves out the ASCII mascot in goose's start banner, keeps every other line.
"$HOME_DIR/bin/goose" run --no-session --with-builtin developer --text "$TASK" 2>&1 \
  | sed -u -E 's/^ *(__\( O\)>|\\____\)|L L) +/  /' | tee -a "$VIEW"
rc=${PIPESTATUS[0]}
printf '\n[goose exited with code %s]\n' "$rc" >> "$VIEW"
[ "$rc" = 0 ] && echo "=== SUCCESS ===" || echo "=== NOT FINISHED ==="
exit "$rc"
