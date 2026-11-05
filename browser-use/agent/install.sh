#!/usr/bin/env bash
# Installs browser-use on a Maritime Linux desktop. Runs inside the computer.
# Everything lives under /data, which survives sleep, wake and restarts.
set -euo pipefail

BROWSER_USE_VERSION="0.13.14"   # pinned upstream release (pypi.org/project/browser-use)
UV_VERSION="0.9.5"
HOME_DIR=/data/agents/browser-use

mkdir -p "$HOME_DIR" /data/bin
export UV_CACHE_DIR=/data/.uv-cache

if [ ! -x /data/bin/uv ]; then
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | env UV_INSTALL_DIR=/data/bin UV_NO_MODIFY_PATH=1 sh
fi

cd "$HOME_DIR"
[ -x .venv/bin/python ] || /data/bin/uv venv -q --python /usr/bin/python3 .venv
/data/bin/uv pip install -q --python .venv/bin/python "browser-use==${BROWSER_USE_VERSION}"

echo "MARITIME_AGENT_READY browser-use ${BROWSER_USE_VERSION}"
