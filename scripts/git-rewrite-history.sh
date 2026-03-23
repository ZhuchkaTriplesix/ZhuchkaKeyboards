#!/usr/bin/env bash
# Rewrites all refs: normalize author/committer for matching emails, strip "Made-with: Cursor" from messages.
# Usage:
#   bash scripts/git-rewrite-history.sh              # monorepo root (parent of scripts/)
#   bash scripts/git-rewrite-history.sh /path/to/repo # any clone (e.g. submodule)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -n "${1:-}" ]; then
  cd "$1"
else
  cd "$SCRIPT_DIR/.."
fi
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "skip $(pwd): no commits"
  exit 0
fi

export FILTER_BRANCH_SQUELCH_WARNING=1

# Use if/or instead of case: '+' in case patterns can mis-match on some sh builds.
git filter-branch -f \
  --env-filter '
CORRECT_NAME=$(git config user.name)
CORRECT_EMAIL=$(git config user.email)
if [ "$GIT_AUTHOR_EMAIL" = "mrlololoshka94@gmail.com" ] || [ "$GIT_AUTHOR_EMAIL" = "114882226+ZhuchkaTriplesix@users.noreply.github.com" ]; then
  export GIT_AUTHOR_NAME="$CORRECT_NAME"
  export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_COMMITTER_EMAIL" = "mrlololoshka94@gmail.com" ] || [ "$GIT_COMMITTER_EMAIL" = "114882226+ZhuchkaTriplesix@users.noreply.github.com" ]; then
  export GIT_COMMITTER_NAME="$CORRECT_NAME"
  export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
' \
  --msg-filter "sed -e '/^Made-with: Cursor$/d'" \
  -- --all
