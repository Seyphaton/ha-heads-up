#!/usr/bin/env bash
# Build dist/heads_up.zip: the contents of custom_components/heads_up/ at the zip root
# (manifest.json at the top level), as `zip_release` in hacs.json expects.
# Usage: scripts/build_release_zip.sh [expected-version]
# With an expected version (the release tag without "v"), the build fails if manifest.json differs.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
src="$root/custom_components/heads_up"
out="$root/dist/heads_up.zip"

version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$src/manifest.json")"
if [ -n "${1:-}" ] && [ "$1" != "$version" ]; then
  echo "manifest.json version $version does not match $1" >&2
  exit 1
fi

mkdir -p "$root/dist"
rm -f "$out"
(cd "$src" && zip -qr -X "$out" . -x '*__pycache__*' '*.pyc' '*.DS_Store')

listing="$(unzip -l "$out")"
grep -q ' manifest.json$' <<<"$listing" || { echo "manifest.json is not at the zip root" >&2; exit 1; }
echo "Built $out (version $version)"
