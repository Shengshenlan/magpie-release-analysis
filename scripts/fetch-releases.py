#!/usr/bin/env python3
"""抓取 yetone/magpie 主仓库的全部 release 列表。"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

OUT = "/tmp/m2"
os.makedirs(f"{OUT}/pages", exist_ok=True)
os.makedirs(f"{OUT}/raw", exist_ok=True)
TOKEN = open("/tmp/magpie_data/.tok").read().strip() if os.path.exists("/tmp/magpie_data/.tok") else ""


def get(page, tries=6):
    path = f"{OUT}/pages/{page}.tsv"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return page, "cached"
    url = f"https://api.github.com/repos/yetone/magpie/releases?per_page=100&page={page}"
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "magpie-analysis",
                **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
            })
            with urllib.request.urlopen(req, timeout=150) as r:
                data = json.loads(r.read())
            with open(path, "w") as f:
                for rel in data:
                    f.write(f"{rel['tag_name']}\t{rel['published_at']}\t{len(rel.get('assets', []))}\n")
            return page, len(data)
        except Exception as e:
            last = str(e)[:80]
            time.sleep(3 * (a + 1))
    return page, f"FAIL {last}"


pages = list(range(1, 32))
with ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(get, pages))

ok = sum(1 for _, r in results if isinstance(r, int))
print(f"成功 {ok}/{len(pages)} 页")
for p, r in results:
    if not isinstance(r, int) or r < 100:
        print(f"  page {p}: {r}")
