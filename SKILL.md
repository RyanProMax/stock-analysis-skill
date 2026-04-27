---
name: stock-analysis-skill
description: Use when users ask in Chinese or natural language for stock objective analysis, realtime quotes, research-report summaries, HK IPO pool screening, raw Tushare data, or read-only Futu/OpenD market/account queries.
metadata:
  version: 2.1.1
---

# stock-analysis-skill

`stock-analysis-skill` 是股票任务的意图路由与输出约束，不是行情、分析或交易实现源。当前只保留四类入口：

- `CLI 使用技能`：标准化 A 股客观分析、单票研报摘要、A 股 / ETF 低 token 实时行情。
- `Futu/OpenD 使用技能`：港 / 美 / 多市场行情、深度行情、衍生品、账户 / 持仓 / 订单等只读查询。
- `Tushare 使用技能`：用户明确要求的原始 Tushare 接口、字段、时间窗或接口查阅。
- `Slash Commands`：`/hkipo` 港股 IPO 池研究工作流；`/cnipo` 目前占位。

## 全局只读护栏

运行时使用本 skill 时只允许查询和结果展示；不得产生任何账户、订单、订阅、配置、自选股、提醒或本地文件状态变更。

- 允许：行情、K 线、盘口、逐笔、分时、IPO、期权链、账户、资金、持仓、订单、成交、流水等只读查询。
- 禁止：下单、改单、撤单、交易解锁、订阅推送、创建 / 修改价格提醒、写入 watchlist、修改配置、导出文件或任何其他写入动作。
- 用户请求写入 / 编辑 / 下单 / 订阅 / 解锁时，必须拒绝执行；不得用模拟账户、已登录 OpenD 或用户二次确认作为绕过理由。
- 仓库维护例外：只有在用户明确要求维护本仓库文档 / 脚本时，才允许运行会更新本仓库文件的维护命令，例如 `scripts/tushare_toolkit.py generate-docs`。
- 不输出买卖建议、目标价、主观 conviction、`recommendation`、`confidence`、`price_target`、`thesis`。
- 账户、资金、持仓等敏感信息按最小必要原则展示。

## 路由优先级

先判断用户意图，再选择唯一主路由；不要为同一个问题同时散开到多个数据源。

| 用户意图 | 默认路由 | 关键边界 |
| --- | --- | --- |
| `/hkipo` | `Slash Commands` | 自动发现港股 IPO 池，按 `references/hkipo.md` 评分 |
| `/cnipo` | `Slash Commands` | 当前只返回占位说明 |
| 单票客观分析、研报式摘要、“最近怎么样” | `CLI 使用技能` | 默认走 `stock_analyze.py`，不直接查原始 `report_rc` |
| A 股股票 / ETF 低 token 实时行情 | `CLI 使用技能` | 默认走 `poll_realtime_quotes.py` |
| 港 / 美 / 多市场行情、盘口、逐笔、分时、K 线、期权、持仓、订单等只读查询 | `Futu/OpenD 使用技能` | 仅限只读；OpenD 问题转 `install-futu-opend` |
| 原始 Tushare 数据、接口清单、自定义字段或时间窗 | `Tushare 使用技能` | 只有用户明确要求原始接口时才使用 |

明确例外：

- “查 300627 的研报”默认走 `stock_analyze.py`；只有“原始券商研报记录 / 原始 report_rc 数据”才走 Tushare。
- A 股 watchlist 只需现价、涨跌幅、全量快照或简单异动提醒时，默认仍走 `poll_realtime_quotes.py`。
- 混合市场 watchlist、带 `HK.` / `US.` 等前缀，或需要盘口、逐笔、分时、K 线时，走 `Futu/OpenD 使用技能`。

## CLI 使用技能

适用于标准化结果、固定模板和稳定 JSON contract。执行前确认：

1. `STOCK_ANALYSIS_API_ROOT` 指向 `stock-analysis-api` 仓库根目录。
2. `uv` 可用。
3. API 仓库存在 `scripts/poll_realtime_quotes.py` 与 `scripts/stock_analyze.py`。
4. A 股数据所需的 `TUSHARE_TOKEN` / `TUSHARE_HTTP_URL` 可被 API 仓库读取。

标准命令：

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty
```

输出规则统一见 `references/cli.md`。默认不要原样转贴 raw JSON；除非用户明确要求调试或原始输出，优先按固定模板汇总。`change_pct`、`turnover_rate`、`amplitude` 等 ratio 字段面向用户展示为百分比。

## Futu/OpenD 使用技能

适用于 `HK.` / `US.` 等多市场代码、深度行情、期权链、窝轮 / 牛熊证、期货资料、资金流、板块、条件选股、账户、资金、持仓、订单、成交和流水等只读查询。

进入该路由前确认：

1. `futuapi` skill 已安装并可加载。
2. OpenD 正在运行，默认地址 `127.0.0.1:11111`。
3. Python SDK `futu-api` 版本满足 `futuapi` skill 要求。
4. 请求不涉及交易、订阅、提醒、自选股、配置或本地文件写入。

OpenD 未安装、未启动或 SDK 版本不满足时，转入 `install-futu-opend`。输出 contract、watchlist 选路、失败降级和拒绝模板统一见 `references/futu.md`。

## Tushare 使用技能

仅在用户明确要求原始 Tushare 数据或接口能力时使用，例如：

- 点名 `report_rc`、`research_report`、`news` 等接口。
- 要求自定义字段、自定义时间窗或接口清单。
- CLI 无法覆盖当前需求，且需要继续深挖原始数据。

原则：

- 单票分析、单票研报摘要、A 股标准化实时行情，默认回到 `CLI 使用技能`。
- 数据权限不够或接口返回为空时，直接说明限制，不伪造。
- 面向用户的查询默认只在回复中展示结果，不写文件、不导出。
- `scripts/tushare_toolkit.py generate-docs` 只用于仓库维护任务；接口总表见 `references/api_reference.md`。

## Slash Commands

- `/hkipo`：自动发现当前“可认购 + 已截止认购但未上市”的港股 IPO 池，并按评分卡输出简明优先级报告。
- `/cnipo`：预留 A 股 IPO 指令位，当前只返回占位说明。

`/hkipo` 要求：

- 读取 `references/hkipo.md`，使用 0-100 首日赔率评分卡。
- 事实层优先依赖当前联网检索到的 HKEX / 公司公告等一手来源；财经站只补充认购倍数、中签率、灰市、首日涨幅等二级数据。
- 必须检查绿鞋 / 超额配股权、稳定价格操作人、基石质量与占比、保荐人、回拨和公众货比例。
- 默认输出简明报告：结论先行、单表评分总览、回测校准、Sources；维度细节整合进表格，不单列“简评”。
- 需要校准权重时运行：`python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`。

## 输出要求

- 结论先行，只输出影响用户决策、验收或下一步行动的信息。
- 面向用户展示时间默认使用北京时间（Asia/Shanghai, UTC+8）。
- 明确标注数据源、请求标的、成功 / 失败 / 降级状态。
- 源端不可用、权限不足或结果缺失时，说明限制，不补编。
- 财务与账户相关结果只做事实汇总和风险提示，不替代投资顾问。

## References

- CLI 使用说明：`references/cli.md`
- 港股 IPO 评分与回测：`references/hkipo.md`
- Tushare 接口总表：`references/api_reference.md`
- Futu/OpenD 路由与输出 Contract：`references/futu.md`
- Futu/OpenD 能力：已安装的 `futuapi` 与 `install-futu-opend` skills
- Tushare 官方文档：<https://tushare.pro/document/1?doc_id=290>
