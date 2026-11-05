#!/usr/bin/env bash
# Installs Open Interpreter on a Maritime Linux desktop. Runs inside the computer.
# Everything lives under /data, which survives sleep, wake and restarts.
set -euo pipefail

OPEN_INTERPRETER_VERSION="0.4.3"   # pinned upstream release (pypi.org/project/open-interpreter), the last Python release
UV_VERSION="0.9.5"
HOME_DIR=/data/agents/open-interpreter

mkdir -p "$HOME_DIR" /data/bin
export UV_CACHE_DIR=/data/.uv-cache UV_PYTHON_INSTALL_DIR=/data/.uv-python

if [ ! -x /data/bin/uv ]; then
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | env UV_INSTALL_DIR=/data/bin UV_NO_MODIFY_PATH=1 sh
fi

cd "$HOME_DIR"
# Open Interpreter 0.4.x supports Python up to 3.12; uv fetches 3.12 into /data.
[ -x .venv/bin/python ] || /data/bin/uv venv -q --python 3.12 .venv
# setuptools 80 still ships pkg_resources, which Open Interpreter 0.4.3 imports at start.
# pip and matplotlib in the same environment, so the code it writes can install and plot.
/data/bin/uv pip install -q --python .venv/bin/python "open-interpreter==${OPEN_INTERPRETER_VERSION}" \
  "setuptools==80.9.0" pip matplotlib
chmod +x run.sh session.sh

echo "MARITIME_AGENT_READY open-interpreter ${OPEN_INTERPRETER_VERSION}"
