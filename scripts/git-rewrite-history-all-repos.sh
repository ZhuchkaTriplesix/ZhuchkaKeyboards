#!/usr/bin/env bash
# Run git-rewrite-history.sh on monorepo root and every submodule path that is a git clone.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RUN="${1:-}"

run_one() {
  local dir="$1"
  if [ ! -d "$dir/.git" ]; then
    return 0
  fi
  echo "========== $(pwd) -> $dir =========="
  bash "$SCRIPT_DIR/git-rewrite-history.sh" "$dir"
}

if [ -n "$RUN" ]; then
  run_one "$RUN"
  exit 0
fi

run_one "$ROOT"
for d in "$ROOT"/services/* "$ROOT"/bots/* "$ROOT"/frontend/*; do
  [ -d "$d" ] || continue
  run_one "$d"
done

echo "Done. For each repo: git push --force-with-lease --all && git push --force-with-lease --tags"
