#!/usr/bin/env python3
"""Parse one page of releases JSON into a tag<TAB>published_at tsv."""
import json, sys

raw, out = sys.argv[1], sys.argv[2]
try:
    data = json.load(open(raw))
except Exception:
    sys.exit(1)
if not isinstance(data, list):
    sys.exit(1)
with open(out, "w") as f:
    for r in data:
        f.write(f"{r['tag_name']}\t{r['published_at']}\n")
sys.exit(0)
