#!/usr/bin/env python3
"""
整理 magpie release 分析数据，输出干净可用的文件。

输入（已有）:
  /tmp/magpie_data/pages/*.tsv    release 列表 (tag, published_at)
  /tmp/magpie_data/diffs/*.json   compare API 原始响应

输出到 ~/magpie-data/out/:
  releases.csv    每个 release 一行：tag, 时间, commit数, 文件数, 增删行, 模块数, 模块列表
  daily.csv       每天一行：日期, release数, 平均文件数, 平均模块数
  modules.csv     模块频率排行
  phases.csv      三阶段汇总
  summary.json    关键数字汇总（给图表脚本用）
  dataset.json    完整明细（含文件路径）
"""

import json, glob, os, csv, statistics, collections, datetime

SRC = "/tmp/magpie_data"
OUT = os.path.expanduser("~/magpie-data/out")
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


def load_releases():
    seen = {}
    for f in glob.glob(f"{SRC}/pages/*.tsv"):
        for line in open(f):
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or not parts[0].startswith("v0.1."):
                continue
            seen[parts[0]] = parts[1]

    def vkey(t):
        try:
            return int(t.split(".")[-1])
        except ValueError:
            return -1
    return [(t, seen[t]) for t in sorted(seen, key=vkey)]


def load_diffs():
    out = {}
    for f in glob.glob(f"{SRC}/diffs/*.json"):
        tag = os.path.basename(f)[:-5]
        try:
            d = json.load(open(f))
        except Exception:
            continue
        files = d.get("files") or []
        paths = [x.get("filename", "") for x in files]
        mods = sorted({module_of(p) for p in paths if p})
        out[tag] = {
            "commits": d.get("total_commits", 0),
            "files": len(files),
            "add": sum(x.get("additions", 0) for x in files),
            "del": sum(x.get("deletions", 0) for x in files),
            "modules": mods,
            "nmods": len(mods),
            "paths": paths,
        }
    return out


def phase_of(day):
    if day <= "2026-10-05":
        return "P1 堆功能"
    if day <= "2026-10-22":
        return "P2 规范建设"
    return "P3 稳定高频"


