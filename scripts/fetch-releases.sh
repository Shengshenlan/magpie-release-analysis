#!/bin/bash
# Fetch all release pages. HTTP/1.1 + compression + resume + parallel.
TOKEN=$(cat /tmp/magpie_data/.tok)
PAGES=$1
PAR=${2:-6}

fetch_one() {
  p=$1
  f="/tmp/magpie_data/pages/$p.tsv"
  raw="/tmp/magpie_data/pages/$p.raw"
  [ -s "$f" ] && return 0
  for attempt in 1 2 3 4 5; do
    curl -s --http1.1 --compressed --max-time 150 \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/yetone/magpie-releases/releases?per_page=100&page=$p" \
      -o "$raw" 2>/dev/null
    if python3 /tmp/magpie_data/parse_page.py "$raw" "$f" 2>/dev/null; then
      rm -f "$raw"
      return 0
    fi
    sleep 5
  done
  echo "PAGE $p FAILED" >&2
  return 1
}
export -f fetch_one
export TOKEN

seq 1 "$PAGES" | xargs -P "$PAR" -I{} bash -c 'fetch_one {}'
echo "DONE pages=$(ls /tmp/magpie_data/pages/*.tsv 2>/dev/null | wc -l)"
