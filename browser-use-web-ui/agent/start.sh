#!/usr/bin/env bash
# Starts the browser-use Web UI (once) and opens it in the desktop's Chromium.
# Runs inside the computer.
set -u
HOME_DIR=/data/agents/browser-use-web-ui
cd "$HOME_DIR/web-ui-3.0.0"
export DISPLAY=:1
# The agent's browser is reached at "localhost", and this desktop image ships an
# empty /etc/hosts. Give the Web UI its own /etc/hosts in a private mount
# namespace (no root needed; it still runs as the desktop user).
printf '127.0.0.1 localhost\n::1 localhost\n' > "$HOME_DIR/hosts"
if getent hosts localhost >/dev/null; then
  RUN=""
else
  RUN="unshare -rm sh -c 'mount --bind $HOME_DIR/hosts /etc/hosts && exec unshare --user --map-user=$(id -u) --map-group=$(id -g) \"\$0\" \"\$@\"'"
fi
if ! curl -s -o /dev/null http://127.0.0.1:7788/; then
  eval nohup $RUN ../.venv/bin/python webui.py --ip 127.0.0.1 --port 7788 > "$HOME_DIR/webui.log" 2>&1 < /dev/null &
  for _ in $(seq 1 60); do curl -s -o /dev/null http://127.0.0.1:7788/ && break; sleep 2; done
fi
pkill -f "user-data-dir=$HOME_DIR/ui-profile" ; sleep 1
nohup chromium --user-data-dir="$HOME_DIR/ui-profile" --no-first-run --no-default-browser-check \
  --start-maximized --force-device-scale-factor=0.67 --app=http://127.0.0.1:7788/ > /dev/null 2>&1 < /dev/null &
echo MARITIME_UI_READY
