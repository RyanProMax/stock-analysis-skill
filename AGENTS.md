# Repository Guidelines

## Project Structure & Module Organization

这是一个根目录单一 `stock-analysis-skill` 仓库。当前只保留五类能力说明：

- `CLI 使用技能`：直接消费 `stock-analysis-api` 仓库中的内部 CLI
- `Futu/OpenD 使用技能`：`/hkipo` 与 `/research` 已用能力走 `stock-analysis-api` Futu CLI；盘口、逐笔、分时、期权链、账户、资金、持仓、订单、成交和流水等只读查询也走 API Futu CLI；其他尚未迁移能力明确标记为待 API provider 扩展，不再路由到外部 Futu skill
- `模拟盘 dry-run 使用技能`：只在用户明确要求模拟盘自动化、回放或链路验证时调用 `stock-analysis-api/scripts/trading_run_once.py`；默认 dry-run broker；定时轮询调用 `stock-analysis-api/scripts/trading_scheduler_tick.py`；盘后总结和策略候选评审调用 `trading_daily_summary.py` / `trading_strategy_review.py`；历史 K 线回测调用 `trading_strategy_backtest.py`；连接 Futu 模拟盘必须显式使用 `--broker futu-simulate`
- `Tushare 使用技能`：保留 Tushare 本地工具与接口参考资产
- `Slash Commands`：通过 `commands.json` + `commands/*.py` 暴露单票研报与 IPO 池类命令

核心文件如下：

- `SKILL.md`: skill 元数据与智能体使用说明
- `commands.json`: skill command 声明
- `commands/*.py`: slash command 执行入口
- `scripts/tushare_toolkit.py`: `.env` 加载、Tushare 初始化、代码标准化与参考文档生成
- `references/cli.md`: CLI 使用说明、JSON 结构、汇总规则、固定模板
- `references/research.md`: `/research` 单票深度研报模板、市场路由、降级与 Sources 规范
- `references/api_reference.md`: Tushare 接口总表
- `references/futu.md`: Futu/OpenD 路由与输出 Contract
- `PLANS/ROADMAP.md`: 跨轮次长期跟进项与整合路线
- `PLANS/ACTIVE.md`: 当前复杂任务目标、milestone、验证与 handoff
- `.env.example`: 本地环境变量模板

当前架构要点：

- 当前仓库不是行情 / 分析实现源
- 标准化 quote / analyze 能力统一直接消费 `stock-analysis-api`：
  - `scripts/poll_realtime_quotes.py`
  - `scripts/stock_analyze.py`
- 单票分析、单票研报摘要、A 股标准化实时行情默认先走 CLI，不先走 Futu 或 Tushare
- `/hkipo` 与 `/research` 用到的 Futu/OpenD 只读能力默认路由到 `stock-analysis-api/scripts/futu_market_data.py`
- 港 / 美 / 多市场盘口、逐笔、分时、期权链、账户、资金、持仓、订单、成交和流水只读查询默认路由到 `stock-analysis-api/scripts/futu_market_data.py`
- 模拟盘 dry-run 自动化默认路由到 `stock-analysis-api/scripts/trading_run_once.py`；cron / launchd / Agent 高频调用默认路由到 `stock-analysis-api/scripts/trading_scheduler_tick.py`；盘后总结和策略候选评审默认路由到 API `trading_daily_summary.py` / `trading_strategy_review.py`；历史 K 线回测默认路由到 API `trading_strategy_backtest.py`；Futu 模拟盘执行必须显式 `--broker futu-simulate`；本 skill 不实现真实交易或自动应用策略
- 窝轮 / 牛熊证、资金流、资金分布、经纪队列、板块与成分股、条件选股、期货资料等尚未迁移能力默认返回“尚未迁入 API”，不得绕回外部 Futu skill
- `/research` 与 IPO 池类命令允许通过 `commands.json` + `commands/*.py` 暴露；复杂研究型 command 优先输出结构化提示词，由宿主 Agent 继续完成联网分析
- `/research` A 股 / 美股命令由 executor 优先按 `STOCK_ANALYSIS_API_ROOT`、再按 skill 安装目录附近的 sibling `stock-analysis-api` 解析绝对 CLI；找不到时必须在 prompt 中显式预检失败并降级
- 本仓库不再维护对应 wrapper 脚本
- Tushare 本地辅助能力统一收口到 `scripts/tushare_toolkit.py`
- `references/cli.md` 是唯一 CLI 使用说明
- `references/api_reference.md` 是唯一 Tushare 接口总表
- Futu/OpenD 能力不在本仓库实现；`/hkipo` / `/research` 已迁移能力通过 API 仓库 CLI，其他能力等待 `stock-analysis-api` provider 扩展。本仓库不复制富途脚本、不保存交易密码；通过本 skill 默认只允许查询操作，禁止下单、改单、撤单、订阅、交易解锁或任何写入类行为。模拟盘 dry-run 是唯一写入例外，只允许写 API 侧 dry-run ledger，不允许真实交易

