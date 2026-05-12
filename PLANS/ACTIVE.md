# Active Plan

> 本文件是当前复杂任务的单一真相源。一次只允许一个 milestone 处于 `in_progress`。

## Current Task — `/otc` 港股暗盘单次与轮询指令

Goal:

- 新增 `/otc <HK symbol>` slash command，支持单次查询，例如 `/otc 07666.HK`。
- 支持 `/otc 07666.HK --loop=300s` 映射到 API 侧 scheduler tick，代表 5 分钟轮询间隔。
- command 入口必须先校验北京时间暗盘窗口；非暗盘时间直接返回提示，不继续调用 API。
- 保持只读安全边界：不下单、不订阅、不交易解锁、不写券商状态；仅允许 API 侧 scheduler tick 节流状态。

Allowed scope:

- `commands.json`
- `commands/otc.py`
- `tests/test_otc_command.py`
- `SKILL.md`
- `README.md`
- `AGENTS.md`
- `references/cli.md`
- `references/futu.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest tests.test_otc_command -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 -m unittest discover -s tests -v`
- `git diff --check`

### M46 — OTC slash command

Status: `done`

Progress:

- 2026-05-12 北京时间：用户要求新增 `/otc 07666.HK` 单次查询和 `/otc 07666.HK --loop=300s` 轮询查询，并在非暗盘时段直接结束提示。
- 2026-05-12 北京时间：API 侧已补 `grey_market_watch.py --once` contract，单次查询不读写 scheduler tick 状态；默认 tick 模式继续按 `--interval-seconds` 节流。
- 2026-05-12 北京时间：已新增 `commands/otc.py`、注册 `commands.json`，支持 `07666.HK` / `HK.07666` 归一化为 `HK.07666`，并在暗盘窗口外直接返回 final markdown，不生成 API 命令。
- 2026-05-12 北京时间：已同步 `SKILL.md`、`README.md`、`AGENTS.md`、`references/cli.md`、`references/futu.md` 和 roadmap，固定 `/otc` 单次 / 轮询语义和只读边界。

Validation status:

- passed 2026-05-12 北京时间：
  - API: `uv run python -m pytest tests/test_grey_market_watch_cli.py`
  - API: `uv run black --check --line-length 100 --target-version py312 scripts/grey_market_watch.py src/services/grey_market_watch_cli.py src/services/grey_market_watch_service.py tests/test_grey_market_watch_cli.py`
  - API: `uv run python -m py_compile scripts/grey_market_watch.py src/services/grey_market_watch_cli.py src/services/grey_market_watch_service.py`
  - API: `uv run python scripts/grey_market_watch.py --once --code HK.07666 --now 2026-05-12T15:00:00+08:00 --json` 返回 `outside_active_window`
  - skill: `python3 -m unittest tests.test_otc_command -v`
  - skill: `python3 -m unittest discover -s tests -v`
  - skill: `python3 -m py_compile scripts/*.py commands/*.py`
  - `git diff --check`

Review status:

- passed 2026-05-12 北京时间：diff 只增加 `/otc` slash command、API `--once` contract、对应文档和回归测试；没有新增下单、订阅、交易解锁或券商写入路径。`--once` 不打开 SQLite state DB；轮询 tick 保持原 scheduler 节流状态。

Handoff:

- `/otc 07666.HK` 会在北京时间 `16:15-18:30` 内生成 API `grey_market_watch.py --once --code HK.07666` 单次查询；窗口外直接提示下次窗口。
- `/otc 07666.HK --loop=300s` 会生成 `grey_market_watch.py --code HK.07666 --interval-seconds 300` 轮询 tick；宿主若支持定时任务，应按该间隔重复触发，API 会用 state DB 节流。

### M45 — HK grey-market watch routing

Status: `done`

Progress:

- 2026-05-12 北京时间：用户确认通过 API 和 skill 结合使用，并要求支持定时任务查询。
- 2026-05-12 北京时间：本轮约束为 skill 不复制实现，API 负责 `grey_market_watch.py`；skill 只补路由、输出 contract 和安全边界。
- 2026-05-12 北京时间：已同步 `SKILL.md`、`references/cli.md`、`references/futu.md`、`README.md`、`AGENTS.md` 和 roadmap，固定暗盘 watch 路由与 provider capability 语义。

Validation status:

- passed 2026-05-12 北京时间：
  - `python3 -m py_compile scripts/*.py commands/*.py`
  - `python3 -m unittest discover -s tests -v`
  - `git diff --check`

Review status:

- passed 2026-05-12 北京时间：diff 只增加灰市 / 暗盘 watch 路由说明、CLI 示例、只读定时任务状态边界和 roadmap/active plan 更新；未改变 slash command 执行逻辑。

Handoff:

- 港股 IPO 暗盘 / OTC 查询以后默认走 `stock-analysis-api/scripts/grey_market_watch.py`；Futu 有正式 provider，Tiger / 复星等未接入正式授权 API 的 provider 只返回 `unsupported`，不要网页抓取或伪造“所有券商”报价。

---

## Previous Task — `/hkipo` 多源实时热度聚合

Goal:

- 修复 `/hkipo` 热度链路过度依赖单一券商页面的问题；当辉立、Futu CLI 或任一来源拿不到最新数据时，必须自动扩展到多家权威信源。
- 在 command prompt、skill 入口说明、README 和 `references/hkipo.md` 中统一要求每只开放认购 IPO 必须做当日多源最新热度聚合；不能用单一旧口径或单一券商下限替代当前主评分。

Allowed scope:

- `commands/hkipo.py`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest tests.test_hkipo_command -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

### M44 — HK IPO multi-source latest heat aggregation

Status: `done`

Progress:

- 2026-05-12 北京时间：用户指出翼菲科技 Futu App 当前热度已到约 4700x，而上一轮报告仍使用辉立单一券商 21 亿 / 约 56x 口径；根因是 prompt 虽要求同日复核，但没有禁止在权威更新源缺失时死用单一券商下限。
- 2026-05-12 北京时间：本轮目标是把“多权威源优先拿最新、单源失败即扩源、Futu CLI 不暴露 App 热度时必须查 Futu App/牛牛圈/TradeGo/华盛/老虎/AAStocks/ETNet/智通/格隆汇等同日源”写成硬约束，并补回归测试。
- 2026-05-12 北京时间：已新增回归测试锁定多权威机构最新热度聚合、Futu CLI 不暴露 App 热度时继续扩源、不得把单一券商孖展下限当作全市场主热度。
- 2026-05-12 北京时间：已更新 `commands/hkipo.py`、`SKILL.md`、`README.md` 和 `references/hkipo.md`，把热度核验顺序调整为 Futu/OpenD + Futu App / 牛牛 → 同日多券商汇总 / 全市场聚合 → 单券商孖展表 → 财经门户 → 暗盘。

Validation status:

