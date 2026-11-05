#!/usr/bin/env bash
# Runs one smolagents task in a terminal window on the desktop (DISPLAY :1), so you can
# watch it live, and copies the terminal's output to stdout for deploy.py.
#
#     ./run.sh "What is the latest release of the requests library on PyPI?"
set -u
HOME_DIR=/data/agents/smolagents
TITLE="smolagents"
cd "$HOME_DIR"
stamp=$(date +%s)
out="$HOME_DIR/term-$stamp.txt"
done_file="$HOME_DIR/term-$stamp.done"
printf '%s' "$*" > "$HOME_DIR/task-$stamp.txt"
printf 'export PATH=%q\n' "$PATH" > "$HOME_DIR/path.sh"   # the terminal starts with a shorter PATH
: > "$out"

export DISPLAY=:1
pkill -f "xfce4-terminal --disable-server --title=$TITLE " 2>/dev/null   # close the previous run's window
xfce4-terminal --disable-server --title="$TITLE" --maximize --zoom=2 \
  -x script -qfec "bash $HOME_DIR/session.sh $stamp" "$out" >/dev/null 2>&1 &

# Stream the terminal transcript, without colour codes and padding, until the session ends.
tail -n +1 -f --pid=$$ "$out" | sed -u -r 's/\x1b\[[0-9;?]*[ -\/]*[@-~]//g; s/\x1b\][^\x07]*\x07//g; s/\x1b[()][A-Z0-9]//g; s/\r//g; s/[ ]+$//; /^$/d' &
while [ ! -f "$done_file" ]; do sleep 2; done
sleep 2   # tail stops by itself when this script exits
exit "$(cat "$done_file")"
