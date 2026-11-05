#!/usr/bin/env bash
# Installs browser-use Web UI on a Maritime Linux desktop. Runs inside the computer.
# Everything lives under /data, which survives sleep, wake and restarts.
set -euo pipefail

WEB_UI_VERSION="3.0.0"   # pinned upstream release tag (github.com/browser-use/web-ui/releases)
PYTHON_VERSION="3.11"    # the version upstream's Dockerfile uses
UV_VERSION="0.9.5"
HOME_DIR=/data/agents/browser-use-web-ui

mkdir -p "$HOME_DIR" /data/bin
export UV_CACHE_DIR=/data/.uv-cache UV_PYTHON_INSTALL_DIR=/data/python

if [ ! -x /data/bin/uv ]; then
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | env UV_INSTALL_DIR=/data/bin UV_NO_MODIFY_PATH=1 sh
fi

cd "$HOME_DIR"
if [ ! -f "web-ui-${WEB_UI_VERSION}/webui.py" ]; then
  curl -LsSf "https://github.com/browser-use/web-ui/archive/refs/tags/v${WEB_UI_VERSION}.tar.gz" | tar xz
fi
[ -x .venv/bin/python ] || /data/bin/uv venv -q --python "$PYTHON_VERSION" .venv
/data/bin/uv pip install -q --python .venv/bin/python -c constraints.txt -r "web-ui-${WEB_UI_VERSION}/requirements.txt"

echo "MARITIME_AGENT_READY browser-use-web-ui ${WEB_UI_VERSION}"
