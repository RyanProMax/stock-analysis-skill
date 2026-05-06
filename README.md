# stock-analysis-skill

`stock-analysis-skill` 是一个单一 skill 仓库，当前包含四类能力约定：

- `CLI 使用技能`：直接消费 `stock-analysis-api` 仓库中的内部 CLI
- `Futu/OpenD 使用技能`：`/hkipo` 与 `/research` 已用能力走 `stock-analysis-api` Futu CLI；其他尚未迁移能力明确标记为待 API provider 扩展，不再路由到外部 Futu skill
- `Tushare 使用技能`：保留 Tushare 本地工具与接口参考资产
- `Slash Commands`：为 skill command dispatch 暴露 `/research`、`/hkipo` 与 `/cnipo`

本仓库不是行情 / 分析 / 交易实现源，不再维护本地 quote / analyze / trade wrapper。

默认路由原则：

- 单票分析、单票研报、客观摘要、A 股标准化实时行情：先走 `stock-analysis-api` CLI
- `/hkipo`、`/research` 港股预检 / snapshot / K 线和 HK IPO 回测：走 `stock-analysis-api/scripts/futu_market_data.py`
- 港 / 美 / 多市场盘口、期权、账户、持仓、订单等尚未迁移的只读查询：返回“尚未迁入 API”，不绕回外部 Futu skill
- 只有明确要原始 Tushare 数据 / 接口 / 自定义字段或时间窗时，才走 Tushare
- `/research` 与 IPO 池等研究型命令通过 slash command 触发，由宿主 Agent 继续完成联网分析

## 仓库结构

