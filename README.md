# stock-analysis-skill

`stock-analysis-skill` 是一个单一 skill 仓库，当前包含四类能力约定：

- `CLI 使用技能`：直接消费 `stock-analysis-api` 仓库中的内部 CLI
- `Futu/OpenD 使用技能`：路由到已安装的 `futuapi` / `install-futu-opend` skills
- `Tushare 使用技能`：保留 Tushare 本地工具与接口参考资产
- `Slash Commands`：为 skill command dispatch 暴露 `/hkipo` 与 `/cnipo`

本仓库不是行情 / 分析 / 交易实现源，不再维护本地 quote / analyze / trade wrapper。

默认路由原则：

- 单票分析、单票研报、客观摘要、A 股标准化实时行情：先走 `stock-analysis-api` CLI
- 港 / 美 / 多市场行情、盘口、期权、账户、持仓、订单、订阅：走 Futu/OpenD skills
- 只有明确要原始 Tushare 数据 / 接口 / 自定义导出时，才走 Tushare
- IPO 池研究型命令通过 slash command 触发，由宿主 Agent 继续完成联网分析

## 仓库结构

- `SKILL.md`: skill 使用说明与约束
- `commands.json`: skill command 声明
- `commands/*.py`: slash command 执行入口
- `scripts/tushare_toolkit.py`: `.env` 加载、Tushare 初始化、参考文档生成
- `references/cli.md`: CLI 使用说明、JSON 结构、固定模板
- `references/api_reference.md`: Tushare 接口总表
- `references/futu.md`: Futu/OpenD 路由与输出 Contract
- `PLANS/ROADMAP.md`: 跨轮次长期跟进项与整合路线
- `PLANS/ACTIVE.md`: 当前复杂任务目标、milestone、验证与 handoff
- `.env.example`: 本地环境变量模板

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 环境变量

复制模板：

```bash
cp .env.example .env
```

本仓库当前使用以下环境变量：

```bash
STOCK_ANALYSIS_API_ROOT="/absolute/path/to/stock-analysis-api"
TUSHARE_TOKEN="your_token_here"
TUSHARE_HTTP_URL=""
```

说明：

- `STOCK_ANALYSIS_API_ROOT`: 指向 `stock-analysis-api` 仓库根目录，供 CLI 使用技能直接调用其脚本
- `TUSHARE_TOKEN`: 供 Tushare 使用技能和 `scripts/tushare_toolkit.py` 使用
- `TUSHARE_HTTP_URL`: 可选，用于覆盖默认 Tushare 接口地址

## CLI 使用技能

标准命令统一直接调用 API 仓库：

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty
cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty
```

对应的：

- 原始 JSON 结构
- 固定模板
- 汇总规则
- downgrade / partial 语义

统一记录在 [references/cli.md](./references/cli.md)。


## Futu/OpenD 使用技能

Futu/OpenD 能力不在本仓库实现，统一路由到已安装的 skills：

- `futuapi`: 行情快照、K 线、盘口、逐笔、分时、市场状态、资金流、板块、条件选股、期权、账户、资金、持仓、订单、订阅、模拟/实盘交易
- `install-futu-opend`: OpenD 下载、安装、升级、启动、SDK 环境检查

路由边界：

- A 股标准化客观分析和低 token quote 仍优先走 `stock-analysis-api` CLI
- A 股 watchlist 只需现价 / 涨跌幅 / 简单异动提醒时，优先走 `poll_realtime_quotes.py`
- 混合市场 watchlist、带 `HK.` / `US.` 等前缀，或需要盘口 / 逐笔 / 分时 / K 线 / 订阅推送时，优先走 `futuapi`
- 港 / 美 / 多市场盘口、期权、账户、持仓、订单、订阅优先走 `futuapi`
- OpenD 未安装、未启动、SDK 版本不满足时，转入 `install-futu-opend`

输出 contract 见 [references/futu.md](./references/futu.md)。

安全边界：

- 默认只读或模拟交易
- 实盘交易必须用户明确要求，并在执行前二次确认账户、市场、代码、方向、数量、价格 / 订单类型、交易环境和有效期
- 禁止 AI 接触交易密码；OpenD 解锁必须由用户在 GUI 中手动完成

## Tushare 使用技能

本仓库继续保留本地 Tushare 工具：

```bash
python scripts/tushare_toolkit.py generate-docs
```

生成逻辑：

- 优先使用本地未跟踪的 `data/api-doc.csv.csv`
- 生成并更新 `references/api_reference.md`
- 若本地没有 CSV，则自动回退到已有 `references/api_reference.md` 重新规范化

Tushare 接口总表见 [references/api_reference.md](./references/api_reference.md)。

## Slash Commands

当宿主启用 skill command dispatch 后：

- `/hkipo`: 自动发现当前“可认购 + 已截止认购但未上市”的港股 IPO 池，并按评分卡输出简明优先级报告
- `/cnipo`: 预留 A 股 IPO 指令位，当前只返回占位说明

`/hkipo` 的事实数据优先来自当前联网检索到的 HKEX / 公司公告等一手来源；财经站只补充认购倍数、中签率、灰市、首日涨幅等二级数据。评分、融资倍数热度、绿鞋/基石检查、回测校准和单表简明输出规则见 [references/hkipo.md](./references/hkipo.md)。

## Skill 使用

在本地智能体中加载根目录 [SKILL.md](./SKILL.md) 后：

- 标准化客观分析 / 单票研报摘要 / A 股实时 quote 任务，优先走 `CLI 使用技能`
- 港 / 美 / 多市场行情、盘口、期权、账户、持仓、订单、订阅任务，走 `Futu/OpenD 使用技能`
- 自定义 Tushare 数据研究、接口查阅、文档生成任务，走 `Tushare 使用技能`
- `/hkipo` 这类 IPO 池研究命令，走 slash command 工作流，由宿主 Agent 继续完成联网分析、融资热度评分与单表简明优先级输出

## 注意事项

- 本项目仅供学习和研究使用，请勿用于商业用途
- 使用时请遵守 [Tushare 官方文档](https://tushare.pro/document/1?doc_id=290)、Futu OpenAPI 与对应使用条款
- 不自动执行实盘交易；交易动作必须由用户明确请求并二次确认
