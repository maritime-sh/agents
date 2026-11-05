#!/usr/bin/env bash
# Installs OpenManus on a Maritime Linux desktop. Runs inside the computer.
# Everything lives under /data, which survives sleep, wake and restarts.
set -euo pipefail

OPENMANUS_COMMIT="3309bf4e416fb1c74b008f3e86494439a31bad53"   # pinned upstream commit (github.com/FoundationAgents/OpenManus)
BROWSER_USE_VERSION="0.13.14"   # the browser tool OpenManus starts (pypi.org/project/browser-use)
UV_VERSION="0.9.5"
HOME_DIR=/data/agents/openmanus

mkdir -p "$HOME_DIR" /data/bin
export UV_CACHE_DIR=/data/.uv-cache UV_PYTHON_INSTALL_DIR=/data/uv-python

if [ ! -x /data/bin/uv ]; then
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | env UV_INSTALL_DIR=/data/bin UV_NO_MODIFY_PATH=1 sh
fi

cd "$HOME_DIR"
if [ ! -f "src/.commit-${OPENMANUS_COMMIT}" ]; then
  rm -rf src && mkdir src
  curl -fsSL "https://codeload.github.com/FoundationAgents/OpenManus/tar.gz/${OPENMANUS_COMMIT}" \
    | tar -xz -C src --strip-components=1
  touch "src/.commit-${OPENMANUS_COMMIT}"
fi

# OpenManus needs Python 3.12; uv fetches it into /data.
[ -x .venv/bin/python ] || /data/bin/uv venv -q --python 3.12 .venv
# --torch-backend cpu: a benchmark dependency (browsergym) pulls in torch; the CPU build
# is a fraction of the CUDA one and these computers have no GPU.
/data/bin/uv pip install -q --python .venv/bin/python --torch-backend cpu -r src/requirements.txt

# The browser tool, pinned, in its own environment (OpenManus talks to it over MCP).
[ -x bu/bin/python ] || /data/bin/uv venv -q --python /usr/bin/python3 bu
/data/bin/uv pip install -q --python bu/bin/python "browser-use==${BROWSER_USE_VERSION}"
chmod +x run.sh

echo "MARITIME_AGENT_READY openmanus ${OPENMANUS_COMMIT:0:7}"
