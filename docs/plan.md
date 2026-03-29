# Task Plan

## Task

将仓库从 “Tushare-only 轮询实现仓库” 收口为 `stock-analysis-skill`，只保留：

- `CLI 使用技能`
- `Tushare 使用技能`

## Goal

- 删除本地 quote wrapper，标准化客观分析 / 实时 quote 统一直接消费 `stock-analysis-api`
- 将仓库命名、文档和职责统一收口到 `stock-analysis-skill`
- 保留 `scripts/tushare_toolkit.py` 与 `references/api_reference.md`
- 新增 `references/cli.md`，统一记录 CLI 命令、JSON 结构、汇总规则和固定模板

## Planned Changes

- [x] 更新当前任务计划与执行进度
- [x] 删除 `scripts/poll_realtime_quotes.py`
- [x] 精简 `requirements.txt`
- [x] 更新 `.env.example`
- [x] 重写 `README.md`
- [x] 重写 `SKILL.md`
- [x] 重写 `AGENTS.md`
- [x] 新增 `references/cli.md`
- [ ] 运行语法检查与真实命令验证
- [ ] 提交一次独立 commit

## Progress

- 2026-03-29: 已确认标准化 quote / analyze 的唯一实现源改为 `stock-analysis-api`，本仓库不再维护 wrapper。
- 2026-03-29: 已确认 `Tushare 使用技能` 继续保留 `scripts/tushare_toolkit.py` 与 `references/api_reference.md`。
- 2026-03-29: 已确认本仓库改名为 `stock-analysis-skill`，并采用“单一 skill、双能力模式”。
- 2026-03-29: 已移除本地 `scripts/poll_realtime_quotes.py`，文档改为直接调用 `STOCK_ANALYSIS_API_ROOT` 下的 CLI。

## Validation

- 待执行 `python -m py_compile scripts/*.py`
- 待执行 `python scripts/tushare_toolkit.py generate-docs`
- 待执行：
  - `cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`
  - `cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty`
- 待检查 `README.md` / `SKILL.md` / `AGENTS.md` / `references/cli.md` 对仓库职责表述一致

## Completion Notes

- 待完成
