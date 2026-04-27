# CLI Reference

本文件是 `stock-analysis-skill` 的唯一 CLI 使用说明。

当前标准化能力统一直接调用 `stock-analysis-api` 仓库中的内部 CLI，本仓库不再维护 quote / analyze wrapper。

## 默认选择规则

以下请求默认直接走 CLI，不先走 Futu 或 Tushare：

- 单票客观分析
- 单票研报摘要
- 单票“最近怎么样”
- A 股股票 / ETF 标准化实时行情轮询

示例：

- “查 300627 的研报” 默认走 `stock_analyze.py`
- 只有“查 300627 的原始 report_rc 记录”才走 Tushare 直连
- 港 / 美 / 多市场 watchlist、盘口、逐笔、分时、K 线、订阅推送见 `references/futu.md`

## 环境变量

```bash
STOCK_ANALYSIS_API_ROOT="/absolute/path/to/stock-analysis-api"
TUSHARE_TOKEN="your_token_here"
TUSHARE_HTTP_URL=""
```

字段说明：

- `STOCK_ANALYSIS_API_ROOT`: `stock-analysis-api` 仓库根目录
- `TUSHARE_TOKEN`: A 股 realtime / Tushare 直连能力需要
- `TUSHARE_HTTP_URL`: 可选，覆盖默认 Tushare 接口地址

## 标准命令

### 1. realtime quote

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty
```

参数：

- `--symbols`: 逗号分隔的 A 股 / ETF 代码
- `--pretty`: 可选，格式化 JSON

### 2. objective analyze

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty
```

参数：

- `--market`
- `--symbols`
- `--start-date`
- `--end-date`
- `--mode`
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

## 禁止事项

固定模板不得把源端字段升级成主观建议，不输出：

- `recommendation`
- `confidence`
- `price_target`
- `thesis`
- `conviction`
