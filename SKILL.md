---
name: stock-analysis-skill
description: 面向中文自然语言的股票分析技能。优先通过 `stock-analysis-api` 的标准 CLI 获取客观分析与低 token 行情结果；同时保留 Tushare 的直接使用能力，用于自定义数据研究、接口查阅和参考文档生成。
metadata:
  version: 2.0.2
---

# stock-analysis-skill

这是一个单一 skill，但当前只保留两类能力说明：

- `CLI 使用技能`
- `Tushare 使用技能`

不要再把这个仓库当成 quote / analyze 的实现源。标准化客观分析和标准化实时行情，统一直接消费 `stock-analysis-api` 的 CLI。

## 路由优先级

先判断是不是“标准化分析 / 标准化行情”问题，再决定是否进入 Tushare。

### 默认必须先走 CLI 的场景

以下请求默认必须先走 `CLI 使用技能`，不要先走 Tushare：

- 单只股票的客观分析
- 单只股票的“研报 / 研究摘要 / 最新看法 / 客观结论”
- “帮我看 300627 最近怎么样”
- “帮我查 300627 的研报”
- “给我 300627 的客观分析结果”
- 一组股票 / ETF 的低 token 实时行情轮询

这些请求的默认目标是：

- 标准化结果
- 固定模板
- 稳定 JSON contract

所以应先调用：

- `scripts/stock_analyze.py`
- `scripts/poll_realtime_quotes.py`

### 只有这些情况才走 Tushare

只有在以下场景，才优先进入 `Tushare 使用技能`：

- 用户明确要求原始 Tushare 接口数据
- 用户明确点名 `report_rc`、`research_report`、`news` 等接口
- 用户要自定义字段、自定义时间窗、自定义导出
- 用户要查接口列表、生成参考文档、研究 Tushare 能力边界
- CLI 无法覆盖当前需求，且需要继续深挖原始数据

### 明确例外

- “查 300627 的研报” 默认按 `stock_analyze.py` 处理，不默认按 `report_rc` 原始接口处理
- 只有当用户明确说“我要原始券商研报记录 / 原始 report_rc 数据”时，才改走 Tushare

## CLI 使用技能

### 适用场景

以下场景优先直接调用 `stock-analysis-api`：

- 获取指定股票的客观分析结果
- 获取指定股票的研报式客观摘要
- 获取一组 A 股 / ETF 的低 token 实时行情
- 需要稳定 JSON contract，而不是自由文本
- 需要固定模板汇总结果，而不是临时发挥

### 环境检查

执行前先检查：

1. `STOCK_ANALYSIS_API_ROOT` 已配置，且指向 `stock-analysis-api` 仓库根目录
2. `uv` 可用
3. `stock-analysis-api` 仓库中存在：
   - `scripts/poll_realtime_quotes.py`
   - `scripts/stock_analyze.py`
4. 若查询 A 股数据，确认 API 仓库可读取 `TUSHARE_TOKEN` / `TUSHARE_HTTP_URL`

推荐 `.env`：

```bash
STOCK_ANALYSIS_API_ROOT="/absolute/path/to/stock-analysis-api"
TUSHARE_TOKEN="your_token_here"
TUSHARE_HTTP_URL=""
```

### 标准命令

实时行情：

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty
```

客观分析：

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty
```

### 固定模板

默认不要直接把 raw JSON 原样塞给用户；优先按固定模板汇总。

#### realtime quote 模板

- `请求`
- `结果摘要`
- `逐标的行情`
- `降级与异常`

汇总规则：

- 顶层摘要只看 `summary.ok / summary.failed`
- 单标的内容只看 `items[]`
- `quote_data.mode != realtime` 或 `item.status != ok` 必须进入“降级与异常”
- `change_pct / turnover_rate / amplitude` 一律按 ratio 解读

#### objective analyze 模板

- `请求`
- `执行状态`
- `客观分析摘要`
- `模块摘要`
- `降级与限制`

汇总规则：

- 主摘要只取 `data.items[0].summary.research_strategy`
- 必须按固定 8 项输出：
  - `expectations_vs_reported`
  - `fundamental_quality`
  - `valuation_context`
  - `catalyst_path`
  - `price_action_confirmation`
  - `cross_signal_alignment`
  - `risk_flags`
  - `evidence_strength`
- 模块状态只取 `item.meta.modules`
- 禁止把源端字段升级成主观建议，不输出：
  - `recommendation`
  - `confidence`
  - `price_target`
  - `thesis`
  - `conviction`

详细 JSON 结构、字段说明、模板示例统一见 `references/cli.md`。

## Tushare 使用技能

### 适用场景

以下场景使用本仓库自带的 Tushare 能力：

- 用户明确要求原始 Tushare 数据，而不是标准化分析结论
- 查询和整理 Tushare 接口
- 做自定义数据研究
- 生成或刷新本地接口总表
- 直接围绕 Tushare 组织研究工作流

### 环境检查

执行前先检查：

1. Python 可用
2. `tushare` 已安装
3. `TUSHARE_TOKEN` 已配置；如需覆盖接口地址，再配置 `TUSHARE_HTTP_URL`

若缺失 token，最短修复路径：

```bash
TUSHARE_TOKEN=your_token
TUSHARE_HTTP_URL=
```

### 本地工具

生成 / 刷新接口总表：

```bash
python scripts/tushare_toolkit.py generate-docs
```

说明：

- `scripts/tushare_toolkit.py` 负责 `.env` 加载、Tushare 初始化、参考文档生成
- `references/api_reference.md` 是当前唯一 Tushare 接口总表

### 使用原则

- 单票分析 / 单票研报 / 单票客观总结，默认回到 `CLI 使用技能`
- 先理解任务，再选接口
- 数据权限不够时要明确说限制，不要硬编
- 缺失数据时宁可说明为空，也不要伪造
- 需要标准化客观分析或标准化实时行情时，回到 `CLI 使用技能`

## What This Skill Is Not For

- 不直接给买卖建议或替代投资顾问
- 不自动下单或执行交易
- 不输出主观 thesis、confidence 或 target price
- 不在没有权限或数据的情况下伪造结果

## References

- CLI 使用说明：`references/cli.md`
- Tushare 接口总表：`references/api_reference.md`
- Tushare 官方文档：<https://tushare.pro/document/1?doc_id=290>