- passed 2026-05-12 北京时间：
  - `python3 -m unittest tests.test_hkipo_command -v`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/*.py commands/*.py`
  - `git diff --check`

Review status:

- passed 2026-05-12 北京时间：diff 只收紧 `/hkipo` 热度来源聚合规则、对应 prompt/reference/README/SKILL 文案和回归测试；未改变 Futu/OpenD 只读基础池命令、输出格式或其他 slash command 行为。

Handoff:

- `/hkipo` 以后不能在辉立、耀才等单一券商页面拿不到最新全市场口径时继续沿用单券商下限；必须扩源到 Futu/牛牛、TradeGo / 活报告、多券商孖展统计、AAStocks、ETNet、智通 / 新浪、格隆汇、华盛、老虎等同日源，并优先使用同日多券商汇总 / 全市场聚合最新值。

### M43 — HK IPO heat freshness hard gate

Status: `done`

Progress:

- 2026-05-12 北京时间：用户反馈翼菲科技当日孖展倍率已快速更新到 2800x+，上一轮报告仍使用 5/11 的 218x，说明现有 prompt 对“最接近报告日”过于宽松。
- 2026-05-12 北京时间：根因定位为 `/hkipo` freshness gate 没有强制开放认购中 IPO 的同日多源复核，也没有在热度缺失时要求重试和扩大来源。
- 2026-05-12 北京时间：新增 `/hkipo` prompt / reference 回归测试，锁定同日热度硬门槛、至少 3 类权威来源、自动重试和旧数据不得主评分。
- 2026-05-12 北京时间：同步 `commands/hkipo.py`、`SKILL.md` 和 `references/hkipo.md`，要求开放认购中的 IPO 用同日券商新股中心 / 孖展表、财经门户新股频道、主流行情 App 或官方时间表扩源复查；拿不到当日热度时写“热度未达当日核验门槛”。

Validation status:

- passed 2026-05-12 北京时间：
  - `python3 -m unittest tests.test_hkipo_command -v`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/*.py commands/*.py`
  - `git diff --check`

Review status:

- passed 2026-05-12 北京时间：diff 只改 `/hkipo` prompt contract、对应 reference / skill 说明、回归测试和计划文件；未改变 Futu/OpenD 只读入口、输出格式或其他 slash command 行为。

Handoff:

- `/hkipo` 后续报告遇到开放认购 IPO 时，前一日孖展 / 公开认购 / 暗盘数据只能作趋势，不得进入 Subscription Heat 主评分；若当日多源复查失败，必须显式写“热度未达当日核验门槛”。

---

## Task

把富途 OpenAPI skills 的能力纳入 `stock-analysis-skill` 的统一规划，并建立与 Cli Claw 风格一致的 `PLANS/ROADMAP.md` + `PLANS/ACTIVE.md` 工作流入口。

## Context

- 当前仓库仍是 skill 路由与说明仓库，不承担行情 / 分析实现。
- 已安装外部 skills：`futuapi`、`install-futu-opend`。
- 当前 A 股标准化实时行情和客观分析仍由 `stock-analysis-api` CLI 提供。
- 富途能力覆盖行情、盘口、K 线、期权、账户、持仓、订单、订阅和交易。
- 对用户展示任务时间时，默认使用北京时间（Asia/Shanghai, UTC+8）。

## Milestones

### M42 — API Futu 只读 provider 扩展与安全回归

Status: `done`

Scope:

- `SKILL.md`
- `README.md`
- `AGENTS.md`
- `references/cli.md`
- `references/futu.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`
- API: `src/data_provider/sources/futu.py`
- API: `src/services/futu_market_data_cli.py`
- API: `tests/test_futu_market_data_cli.py`
- API: `README.md`
- API: `docs/architecture.md`
- API: `docs/plan.md`
- API: `docs/specs/futu-internal-cli-contract.md`
- API: `docs/specs/skill-cli-contract.md`

Validation:

- API targeted：`uv run python -m pytest tests/test_futu_market_data_cli.py`
- API broker regression：`uv run python -m pytest tests/test_futu_simulate_broker.py tests/test_trading_run_once_cli.py tests/test_trading_automation.py`
- API full：`uv run python -m pytest`
- API format：`uv run black --check --line-length 100 --target-version py312 scripts src tests`
- API diff check：`git diff --check`
- skill：`python3 -m unittest discover -s tests -v`
- skill：`python3 -m py_compile scripts/*.py commands/*.py`
- skill：`git diff --check`

Progress:

- 2026-05-07 北京时间：扩展 API `scripts/futu_market_data.py`，新增盘口、逐笔、分时、期权到期日、期权链、Futu `SIMULATE` 账户、持仓、订单、成交和流水只读查询子命令。
- 2026-05-07 北京时间：补充 Futu 只读 CLI contract 测试和安全回归，确保 CLI 不暴露 `place-order`、`modify-order`、`cancel-order`、`unlock-trade`、`subscribe` 等写入类子命令。
- 2026-05-07 北京时间：同步 skill 路由说明，明确这些能力已迁入 API，不再返回“尚未迁入 API”，也不绕回外部 Futu skill。

Validation status:

- passed 2026-05-07 北京时间：
  - API targeted：`uv run python -m pytest tests/test_futu_market_data_cli.py tests/test_futu_simulate_broker.py tests/test_trading_run_once_cli.py tests/test_trading_automation.py`
  - API full：`uv run python -m pytest`
  - API format：`uv run black --check --line-length 100 --target-version py312 scripts src tests`
  - API diff check：`git diff --check`
  - skill：`python3 -m unittest discover -s tests -v`
  - skill：`python3 -m py_compile scripts/*.py commands/*.py`
  - skill：`git diff --check`

Handoff:

- `futu_market_data.py` 现在覆盖高频 Futu/OpenD 只读查询，不再需要外部 Futu skill 承接盘口、逐笔、分时、期权链、账户、持仓、订单、成交或流水查询。
- 账户、持仓、订单、成交和流水查询固定为 Futu `SIMULATE` 只读路径；CLI 未暴露写入类子命令。
- 尚未迁入范围收窄为窝轮 / 牛熊证、资金流、资金分布、经纪队列、板块与成分股、条件选股、期货资料等长尾只读能力。

### M41 — API 盘后总结 summary-only 输出收口

Status: `done`

Scope:

- `SKILL.md`
- `README.md`
- `references/cli.md`
- `AGENTS.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest discover -s tests -v`
- `git diff --check`
- API full：`uv run python -m pytest`
- API format：`uv run black --check --line-length 100 --target-version py312 scripts src tests`
- API diff check：`git diff --check`

Progress:

- 2026-05-07 北京时间：API `trading_daily_summary.py` 默认改为 summary-only，只保留盘后总结必要字段；`orders` / `risk_decisions` / `runs` 明细必须显式 `--include-details` 才输出。
- 本轮同步 skill 路由与 CLI reference，要求面向用户默认消费 summary-only，不原样转贴 ledger 明细。

Validation status:

- passed 2026-05-07 北京时间：
  - API full：`uv run python -m pytest`
  - API format：`uv run black --check --line-length 100 --target-version py312 scripts src tests`
  - API diff check：`git diff --check`
  - skill：`python3 -m unittest discover -s tests -v`
  - skill：`git diff --check`

Handoff:

- 盘后总结 CLI 仍然只读 API 侧 SQLite ledger，不进入盘中执行链路。
- 默认输出遵循最小必要原则；只有排障或内部评审需要时才使用 `--include-details`。
- 策略评审内部仍显式读取明细做 ledger replay，但 proposal 不自动应用策略、不写配置、不触发 broker。

### M40 — API 历史 K 线回测入口路由说明收口

Status: `done`

Scope:

- `SKILL.md`
- `README.md`
- `references/cli.md`
- `AGENTS.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- API targeted：`trading_strategy_backtest.py` unit + script entrypoint tests
- API full：`uv run python -m pytest`

Progress:

- 2026-05-07 北京时间：API 已新增 `trading_strategy_backtest.py`，支持注入 K 线 JSON 或 Futu 历史 K 线，对固定 threshold 策略做离线回测；本轮同步 skill 路由说明，明确它和 `ledger_snapshot_replay` 是不同口径。

Validation status:

- passed 2026-05-07 北京时间：
  - API targeted：`uv run python -m pytest tests/test_trading_strategy_backtest_cli.py tests/test_trading_strategy_backtest_e2e.py`
  - API full：`uv run python -m pytest`
  - API format / syntax：`uv run black --check ...`、`uv run python -m py_compile ...`、`git diff --check`
  - skill：`python3 -m unittest discover -s tests -v`
  - skill：`python3 -m py_compile scripts/*.py commands/*.py`
  - skill：`git diff --check`

Handoff:

- skill 已明确历史 K 线回测走 API `scripts/trading_strategy_backtest.py`。
- 该入口与 `trading_strategy_review.py` 的 `ledger_snapshot_replay` 口径不同：backtest 读历史 K 线，review 读 ledger。
- 回测入口不读写 ledger，不触发 broker，不应用策略。

### M39 — API Futu SIMULATE broker 路由说明收口

Status: `done`

Scope:

- `SKILL.md`
- `README.md`
- `references/cli.md`
- `AGENTS.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- API full：`uv run python -m pytest`
- 安全检查：API Futu SIMULATE broker 源码不封装 `unlock_trade`

Progress:

- 2026-05-07 北京时间：API 已新增显式 opt-in 的 `--broker futu-simulate`；本轮同步 skill 说明，明确默认仍为 dry-run，Futu SIMULATE 只在用户明确要求连接模拟盘时使用，且不能和 `--snapshots-json` 混用。

Validation status:

- passed 2026-05-07 北京时间：
  - API targeted：`uv run python -m pytest tests/test_futu_simulate_broker.py tests/test_trading_scheduler_tick_cli.py tests/test_trading_run_once_cli.py tests/test_trading_automation.py`
  - API full：`uv run python -m pytest`
  - API format / syntax：`uv run black --check ...`、`uv run python -m py_compile ...`、`git diff --check`
  - API safety check：`rg -n "unlock_trade|TrdUnlock|unlock" ...` 只命中文档中的禁止说明，没有代码调用。
  - skill：`python3 -m unittest discover -s tests -v`
  - skill：`python3 -m py_compile scripts/*.py commands/*.py`
  - skill：`git diff --check`

Handoff:

- skill 已明确默认 broker 仍为 dry-run。
- 只有用户明确要求连接 Futu 模拟盘执行时才使用 `--broker futu-simulate`。
- Futu 模拟盘路径固定 `TrdEnv.SIMULATE`，禁止 `unlock_trade`，并且不能和 `--snapshots-json` 混用。

### M38 — API 盘后总结与策略评审路由说明收口

Status: `done`

Scope:

- `SKILL.md`
- `README.md`
- `references/cli.md`
- `AGENTS.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- API CLI smoke：`trading_run_once.py` 写入 ledger 后，`trading_daily_summary.py` 与 `trading_strategy_review.py` 读取同一 ledger 输出严格 JSON

Progress:

- 2026-05-07 北京时间：API 已新增 `trading_daily_summary.py` 与 `trading_strategy_review.py`；本轮同步 skill 路由说明，明确盘后总结和策略候选评审走 API CLI，skill 不新增 wrapper，不放开真实交易或自动应用策略。

Validation status:

- passed 2026-05-07 北京时间：
  - API targeted：`uv run python -m pytest tests/test_trading_daily_summary_cli.py tests/test_trading_strategy_review_cli.py tests/test_trading_post_market_e2e.py tests/test_trading_scheduler_tick_cli.py tests/test_trading_run_once_cli.py tests/test_trading_automation.py`
  - API full：`uv run python -m pytest`
  - API format / syntax：`uv run black --check ...`、`uv run python -m py_compile ...`、`git diff --check`
  - API CLI smoke：`trading_run_once.py` 写入临时 ledger 后，`trading_daily_summary.py` 与 `trading_strategy_review.py` 读取同一 ledger，三段 stdout 均为严格 JSON。
  - skill：`python3 -m unittest discover -s tests -v`
  - skill：`python3 -m py_compile scripts/*.py commands/*.py`（普通沙箱无法写 `__pycache__`，已按权限流程提升后重跑）
  - skill：`git diff --check`

Handoff:

- skill 现在把模拟盘盘后总结路由到 API `scripts/trading_daily_summary.py`。
- skill 现在把策略候选评审路由到 API `scripts/trading_strategy_review.py`。
- `strategy_proposal` 明确是候选产物：`approval_required=true`，不会自动写运行时策略、调度 state 或 broker。

### M37 — API scheduler tick 路由说明收口

Status: `done`

Scope:

- `SKILL.md`
- `README.md`
- `references/cli.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- API CLI smoke：`scripts/trading_scheduler_tick.py` 输出严格 JSON

Progress:

- 2026-05-07 北京时间：API 已新增 `trading_scheduler_tick.py` 调度 tick；本轮同步 skill 路由说明，明确 cron / launchd / Agent 高频入口走 scheduler tick，单轮执行仍由 `trading_run_once.py` 负责。

Validation status:

- passed 2026-05-07 北京时间：
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/*.py commands/*.py`
  - `git diff --check`
  - API CLI smoke：`trading_scheduler_tick.py` 真实 Futu snapshot + dry-run broker 输出严格 JSON，stderr 为空。

Handoff:

- skill 现在把“定时轮询模拟盘”明确路由到 API `scripts/trading_scheduler_tick.py`。
- scheduler tick 只做时间窗、间隔和 state key 判断；到点后复用单轮 dry-run，不放开真实交易。

### M36 — API dry-run trading CLI 路由说明收口

Status: `done`

Scope:

- `SKILL.md`
- `README.md`
- `references/cli.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- API CLI smoke：`scripts/trading_run_once.py` dry-run 输出严格 JSON

Progress:

- 2026-05-07 北京时间：API 已新增 `trading_run_once.py` dry-run 模拟盘入口、SQLite ledger、严格 JSON 输出和默认调度锁；本轮同步 skill 路由说明，明确 skill 只指向 API dry-run CLI，不放开真实交易、交易解锁或订阅能力。

Validation status:

- passed 2026-05-07 北京时间：
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/*.py commands/*.py`（普通沙箱无法写 `__pycache__`，已按权限流程提升后重跑）
  - `git diff --check`
  - API CLI smoke：`trading_run_once.py` 真实 Futu snapshot + dry-run broker 输出严格 JSON，stderr 为空。

Handoff:

- skill 现在把模拟盘 dry-run 明确路由到 API `scripts/trading_run_once.py`。
- 该入口只允许 dry-run 模拟执行和审计，不放开真实下单、交易解锁、订阅或 OpenD 写入能力。

### M35 — /research 机构目标价披露边界

Status: `done`

Scope:

- 修正 `/research` prompt、reference 和入口说明中“目标价一概禁止”和“机构研报可汇总目标价但不得作为建议”的冲突
- 在“机构观点综合 / 权威机构研报汇总”中强制列出可核验的机构目标价、评级/观点、发布日期、来源和分歧
- 明确目标价只作为外部机构观点披露，不得作为本系统建议、交易指令、目标价字段或确定性承诺

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-06 北京时间：用户指出 SNDK 报告缺少权威机构目标价；定位到 prompt/reference 同时存在“不得把评级/目标价写成建议”和“完全不输出目标价”的冲突。
- 2026-05-06 北京时间：已将 `/research` prompt、`references/research.md`、`SKILL.md`、`README.md` 调整为：机构目标价必须列入机构观点综合，但只能作为带来源、日期、币种的外部观点，不得作为本系统建议。
- 2026-05-06 北京时间：已补测试覆盖 prompt/reference 对机构目标价、评级/观点和“不得作为本系统建议”的要求。

Validation status:

- passed 2026-05-06 北京时间：
  - `python3 -m unittest tests/test_research_command.py -v`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/*.py commands/*.py`（普通沙箱无法写 `__pycache__`，已按权限流程提升后重跑）
  - `git diff --check`

Review status:

- passed 2026-05-06 北京时间：人工复核 diff；改动只收敛 `/research` 机构目标价披露边界，没有放开买卖建议、系统目标价、`price_target` 字段或交易指令。

### M33 — 安装副本读取 skill `.env` 后调用 API Futu

Status: `done`

Scope:

- `commands/env_loader.py`
- `commands/hkipo.py`
- `commands/research.py`
- `tests/test_hkipo_command.py`
- `tests/test_research_command.py`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- Installed skill smoke:
  - `python3 commands/hkipo.py`
  - `python3 commands/research.py` with `HK.00700`

Progress:

- 2026-05-06 北京时间：用户反馈 Futu 再次不可用；初查确认 `stock-analysis-api/scripts/futu_market_data.py global-state`、`snapshot HK.00700`、`ipo-list --market HK` 均可正常调用，OpenD / API Futu CLI 本身可用。
- 2026-05-06 北京时间：安装副本直接执行 `/research HK.00700` 复现失败，错误为未找到 `stock-analysis-api Futu CLI`；根因是 command 脚本自身不读取安装目录 `.env`，脱离 dispatcher 或 dispatcher 环境异常时拿不到 `STOCK_ANALYSIS_API_ROOT`。

Validation results:

- passed 2026-05-06 北京时间：
  - `python3 -m unittest tests/test_hkipo_command.py tests/test_research_command.py`
  - `python3 -m unittest discover -s tests`
  - `python3 -m py_compile scripts/*.py commands/*.py`（普通沙箱无法写 `__pycache__`，已按权限流程提升后重跑）
  - `git diff --check`
  - 源码 `/research HK.00700` 真实 smoke：OpenD 预检通过，输出 API Futu `global-state` / `snapshot` / `kline` 入口。
  - 源码 `/hkipo` 真实 smoke：输出 API Futu `ipo-list --market HK --json` 入口。
  - 已同步到 Cli Claw 安装副本；安装副本 `/research HK.00700` 真实 smoke 通过，OpenD 预检通过。
  - 安装副本 `/hkipo` 真实 smoke 通过，输出 API Futu `ipo-list --market HK --json` 入口。
- passed review gate 2026-05-06 北京时间：仓库无 `scripts/review.sh`，已人工复核 diff；改动仅增加 command `.env` 读取与安装副本回归测试，不恢复外部 `futuapi` skill 调用链。

Handoff:

- Futu/OpenD 本身可用；本次故障是安装副本 command 环境没有稳定读取 `.env`，导致找不到迁移后的 `stock-analysis-api/scripts/futu_market_data.py`。
- `/hkipo` / `/research` 现在即使脱离 dispatcher 直接执行，也会先读取 skill 安装目录 `.env`，再解析 `STOCK_ANALYSIS_API_ROOT` / `STOCK_ANALYSIS_UV`。
- 已把 `commands/env_loader.py`、`commands/hkipo.py`、`commands/research.py` 同步到当前 Cli Claw 安装副本。

### M32 — /hkipo 与 /research 删除 futuapi 调用链残留

Status: `done`

Scope:

- `commands/hkipo.py`
- `commands/research.py`
- `tests/test_hkipo_command.py`
- `tests/test_research_command.py`
- `SKILL.md`
- `README.md`
- `AGENTS.md`
- `references/futu.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`
- `/Users/ryan/projects/stock-analysis-api/src/services/__init__.py`
- `/Users/ryan/projects/stock-analysis-api/tests/test_futu_market_data_cli.py`
- `/Users/ryan/projects/stock-analysis-api/docs/plan.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- `uv run python -m pytest tests/test_futu_market_data_cli.py`
- `uv run python -m py_compile scripts/futu_market_data.py src/services/__init__.py src/services/futu_market_data_cli.py`
- Real command smoke:
  - `python3 commands/hkipo.py`
  - `python3 commands/research.py` with `HK.00700`

Progress:

- 2026-05-06 北京时间：用户要求确认 `/hkipo` / `/research` 调用链是否仍有 `futuapi` skill，并要求用真实 command 链路输出验证，而不是只看 helper 函数。
- 2026-05-06 北京时间：初查确认 command 主路径已走 `stock-analysis-api/scripts/futu_market_data.py`，但 `SKILL.md` / README / reference / roadmap 仍保留“未迁移能力走 `futuapi` skill”的规划性 fallback，与最终删除 `futuapi` skill 的目标不一致。
- 2026-05-06 北京时间：新增 `/hkipo` 和 `/research HK.00700` 的真实 command 子进程回归测试，直接检查最终输出包含 API Futu CLI 命令且不包含外部 Futu skill 路由。
- 2026-05-06 北京时间：真实 `/research HK.00700` smoke 暴露 API Futu CLI import 会被 `src.services` eager import 带入 SQLite 行情仓初始化；已在 API 仓库改为 lazy export，Futu CLI import 不再触碰无关仓库。
- 2026-05-06 北京时间：同步 SKILL / README / AGENTS / references / ROADMAP，将未迁移 Futu 能力改为“待 API provider 扩展 / 暂未支持”，不再指向外部 Futu skill。

Validation results:

- passed 2026-05-06 北京时间：
  - `uv run python -m pytest tests/test_futu_market_data_cli.py`
  - `uv run python -m py_compile scripts/futu_market_data.py src/services/__init__.py src/services/futu_market_data_cli.py`
  - `python3 -m unittest tests/test_hkipo_command.py tests/test_research_command.py`
  - `python3 -m unittest discover -s tests`
  - `python3 -m py_compile scripts/*.py commands/*.py`（普通沙箱无法写 `__pycache__`，已按权限流程提升后重跑）
  - `git diff --check` in `stock-analysis-api`
  - `git diff --check` in `stock-analysis-skill`
  - `rg -n "futuapi|install-futu-opend|外部 skill|external skill|futuapi/scripts|quote/get_ipo_list|quote/get_global_state|find_futuapi|candidate_futuapi" commands SKILL.md README.md AGENTS.md references/futu.md references/research.md references/hkipo.md PLANS/ROADMAP.md` 无命中
- passed real smoke 2026-05-06 北京时间：
  - `uv run python scripts/futu_market_data.py global-state --json` returned `status=ok`, `source=futu_opend`, `qot_logined=true`.
  - `python3 commands/hkipo.py` emitted an `assistant_prompt` whose IPO list command is `stock-analysis-api/scripts/futu_market_data.py ipo-list --market HK --json`.
  - `python3 commands/research.py` with `HK.00700` emitted an `assistant_prompt`, OpenD preflight passed, and the prompt points to API `global-state` / `snapshot` / `kline`.

Handoff:

- `/hkipo` / `/research` 当前输出链路没有外部 Futu skill；只走 API Futu CLI。
- 未迁入 API 的 Futu 能力现在明确为暂未支持 / 待 API provider 扩展；不能再 fallback 到外部 Futu skill。
- API 侧 `src.services` lazy export 是为保证 `futu_market_data.py` 启动不初始化无关 SQLite 仓。

### M31 — /hkipo 与 /research Futu 能力迁移到 API

Status: `done`

Scope:

- `commands/hkipo.py`
- `commands/research.py`
- `scripts/hkipo_backtest.py`
- `tests/test_hkipo_command.py`
- `tests/test_research_command.py`
- `tests/test_hkipo_backtest.py`
- `SKILL.md`
- `README.md`
- `references/futu.md`
- `references/research.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py tests/test_research_command.py tests/test_hkipo_backtest.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-06 北京时间：用户要求先把 `/hkipo` 与 `/research` 用到的 Futu/OpenD 能力全量迁移到 `stock-analysis-api`。
- 2026-05-06 北京时间：确认迁移范围为 `/hkipo` IPO list、`/research` OpenD global-state 预检、HK IPO 回测历史日 K，以及港股研报 prompt 中引用的 snapshot 入口；不包含盘口、逐笔、分时、期权、账户、持仓和订单等尚未被这两个命令直接使用的能力。
- 2026-05-06 北京时间：已将 `/hkipo` IPO list 命令、`/research` 港股 OpenD 预检与 prompt 中的 snapshot/kline 入口，以及 `hkipo_backtest.py --debut-price-source futu-kline` 切换到 `stock-analysis-api/scripts/futu_market_data.py`。

Validation results:

- failed as expected 2026-05-06 北京时间：`python3 -m unittest tests/test_hkipo_command.py tests/test_research_command.py tests/test_hkipo_backtest.py`，新增测试证明旧实现仍调用外部 `futuapi` 脚本 / SDK。
- passed 2026-05-06 北京时间：`python3 -m unittest tests/test_hkipo_command.py tests/test_research_command.py tests/test_hkipo_backtest.py`
- passed 2026-05-06 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-06 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`（普通沙箱无法写 `__pycache__`，已按权限流程提升后重跑）
- passed 2026-05-06 北京时间：`git diff --check`
- passed 2026-05-06 北京时间：`rg -n "futuapi/scripts|quote/get_ipo_list|quote/get_global_state|find_futuapi|candidate_futuapi|FUTU_OPEND_PREFLIGHT_SCRIPT|FUTU_IPO_SCRIPT|from futu import" commands scripts tests SKILL.md README.md AGENTS.md references/futu.md references/research.md references/hkipo.md PLANS/ROADMAP.md` 无命中。
- passed 2026-05-06 北京时间：仓库无 `scripts/review.sh`，已按 review gate 人工复核 diff；确认 `/hkipo`、`/research` 与 HK IPO 回测主路径不再调用外部 `futuapi` 脚本，失败路径仍保留确认/降级门槛。

Handoff:

- `/hkipo` 当前 IPO 池改为生成 `stock-analysis-api/scripts/futu_market_data.py ipo-list --market HK --json` 的绝对 API CLI 命令。
- `/research` 显式港股 OpenD 预检改为 `scripts/futu_market_data.py global-state --json`；prompt 中的港股 snapshot / kline 入口也指向 API CLI。
- `scripts/hkipo_backtest.py --debut-price-source futu-kline` 改为通过 API CLI 拉首日 K 线；`--api-root` / `--uv` 可显式指定 API 仓库与 uv。
- 盘口、逐笔、分时、期权、账户、持仓和订单等尚未被 `/hkipo` / `/research` 直接使用的能力仍保留为后续迁移范围。

### M30 — /hkipo 极简正文与热度稳定性

Status: `done`

Scope:

- `commands/hkipo.py`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-05 北京时间：用户反馈 `/hkipo` 不需要 `申购冲突` 小节；个股标题末尾不要再写投资建议/跟踪标签，改成申购截止时间和开奖/配发日期，例如 `🟡 2｜01236 樂動機器人｜74｜5/6截止 | 5/7开奖`。
- 2026-05-05 北京时间：用户反馈正文空行仍过多；目标格式是 `💡 关键结论`、`📌 优先级`、个股条目、`🔗 来源` 紧凑连续，不在顶层小节之间插空白空行。
- 2026-05-05 北京时间：用户指出樂動機器人孖展倍数偶发不稳定；本轮把 prompt/reference 的热度取数规则从“可联网找补充”收紧为固定优先级、必须记录更新时间、旧数据只能降级、不可混用旧孖展作当前评分。

Validation results:

- failed as expected 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`，新增断言证明旧 prompt/reference 仍包含 `申购冲突` 小节、空白空行和标题尾部优先级标签。
- passed 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`
- passed 2026-05-05 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-05 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-05 北京时间：`git diff --check`
- passed 2026-05-05 北京时间：`rg -n "申购冲突|⏱|subscription conflict|同批次资金冲突|可先申购|重点跟踪|高优先级跟踪|投资建议" commands/hkipo.py SKILL.md README.md references/hkipo.md tests/test_hkipo_command.py` 仅命中测试中的反向断言。
- passed 2026-05-05 北京时间：`printf '{}' | python3 commands/hkipo.py | rg -n "输出格式|申购冲突|M/D截止|5/6截止|重点跟踪|投资建议|\\*\\*📌 优先级\\*\\*|\\*\\*🔗 来源\\*\\*|\\*\\*⏱"`，prompt 输出格式中只保留 `M/D截止 | M/D开奖`、紧凑 `📌 优先级` 与 `🔗 来源`，未出现 `申购冲突` 小节或旧建议标签。
- passed 2026-05-05 北京时间：仓库无 `scripts/review.sh`，已按 review checklist 人工复核 diff；scope 仅限 M30，prompt、SKILL、README、reference 和 tests 同步。

Handoff:

- `/hkipo` 正文契约已移除 `申购冲突` 小节；标题尾部改为 `M/D截止 | M/D开奖`；正文不再插空白空行。
- 熱度/孖展稳定性已在 prompt/reference 中收紧为固定来源顺序和更新时间门槛，避免不同搜索路径把旧孖展当成当前主评分。若仍要进一步提升稳定性，需要新增确定性抓取/缓存脚本，而不是继续依赖 agent 自由联网搜索。

### M29 — /hkipo 报告层级与紧凑字段修正

Status: `done`

Scope:

- `commands/hkipo.py`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-05 北京时间：用户反馈实际 `/hkipo` 飞书输出仍把 `申购冲突` 放在每只 IPO 字段块内，且 `阶段`、`热度`、`结构`、`回测`、`风险` 等小字段之间仍有大段空行。
- 2026-05-05 北京时间：确认根因是 M28 将旧模板契约重新固化到 prompt/reference：`申购冲突` 被写成每只 IPO 的重复字段，小字段也被要求逐项留空行。
- 2026-05-05 北京时间：本轮目标是把契约收敛为顶层 `**⏱ 申购冲突**` 小节，与 `💡 关键结论`、`📌 优先级` 同级；个股字段块内只保留 `📍 阶段`、`💰 热度`、`🛡 结构`、`📈 回测`、`⚠️ 风险` 连续紧凑行。

Validation results:

- failed as expected 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`，新增断言先证明旧契约仍把 `申购冲突` 当作 per-IPO 字段，并要求个股 emoji 字段逐项留空行。
- passed 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`
- passed 2026-05-05 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-05 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`（sandbox 下 `__pycache__` 写入被拒，已按权限重跑通过）
- passed 2026-05-05 北京时间：`git diff --check`
- passed 2026-05-05 北京时间：`rg -n "每条 emoji|emoji field inside|inside every IPO block|⏱ 申购冲突：|每只 IPO 字段块的.*申购冲突|写入每只 IPO 字段块.*申购冲突" SKILL.md README.md references/hkipo.md commands/hkipo.py` 无命中。
- passed 2026-05-05 北京时间：`printf '{}' | python3 commands/hkipo.py | rg -n "申购冲突|关键结论|优先级|阶段：招股|热度：最新|结构：绿鞋|回测：对应|风险：一句话|每条 emoji|每只 IPO 字段块"`，prompt 显示顶层 `**⏱ 申购冲突**`，且个股字段块内 `阶段/热度/结构/回测/风险` 连续无空行。
- passed 2026-05-05 北京时间：仓库无 `scripts/review.sh`，已按 review checklist 人工复核 diff；scope 仅限 M29，prompt、SKILL、README、reference 和 tests 不再保留旧 per-IPO `⏱ 申购冲突` 字段契约或小字段逐项空行契约。

Handoff:

- `/hkipo` 输出契约已改为：`**💡 关键结论**`、`**⏱ 申购冲突**`、`**📌 优先级**` 为同级顶层小节；个股字段块只包含 `📍 阶段`、`💰 热度`、`🛡 结构`、`📈 回测`、`⚠️ 风险`，这些小字段之间不留空行。
- 本轮未修改行情抓取逻辑；只修正 `/hkipo` prompt/reference/skill 文档与对应回归测试。

### M28 — /hkipo 报告正文模板边界

Status: `done`

Scope:

- `commands/hkipo.py`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-05 北京时间：用户澄清 Feishu 消息卡片中 step / thinking 的格式约束不应放在 skill；skill 只应约束最终报告正文模板。
- 2026-05-05 北京时间：已将 `/hkipo` prompt、SKILL、README 和 hkipo reference 的输出规则收敛为“报告正文”约束，移除与宿主消息卡片展示混淆的表述。
- 2026-05-05 北京时间：已同步 hkipo reference，申购冲突保留为每只 IPO 字段块的 `⏱ 申购冲突` 字段，并保留每条 emoji 字段上方空行的正文模板要求。

Validation results:

- passed 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`
- passed 2026-05-05 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-05 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`（sandbox 下 `__pycache__` 写入被拒，已按权限重跑通过）
- passed 2026-05-05 北京时间：`git diff --check`
- passed 2026-05-05 北京时间：`rg -n "飞书卡片|must be a top-level section|Do not insert blank lines between|申购冲突只放在顶层|顶层“⏱ 申购冲突”|thinking|tool steps" SKILL.md README.md references/hkipo.md commands/hkipo.py` 无命中。
- passed 2026-05-05 北京时间：`printf '{}' | python3 commands/hkipo.py`，prompt 只约束报告正文，并保留每只 IPO 字段块的 `⏱ 申购冲突`。
- passed 2026-05-05 北京时间：已同步当前 Cli Claw 安装副本，`commands/hkipo.py` 与 `references/hkipo.md` 和源码一致；安装副本 smoke check 通过。
- passed 2026-05-05 北京时间：仓库无 `scripts/review.sh`，已人工复核 diff，确认未触碰非 `/hkipo` 报告正文模板相关逻辑。

Handoff:

- `/hkipo` skill 现在只约束最终报告正文模板：窄字段块、每条 emoji 字段上方空行、每只 IPO 的 `⏱ 申购冲突` 字段。
- Feishu message card 的 thinking / tool steps / 折叠展示仍由 Cli Claw runtime presentation 层负责，不在 skill 中定义。

### M27 — /hkipo 申购冲突语义与换行

Status: `done`

Scope:

- `commands/hkipo.py`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-05 北京时间：用户要求 `/hkipo` 的 `💡 关键结论`、`📌 优先级`、`⏱ 申购冲突` 等小节/字段上方保留空行，提升飞书卡片可读性。
- 2026-05-05 北京时间：用户澄清“申购冲突”应比较当前 IPO 池里的资金时间线，例如判断樂動機器人能否先梭哈、等结果后再申劑泰科技-P/英派藥業-B，而不是和历史旧批次对比。
- 2026-05-05 北京时间：已将 `/hkipo` prompt 的申购冲突语义改为当前 IPO 池内资金时间线比较；输出字段改为 `⏱ 申购冲突`，并要求列出对象、申购截止日、配发/退款日和判断。
- 2026-05-05 北京时间：已将输出模板改为每个加粗小节标题和每条 emoji 字段上方保留空行，同步 README、SKILL 和 hkipo reference。

Validation results:

- failed as expected 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`，新增断言确认旧 prompt 缺少当前池资金时间线语义和空行格式。
- passed 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`
- passed 2026-05-05 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-05 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`（sandbox 下 `__pycache__` 写入被拒，已按权限重跑通过）
- passed 2026-05-05 北京时间：`git diff --check`
- passed 2026-05-05 北京时间：`printf '{}' | python3 commands/hkipo.py` smoke check，prompt 包含空行格式、`⏱ 申购冲突`、用户点名 A/B/C 的资金复用判断规则和“不要和历史旧批次”约束。

Handoff:

- `/hkipo` 申购冲突现在只比较当前报告 IPO 池里的资金时间线，不再拿历史旧批次或回测样本对比。报告需要明确回答能否先集中申购 A，等 A 配发/退款后再申 B/C。
- 飞书报告模板已要求 `💡 关键结论`、`📌 优先级`、`⏱ 申购冲突` 等小点上方留空行，避免窄卡片内容挤在一起。

### M26 — /hkipo 申购冲突字段

Status: `done`

Scope:

- `commands/hkipo.py`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-05 北京时间：用户要求 `/hkipo` 根据新股申购截止日增加“申购冲突”字段，区分只能同批次申购和可等上批次结果后再申购。
- 2026-05-05 北京时间：已新增 RED 测试，要求 prompt 包含申购冲突、同批次资金冲突、可等上批次结果后再申购和卡片字段。
- 2026-05-05 北京时间：已在 `/hkipo` prompt 输出格式新增 `⏱ 冲突` 卡片行；执行规则要求按申购截止日和配发结果公告日判断同批次资金冲突或可等上批次结果后再申购。
- 2026-05-05 北京时间：已同步 `SKILL.md`、`README.md` 和 `references/hkipo.md`，将申购冲突列为每只 IPO 的必备短字段。

Validation results:

- failed as expected 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`，新增用例确认当前 prompt 缺少申购冲突字段。
- passed 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`
- passed 2026-05-05 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-05 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-05 北京时间：`git diff --check`
- passed 2026-05-05 北京时间：`python3 commands/hkipo.py <<<'{}'` 输出包含申购冲突规则和 `⏱ 冲突` 字段。
- passed 2026-05-05 北京时间：已在当前 Cli Claw 安装副本验证默认 prompt 包含申购冲突规则和 `⏱ 冲突` 字段。

Handoff:

- `/hkipo` 每只 IPO 卡片新增 `⏱ 冲突` 行；根据申购截止日和配发结果公告日判断同批次资金冲突或可等上批次结果后再申购。
- 已同步当前 Cli Claw 安装副本；本轮未修改宿主服务代码，不需要重启 Cli Claw。

### M25 — /hkipo 全量参数改为 --all

Status: `done`

Scope:

- `commands/hkipo.py`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-05 北京时间：用户要求把 `/hkipo` 纳入已截止新股的参数改成更直观的 `--all`。
- 2026-05-05 北京时间：已新增 RED 测试，覆盖默认 prompt 只提示 `/hkipo --all`，以及 `--all` 可纳入已截止但未上市标的。
- 2026-05-05 北京时间：已将 executor、prompt、README、SKILL 和 hkipo reference 全部切换为 `--all`，并移除旧参数文案。

Validation results:

- failed as expected 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`，两个新断言确认旧实现还没有识别 `--all`。
- passed 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`
- passed 2026-05-05 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-05 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-05 北京时间：`git diff --check`
- passed 2026-05-05 北京时间：`python3 commands/hkipo.py <<<'{}'` 默认提示 `/hkipo --all` 才纳入已截止新股。
- passed 2026-05-05 北京时间：`python3 commands/hkipo.py <<<'{"argsText":"--all","args":["--all"]}'` 提示纳入已截止但未上市标的。
- passed 2026-05-05 北京时间：用户可见文档和 prompt 中不再出现旧参数名。
- passed 2026-05-05 北京时间：已在当前 Cli Claw 安装副本验证默认 prompt 和 `/hkipo --all` prompt 均为新参数文案。

Handoff:

- `/hkipo` 默认只输出当前仍可认购 IPO；如需纳入已截止但未上市标的，使用 `/hkipo --all`。
- 已同步当前 Cli Claw 安装副本；本轮未修改宿主服务代码，不需要重启 Cli Claw。

### M24 — /hkipo 默认过滤已截止新股

Status: `done`

Scope:

- `commands/hkipo.py`
- `commands.json`
- `tests/test_hkipo_command.py`
- `SKILL.md`
- `README.md`
- `references/hkipo.md`
- `PLANS/ACTIVE.md`

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-05 北京时间：用户要求 `/hkipo` 默认不输出已截止新股，并加参数控制是否纳入已截止但未上市标的。
- 2026-05-05 北京时间：已新增 RED 测试，覆盖默认过滤 `is_subscribe_status=false`，以及显式参数纳入已截止待上市。
- 2026-05-05 北京时间：已实现 `/hkipo` 参数解析；默认 prompt 要求过滤已截止新股，显式全量参数会纳入已截止但未上市标的。
- 2026-05-05 北京时间：已同步 `SKILL.md`、`README.md`、`references/hkipo.md` 和 `commands.json` 的默认范围说明。

Validation results:

- failed as expected 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`，两个新用例确认旧 prompt 仍默认包含已截止待上市。
- passed 2026-05-05 北京时间：`python3 -m unittest tests/test_hkipo_command.py`
- passed 2026-05-05 北京时间：`python3 -m unittest discover -s tests`
- passed 2026-05-05 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-05 北京时间：`git diff --check`
- passed 2026-05-05 北京时间：已在当前 Cli Claw 安装副本验证 `python3 commands/hkipo.py <<<'{}'` 默认提示过滤已截止新股。
- passed 2026-05-05 北京时间：已在当前 Cli Claw 安装副本验证显式全量参数提示纳入已截止但未上市标的。

Handoff:

- `/hkipo` 默认只输出当前仍可认购 IPO；如需恢复旧范围，使用显式全量参数。
- 已同步当前 Cli Claw 安装副本；本轮未修改宿主服务代码，不需要重启 Cli Claw。

### M23 — 港股 research OpenD 前置确认

Status: `done`

Scope:

- `commands/research.py`
- `tests/test_research_command.py`
- `README.md`
- `SKILL.md`
- `references/futu.md`
- `references/research.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-04 北京时间：确认 `/research` 港股路径当前只在 prompt 中允许 Futu/OpenD 不可用后降级，executor 没有本地阻断；这会导致 OpenD 拿不到时 agent 自行继续。
- 2026-05-04 北京时间：本轮目标是 explicit HK `/research` 在进入 agent 前先做 OpenD 只读预检；预检失败时只返回确认提示，用户确认后才允许降级继续。
- 2026-05-04 北京时间：已补 RED 用例覆盖三种路径：OpenD 不可用时返回 `final_markdown` 确认提示、`--continue-without-opend` 后才生成降级 prompt、OpenD 可用时 prompt 明确预检通过。
- 2026-05-04 北京时间：已在 executor 增加 futuapi `get_global_state.py --json` 预检，使用 futuapi 自身 `.venv/bin/python`；不回退到宿主 Python，避免服务重启后环境漂移。
- 2026-05-04 北京时间：已约束待解析输入若唯一核验为港股，OpenD 不可用时也必须先询问用户，不能自行改用 HKEX / yfinance 继续。

Validation results:

- passed 2026-05-04 北京时间：`python3 -m unittest tests/test_research_command.py -v`
- passed 2026-05-04 北京时间：`python3 -m unittest discover -s tests -v`
- passed 2026-05-04 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-04 北京时间：`git diff --check`

Handoff:

- `/research HK.00700` / `/research 0700.HK` 现在会在进入 agent 前先跑 futuapi OpenD 只读预检；失败时只返回确认提示，不生成研报 prompt。
- 用户确认继续时使用 `--continue-without-opend`；该确认只允许港股数据源降级，不改变只读护栏。
- 已同步当前 Cli Claw 安装副本；本轮未修改宿主服务代码，不需要重启 Cli Claw。

### M22 — 固定 skill Python / uv 环境

Status: `done`

Scope:

- `commands/research.py`
- `tests/test_research_command.py`
- `README.md`
- `SKILL.md`
- `AGENTS.md`
- `references/cli.md`
- `references/research.md`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-04 北京时间：确认 `/research` 生成 `uv run python` 裸命令，依赖重启后服务进程 PATH；这是“修完重启后环境又乱”的根因。
- 2026-05-04 北京时间：已新增 `STOCK_ANALYSIS_UV` / `UV_BIN` / `UV` / PATH / `$HOME/.local/bin/uv` / `$HOME/.cargo/bin/uv` 的固定解析顺序，生成命令时输出绝对 `uv` 路径。
- 2026-05-04 北京时间：找到 API 仓库但找不到 `uv` 时，prompt 显式预检失败，不再让 agent 自行猜裸 `uv` 或当前工作区环境。

Validation results:

- passed 2026-05-04 北京时间：`python3 -m unittest tests/test_research_command.py -v`
- passed 2026-05-04 北京时间：`python3 -m unittest discover -s tests -v`
- passed 2026-05-04 北京时间：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-04 北京时间：`git diff --check`

Handoff:

- 宿主层也已确保 skill command executor 自身优先使用 skill `.venv` Python；对应改动在 `cli-claw` 的 skill command dispatch 中完成。
- `/research` 现在生成绝对 `uv` 命令；找不到 `uv` 时显式预检失败，不再让 agent 依赖重启后的 PATH。

### M21 — /research 英文公司名纠偏与 MiniMax 路由

Status: `done`

Scope:

- `commands/research.py`
- `references/research.md`
- `SKILL.md`
- `tests/test_research_command.py`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-04：确认 `/research MINIMAX` 被本地 executor 在上游前按全大写正则归为 `us`，导致 prompt 和标题固定为 `US.MINIMAX`，上游和联网证据没有纠偏空间。
- 2026-05-04：本轮目标是让长英文公司名输入进入“待解析/可纠偏”路径；若公开来源唯一指向港股，最终报告必须切到港股标题和港股数据路径。
- 2026-05-04：已将短裸美股 ticker 与较长英文公司名拆开处理；`MINIMAX` 生成 `待解析` 路由，不再生成 `--market us --symbols MINIMAX` 或 `US.MINIMAX` 固定标题。
- 2026-05-04：已同步 `SKILL.md` 和 `references/research.md`，要求读取上游结构化失败字段后再澄清或改道，不能把美股行情失败包装成有效美股报告。

Validation results:

- passed 2026-05-04：`python3 -m unittest tests/test_research_command.py`
- passed 2026-05-04：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-04：`git diff --check`

Handoff:

- 后续若需要把 `MINIMAX` 自动落到 `HK.00100`，应在上游身份解析层增加跨市场唯一匹配能力；本轮 skill executor 负责避免错误预分类，并把纠偏要求明确写入 prompt。

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


### M7 — 港股 IPO 回测加入行业/估值/结构/暗盘维度

Status: `done`

Scope:

- 扩展 `scripts/hkipo_backtest.py`：加入行业启发式分类、市值/估值分桶、多维评分、enrichment CSV 支持绿鞋/基石/暗盘
- 更新 `README.md` / `references/hkipo.md`，说明 enrichment CSV 和缺失字段处理
- 运行增强版 100 样本回测并记录校准结果

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 scripts/hkipo_backtest.py --limit 20 --source aastocks --format markdown`
- `python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`

Progress:

- 2026-04-27：增强版 100 样本回测已跑通：多维评分相关系数 0.412；市值字段覆盖 47/100；绿鞋/基石/暗盘在 AAStocks 列表源中覆盖 0/100，需要 enrichment CSV 或逐票来源补充。
- 2026-04-27：行业分桶显示 `ai_tech`、`biotech`、`semiconductor` 中位首日涨幅较强；`consumer` 分桶显著偏弱。


### M8 — 安装受控 Futu/OpenD 本地环境

Status: `done`

Scope:

- 确认当前主机默认 Python、`pyenv` 与 `uv` 状态
- 使用独立 `uv` venv 安装并固定 Futu SDK 与数据分析依赖版本
- 安装 macOS GUI 版 Futu OpenD，并写入 futu skill 版本戳
- 验证 SDK import 与 OpenD 只读连接状态
- 为 `stock-analysis-skill` 增加全局只读护栏，禁止任何写入、编辑、下单或交易状态变更行为

Validation:

- `python3 --version`
- `pyenv --version`
- `uv --version`
- `.venv/bin/python -c 'import sys, futu, google.protobuf; ...'`
- `.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- `grep -R "模拟/实盘交易\|实盘下单 / 撤单 / 改单\|trade_intent\|确认执行" -n SKILL.md README.md AGENTS.md references/futu.md`

Progress:

- 2026-04-27 20:08 北京时间：确认默认 `python3` 是 Homebrew `3.14.3`；主机同时安装了 `pyenv 2.6.26` 与 `uv 0.10.12`。
- 2026-04-27 20:08 北京时间：已用 `uv` 创建 `.venv`，Python 版本为 `3.12.12`，并安装 `futu-api==10.4.6408`、`backtrader==1.9.78.123`、`matplotlib==3.10.9`、`pandas==3.0.2`、`numpy==2.4.4`。
- 2026-04-27 20:08 北京时间：已新增 `requirements-futu.txt` 与 `requirements-futu.lock` 记录固定版本，并在 `.gitignore` 忽略 `.venv`。
- 2026-04-27 20:08 北京时间：已下载并安装 GUI 版 `/Applications/Futu_OpenD.app`，版本 `10.4.6408`，并写入 `/Users/ryan/.futu_skill_version=0.1.1`。
- 2026-04-27 23:49 北京时间：用户完成 OpenD 登录后，`get_ipo_list.py HK --json` 已只读查询成功，返回 5 条港股 IPO 记录。
- 2026-04-27 23:49 北京时间：已在 `SKILL.md` 增加全局只读护栏，并同步 `README.md` / `AGENTS.md` / `references/futu.md`，明确禁止下单、改单、撤单、订阅、交易解锁和其他写入类行为。

Blockers:

- 无。


### M9 — 优化 skill md 说明

Status: `done`

Scope:

- 优化 `SKILL.md` 的 frontmatter description，使其只描述触发条件，不复述执行流程
- 收敛 `SKILL.md` / `README.md` / `AGENTS.md` / `references/*.md` 中只读边界、订阅和导出表述
- 保留 CLI、Futu/OpenD、Tushare、Slash Commands 四类路由，但减少重复说明并改为引用 owner reference

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- 人工检查 `SKILL.md` / `README.md` / `AGENTS.md` / `references/cli.md` / `references/futu.md` 的路由和只读约束一致

Progress:

- 2026-04-28 00:38 北京时间：开始按 skill 编写要求优化 md 说明，优先处理 description、重复说明和只读边界冲突。
- 2026-04-28 00:38 北京时间：已完成 `SKILL.md` 精简、frontmatter description 调整，并同步 `README.md` / `AGENTS.md` / `references/cli.md` / `references/futu.md` 的只读边界表述。

### M10 — 回测评分合理性校准

Status: `done`

Scope:

- 扩展 `scripts/hkipo_backtest.py`：按评分分桶、排序相关性和失配样本评估评分与首日涨幅的一致性
- 新增最小回归测试覆盖评分校准摘要
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md` 的回测输出说明
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录 100 样本校准结论

Validation:

- `python3 -m unittest tests/test_hkipo_backtest.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：开始按用户要求评估最近 100 个港股新股的评分与首日涨幅是否匹配；当前缺口是只有相关系数和 Top/Worst 首日表现，缺少评分分桶与高分破发/低分大涨失配样本。
- 2026-04-28 北京时间：已新增评分分桶、评分排序相关性、Top/Bottom 评分分位首日涨幅差和高分破发 / 低分大涨失配样本。
- 2026-04-28 北京时间：100 样本回测结果显示评分方向基本合理：评分排序相关系数 0.561；Top 20% 评分中位首日涨幅 88.78%，Bottom 20% 为 0.00%；80-89 分桶胜率 95.8%、中位首日涨幅 95.34%，<50 分桶胜率 41.7%、中位首日涨幅 -2.21%。
- 2026-04-28 北京时间：限制仍明确保留：绿鞋 / 基石 / 暗盘覆盖为 0/100，行业分是同源样本内启发式，不等同于样本外预测。

Validation status:

- passed

Review status:

- passed

### M11 — Futu K 线校验港股 IPO 首日回测

Status: `done`

Scope:

- 扩展 `scripts/hkipo_backtest.py`：支持用 Futu/OpenD 历史日 K 线重算首日涨幅
- 保留 AAStocks 作为最近 100 个已上市 IPO 样本清单来源，明确 Futu `get_ipo_list` 只覆盖当前 IPO 列表
- 新增最小回归测试覆盖 Futu 首日收益写回逻辑
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md` 的 Futu 回测命令与数据边界
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录 Futu/OpenD 实测结果

Validation:

- `.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- `.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_history_kl_quota.py --json`
- `python3 -m unittest tests/test_hkipo_backtest.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --debut-price-source futu-kline --format markdown`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户明确要求用已登录的 Futu/OpenD 拉数据并回测；已确认 `get_ipo_list(HK)` 只返回当前 IPO 列表且不含绿鞋 / 基石 / 暗盘字段。
- 2026-04-28 北京时间：已用 Futu 历史日 K 线接口成功读取 `HK.02635` 上市日 K 线，可用于重算首日收盘涨幅。
- 2026-04-28 北京时间：首次用系统 `python3` 跑 Futu 模式失败，原因是 Futu SDK 安装在项目 `.venv`；已将 Futu 模式验证命令改为 `.venv/bin/python`。
- 2026-04-28 北京时间：Futu/OpenD 100 样本回测跑通，上市日 K 线覆盖 95/100；报告中 `首日涨幅来源` 显示 `futu_kline 95`。
- 2026-04-28 北京时间：Futu K 线重算后的结果与表格首日涨幅基本一致：评分排序相关系数 0.561，Top 20% 评分中位首日涨幅 88.78%，80-89 分桶中位首日涨幅 95.34%。

Validation status:

- passed

Review status:

- passed

### M12 — 补全绿鞋/基石/暗盘 enrichment 并回测

Status: `done`

Scope:

- 参考 AKShare 的公开网页数据接口实现方式，新增可选公开数据源 enrichment
- 扩展 `scripts/hkipo_backtest.py`：支持按代码从新股渔夫公开 API 补绿鞋、基石、暗盘、保荐人和稳价人字段
- 保持 AAStocks 作为样本清单，Futu/OpenD 作为首日 K 线来源
- 新增最小回归测试覆盖 enrichment 字段映射
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md` 的命令和数据源边界
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录补全覆盖率和回测结果

Validation:

- `python3 -m unittest tests/test_hkipo_backtest.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --enrichment-source xinguyufu --debut-price-source futu-kline --format markdown`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：开始按用户要求参考开源实现补全数据源。已确认 AKShare `stock_ipo_hk_ths` 的模式是带浏览器 UA 抓公开页面并抽取表格；新股渔夫公开页面暴露 `/api/ipo` JSON 字段，可按单个代码查询绿鞋、基石、暗盘等字段。
- 2026-04-28 北京时间：已新增 `--enrichment-source xinguyufu`，逐票按代码补充绿鞋、基石、辉立暗盘、富途暗盘、保荐人、稳价人、回拨和行业字段。
- 2026-04-28 北京时间：100 样本实测：新股渔夫补充字段覆盖 97/100；Futu/OpenD 首日 K 线覆盖 95/100。
- 2026-04-28 北京时间：补全字段后的评分校准结果：评分排序相关系数 0.579；Top 20% 评分中位首日涨幅 87.26%，Bottom 20% 为 -0.12%；80-89 分桶胜率 95.0%、中位首日涨幅 88.02%。

Validation status:

- passed

Review status:

- passed

### M13 — 约束 hkipo 当前数据源优先级与新鲜度

Status: `done`

Scope:

- 强化 `SKILL.md` 的 `/hkipo` 规则：当前 IPO 池发现和上市/招股状态必须先走 Futu/OpenD 只读 `get_ipo_list(HK)`。
- 强化 `references/hkipo.md` 的数据源优先级：Futu 当前 IPO 基础字段优先；Futu 缺失的孖展、公开认购、暗盘、中签率等字段才允许使用外部财经源。
- 强化 `/hkipo` prompt：必须按当前日期重新获取最新数据，禁止把过期孖展/暗盘数据当作当前数据使用。
- 同步 `README.md` 的 slash command 说明。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "Futu/OpenD|过期|孖展|当前日期|get_ipo_list|外部财经" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户指出天星医疗孖展数据使用了过期的 2026-04-24 口径；本轮目标是把“当前日期最新数据 + Futu 优先 + 外部源兜底”写成硬约束。
- 2026-04-28 北京时间：`/hkipo` prompt 已改用北京时间日期，避免美国本地时区导致报告日期落后一天。
- 2026-04-28 北京时间：已将当前 IPO 池发现和基础日程字段约束为优先使用 Futu/OpenD `get_ipo_list(HK)`；孖展、暗盘、中签率等 Futu 缺失字段才允许用外部财经源补齐。

Validation status:

- passed

Review status:

- passed

### M14 — 压缩 hkipo 输出为关键表格

Status: `done`

Scope:

- 收紧 `/hkipo` prompt，禁止解释触发文本日期差异、推导过程和冗长回测段落。
- 将关键结论、数据源新鲜度、Futu 覆盖/外部补充、回测映射都整合进评分总览表。
- 更新 `references/hkipo.md` / `SKILL.md` / `README.md` 的输出 contract。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "触发文本|推导过程|废话|只保留|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户反馈 `/hkipo` 输出废话太多，并指出不应写死或解释旧触发文本日期；本轮目标是把报告压缩为极短结论 + 单表 + Sources。
- 2026-04-28 北京时间：已将 `/hkipo` 输出模板改为最多 3 条结论 + 单张评分总览表 + Sources；移除单独回测校准段落，回测映射和数据源覆盖全部进表格。
- 2026-04-28 北京时间：prompt 已明确禁止解释触发文本、系统日期或取数过程；若用户消息日期与当前北京时间日期不一致，直接按当前日期输出，不写差异说明。

Validation status:

- passed

Review status:

- passed

### M15 — 优化 hkipo 飞书卡片排版

Status: `done`

Scope:

- 将 `/hkipo` 从宽 Markdown 表格改为飞书友好的窄卡片列表，避免横向滚动和长表格裁切。
- 保留关键必要信息：结论、每只 IPO 的评分/阶段/热度/结构/回测/风险、关键 Sources。
- 更新 `commands/hkipo.py`、`references/hkipo.md`、`SKILL.md`、`README.md`。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "Markdown 表格|窄卡片|横向滚动|评分卡片|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户反馈飞书消息卡片里的宽表格排版太差；本轮目标是改成正式、优雅、可读的窄卡片列表。
- 2026-04-28 北京时间：`/hkipo` prompt 已禁止宽 Markdown 表格，改为最多 3 条结论 + 每只 IPO 5-6 行窄卡片 + 短链接 Sources。

Validation status:

- passed

Review status:

- passed

### M16 — 细化 hkipo 飞书视觉层级

Status: `done`

Scope:

- 去除 `/hkipo` 输出中的 `#` / `##` Markdown 大标题，改为普通加粗标签和短分隔。
- 为结论、热度、结构、回测、风险、来源加入固定 emoji 信号。
- 更新 `commands/hkipo.py`、`references/hkipo.md`、`SKILL.md`、`README.md`。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "# 港股|## 结论|## Sources|emoji|🟢|💰|⚠️" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户反馈飞书卡片中“结论先行 / 优先级卡片 / Sources”标题过大且重点不明显；本轮目标是去 Markdown 大标题，并用少量 emoji 强化关键信息。
- 2026-04-28 北京时间：`/hkipo` 输出模板已改为普通加粗标题、短分隔和固定 emoji 信号，不再使用 `#` / `##` 大标题。

Validation status:

- passed

Review status:

- passed

### M17 — 修复 hkipo Futu 命令跨目录兼容

Status: `done`

Scope:

- 修复 `/hkipo` prompt 中的 Futu/OpenD 查询命令，不再使用当前工作区相对 `.venv/bin/python` 或用户机器硬编码路径。
- 在 command executor 运行时解析当前 `stock-analysis-skill` 安装目录、可用 venv Python 和已安装 `futuapi` skill 脚本路径。
- 增加回归测试，覆盖任意安装目录下生成的 prompt 不会依赖 `/Users/ryan` 或工作区 `.venv`。

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/hkipo.py <<< '{}'`
- `cd /Users/ryan/projects/stock-analysis-skill && /Users/ryan/projects/stock-analysis-skill/.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- `git diff --check`

Progress:

- 2026-04-30 北京时间：已确认 `/hkipo` 提示 Futu 不可用的根因是 prompt 使用相对 `.venv/bin/python`，而宿主 Agent 在工作区 cwd `/Users/ryan/projects/cli-claw` 下执行，找不到 `stock-analysis-skill` 的 Futu SDK venv。
- 2026-04-30 北京时间：已将 `/hkipo` Futu 命令改为由 executor 运行时解析当前 skill 安装目录、venv Python 和 `futuapi` 脚本；若缺失则明确预检失败，不再让 Agent 猜工作区 `.venv`。
- 2026-04-30 北京时间：已增加回归测试覆盖任意安装目录、venv symlink 保留、`futuapi` skill 自带 venv fallback 和缺失预检提示。

Validation status:

- passed

Review status:

- passed

### M18 — 新增 /research 单票深度研报命令

Status: `done`

Scope:

- 新增 `/research` skill command，沿用 `/hkipo` 的 thin executor + `assistant_prompt` 模式。
- 第一版支持单只股票参数解析：A 股 6 位代码、`cn/us/hk` 显式市场、`US.AAPL` / `HK.00700` / `0700.HK` 等常见前缀格式。
- A 股 / 美股优先复用 `stock-analysis-api/scripts/stock_analyze.py --mode full`；港股先作为后置支持，要求 Futu/OpenD + HKEX / AKShare / yfinance 降级路径。
- 新增 `references/research.md`，沉淀统一研报模板、数据源路由、禁止事项、降级与来源规范。
- 更新 `SKILL.md`、`README.md`、`commands.json` 与测试，确保 `/help` 可展示新命令且 command 输出 contract 一致。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/research.py <<< '{"argsText":"300750","args":["300750"],"workspace":{"name":"test"}}'`
- `python3 commands/research.py <<< '{"argsText":"US.AAPL","args":["US.AAPL"],"workspace":{"name":"test"}}'`
- `python3 commands/research.py <<< '{"argsText":"HK.00700","args":["HK.00700"],"workspace":{"name":"test"}}'`
- `git diff --check`

Progress:

- 2026-05-01 北京时间：用户确认新增 `/research` 并要求 subagents 协作；已派生 reader 检查测试模式、implementer 草拟 `references/research.md`。
- 2026-05-01 北京时间：本轮实现采用 TDD；先新增失败测试覆盖参数解析、assistant prompt、单票限制、A 股/美股 CLI 指令与港股后置数据层提示。
- 2026-05-01 北京时间：已新增 `commands/research.py`、`references/research.md`、`tests/test_research_command.py`，并在 `commands.json` 注册 `/research`。
- 2026-05-01 北京时间：review 发现 `US.` 前缀路径可能绕过 ticker 校验；已补安全回归测试、统一美股 symbol 校验并对可复制 CLI 参数使用 `shlex.quote`。

Validation status:

- passed

Review status:

- passed

### M19 — /research 动态解析 stock-analysis-api 命令

Status: `done`

Scope:

- 让 `/research` executor 运行时解析可用的 `stock-analysis-api` 根目录，不再只在 prompt 中依赖 `$STOCK_ANALYSIS_API_ROOT`。
- 搜索顺序优先环境变量，其次当前 skill 安装目录附近的 sibling `stock-analysis-api`；找到时输出可直接复制执行的绝对 `cd ... && uv run python scripts/stock_analyze.py ...` 命令。
- 找不到 API 根目录时，在 prompt 中明确预检失败原因，并提示才允许按数据源不可用处理。
- 增加回归测试覆盖 sibling root、环境变量优先、缺失预检和 shell-safe 命令参数。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/research.py <<< '{"argsText":"300750","args":["300750"],"workspace":{"name":"test"}}'`
- `python3 commands/research.py <<< '{"argsText":"US.AAPL","args":["US.AAPL"],"workspace":{"name":"test"}}'`
- `git diff --check`

Progress:

- 2026-05-01 北京时间：用户要求继续下一轮开发；本轮聚焦 `/research` 的 API CLI 命令可执行性，避免宿主 Agent 在不同 cwd 下猜环境变量或相对路径。
- 2026-05-01 北京时间：已为 `/research` 增加 `stock-analysis-api` 根目录解析：`STOCK_ANALYSIS_API_ROOT` 优先，随后查找当前 skill 安装目录附近的 sibling `stock-analysis-api`；生成 shell-safe 绝对 `cd ... && uv run python scripts/stock_analyze.py ...` 命令。
- 2026-05-01 北京时间：已补充回归测试，覆盖 sibling root、环境变量优先、空 env 不读取进程环境、缺失预检、不从宿主 cwd 猜 API 仓库、subprocess 入口和 `CLI_CLAW_SKILL_DIR` 驱动的宿主路径解析。
- 2026-05-01 北京时间：已同步 `SKILL.md` / `README.md` / `AGENTS.md` / `references/research.md`，明确找不到 API 仓库时必须显式降级，不能猜相对路径或虚构 `$STOCK_ANALYSIS_API_ROOT`。

Validation status:

- passed

Review status:

- passed

### M20 — /research 可信度、风险与历史验证模块

Status: `done`

Scope:

- 在 `/research` prompt 和 `references/research.md` 中固定可信度层：`module_status`、`source_freshness`、`data_gaps`。
- 将风险评估整合进 `/research`，覆盖单票风险、组合/持仓只读风险和反证信号，不新增独立 `/risk` 指令。
- 增加“历史验证”模块边界：只做可复现历史统计、样本数、窗口、假设和限制，不输出买卖建议或策略执行指令。
- 补充回归测试，确保 `/research` executor prompt 强制包含以上模块。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-03 北京时间：用户确认按 Vibe-Trading 对比后的方向优化，但要求风险不新增指令，统一整合到 `/research`；历史验证也作为 `/research` 模块而不是独立 `/backtest`。
- 2026-05-03 北京时间：已在 `/research` prompt 和 `references/research.md` 固定 `module_status`、`source_freshness`、`data_gaps` 可信度层。
- 2026-05-03 北京时间：已把风险评估收敛为 `/research` 内的“风险与反证”，并把组合/持仓风险定义为同入口只读约束，不新增 `/risk`。
- 2026-05-03 北京时间：已新增“历史验证”模块边界：只做可复现历史统计，必须说明样本数、窗口、条件、指标和限制，不给交易指令。

Validation status:

- passed

Review status:

- passed

### M21 — /research 飞书短版与最终回复清洗

Status: `done`

Scope:

- 约束 `/research` 最终回复不得混入执行过程日志、工具尝试过程或调试错误堆栈。
- 将 IM/飞书默认输出改为短版研报：结论摘要、数据可信度、关键风险与反证、降级说明、Sources。
- 深度章节仅在用户明确要求详细/完整/深度时展开；历史验证默认压缩，无法验证时一行说明。
- 维护 debug 细节边界：函数名、异常栈、环境排查细节只进入降级摘要，不进入用户版正文。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-03 北京时间：用户要求优化实际研报输出；本轮聚焦可读性和最终消息清洁度，不改数据采集实现。
- 2026-05-03 北京时间：已约束最终回复必须直接从 `**/research｜...**` 标题开始，不得混入执行过程日志、工具尝试、调试细节或异常堆栈。
- 2026-05-03 北京时间：已将 IM/飞书默认输出改为 2500-3500 字短版，只保留结论摘要、数据可信度、关键风险与反证、降级说明和 Sources。
- 2026-05-03 北京时间：已明确调试细节只压缩为用户可理解的降级原因，内部函数名/堆栈/本地路径不进用户版报告。

Validation status:

- passed

Review status:

- passed


### M22 — /research 股票名交由上游 CLI 识别

Status: `done`

Scope:

- `/research` 支持输入股票名 / 公司名，并将原始输入传给 `stock-analysis-api` CLI
- executor 不读取 SQLite / 本地缓存、不硬编码匹配、不生成下游标的识别模板
- `stock-analysis-api` 在 CLI 入口解析唯一市场和代码后再调用分析链路
- 上游返回 `identity_conflict` / `identity_not_found` 时，agent 先向用户澄清，不自行猜测代码
- 同步 README / SKILL / research reference，并验证 slash command 行为

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- `STOCK_ANALYSIS_API_ROOT=/Users/ryan/projects/stock-analysis-api python3 commands/research.py <<< '{"argsText":"宁德时代","args":["宁德时代"]}'`

Progress:

- 2026-05-03 北京时间：已按用户反馈补 `/research 宁德时代`、`/research cn 宁德时代`、API root 缺失场景单测。
- 2026-05-04 北京时间：已撤掉下游 agent 标的识别流程，股票名输入现在生成 `--symbols 原始输入`，由上游 CLI 解析。
- 2026-05-04 北京时间：已同步 README / SKILL / research reference，明确 executor 不硬匹配、上游 CLI 识别、多候选先澄清。

Validation status:

- passed

Review status:

- passed


### M23 — /research 增加行业与研报维度

Status: `done`

Scope:

- `/research` prompt 强制补充行业整体趋势和市场热度
- 强制给出同类公司平均 PE，并说明可比公司样本、PE 口径、异常值处理和数据日期
- 强制汇总权威机构研报，列机构、研报发布日期、核心观点、共识与分歧
- 数据不可得时写入 `data_gaps` / 降级说明，不伪造，不把评级或目标价作为建议

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-04 北京时间：已补 prompt/reference 单测，锁定行业整体趋势、市场热度、同类公司平均 PE、权威机构研报汇总四个必备模块。
- 2026-05-04 北京时间：已更新 `/research` prompt 和 `references/research.md`，要求写清来源日期、样本口径、异常 PE 处理、机构观点共识与分歧。
- 2026-05-04 北京时间：已同步 README / SKILL，飞书短版也必须压缩纳入四个模块；不可得时写入可信度或降级说明。

Validation status:

- passed

Review status:

- passed

### M34 — /research 默认重点版短报结构

Status: `done`

Scope:

- 将 `/research` IM/飞书默认输出改为用户反馈确认的重点版结构
- 默认先回答财务结构是否健康、估值合理性、行业相对高低估、当下情绪热度、未来叙事与增长点、权威机构观点共识与分歧
- 保留可信度层、风险与反证、降级说明和 Sources，但不再把工程可信度放在正文最前面抢占注意力
- 同步 `references/research.md`、`commands/research.py`、入口说明和测试

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-06 北京时间：用户确认 TSLA 重点版结构更符合需求；本轮固化为 `/research` 默认飞书短版模板。
- 2026-05-06 北京时间：已更新 `references/research.md` 的 Default Feishu Short Form，默认采用重点版 / 决策看板结构。
- 2026-05-06 北京时间：已同步 `commands/research.py` prompt 输出格式、`SKILL.md` / `README.md` 入口说明，并增加测试断言。
- 2026-05-06 北京时间：已抽样生成 `/research TSLA` prompt，确认飞书短版要求先回答财务结构、估值相对位置、情绪热度、叙事增长点和机构观点综合。

Validation status:

- passed

Review status:

- passed

## Progress

- 2026-05-06：`/research` 飞书默认短版已改为重点版 / 决策看板结构，优先回答财务健康、估值相对位置、情绪热度、叙事增长点和机构观点综合，再给风险、可信度和降级说明。
- 2026-05-04：`/research` 已新增行业整体趋势、市场热度、同类公司平均 PE、权威机构研报汇总四个强制模块；数据不可得时进入可信度/降级说明。
- 2026-05-04：`/research` 股票名输入已改为上游 CLI 识别；executor 只传原始输入，不查本地缓存、不硬编码匹配、不生成下游识别模板。
- 2026-04-27：移除旧 `docs/plan.md`，统一使用 `PLANS/`。
- 2026-04-27：确认用户要求后续任务时间改用北京时间展示。
- 2026-04-27：开始创建 `PLANS/ROADMAP.md` 与 `PLANS/ACTIVE.md`，并把富途整合纳入长期 roadmap。
- 2026-04-27：已在 `SKILL.md` / `README.md` / `AGENTS.md` 增加 Futu/OpenD 路由优先级、边界和交易安全要求。
- 2026-04-27：新增 `references/futu.md`，定义 quote snapshot、watch alert、option chain、portfolio risk、trade intent contract。
- 2026-04-27：补充 watchlist 自动选路规则：A 股轻量轮询走 `poll_realtime_quotes.py`，混合市场 / 盘口 / 订阅 / 持仓联动走 `futuapi`。

## Validation

- 已通过：M34 `python3 -m unittest tests/test_research_command.py -v`、`python3 -m py_compile scripts/*.py commands/*.py`、`git diff --check`
- 已通过：M34 抽样执行 `python3 commands/research.py` 生成 `/research TSLA` prompt，确认重点版短报章节进入输出约束。
- 已通过：M23 `python3 -m unittest discover -s tests -v`、`python3 -m py_compile scripts/*.py commands/*.py`、`git diff --check`
- 已通过：`python3 -m unittest tests/test_research_command.py -v`
- 已通过：`python3 -m unittest discover -s tests -v`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/research.py` 抽样验证 `/research 宁德时代` 生成 `--symbols 宁德时代` 并声明上游 CLI 负责解析
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 20 --source aastocks --format markdown`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`
- 已通过：人工检查 `SKILL.md` / `README.md` / `commands/hkipo.py` / `references/hkipo.md` 的 `/hkipo` 评分、绿鞋、回测和简明输出规则一致
- 已通过：`test ! -e docs/plan.md && test -f PLANS/ROADMAP.md && test -f PLANS/ACTIVE.md && test -f references/futu.md`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：人工检查 `AGENTS.md` / `README.md` / `SKILL.md` / `PLANS/*.md` / `references/futu.md` 职责不冲突
- 已通过：确认 `PLANS/ACTIVE.md` 中没有进行中的 milestone
- 已通过：`.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- 已通过：人工检查 `SKILL.md` / `README.md` / `AGENTS.md` / `references/futu.md` 的 Futu/OpenD 说明已统一为只读查询，且不再保留实盘/模拟交易执行路径
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "订阅默认|订阅推送见|自定义导出|文档生成任务|三类能力|价格提醒联动|原始 Tushare 字段或导出" SKILL.md README.md AGENTS.md references/*.md PLANS/*.md` 无命中
- 已通过：`git diff --check`
- 已通过：`python3 -m unittest tests/test_hkipo_backtest.py`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`
- 已通过：`git diff --check`
- 已通过：`.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- 已通过：`.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_history_kl_quota.py --json`
- 已通过：`python3 -m unittest tests/test_hkipo_backtest.py`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --debut-price-source futu-kline --format markdown`
- 已通过：`git diff --check`
- 已通过：`python3 -m unittest tests/test_hkipo_backtest.py`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --enrichment-source xinguyufu --debut-price-source futu-kline --format markdown`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "Futu/OpenD|过期|孖展|当前日期|get_ipo_list|外部财经" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "触发文本|推导过程|废话|只保留|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "Markdown 表格|窄卡片|横向滚动|评分卡片|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "# 港股|## 结论|## Sources|emoji|🟢|💰|⚠️" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`

## Handoff

- M1 已完成：计划入口、北京时间口径与富途整合 roadmap 均已落盘。
- 2026-04-27：用户要求移除 `docs/plan.md`，后续统一使用 `PLANS/`。
- 2026-04-27：M2 已完成：`SKILL.md` / `README.md` / `AGENTS.md` 已同步 Futu/OpenD 路由矩阵与安全边界。
- M3 已完成：统一输出 contract 已落到 `references/futu.md`。
- M4 已完成：watchlist 自动选路规则已落到 `references/futu.md`，并同步 `SKILL.md` / `README.md` / `references/cli.md`。
- M5 已完成：`/hkipo` 已升级为评分卡 + 简明报告 + 绿鞋/基石 + 首日回测校准工作流，并新增 `references/hkipo.md`。
- M6 已完成：新增 `scripts/hkipo_backtest.py`，可抓取 AAStocks 近期已上市港股 IPO 并输出首日表现分桶回测。
- M7 已完成：回测加入行业启发式分类、市值/估值分桶，并支持通过 enrichment CSV 补充绿鞋、基石、暗盘。
- M8 已完成：Futu/OpenD 登录后只读 IPO 查询验证通过；`stock-analysis-skill` 已增加全局只读护栏，禁止任何写入、编辑、下单、订阅或交易解锁行为。
- 下一轮可在只读边界内继续补 quote / IPO / 持仓查询类封装或输出模板。
- M9 已完成：`SKILL.md` 按 skill 编写要求精简为路由规范；description 改为触发条件描述；只读边界、订阅、导出和文档生成表述已同步。
- M10 已完成：`hkipo_backtest.py` 已能按评分分桶、评分排序相关性和失配样本评估评分与首日涨幅的一致性；最近 100 样本验证显示评分方向基本合理，但绿鞋 / 基石 / 暗盘仍需 enrichment 数据源补齐。
- M11 已完成：`hkipo_backtest.py` 已支持 Futu/OpenD 历史日 K 线重算首日收盘涨幅；最近 100 样本实测覆盖 95/100，Futu 重算后评分方向仍基本合理。
- M12 已完成：`hkipo_backtest.py` 已支持新股渔夫公开 API enrichment；最近 100 样本补充字段覆盖 97/100，绿鞋 80/100、基石 97/100、辉立暗盘 97/100、富途暗盘 95/100，结合 Futu K 线后的评分排序相关系数 0.579。
- M13 已完成：`/hkipo` 已强制按北京时间当前日期取数；当前 IPO 池和基础日程字段优先 Futu/OpenD，Futu 缺失的孖展、暗盘、中签率等字段才允许外部财经源补充，且过期数据不得用于当前热度主评分。
- M14 已完成：`/hkipo` 输出已压缩为最多 3 条结论 + 单张评分总览表 + Sources；不再解释触发文本日期差异、取数过程或评分推导。
- M15 已完成：`/hkipo` 输出改为飞书友好的窄卡片列表，避免宽 Markdown 表格横向滚动和裁切；Sources 要求短链接和用途/日期标签。
- M16 已完成：`/hkipo` 去除 `#` / `##` 大标题，改用普通加粗标签、短分隔和 🟢/🟡/⚪/💰/🛡/📈/⚠️/🔗 固定信号。
- M19 已完成：`/research` A 股 / 美股 prompt 已改为运行时解析 `stock-analysis-api` 绝对命令；找不到 API 仓库时显式预检失败并按研报降级规则继续。
- M20 已完成：`/research` 已增加可信度层、风险与反证、历史验证模块；风险不新增独立指令，组合/持仓风险纳入同入口只读约束。
- M21 已完成：`/research` 默认飞书短版和最终回复清洗已落地；最终正文直接从标题开始，过程日志和 debug 细节不进入用户版报告。
- M34 已完成：`/research` 飞书默认短版升级为重点版 / 决策看板结构；默认先回答财务结构、估值合理性、行业相对位置、情绪热度、叙事增长点和机构观点综合，再给风险、可信度、降级说明与 Sources。
