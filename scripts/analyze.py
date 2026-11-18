#!/usr/bin/env python3
"""分析 yetone/magpie 主仓库 3,043 个 release。"""
import json, glob, os, csv, statistics, collections

SRC = "/tmp/m2"
OUT = "/tmp/m2/out"
os.makedirs(OUT, exist_ok=True)


def module_of(path):
    if path.startswith("internal/"):
        parts = path.split("/")
        return "internal/" + parts[1] if len(parts) > 2 else "internal"
    for p in ("docs", "site", "plugins", "native", "build", "third_party"):
        if path.startswith(p + "/"):
            return p
    if path.startswith(".github/"):
        return ".github"
    if "/" not in path:
        return "(root)"
    return path.split("/")[0]


def load():
    rows = [l.rstrip("\n").split("\t") for l in open(f"{SRC}/all.tsv")]
    rows = [r for r in rows if len(r) >= 2 and r[0].startswith("v0.1.")]
    rows.sort(key=lambda r: r[1])
    tags = [(r[0], r[1]) for r in rows]
    diffs = {}
    for f in glob.glob(f"{SRC}/diffs/*.json"):
        tag = os.path.basename(f)[:-5]
        try:
            diffs[tag] = json.load(open(f))
        except Exception:
            pass
    return tags, diffs


def main():
    tags, diffs = load()
    rows, missing = [], []
    for tag, ts in tags:
        d = diffs.get(tag)
        if d is None:
            missing.append(tag)
            continue
        paths = [f["filename"] for f in d["files"] if f.get("filename")]
        mods = sorted({module_of(p) for p in paths})
        rows.append({
            "tag": tag, "ts": ts, "day": ts[:10],
            "commits": d["total_commits"], "files": len(paths),
            "add": sum(f["additions"] for f in d["files"]),
            "del": sum(f["deletions"] for f in d["files"]),
            "modules": mods, "nmods": len(mods),
        })

    print(f"release {len(tags)}，有 diff {len(rows)}，缺 {len(missing)}")
    if missing:
        print("  缺:", ", ".join(missing[:10]))

    days = sorted({r["day"] for r in rows})
    by_day = collections.defaultdict(list)
    for r in rows:
        by_day[r["day"]].append(r)

    # 三阶段：按日均发布量找转折点
    print("\n每日 release 数:")
    for d in days:
        print(f"  {d}  {len(by_day[d]):>4}  文件均值 {statistics.mean([x['files'] for x in by_day[d]]):>5.1f}"
              f"  模块均值 {statistics.mean([x['nmods'] for x in by_day[d]]):>4.2f}")

    modc = collections.Counter()
    for r in rows:
        for m in r["modules"]:
            modc[m] += 1
    dist = collections.Counter(min(r["nmods"], 9) for r in rows)
    one = sum(1 for r in rows if r["commits"] == 1)
    n = len(rows)

    summary = {
        "source": "github.com/yetone/magpie",
        "counts": {"releases": len(tags), "with_diff": n, "missing": missing,
                   "days": len(days), "first": days[0], "last": days[-1]},
        "overall": {
            "total_commits": sum(r["commits"] for r in rows),
            "median_files": statistics.median(r["files"] for r in rows),
            "mean_files": round(statistics.mean(r["files"] for r in rows), 2),
            "median_modules": statistics.median(r["nmods"] for r in rows),
            "mean_modules": round(statistics.mean(r["nmods"] for r in rows), 2),
            "single_commit_pct": round(one / n * 100, 1),
            "one_two_modules_pct": round((dist[1] + dist[2]) / n * 100, 1),
            "within_five_pct": round(sum(dist[i] for i in range(1, 6)) / n * 100, 1),
        },
        "module_distribution": {("1" if k == 1 else "2" if k == 2 else "3" if k == 3 else
                                 "4" if k == 4 else "5" if k == 5 else "6-8" if k <= 8 else "9+"): v
                                for k, v in sorted(dist.items())},
        "daily": {
            "days": days,
            "releases": [len(by_day[d]) for d in days],
            "avg_files": [round(statistics.mean([x["files"] for x in by_day[d]]), 1) for d in days],
            "avg_modules": [round(statistics.mean([x["nmods"] for x in by_day[d]]), 2) for d in days],
        },
        "top_modules": [{"module": m, "count": c} for m, c in modc.most_common(15)],
    }

    with open(f"{OUT}/summary.json", "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(f"{OUT}/releases.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tag", "published_at", "day", "commits", "files",
                    "additions", "deletions", "module_count", "modules"])
        for r in rows:
            w.writerow([r["tag"], r["ts"], r["day"], r["commits"], r["files"],
                        r["add"], r["del"], r["nmods"], "|".join(r["modules"])])
    with open(f"{OUT}/dataset.json", "w") as f:
        json.dump({"summary": summary, "releases": rows}, f, ensure_ascii=False)

    print(f"\n=== 总计 ===")
    print(f"release {len(tags)}  commit {summary['overall']['total_commits']}")
    print(f"文件中位 {summary['overall']['median_files']}  模块中位 {summary['overall']['median_modules']}")
    print(f"单commit {summary['overall']['single_commit_pct']}%  1-2模块 {summary['overall']['one_two_modules_pct']}%")
    print("\n模块 Top10:")
    for m in summary["top_modules"][:10]:
        print(f"  {m['module']:<24} {m['count']}")


if __name__ == "__main__":
    main()
