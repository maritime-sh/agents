#!/usr/bin/env bash
# The Aider session shown in the desktop terminal: a fresh git repo, one task, then the tests.
set -u
HOME_DIR=/data/agents/aider
stamp=$1
trap 'echo 1 > "$HOME_DIR/term-$stamp.done"' EXIT   # if anything below fails early
task=$(cat "$HOME_DIR/task-$stamp.txt")
. "$HOME_DIR/path.sh"
. "$HOME_DIR/.env"
export PATH="$HOME_DIR/.venv/bin:$PATH:/nix/var/nix/profiles/default/bin"   # git lives there on the desktop

repo=/data/projects/aider-$stamp
mkdir -p "$repo" && cd "$repo"
git init -q
git config user.name "Aider on Maritime"
git config user.email "aider@localhost"

model="${AIDER_MODEL:-gpt-5.4}"
args=(--yes-always --no-check-update --no-show-model-warnings --no-analytics
      --no-show-release-notes --no-gitignore --no-stream
      --test-cmd "python3 -m unittest -v" --auto-test)
args+=(--model "openai/$model")   # any OpenAI-compatible endpoint
[ -n "${OPENAI_BASE_URL:-}" ] && args+=(--openai-api-base "$OPENAI_BASE_URL")

echo "\$ aider --message \"$task\""
aider "${args[@]}" --message "$task"
echo
echo "\$ python3 -m unittest -v"
python3 -m unittest -v
rc=$?
echo
echo "\$ git log --oneline"
git log --oneline | cat
echo
if [ $rc -eq 0 ] && ls *.py >/dev/null 2>&1; then echo "=== SUCCESS ==="; else echo "=== NOT FINISHED ==="; fi
echo "Project: $repo"
# Tell run.sh the session ended, then keep the window open with a shell.
trap - EXIT
echo "${rc:-1}" > "$HOME_DIR/term-$stamp.done"
PS1="$ " exec bash --norc -i
