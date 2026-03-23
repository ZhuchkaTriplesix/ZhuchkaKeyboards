#!/usr/bin/env bash
# Rewrites all refs: normalize author/committer for matching emails, strip "Made-with: Cursor" from messages.
# Run from repo root: bash scripts/git-rewrite-history.sh
set -euo pipefail
cd "$(dirname "$0")/.."

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
