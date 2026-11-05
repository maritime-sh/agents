#!/usr/bin/env bash
# Installs the goose CLI on a Maritime Linux desktop. Runs inside the computer.
# Everything lives under /data, which survives sleep, wake and restarts.
set -euo pipefail

GOOSE_VERSION="v1.57.0"   # pinned upstream release (github.com/aaif-goose/goose/releases)
GOOSE_SHA256="10eb96cb6a159b6e1d38eeedbef6ab64cd28168aad91948f1fa5c34eefdf98e3"
HOME_DIR=/data/agents/goose

mkdir -p "$HOME_DIR/bin" "$HOME_DIR/work"
cd "$HOME_DIR"
if [ ! -x bin/goose ] || ! bin/goose --version 2>/dev/null | grep -q "${GOOSE_VERSION#v}"; then
  curl -fsSL -o goose.tar.gz \
    "https://github.com/aaif-goose/goose/releases/download/${GOOSE_VERSION}/goose-x86_64-unknown-linux-gnu.tar.gz"
  echo "${GOOSE_SHA256}  goose.tar.gz" | sha256sum -c -
  tar -xzf goose.tar.gz -C bin
  rm goose.tar.gz
  chmod +x bin/goose
fi
chmod +x "$HOME_DIR/run.sh"

echo "MARITIME_AGENT_READY goose $(bin/goose --version | tr -d '\n')"