- `SKILL.md`: skill 使用说明与约束
- `commands.json`: skill command 声明
- `commands/*.py`: slash command 执行入口
- `scripts/tushare_toolkit.py`: `.env` 加载、Tushare 初始化、参考文档生成
- `references/cli.md`: CLI 使用说明、JSON 结构、固定模板
- `references/research.md`: `/research` 单票深度研报模板、数据源路由与降级规则
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
STOCK_ANALYSIS_UV="/absolute/path/to/uv"
TUSHARE_TOKEN="your_token_here"
TUSHARE_HTTP_URL=""
```

说明：

- `STOCK_ANALYSIS_API_ROOT`: 指向 `stock-analysis-api` 仓库根目录，供 CLI 使用技能直接调用其脚本；`/research` 会优先使用该变量，未设置时再尝试当前 skill 安装目录附近的 sibling `stock-analysis-api`
- `STOCK_ANALYSIS_UV`: 可选但推荐，指向固定 `uv` 可执行文件；未设置时 `/research` 依次查 `UV_BIN` / `UV` / 当前 PATH / `$HOME/.local/bin/uv` / `$HOME/.cargo/bin/uv`，生成命令时使用解析后的绝对 `uv` 路径，避免服务重启后 PATH 漂移
- `TUSHARE_TOKEN`: 供 Tushare 使用技能和 `scripts/tushare_toolkit.py` 使用
- `TUSHARE_HTTP_URL`: 可选，用于覆盖默认 Tushare 接口地址

## CLI 使用技能

标准命令统一直接调用 API 仓库：

```bash
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty
cd "$STOCK_ANALYSIS_API_ROOT" && "$STOCK_ANALYSIS_UV" run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty
```

对应的：

- 原始 JSON 结构
- 固定模板
- 汇总规则
- downgrade / partial 语义

统一记录在 [references/cli.md](./references/cli.md)。


## Futu/OpenD 使用技能

Futu/OpenD 能力不在本仓库实现；统一路由到 API 仓库内部 CLI / provider：

- `stock-analysis-api/scripts/futu_market_data.py`: `/hkipo` 当前 IPO 池、`/research` 港股 OpenD 预检 / snapshot / K 线，以及 HK IPO 回测首日 K 线
- 尚未迁入 API 的盘口、逐笔、分时、期权、账户、资金、持仓、订单等能力：明确返回未支持，并进入 API provider backlog

路由边界：

- A 股标准化客观分析和低 token quote 仍优先走 `stock-analysis-api` CLI
- A 股 watchlist 只需现价 / 涨跌幅 / 简单异动提醒时，优先走 `poll_realtime_quotes.py`
- 混合市场 watchlist、带 `HK.` / `US.` 等前缀，或需要盘口 / 逐笔 / 分时 / K 线查询时，只使用 API 已实现的 Futu CLI 能力
- 港 / 美 / 多市场盘口、期权、账户、持仓、订单等未迁移只读查询，明确说明暂未迁入 API
- OpenD 未安装、未启动、SDK 版本不满足时，说明 API Futu CLI / OpenD 环境不可用

输出 contract 见 [references/futu.md](./references/futu.md)。

安全边界：

- 只允许查询操作；禁止下单、改单、撤单、订阅、交易解锁或任何账户 / 订单 / 配置状态变更
- 即使用户已登录 OpenD、使用模拟账户或明确要求，也不得调用写入、编辑、下单或交易类脚本
- 禁止 AI 接触交易密码；禁止通过 SDK 或脚本调用交易解锁

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

- `/hkipo`: 默认自动发现当前仍可认购的港股 IPO 池，并按评分卡输出简明优先级报告；`/hkipo --all` 才纳入已截止认购但未上市标的
- `/research`: 对一只 A 股 / 美股 / 港股生成深度研报 prompt；支持股票名输入，由上游 `stock-analysis-api` CLI 解析唯一上市代码后再分析；A 股 / 美股优先复用运行时解析出的 `stock-analysis-api` full mode 绝对命令；显式港股先做 OpenD 预检，失败时先询问是否继续
- `/cnipo`: 预留 A 股 IPO 指令位，当前只返回占位说明

`/research` 只支持单只股票。常用输入包括 `/research 宁德时代`、`/research 300750`、`/research cn 300750`、`/research US.AAPL`、`/research AAPL`、`/research HK.00700` 和 `/research 0700.HK`。命令本身只做参数解析、`stock-analysis-api` / OpenD 预检和 prompt 生成；股票名 / 公司名会原样传给上游 CLI 的 `--symbols`，由 `stock-analysis-api` 在调用分析链路前解析唯一代码；executor 不查本地库、不硬编码匹配、不生成下游标的识别阶段。A 股 / 美股 prompt 中的 CLI 命令由 executor 按 `STOCK_ANALYSIS_API_ROOT` 或 sibling `stock-analysis-api` 动态解析 API 根目录，并按 `STOCK_ANALYSIS_UV` / `UV_BIN` / `UV` / PATH / `$HOME/.local/bin/uv` / `$HOME/.cargo/bin/uv` 解析绝对 `uv`；代码输入和股票名输入都会生成完整命令，找不到 API 仓库时必须显式进入降级；若上游返回 `identity_conflict` / `identity_not_found`，agent 必须先向用户澄清。显式港股会在进入 agent 前调用 `stock-analysis-api/scripts/futu_market_data.py global-state --json` 做 OpenD 只读预检；预检失败时直接返回确认提示，不生成研报 prompt。用户明确发送 `/research HK.00700 --continue-without-opend` 后，才允许按 HKEX / 公司公告 / AKShare / yfinance 降级继续。研报必须按 [references/research.md](./references/research.md) 输出，明确 `module_status`、`source_freshness`、`data_gaps`、行业整体趋势、市场热度、同类公司平均 PE、权威机构研报汇总、风险与反证、历史验证、Sources 和降级原因；飞书默认短版且最终回复必须直接从标题开始，不混入执行过程日志；不输出买卖建议、目标价或确定性承诺。

`/hkipo` 必须按当前日期重新取数。默认只输出当前仍可认购的港股 IPO，过滤 Futu/OpenD 返回的 `is_subscribe_status=false` 已截止新股；用户显式发送 `/hkipo --all` 时才纳入已截止认购但未上市标的。当前 IPO 池、招股状态、上市日、招股截止日、发售价、一手股数和入场费优先使用 `stock-analysis-api/scripts/futu_market_data.py ipo-list --market HK --json`；命令由 executor 按当前 skill 安装目录动态生成，不能依赖用户工作区相对 `.venv` 或其他脚本。Futu/OpenD 不可用或字段缺失时，才用 HKEX / 公司公告 / 财经站补齐并标注降级。热度字段按固定顺序核验：Futu/OpenD 当前字段、当日或最接近报告日的券商/财经站孖展统计、公开认购倍数/一手中签率、暗盘；所有数值必须标注来源更新时间，旧孖展/暗盘只能作趋势参考，不能进入当前热度主评分。输出只约束最终报告正文：不用 `#` / `##` 大标题和宽 Markdown 表格；结论最多 3 条，个股标题末尾写 `M/D截止 | M/D开奖`，不写建议性措辞或跟踪标签；个股核心内容整合进窄字段块列表。正文不要插入空白空行；`关键结论`、`优先级`、个股条目、`来源` 和 `阶段`、`热度`、`结构`、`回测`、`风险` 小点都用单换行连续排列。评分、融资倍数热度、绿鞋/基石检查、回测映射和字段块输出规则见 [references/hkipo.md](./references/hkipo.md)。