## Task Workflow

每次任务都必须遵循下面的顺序：

1. 所有任务统一使用 `PLANS/`；先看 `PLANS/ROADMAP.md`，再更新 `PLANS/ACTIVE.md`。
2. 若 `PLANS/ACTIVE.md` 不存在，先创建；不要再使用 `docs/plan.md`。
3. `PLANS/ACTIVE.md` 是复杂任务执行期间的单一真相源；一次只允许一个 milestone 处于 `in_progress`。
4. 实现过程中持续回填 active plan 的 `Progress` 和 `Validation`；未完成但需跨轮次追踪的事项同步回写 `PLANS/ROADMAP.md`。
5. 任务完成后，重新梳理当前项目架构并按需更新到本文件。
6. 每次完成任务必须提交一次 commit，不把多个已完成任务混在同一个 commit 里；若上层执行环境禁止自动提交，则在收尾说明中明确未提交。

## Timezone Convention

- 面向用户展示任务时间、轮询时间、下一次运行时间时，默认使用北京时间（Asia/Shanghai, UTC+8）。
- 若底层调度或数据库存储使用 UTC，回复用户时必须转换为北京时间并标注“北京时间”。

## Build, Test, and Development Commands

- `python -m venv .venv && source .venv/bin/activate`: 创建本地虚拟环境
- `python -m pip install -r requirements.txt`: 安装运行依赖
- `python -m py_compile scripts/*.py commands/*.py`: 快速语法校验
- `python scripts/tushare_toolkit.py generate-docs`: 根据本地 CSV 重新生成 `references/api_reference.md`
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`: 调用 API 仓库 realtime quote CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty`: 调用 API 仓库客观分析 CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/futu_market_data.py ipo-list --market HK --json`: 调用 API 仓库 Futu/OpenD 只读 CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/futu_market_data.py order-book --code HK.00700 --num 10 --json`: 调用 API 仓库 Futu/OpenD 盘口只读 CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/futu_market_data.py positions --market HK --code HK.00700 --json`: 调用 API 仓库 Futu/OpenD 持仓只读 CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/trading_daily_summary.py --date 2026-05-07 --pretty`: 调用 API 仓库模拟盘盘后总结 CLI，默认只输出 summary-only 关键信息
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/trading_strategy_review.py --date 2026-05-07 --min-runs 3 --pretty`: 调用 API 仓库策略候选评审 CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/trading_strategy_backtest.py --codes HK.00700 --buy-above HK.00700=100 --start 2026-05-01 --end 2026-05-07 --pretty`: 调用 API 仓库历史 K 线回测 CLI

## Testing Guidelines

当前以 `unittest` 覆盖 slash command / 回测脚本，以 `py_compile` 做快速语法校验。每次改动至少完成以下验证：

- 运行 `python -m py_compile scripts/*.py commands/*.py`
- 若修改了 Tushare 工具脚本，运行 `python scripts/tushare_toolkit.py generate-docs`
- 设置 `STOCK_ANALYSIS_API_ROOT` 后，至少执行一次：
  - `uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`
  - `uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty`
- 检查 `README.md`、`SKILL.md`、`AGENTS.md`、`commands.json` 对命令、字段和固定模板的描述一致

## Coding Style & Naming Conventions

遵循现有 Python 风格：

- 4 空格缩进
- 函数与变量使用 `snake_case`
- 公共辅助函数保留简短 docstring
- 用户可见文本以中文为主，保持术语一致
- 本仓库不新增 CLI wrapper；如需新增本地脚本，优先证明无法直接通过 API 仓库 CLI 满足需求
- 本地辅助能力优先集中在 `scripts/tushare_toolkit.py`

## Commit & Pull Request Guidelines

提交信息保持短而直接，优先中文动宾结构。一次提交只解决一个已完成任务。PR 需要说明：

- 改了什么能力或结构
- 是否更新了 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`
- 是否影响 `SKILL.md` / `references/cli.md` / `references/api_reference.md`
- 若改了 CLI 使用说明，附一段对应命令示例

## Security & Configuration Tips

不要提交真实 `TUSHARE_TOKEN`、本地导出数据或 IDE/Agent 私有状态。`.env` 只在本地使用，仓库中只保留 `.env.example`。`data/` 视为本地输入目录，不默认提交。
