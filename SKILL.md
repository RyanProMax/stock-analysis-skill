---
name: stock-analysis-skill
description: 面向中文自然语言的股票分析技能。优先通过 `stock-analysis-api` 的标准 CLI 获取客观分析与低 token 行情结果；同时保留 Tushare 原始数据能力、Futu/OpenD 多市场行情与交易路由能力，并提供 IPO 池类 slash command 工作流。
metadata:
  version: 2.1.0
---

# stock-analysis-skill

这是一个单一 skill，但当前只保留四类能力说明：

- `CLI 使用技能`
- `Futu/OpenD 使用技能`
- `Tushare 使用技能`
- `Slash Commands`

不要再把这个仓库当成 quote / analyze / trade 的实现源。标准化客观分析和标准化 A 股实时行情，统一直接消费 `stock-analysis-api` 的 CLI；Futu/OpenD 能力通过已安装的 `futuapi` / `install-futu-opend` skills 路由。

## Slash Commands

当前仓库额外提供一层 skill command 入口，供 cli-claw 这类宿主在 slash command 上直接调用：

- `/hkipo`: 自动发现当前“可认购 + 已截止认购但未上市”的港股 IPO 池，并按评分卡输出简明优先级报告
- `/cnipo`: 预留 A 股 IPO 指令位，当前只返回占位说明

这些 command 不等价于 `stock-analysis-api` CLI：

- `/hkipo` 是 IPO 池研究工作流，不要求用户先给代码
- 当前 `stock-analysis-api` 的标准 `stock_analyze.py` 仍以 `cn/us` 为主，不负责港股 IPO 状态发现
- `/hkipo` 事实层必须依赖当前联网检索到的 HKEX / 公司公告等一手来源；财经站只补充认购倍数、中签率、灰市、首日涨幅等二级数据
- `/hkipo` 必须读取 `references/hkipo.md`，使用 0-100 首日赔率评分卡，优先覆盖融资/认购热度、发行结构、回测适配，再覆盖基本面、估值、证据质量
- `/hkipo` 必须检查绿鞋 / 超额配股权、稳定价格操作人、基石质量与占比、保荐人、回拨和公众货比例
- `/hkipo` 默认输出简明报告：结论先行、单表评分总览、回测校准、Sources；不要输出单独“简评”章节，维度细节整合进表格
- 需要校准权重时，运行 `python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown` 获取近 100 个已上市港股 IPO 的首日表现分桶

## 路由优先级

先判断是不是“标准化分析 / 标准化行情”问题，再按能力边界决定进入 `CLI 使用技能`、`Futu/OpenD 使用技能`、`Tushare 使用技能` 或 `Slash Commands`。

### 默认必须先走 CLI 的场景

以下请求默认必须先走 `CLI 使用技能`，不要先走 Futu 或 Tushare：

- 单只股票的客观分析
- 单只股票的“研报 / 研究摘要 / 最新看法 / 客观结论”
- “帮我看 300627 最近怎么样”
- “帮我查 300627 的研报”
- “给我 300627 的客观分析结果”
- A 股股票 / ETF 的低 token 实时行情轮询

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
- `/hkipo` 属于 skill-native IPO 池工作流：默认先发现当前港股 IPO 池，再按 `references/hkipo.md` 做首日赔率评分、融资倍数热度评估、绿鞋/基石检查、首日回测校准和单表简明优先级输出，不要求用户提供股票代码
- `/cnipo` 当前只占位，不进入真实分析

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

## Futu/OpenD 使用技能

### 适用场景

以下场景优先路由到已安装的 `futuapi` skill；若 OpenD 未安装、未启动或 SDK 版本不满足要求，再路由到 `install-futu-opend`：

- 港股 / 美股 / 多市场行情快照、报价、K 线、分时、盘口、逐笔成交、市场状态
- 期权链、到期日、Greeks、窝轮 / 牛熊证、期货资料
- 资金流、资金分布、经纪队列、板块列表、板块成分股、条件选股
- 用户自选股、自选分组、账户、资金、持仓、订单、成交、资金流水
- 订阅 quote、ticker、orderbook、kline、rt_data、broker 等实时推送
- 用户明确要求通过 Futu/OpenD 查询或操作

### 环境检查

进入 Futu/OpenD 路由前先确认：

1. `futuapi` skill 已安装并可被当前宿主加载
2. OpenD 正在运行，默认地址 `127.0.0.1:11111`
3. Python SDK `futu-api` 版本满足 `futuapi` skill 要求
4. 交易相关能力默认使用模拟环境；实盘交易必须由用户明确要求

### 路由边界

- A 股标准化客观分析、A 股低 token quote、固定模板研究摘要：默认仍回到 `CLI 使用技能`
- A 股 watchlist 只需要现价、涨跌幅、全量快照、简单异动提醒时：默认走 `poll_realtime_quotes.py`
- 混合市场 watchlist、带 `HK.` / `US.` 等前缀代码，或需要盘口、逐笔、分时、K 线、订阅推送时：走 `Futu/OpenD 使用技能`
- 原始 Tushare 接口、接口清单、自定义字段导出：走 `Tushare 使用技能`
- 港 / 美 / 多市场盘口、期权、账户、持仓、订单、订阅：走 `Futu/OpenD 使用技能`
- OpenD 下载、安装、升级、启动、SDK 升级：走 `install-futu-opend`

### 交易安全

- 默认只读或模拟交易；不得默认执行实盘交易
- 实盘下单 / 撤单 / 改单必须满足：用户明确说“实盘”或等价表达，并在执行前二次确认关键字段
- 二次确认至少包含：账户、市场、代码、方向、数量、价格 / 订单类型、交易环境、有效期
- 禁止要求、保存或代填交易密码；OpenD 解锁必须由用户在 GUI 中手动完成
- 任何交易动作都要在回复中保留 audit 摘要：时间（北京时间）、操作、参数、执行结果或失败原因

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
- 不自动下单或执行交易；只有用户明确要求并二次确认后，才可路由到 Futu/OpenD 交易能力
- 不输出主观 thesis、confidence 或 target price
- 不在没有权限或数据的情况下伪造结果

## References

- CLI 使用说明：`references/cli.md`
- Tushare 接口总表：`references/api_reference.md`
- Futu/OpenD 路由与输出 Contract：`references/futu.md`
- Futu/OpenD 能力：已安装的 `futuapi` 与 `install-futu-opend` skills
- Tushare 官方文档：<https://tushare.pro/document/1?doc_id=290>