def main():
    rel = load_releases()
    diffs = load_diffs()

    rows = []
    missing = []
    for tag, ts in rel:
        d = diffs.get(tag)
        if not d:
            missing.append(tag)
            continue
        rows.append({
            "tag": tag, "ts": ts, "day": ts[:10], "phase": phase_of(ts[:10]),
            **d,
        })

    print(f"release 总数 {len(rel)}，有 diff 数据 {len(rows)}，缺失 {len(missing)}")
    if missing:
        print("  缺失（无共同祖先，已排除）:", ", ".join(missing))

    # ── releases.csv ──
    with open(f"{OUT}/releases.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tag", "published_at", "day", "phase", "commits",
                    "files", "additions", "deletions", "module_count", "modules"])
        for r in rows:
            w.writerow([r["tag"], r["ts"], r["day"], r["phase"], r["commits"],
                        r["files"], r["add"], r["del"], r["nmods"], "|".join(r["modules"])])

    # ── daily.csv ──
    by_day = collections.defaultdict(list)
    for r in rows:
        by_day[r["day"]].append(r)
    days = sorted(by_day)
    with open(f"{OUT}/daily.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["day", "phase", "releases", "avg_files", "avg_modules",
                    "median_files", "median_modules"])
        for d in days:
            g = by_day[d]
            w.writerow([d, phase_of(d), len(g),
                        round(statistics.mean(x["files"] for x in g), 2),
                        round(statistics.mean(x["nmods"] for x in g), 2),
                        statistics.median(x["files"] for x in g),
                        statistics.median(x["nmods"] for x in g)])

    # ── modules.csv ──
    modc = collections.Counter()
    for r in rows:
        for m in r["modules"]:
            modc[m] += 1
    with open(f"{OUT}/modules.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["module", "release_count", "pct_of_releases"])
        for m, c in modc.most_common():
            w.writerow([m, c, round(c / len(rows) * 100, 2)])

    # ── phases.csv ──
    ph = collections.defaultdict(list)
    for r in rows:
        ph[r["phase"]].append(r)
    with open(f"{OUT}/phases.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phase", "days", "releases", "median_files", "median_modules",
                    "avg_modules", "mean_files"])
        for k in sorted(ph):
            g = ph[k]
            ds = len({x["day"] for x in g})
            w.writerow([k, ds, len(g),
                        statistics.median(x["files"] for x in g),
                        statistics.median(x["nmods"] for x in g),
                        round(statistics.mean(x["nmods"] for x in g), 2),
                        round(statistics.mean(x["files"] for x in g), 2)])

    # ── 分布 ──
    mod_dist = collections.Counter(min(r["nmods"], 9) for r in rows)
    one_commit = sum(1 for r in rows if r["commits"] == 1)

    summary = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "source": {
            "releases": "github.com/yetone/magpie-releases",
            "diffs": "github.com/yetone/magpie compare API",
        },
        "counts": {
            "releases_total": len(rel),
            "releases_with_diff": len(rows),
            "releases_missing_diff": missing,
            "days": len(days),
            "first_day": days[0],
            "last_day": days[-1],
        },
        "overall": {
            "median_files": statistics.median(r["files"] for r in rows),
            "mean_files": round(statistics.mean(r["files"] for r in rows), 2),
            "median_modules": statistics.median(r["nmods"] for r in rows),
            "mean_modules": round(statistics.mean(r["nmods"] for r in rows), 2),
            "single_commit_pct": round(one_commit / len(rows) * 100, 1),
            "one_or_two_modules_pct": round(
                (mod_dist[1] + mod_dist[2]) / len(rows) * 100, 1),
            "within_five_modules_pct": round(
                sum(mod_dist[i] for i in range(1, 6)) / len(rows) * 100, 1),
        },
        "module_distribution": {
            ("1" if k == 1 else "2" if k == 2 else "3" if k == 3 else
             "4" if k == 4 else "5" if k == 5 else "6-8" if k <= 8 else "9+"): v
            for k, v in sorted(mod_dist.items())
        },
        "daily_series": {
            "days": days,
            "releases": [len(by_day[d]) for d in days],
            "avg_files": [round(statistics.mean(x["files"] for x in by_day[d]), 1) for d in days],
            "avg_modules": [round(statistics.mean(x["nmods"] for x in by_day[d]), 2) for d in days],
        },
        "phases": {
            k: {
                "days": len({x["day"] for x in g}),
                "releases": len(g),
                "median_files": statistics.median(x["files"] for x in g),
                "median_modules": statistics.median(x["nmods"] for x in g),
                "avg_modules": round(statistics.mean(x["nmods"] for x in g), 2),
            } for k, g in sorted(ph.items())
        },
        "top_modules": [{"module": m, "count": c} for m, c in modc.most_common(15)],
    }

    with open(f"{OUT}/summary.json", "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # ── dataset.json（完整明细）──
    with open(f"{OUT}/dataset.json", "w") as f:
        json.dump({"summary": summary, "releases": rows}, f, ensure_ascii=False)

    print(f"\n已写入 {OUT}/")
    for fn in sorted(os.listdir(OUT)):
        size = os.path.getsize(f"{OUT}/{fn}")
        print(f"  {fn:16} {size/1024:>8.1f} KB")

    print("\n关键数字:")
    o = summary["overall"]
    print(f"  文件数  中位 {o['median_files']}  均值 {o['mean_files']}")
    print(f"  模块数  中位 {o['median_modules']}  均值 {o['mean_modules']}")
    print(f"  单 commit 占比 {o['single_commit_pct']}%")
    print(f"  1~2 模块占比 {o['one_or_two_modules_pct']}%  5 个以内 {o['within_five_modules_pct']}%")
    for k, v in summary["phases"].items():
        print(f"  {k}: {v['releases']} 个 / {v['days']} 天, "
              f"文件中位 {v['median_files']}, 模块中位 {v['median_modules']}")


if __name__ == "__main__":
    main()
