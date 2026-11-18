#!/bin/bash
# Fetch compare diffs between consecutive release tags.
# Writes one JSON per pair: /tmp/magpie_data/diffs/<prev..tag>.json
TOKEN=$(cat /tmp/magpie_data/.tok)
mkdir -p /tmp/magpie_data/diffs

# Build the ordered tag list once, from the fetched pages.
python3 /tmp/magpie_data/build_pairs.py > /tmp/magpie_data/pairs.txt || exit 1
TOTAL=$(wc -l < /tmp/magpie_data/pairs.txt)
echo "pairs=$TOTAL"

fetch_pair() {
  line=$1
  prev=${line%% *}
  tag=${line##* }
  out="/tmp/magpie_data/diffs/$tag.json"
  [ -s "$out" ] && return 0
  for attempt in 1 2 3 4; do
    curl -s --http1.1 --compressed --max-time 60 \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/yetone/magpie/compare/$prev...$tag" -o "$out" 2>/dev/null
    # Valid response has a "files" key or a "message" (e.g. no common ancestor).
    if grep -q '"sha"' "$out" 2>/dev/null; then
      return 0
    fi
    sleep 2
  done
  echo "PAIR $prev..$tag FAILED" >&2
  rm -f "$out"
  return 1
}
export -f fetch_pair
export TOKEN

cat /tmp/magpie_data/pairs.txt | xargs -P 8 -I{} bash -c 'fetch_pair "{}"'
echo "DONE diffs=$(ls /tmp/magpie_data/diffs/*.json 2>/dev/null | wc -l)"
