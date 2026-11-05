#!/usr/bin/env bash
# Installs Aider on a Maritime Linux desktop. Runs inside the computer.
# Everything lives under /data, which survives sleep, wake and restarts.
set -euo pipefail

AIDER_VERSION="0.86.2"   # pinned upstream release (pypi.org/project/aider-chat)
UV_VERSION="0.9.5"
HOME_DIR=/data/agents/aider

mkdir -p "$HOME_DIR" /data/bin
export UV_CACHE_DIR=/data/.uv-cache UV_PYTHON_INSTALL_DIR=/data/.uv-python

if [ ! -x /data/bin/uv ]; then
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | env UV_INSTALL_DIR=/data/bin UV_NO_MODIFY_PATH=1 sh
fi

cd "$HOME_DIR"
# aider-chat supports Python 3.10 to 3.12; uv fetches 3.12 into /data.
[ -x .venv/bin/python ] || /data/bin/uv venv -q --python 3.12 .venv
/data/bin/uv pip install -q --python .venv/bin/python "aider-chat==${AIDER_VERSION}"
chmod +x run.sh session.sh

echo "MARITIME_AGENT_READY aider ${AIDER_VERSION}"
