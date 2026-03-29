---
name: stock-analysis-skill
description: 面向中文自然语言的股票分析技能。优先通过 `stock-analysis-api` 的标准 CLI 获取客观分析与低 token 行情结果；同时保留 Tushare 的直接使用能力，用于自定义数据研究、接口查阅和参考文档生成。
author: stock-analysis-skill
version: 2.0.0
credentials:
  - name: TUSHARE_TOKEN
    description: Tushare Token，用于认证和授权访问 Tushare 数据服务。
    how_to_get: "https://tushare.pro/register"
requirements:
  python: 3.9+
  packages:
    - name: tushare
    - name: python-dotenv
    - name: pandas
  environment_variables:
    - name: STOCK_ANALYSIS_API_ROOT
      required: true
      sensitive: false
    - name: TUSHARE_TOKEN
      required: false
      sensitive: true
    - name: TUSHARE_HTTP_URL
      required: false
      sensitive: false
  network_access: true
---

# stock-analysis-skill

这是一个单一 skill，但当前只保留两类能力说明：

- `CLI 使用技能`
- `Tushare 使用技能`

不要再把这个仓库当成 quote / analyze 的实现源。标准化客观分析和标准化实时行情，统一直接消费 `stock-analysis-api` 的 CLI。

## CLI 使用技能

### 适用场景

以下场景优先直接调用 `stock-analysis-api`：

- 获取指定股票的客观分析结果
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
