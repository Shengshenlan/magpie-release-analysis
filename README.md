# magpie 的 3,039 次 release

`yetone/magpie` 自述「code is written, reviewed, merged and released by agents」——代码由 AI agent 编写、评审、合并和发布。

这里拆的是 **2026-10-11 → 11-18** 这 38 天里，主仓库 `yetone/magpie` 全部 **3,039 个 release** 背后真实的代码改动。

> 数据抓取于 **2026-11-18**。最后一个是 `v0.1.4404`（2026-11-18 02:27 UTC）。

## 先看这几个数

| | |
|---|---|
| release 数 | **3,039**（38 天） |
| main 分支 commit | **8,625**（截至 2026-11-18） |
| 每次改动的文件数 | 中位 **6**，均值 11.8 |
| 每次改动的模块数 | 中位 **2**，均值 3.0 |
| 只含 1 个提交的发布 | **55.2%** |
| 只碰 1~2 个模块 | **47.0%** |
| 碰到模块数 ≤5 | **79.3%** |

关于 commit：8,625 是 main 分支的全部提交；其中 **6,627** 落在这 3,038 个 release 的相邻 `compare` 之间。差额来自首个 release（`v0.1.1194`）之前的历史，那部分没有对应的 release 记录。

## 两个阶段

按 10-23 这个转折点切开：

| | P1 · 10-11 → 10-22 | P2 · 10-23 → 11-18 |
|---|---|---|
| 天数 | 12 | 27 |
| 发布数 | 129 | 2,909 |
| 日均 | 10.8 | 107.7 |
| 文件/次（中位） | **27** | **6** |
| 模块/次（中位） | **7** | **2** |

前 12 天每天只发十来个版本，单次却动 27 个文件、7 个模块；之后每天一百多个，单次压到 6 个文件、2 个模块。

**改得越少，发得越多。**

## 图片

| 文件 | 内容 |
|---|---|
| [`images/1-封面.png`](images/1-封面.png) | 标题 + 四个 KPI + 每日发布柱状图 |
| [`images/2-文件数.png`](images/2-文件数.png) | 每日平均改动文件数（对数刻度） |
| [`images/3-模块数.png`](images/3-模块数.png) | 每日平均跨模块数 + 模块跨度占比 |
| [`images/4-两阶段与文档.png`](images/4-两阶段与文档.png) | 两阶段对照 + 模块频次排行 |
| [`images/5-规范矛盾.png`](images/5-规范矛盾.png) | 规范原文与实测对照 |
| [`images/06-poster-long.png`](images/06-poster-long.png) | 以上合成一张长图（2320×9936） |

## 数据

在 [`out/`](out/) 下：

- **`summary.json`** — 全部聚合指标、阶段拆分、模块分布
- **`releases.csv`** — 3,038 行，每个 release 的 commits / files / additions / deletions / 模块数 / 模块清单
- **`releases-index.tsv`** — 3,043 条原始 release 索引（tag、发布时间、asset 数）
- **`dataset.json`** — summary + 全部 release 明细

三维度指标：**每天发多少个** / **每次动多少文件** / **每次横跨多少模块**。

## 方法

1. 拉主仓库全部 release 列表（31 页 × 100，共 3,043 条，含 4 个 `pf-v*` 预发布标签）。
2. 按发布时间排序，对相邻两个 tag 调用 `GET /repos/yetone/magpie/compare/{prev}...{tag}`。
3. 取 `total_commits` 和 `files[]` 的真实路径、增删行数。
4. 模块 = `internal/` 下的一级子包，加上 `docs` / `site` / `plugins` 等顶层目录。

3,038 个 compare 全部成功，零失败。首个版本 `v0.1.1194` 没有前置可比，单独剔除。

脚本在 [`scripts/`](scripts/) 下：`fetch-releases.py`、`fetch-diffs.py`、`analyze.py`、`poster.html`。

## 局限

- **时间关联不等于因果。** 10-23 之后形态收敛，只能说时间上吻合，无法排除其他混杂因素（比如这个时间点可能同时发生了别的变化）。
- **主仓库 release 从 `v0.1.1194` 开始**（10-11）。更早的版本号（v0.1.0 ~ v0.1.1193）在主仓库没有 release 记录，所以这里只有后半段。
- **版本号有断档。** 3,039 个 v0.1.x 里缺了 172 个编号，可能是没有发 release 的中间版本。
- **release 密度 ≠ 工作量。** 一个 release 可能只是一个 commit 的自动构建。
- **模块划分是近似的。** `internal/` 下的一级子包不一定等于真实的架构边界。

## License

MIT
