#!/usr/bin/env bash
# Installs smolagents on a Maritime Linux desktop. Runs inside the computer.
# Everything lives under /data, which survives sleep, wake and restarts.
set -euo pipefail

SMOLAGENTS_VERSION="1.26.0"   # pinned upstream release (pypi.org/project/smolagents)
UV_VERSION="0.9.5"
HOME_DIR=/data/agents/smolagents

mkdir -p "$HOME_DIR" /data/bin
export UV_CACHE_DIR=/data/.uv-cache UV_PYTHON_INSTALL_DIR=/data/.uv-python

if [ ! -x /data/bin/uv ]; then
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | env UV_INSTALL_DIR=/data/bin UV_NO_MODIFY_PATH=1 sh
fi

cd "$HOME_DIR"
[ -x .venv/bin/python ] || /data/bin/uv venv -q --python /usr/bin/python3 .venv
# [toolkit] adds the web search and visit-webpage tools, [openai] the OpenAI-compatible model.
/data/bin/uv pip install -q --python .venv/bin/python "smolagents[toolkit,openai]==${SMOLAGENTS_VERSION}"
chmod +x run.sh session.sh

echo "MARITIME_AGENT_READY smolagents ${SMOLAGENTS_VERSION}"
