#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

# Collect staged files (add/copy/modify/rename)
mapfile -t STAGED < <(git diff --cached --name-only --diff-filter=ACMR || true)
[ "${#STAGED[@]}" -eq 0 ] && exit 0

echo "🔍 [Prettier] Checking staged files..."
if ! npm run -s format:check -- "${STAGED[@]}"; then
  echo
  echo "🔧 [Prettier] Fixing staged files..."
  npm run -s format -- "${STAGED[@]}"

  echo
  echo "⚠️  [Prettier] Readd the fixed files to proceed with the commit."
  exit 1
fi

echo "✅ [Prettier] All staged files are properly formatted."
