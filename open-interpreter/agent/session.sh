#!/usr/bin/env bash
# The Open Interpreter session shown in the desktop terminal: one task, the code it writes and runs, the answer.
set -u
HOME_DIR=/data/agents/open-interpreter
stamp=$1
trap 'echo 1 > "$HOME_DIR/term-$stamp.done"' EXIT   # if anything below fails early
task=$(cat "$HOME_DIR/task-$stamp.txt")
. "$HOME_DIR/path.sh"
. "$HOME_DIR/.env"
cd "$HOME_DIR"
# python3 and pip in the shell blocks it writes resolve to its own environment (with matplotlib).
export PATH="$HOME_DIR/.venv/bin:$PATH"
echo "\$ python agent.py \"$task\""
.venv/bin/python agent.py "$task"
rc=$?
# Tell run.sh the session ended, then keep the window open with a shell.
trap - EXIT
echo "${rc:-1}" > "$HOME_DIR/term-$stamp.done"
PS1="$ " exec bash --norc -i
