# CLI Reference

本文件是 `stock-analysis-skill` 的唯一 CLI 使用说明。

当前标准化能力统一直接调用 `stock-analysis-api` 仓库中的内部 CLI，本仓库不再维护 quote / analyze wrapper。

## 默认选择规则

以下请求默认直接走 CLI，不先走 Futu 或 Tushare：

- 单票客观分析
- 单票研报摘要
- 单票“最近怎么样”
- A 股股票 / ETF 标准化实时行情轮询
- 用户明确要求的模拟盘 dry-run 单轮执行、回放或链路验证
- 用户明确要求的模拟盘盘后总结、策略评审或自我迭代方向

示例：

- “查 300627 的研报” 默认走 `stock_analyze.py`
- 只有“查 300627 的原始 report_rc 记录”才走 Tushare 直连
- 港 / 美 / 多市场 watchlist、盘口、逐笔、分时、K 线、市场状态见 `references/futu.md`
- “跑一轮模拟盘 dry-run” 默认走 `trading_run_once.py`，不得改成真实交易
- “定时轮询模拟盘”默认走 `trading_scheduler_tick.py`，不得让 Agent 在实时链路里直接判断是否下单
- “总结今天模拟盘表现 / 生成策略迭代方向”默认走 `trading_daily_summary.py` 与 `trading_strategy_review.py`，proposal 不自动应用

## 环境变量

```bash
STOCK_ANALYSIS_API_ROOT="/absolute/path/to/stock-analysis-api"
STOCK_ANALYSIS_UV="/absolute/path/to/uv"
TUSHARE_TOKEN="your_token_here"
TUSHARE_HTTP_URL=""
TRADING_LEDGER_DB_PATH="/optional/path/to/trading_ledger.sqlite"
```

字段说明：

- `STOCK_ANALYSIS_API_ROOT`: `stock-analysis-api` 仓库根目录
- `STOCK_ANALYSIS_UV`: 固定 `uv` 可执行文件路径；未设置时 `/research` 按 `UV_BIN` / `UV` / PATH / `$HOME/.local/bin/uv` / `$HOME/.cargo/bin/uv` 查找，并在 prompt 中输出绝对路径
- `TUSHARE_TOKEN`: A 股 realtime / Tushare 直连能力需要
- `TUSHARE_HTTP_URL`: 可选，覆盖默认 Tushare 接口地址
- `TRADING_LEDGER_DB_PATH`: 可选，覆盖 API 侧模拟盘 ledger 路径

## 标准命令

### 1. realtime quote

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty
```

参数：

- `--symbols`: 逗号分隔的 A 股 / ETF 代码
- `--pretty`: 可选，格式化 JSON

### 2. objective analyze

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty
```

参数：

- `--market`
- `--symbols`
- `--start-date`
- `--end-date`
- `--mode`
- `--pretty`

### 3. simulated trading dry-run

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/trading_run_once.py --codes HK.00700 --buy-above HK.00700=0 --quantity 1 --max-order-notional 1000000
```

参数：

- `--codes`: 逗号分隔 Futu 格式代码，例如 `HK.00700`
- `--strategy-version`: 默认 `threshold-v1`
- `--buy-above`: 逗号分隔阈值，例如 `HK.00700=100`
- `--quantity`
- `--max-order-notional`
- `--ledger-db`: 可选，覆盖 SQLite ledger 路径
- `--snapshots-json`: 可选，注入离线行情快照做回放或测试
- `--lock-name`: 默认 `trading_run_once`
- `--lock-ttl-seconds`: 默认 900
- `--disable-lock`: 只允许本地调试或显式验证使用

### 4. simulated trading scheduler tick

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/trading_scheduler_tick.py --codes HK.00700 --buy-above HK.00700=0 --quantity 1 --max-order-notional 1000000
```

参数：

