#!/usr/bin/env bash
# Deploy Open Instinct (a personal agent with its own computer) to Maritime.
#
#   export MARITIME_API_KEY=mk_...
#   export ANTHROPIC_API_KEY=sk-ant-...      # or skip it and pass --maritime-llm
#   ./deploy.sh --name "Ada" --handle ada-instinct
#   ./deploy.sh --name "Ada" --handle ada-instinct --maritime-llm   # no model key of your own
#
# It builds the pinned Open Instinct release, creates your agent on Maritime
# (its own micro-VM with a Linux desktop), and says hello to it. Add an iMessage
# line later with INKBOX_ADMIN_API_KEY: see docs/INKBOX.md in the upstream repo.
set -euo pipefail

OPEN_INSTINCT_COMMIT="2e5e71b"   # pinned: github.com/mariagorskikh/open-instinct, main at 2026-10-29
IMAGE="ghcr.io/mariagorskikh/open-instinct-agent:sha-${OPEN_INSTINCT_COMMIT}"   # built from that commit

NAME="" HANDLE="" LLM_FLAG="" TZ_NAME="${TZ_NAME:-America/Los_Angeles}"
while [ $# -gt 0 ]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --handle) HANDLE="$2"; shift 2 ;;
    --timezone) TZ_NAME="$2"; shift 2 ;;
    --maritime-llm) LLM_FLAG="--maritime-llm"; shift ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done
[ -n "$NAME" ] && [ -n "$HANDLE" ] || { echo "usage: ./deploy.sh --name <your name> --handle <agent-handle> [--maritime-llm]" >&2; exit 2; }
[ -n "${MARITIME_API_KEY:-}" ] || { echo "Set MARITIME_API_KEY (maritime.sh, Settings, API keys)" >&2; exit 2; }
[ -n "$LLM_FLAG" ] || [ -n "${ANTHROPIC_API_KEY:-}" ] || { echo "Set ANTHROPIC_API_KEY, or pass --maritime-llm" >&2; exit 2; }
command -v node >/dev/null || { echo "Node 22.19+ is required" >&2; exit 2; }

WORK="${OPEN_INSTINCT_DIR:-$HOME/.maritime-agents/open-instinct}"
if [ ! -d "$WORK/.git" ]; then
  git clone -q https://github.com/mariagorskikh/open-instinct "$WORK"
fi
cd "$WORK"
git fetch -q origin && git checkout -q "$OPEN_INSTINCT_COMMIT"

echo "1/4 Building Open Instinct ${OPEN_INSTINCT_COMMIT} ..."
corepack enable >/dev/null 2>&1 || true
pnpm install --frozen-lockfile --silent
pnpm -r --silent build

instinct() { node packages/cli/dist/bin.js "$@" --data-dir "$WORK/.instinct-$HANDLE"; }

echo "2/4 Writing your agent's config ..."
if [ -n "${INKBOX_ADMIN_API_KEY:-}" ]; then
  instinct init --name "$NAME" --handle "$HANDLE" --timezone "$TZ_NAME"
else
  instinct init --name "$NAME" --handle "$HANDLE" --timezone "$TZ_NAME" --skip-inkbox
fi

echo "3/4 Creating the agent on Maritime (its own micro-VM and Linux desktop) ..."
instinct deploy --image "$IMAGE" --name "instinct-$HANDLE" $LLM_FLAG

echo "4/4 Waiting for the agent to start, then saying hello ..."
AGENT_ID=$(node -e "console.log(require('$WORK/.instinct-$HANDLE/maritime.json').agentId)")
for _ in $(seq 1 60); do
  STATUS=$(curl -s -H "Authorization: Bearer $MARITIME_API_KEY" "https://api.maritime.sh/api/agents/$AGENT_ID" \
    | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{try{console.log(JSON.parse(s).status)}catch{console.log('unknown')}})")
  case "$STATUS" in
    active|running|sleeping) break ;;
    error) echo "The agent failed to start. See https://maritime.sh/dashboard/agents/$AGENT_ID" >&2; exit 1 ;;
  esac
  sleep 10
done
instinct chat "Hi! In one sentence, what can you do for me?" --agent "$AGENT_ID"
echo
echo "Done. Chat again with: (cd $WORK && node packages/cli/dist/bin.js chat \"...\" --agent $AGENT_ID --data-dir $WORK/.instinct-$HANDLE)"
