#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="${REPO_ROOT}/vendor/open-fpl-solver"
UPSTREAM_URL="https://github.com/solioanalytics/open-fpl-solver.git"
TMP_CLONE=$(mktemp -d)
trap 'rm -rf "${TMP_CLONE}"' EXIT

echo "Fetching open-fpl-solver from upstream (${UPSTREAM_URL})..."
git clone --depth 1 "${UPSTREAM_URL}" "${TMP_CLONE}"

cd "${TMP_CLONE}"
COMMIT_HASH=$(git rev-parse --short HEAD)
COMMIT_DATE=$(git log -1 --format=%cd --date=short)

mkdir -p "${VENDOR_DIR}"
rm -rf "${VENDOR_DIR:?}"/*
cp -R "${TMP_CLONE}/"* "${VENDOR_DIR}/"
rm -rf "${VENDOR_DIR}/.git"

echo "commit ${COMMIT_HASH} (${COMMIT_DATE})" > "${VENDOR_DIR}/UPSTREAM_VERSION"
echo "✓ open-fpl-solver synced successfully: commit ${COMMIT_HASH} (${COMMIT_DATE})"