- 透传 dry-run 参数：`--codes`、`--strategy-version`、`--buy-above`、`--quantity`、`--max-order-notional`、`--ledger-db`、`--snapshots-json`
- `--interval-seconds`: 默认 300
- `--timezone`: 默认 `Asia/Shanghai`
- `--active-window`: 默认 `09:30-12:00,13:00-16:00`
- `--state-key`: 可选，不传时按策略参数生成
- `--force`: 忽略时间窗和间隔，仅用于显式验证

### 5. simulated trading daily summary

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/trading_daily_summary.py --date 2026-05-07 --pretty
```

参数：

- `--ledger-db`: 可选，覆盖 SQLite ledger 路径
- `--date`: `YYYY-MM-DD`，不传时按 `--timezone` 取当天
- `--timezone`: 默认 `Asia/Shanghai`
- `--pretty`

### 6. simulated trading strategy review

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/trading_strategy_review.py --date 2026-05-07 --min-runs 3 --pretty
```

参数：

- `--ledger-db`: 可选，覆盖 SQLite ledger 路径
- `--date`: `YYYY-MM-DD`，不传时按 `--timezone` 取当天
- `--timezone`: 默认 `Asia/Shanghai`
- `--min-runs`: 默认 3
- `--max-rejection-rate`: 默认 0.5
- `--pretty`

## 原始 JSON 结构

### realtime quote

顶层：

- `status`
- `computed_at`
- `source`
- `request`
- `summary`
- `items`

单个 `item`：

- `requested_symbol`
- `status`
- `error`
- `info`
- `quote_data`

`quote_data`：

- `price`
- `change_pct`
- `change_amount`
- `open`
- `high`
- `low`
- `pre_close`
- `volume`
- `amount`
- `volume_ratio`
- `turnover_rate`
- `amplitude`
- `as_of`
- `source`
- `mode`

约束：

- `change_pct / turnover_rate / amplitude` 使用 ratio
- `mode` 当前只允许：
  - `realtime`
  - `legacy_realtime`

### objective analyze

顶层固定为 `StandardResponse`：

- `status_code`
- `data`
- `err_msg`

`data`：

- `status`
- `computed_at`
- `source`
- `market`
- `strategy`
- `request`
- `items`

主消费对象默认取 `data.items[0]`。

### simulated trading dry-run

顶层：

- `status`
- `run_id`
- `strategy_version`
- `started_at`
- `finished_at`
- `source`
- `request`
- `account`
- `positions`
- `snapshots`
- `signals`
- `risk_decisions`
- `orders`
- `broker_mode`

约束：

- 成功执行时 `broker_mode` 必须是 `dry_run`。
- 拿不到调度锁时返回 `status=skipped`、`reason=lock_unavailable`，不应继续解读为失败或重复下单。
- 输出必须是严格 JSON，非有限数值会归一化为 `null`。
- 该入口只用于模拟执行、回放和审计；不得作为真实交易指令或投资建议。

### simulated trading scheduler tick

顶层：

- `status`
- `source`
- `schedule`
- `run_once`

跳过语义：

- `reason=outside_active_window`: 当前不在 active window。
- `reason=not_due`: 距离上次执行未达到 `--interval-seconds`。
- `run_once.reason=lock_unavailable`: 单轮 dry-run 锁冲突。

约束：

- `trading_scheduler_tick.py` 只做调度判断，不实现策略、风控或 broker。
- 到点后仍复用 `trading_run_once.py`；不得绕过 dry-run broker 和 SQLite ledger。
- 该入口适合 cron / launchd / Agent 高频调用。

### simulated trading daily summary

顶层：

- `status`
- `source=trading_daily_summary`
- `date`
- `timezone`
- `summary`
- `risk_reason_counts`
- `market`
- `orders`
- `risk_decisions`
- `runs`

约束：

- 只读 API 侧 SQLite ledger。
- `market` 使用 ledger 中已记录的 snapshot 做首末价格与变化比例汇总；缺失时不补编。
- 面向用户展示时默认转为北京时间。

### simulated trading strategy review

顶层：

- `status`
- `source=trading_strategy_review`
- `date`
- `timezone`
- `review`
- `strategy_proposal`

`review.ledger_backtest`：

