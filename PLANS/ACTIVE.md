# Active Plan

> 本文件是当前复杂任务的单一真相源。一次只允许一个 milestone 处于 `in_progress`。

## Task

把富途 OpenAPI skills 的能力纳入 `stock-analysis-skill` 的统一规划，并建立与 Cli Claw 风格一致的 `PLANS/ROADMAP.md` + `PLANS/ACTIVE.md` 工作流入口。

## Context

- 当前仓库仍是 skill 路由与说明仓库，不承担行情 / 分析实现。
- 已安装外部 skills：`futuapi`、`install-futu-opend`。
- 当前 A 股标准化实时行情和客观分析仍由 `stock-analysis-api` CLI 提供。
- 富途能力覆盖行情、盘口、K 线、期权、账户、持仓、订单、订阅和交易。
- 对用户展示任务时间时，默认使用北京时间（Asia/Shanghai, UTC+8）。

## Milestones

### M1 — 建立计划入口

Status: `done`

Scope:

- 创建 `PLANS/ROADMAP.md`
- 创建 `PLANS/ACTIVE.md`
- 移除旧 `docs/plan.md`，统一使用 `PLANS/`
- 更新 `AGENTS.md`，说明新计划入口与北京时间口径

Validation:

- `test -f PLANS/ROADMAP.md && test -f PLANS/ACTIVE.md`
- `python3 -m py_compile scripts/*.py commands/*.py`
- 人工检查 `AGENTS.md` / `README.md` / `SKILL.md` / `PLANS/*.md` 职责不冲突

### M2 — 设计 Futu 路由矩阵

Status: `done`

Scope:

- 在 `SKILL.md` 增加 Futu/OpenD 路由优先级
- 明确 `stock-analysis-api`、Tushare、Futu 三者边界
- 定义交易 / 账户能力的安全确认要求

Validation:

- 文档一致性检查：`SKILL.md`、`README.md`、`AGENTS.md`、`PLANS/ROADMAP.md`
- 若涉及示例命令，只使用只读行情脚本验证，不触发实盘交易

### M3 — 统一输出 contract

Status: `done`

Scope:

- 定义 quote snapshot、watch alert、option chain、portfolio risk、trade intent 输出模板
- 明确 ratio / percent、时区、数据源降级和异常表达
- 给出 watchlist 全量快照 + 异动 emoji 的固定模板

Validation:

- 用当前 A 股 watchlist 场景复核模板可读性
- 确认不输出主观买卖建议、目标价或交易密码相关内容

### M4 — Watchlist 自动选路

Status: `done`

Scope:

- 设计 `poll_realtime_quotes.py` 与 `futuapi get_stock_quote/get_snapshot` 的选择规则
- 明确混合市场 watchlist 的 batch 拆分和合并输出
- 明确失败、降级和用户要求剔除未纳入标的时的表达

Validation:

- 文档一致性检查：`SKILL.md`、`README.md`、`references/cli.md`、`references/futu.md`、`PLANS/ROADMAP.md`
- 不触发真实 Futu/OpenD 交易或订阅


### M5 — 强化 hkipo 评分与回测工作流

Status: `done`

Scope:

- 更新 `SKILL.md` 的 `/hkipo` 边界说明
- 更新 `commands/hkipo.py` 输出的研究 prompt
- 新增 `references/hkipo.md`，沉淀评分、绿鞋与回测校准规则

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/hkipo.py <<< '{}'`
- 人工检查 `SKILL.md` / `commands/hkipo.py` / `references/hkipo.md` 一致

Progress:

- 2026-04-27：根据用户反馈，已将 `/hkipo` 从长报告模板升级为评分卡 + 简报 + 绿鞋/基石 + 首日回测校准工作流。
- 2026-04-27：进一步移除“简评”章节，将维度整合进总览表，并加入融资倍数热度与暗盘修正规则；极端融资/暗盘样本会把首日赔率评分上修。


### M6 — 港股 IPO 近 100 样本回测 MVP

Status: `done`

Scope:

- 新增 `scripts/hkipo_backtest.py`，从公开 IPO 列表抓取近期已上市港股 IPO 样本并输出分桶回测
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md`，说明回测工具的输入、输出和限制
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录本轮进展

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 scripts/hkipo_backtest.py --limit 20 --source aastocks --format markdown`
- 人工检查输出包含样本数、首日胜率、平均/中位涨幅、破发率和热度分桶

Progress:

- 2026-04-27：用户确认开始实现自动回测 MVP；优先使用 AAStocks Listed IPO 页面，因为其公开字段含上市日、发行价、超购倍数、一手中签率和首日涨幅。
- 2026-04-27：100 样本回测已跑通：有效首日涨幅 97 个，胜率 75.3%，中位首日涨幅 16.22%，>=1000x 超购分桶胜率 92.2%、中位首日涨幅 75.53%。

## Progress

- 2026-04-27：移除旧 `docs/plan.md`，统一使用 `PLANS/`。
- 2026-04-27：确认用户要求后续任务时间改用北京时间展示。
- 2026-04-27：开始创建 `PLANS/ROADMAP.md` 与 `PLANS/ACTIVE.md`，并把富途整合纳入长期 roadmap。
- 2026-04-27：已在 `SKILL.md` / `README.md` / `AGENTS.md` 增加 Futu/OpenD 路由优先级、边界和交易安全要求。
- 2026-04-27：新增 `references/futu.md`，定义 quote snapshot、watch alert、option chain、portfolio risk、trade intent contract。
- 2026-04-27：补充 watchlist 自动选路规则：A 股轻量轮询走 `poll_realtime_quotes.py`，混合市场 / 盘口 / 订阅 / 持仓联动走 `futuapi`。

## Validation

- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 20 --source aastocks --format markdown`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`
- 已通过：人工检查 `SKILL.md` / `README.md` / `commands/hkipo.py` / `references/hkipo.md` 的 `/hkipo` 评分、绿鞋、回测和简明输出规则一致
- 已通过：`test ! -e docs/plan.md && test -f PLANS/ROADMAP.md && test -f PLANS/ACTIVE.md && test -f references/futu.md`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：人工检查 `AGENTS.md` / `README.md` / `SKILL.md` / `PLANS/*.md` / `references/futu.md` 职责不冲突
- 已通过：确认 `PLANS/ACTIVE.md` 中没有进行中的 milestone

## Handoff

- M1 已完成：计划入口、北京时间口径与富途整合 roadmap 均已落盘。
- 2026-04-27：用户要求移除 `docs/plan.md`，后续统一使用 `PLANS/`。
- 2026-04-27：M2 已完成：`SKILL.md` / `README.md` / `AGENTS.md` 已同步 Futu/OpenD 路由矩阵与安全边界。
- M3 已完成：统一输出 contract 已落到 `references/futu.md`。
- M4 已完成：watchlist 自动选路规则已落到 `references/futu.md`，并同步 `SKILL.md` / `README.md` / `references/cli.md`。
- M5 已完成：`/hkipo` 已升级为评分卡 + 简明报告 + 绿鞋/基石 + 首日回测校准工作流，并新增 `references/hkipo.md`。
- M6 已完成：新增 `scripts/hkipo_backtest.py`，可抓取 AAStocks 近期已上市港股 IPO 并输出首日表现分桶回测。
- 下一轮可开始实现具体调用封装，或补只读 Futu/OpenD 环境验证。