### 港股 IPO 回测

用于校准 `/hkipo` 的首日赔率评分：

```bash
python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown
```

当前脚本默认使用 AAStocks Listed IPO 页面，自动抓取近期已上市港股 IPO 的上市日、发行价、市值区间、公开超购倍数、一手中签率和首日涨幅，并输出胜率、平均/中位首日涨幅、破发率、热度分桶、评分分桶、行业分桶、估值/市值分桶、多维评分相关性、评分排序相关性和高分破发 / 低分大涨失配样本。

若 OpenD 已登录，可用 Futu 历史日 K 线重算首日收盘涨幅；AAStocks 仍只作为最近 100 个 IPO 样本清单和发行价来源：

```bash
python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --enrichment-source xinguyufu --debut-price-source futu-kline --api-root "$STOCK_ANALYSIS_API_ROOT" --uv "$STOCK_ANALYSIS_UV" --format markdown
```

API Futu CLI 的 `ipo-list --market HK` 只覆盖当前 IPO 列表，不提供最近 100 个已上市 IPO 清单，也不提供绿鞋 / 基石 / 暗盘历史字段。

行业默认通过公司名启发式分类；绿鞋、基石、暗盘、保荐人和稳价人可用新股渔夫公开 API 补充。该抓取方式参考 AKShare 的公开网页接口模式：使用浏览器 UA 请求公开页面 / JSON，再按字段名映射。

```bash
python3 scripts/hkipo_backtest.py --limit 100 --enrichment-source xinguyufu --format markdown
```

离线或人工核验场景也可用 enrichment CSV 补充：

```bash
python3 scripts/hkipo_backtest.py --limit 100 --enrichment-csv data/hkipo_enrichment.csv
```

CSV 可选列：`code,industry,greenshoe,cornerstone,grey_market_return_pct`。若不提供，绿鞋/基石/暗盘按中性缺失处理，并在报告中显示覆盖率。

## Skill 使用

在本地智能体中加载根目录 [SKILL.md](./SKILL.md) 后：

- 标准化客观分析 / 单票研报摘要 / A 股实时 quote 任务，优先走 `CLI 使用技能`
- 港 / 美 / 多市场行情、盘口、期权、账户、持仓、订单等只读查询任务，只走 API 已迁移的 Futu/OpenD 能力；未迁移能力明确说明暂不支持
- 自定义 Tushare 数据研究、接口查阅任务，走 `Tushare 使用技能`；生成参考文档仅限仓库维护任务
- `/research` 单票深度研报和 `/hkipo` IPO 池研究命令，走 slash command 工作流，由宿主 Agent 继续完成联网分析、数据质量标注和结构化输出

## 注意事项

- 本项目仅供学习和研究使用，请勿用于商业用途
- 使用时请遵守 [Tushare 官方文档](https://tushare.pro/document/1?doc_id=290)、Futu OpenAPI 与对应使用条款
- 不执行任何下单、改单、撤单、订阅、交易解锁或其他运行时写入操作