- `method=ledger_snapshot_replay`
- `runs_total`
- `orders_total`
- `risk_decisions_total`
- `rejection_rate`
- `order_mark_to_market`
- `average_order_return_ratio`

`strategy_proposal`：

- `schema_version=trading_strategy_proposal.v1`
- `status=candidate|blocked`
- `strategy_version`
- `approval_required=true`
- `effective_status=candidate_only|not_applied`
- `proposed_changes`
- `evidence`
- `constraints`

约束：

- 当前 `ledger_snapshot_replay` 只是基于已记录 snapshot 和 dry-run order 的回放式评估，不等同完整历史 K 线回测。
- proposal 只作为候选，不写策略配置、不改调度 state、不触发 broker。
- Agent 可以解释 proposal 和总结迭代方向，但不能在盘中链路里直接改策略或决定下单。

## 固定模板

默认优先输出固定模板，不默认附完整 raw JSON。只有用户明确要求调试 / 原始输出时，才附完整 JSON。

### realtime quote 模板

#### 请求

- symbols
- computed_at

#### 结果摘要

- `summary.ok`
- `summary.failed`
- 顶层 `status`

#### 逐标的行情

逐条汇总：

- `requested_symbol`
- `info.name`
- `quote_data.price`
- `quote_data.change_pct`
- `quote_data.change_amount`
- `quote_data.volume`
- `quote_data.mode`

#### 降级与异常

进入本节的条件：

- `item.status != ok`
- 或 `quote_data.mode != realtime`

### objective analyze 模板

#### 请求

- market
- symbols
- mode
- start_date / end_date

#### 执行状态

- `status_code`
- `data.status`
- `data.strategy`
- `item.status`
- `data.computed_at`

#### 客观分析摘要

只取 `data.items[0].summary.research_strategy`，并按固定顺序输出：

1. `expectations_vs_reported`
2. `fundamental_quality`
3. `valuation_context`
4. `catalyst_path`
5. `price_action_confirmation`
6. `cross_signal_alignment`
7. `risk_flags`
8. `evidence_strength`

#### 模块摘要

优先使用：

- `summary.technical`
- `summary.earnings`
- `summary.catalysts`
- `summary.screen`
- `summary.models`

#### 降级与限制

只取：

- `item.error`
- `item.meta.modules`

必须显式暴露：

- `partial`
- `permission_denied`
- `not_supported`
- 任何非 `ok` 模块状态

### simulated trading daily summary 模板

#### 请求

- `date`
- `timezone`
- ledger 来源

#### 当日摘要

- `summary.runs_total`
- `summary.orders_total`
- `summary.risk_decisions_total`
- `summary.accepted_risk_decisions`
- `summary.rejected_risk_decisions`
- `summary.codes`
- `summary.strategy_versions`

#### 行情与操作

- `market[].code`
- `market[].first_price`
- `market[].latest_price`
- `market[].change_ratio`
- `orders[].code`
- `orders[].side`
- `orders[].quantity`
- `orders[].price`
- `risk_reason_counts`

### simulated trading strategy review 模板

#### 评审状态

- `status`
- `review.gate_status`
- `review.gate_reasons`
- `review.ledger_backtest.method`

#### 回放式指标

- `review.ledger_backtest.runs_total`
- `review.ledger_backtest.orders_total`
- `review.ledger_backtest.rejection_rate`
- `review.ledger_backtest.average_order_return_ratio`
- `review.ledger_backtest.order_mark_to_market`

#### 策略候选

- `strategy_proposal.status`
- `strategy_proposal.strategy_version`
- `strategy_proposal.approval_required`
- `strategy_proposal.effective_status`
- `strategy_proposal.proposed_changes`
- `strategy_proposal.constraints`

必须明确说明：

- `ledger_snapshot_replay` 不是完整历史回测。
- proposal 未自动应用，仍需人工批准。

## 禁止事项

固定模板不得把源端字段升级成主观建议，不输出：

- `recommendation`
- `confidence`
- `price_target`
- `thesis`
- `conviction`
