#!/usr/bin/env python3
"""抓取 yetone/magpie 主仓库相邻 release 的 compare diff。"""
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

OUT = "/tmp/m2"
os.makedirs(f"{OUT}/diffs", exist_ok=True)
TOKEN = open("/tmp/magpie_data/.tok").read().strip()


def load_tags():
    rows = []
    for line in open(f"{OUT}/all.tsv"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2 and p[0].startswith("v0.1."):
            rows.append((p[0], p[1]))
    rows.sort(key=lambda r: r[1])
    return rows


def get(pair, tries=5):
    prev, cur = pair
    path = f"{OUT}/diffs/{cur}.json"
    if os.path.exists(path) and os.path.getsize(path) > 10:
        return cur, "cached"
    url = f"https://api.github.com/repos/yetone/magpie/compare/{prev}...{cur}"
    last = ""
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "magpie-analysis",
                **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
            })
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
            keep = {
                "total_commits": data.get("total_commits", 0),
                "files": [{"filename": f.get("filename", ""),
                           "additions": f.get("additions", 0),
                           "deletions": f.get("deletions", 0)}
                          for f in (data.get("files") or [])],
            }
            with open(path, "w") as f:
                json.dump(keep, f)
            return cur, len(keep["files"])
        except Exception as e:
            last = str(e)[:60]
            time.sleep(2 * (a + 1))
    return cur, f"FAIL {last}"


def main():
    tags = load_tags()
    pairs = list(zip([t[0] for t in tags], [t[0] for t in tags][1:]))
    print(f"共 {len(tags)} 个 release，{len(pairs)} 个 compare")
    done = 0
    fails = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (cur, res) in enumerate(ex.map(get, pairs), 1):
            if isinstance(res, str) and res.startswith("FAIL"):
                fails.append((cur, res))
            done += 1
            if i % 250 == 0:
                print(f"  {i}/{len(pairs)}  失败 {len(fails)}", flush=True)
    print(f"完成 {done}，失败 {len(fails)}")
    for c, r in fails[:20]:
        print(f"  {c}: {r}")
    with open(f"{OUT}/fails.txt", "w") as f:
        for c, r in fails:
            f.write(f"{c}\t{r}\n")


if __name__ == "__main__":
    main()
