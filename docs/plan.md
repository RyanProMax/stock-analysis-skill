# Task Plan

## Task

实现 Tushare-first 研报策略脚本，并为未来多源降级保留 provider 骨架。

## Goal

新增面向外部 Agent 的 `scripts/poll_research_snapshot.py`，当前只消费 Tushare、只支持 CN 股票、只输出纯结构化 JSON；同时统一行情与研报脚本的身份 schema，并保留未来多数据源按优先级降级的扩展点。完成后提交一次独立 commit。

## Planned Changes

- [x] 更新当前任务计划与执行进度
- [ ] 在 `scripts/tushare_toolkit.py` 中补充统一 identity schema、provider 骨架和 research fetch helpers
- [ ] 新增 `scripts/poll_research_snapshot.py`
- [ ] 调整 `scripts/poll_realtime_quotes.py` 以复用新的 identity contract
- [ ] 更新 `README.md` / `SKILL.md` / `AGENTS.md` 中对研报脚本与策略边界的说明
- [ ] 运行语法检查与真实 Tushare 查询验证
- [ ] 提交一次独立 commit

## Progress

- 2026-03-28: 已确认当前仓库基本是 Tushare-only，但研报能力仍主要停留在 `SKILL.md` 的高层流程说明里，尚未脚本化。
- 2026-03-28: 已确认 `report_rc` 和 `research_report` 能作为 CN 股票研报策略的核心源；`anns_d`、`news`、`major_news` 可能存在权限限制。
- 2026-03-28: 已确认本次迁移不包含 Agent 主观分析，只迁移 hardcode workflow、schema、时间窗、排序、去重和确定性衍生规则。
- 2026-03-28: 已确认未来多源策略采用“按源优先级降级、首个可用源即停止、不做跨源字段合并”。

## Validation

- 待执行 `python3 -m py_compile scripts/*.py`
- 待执行 `python3 scripts/poll_research_snapshot.py --symbols 600000 --pretty`
- 待执行 `python3 scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`
- 待检查文档中不再把研报能力描述成自由发挥式 Agent 分析

## Completion Notes

- 待完成
