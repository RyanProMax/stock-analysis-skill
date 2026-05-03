# Roadmap

> 本文件负责跨轮次长期跟进。当前轮次执行细节统一写入 `PLANS/ACTIVE.md`。

## 当前长期方向

### 1. 富途 OpenAPI 能力整合

**目标**：把已安装的 `futuapi` / `install-futu-opend` skills 纳入 `stock-analysis-skill` 的统一路由，而不是复制富途脚本或把本仓库变成行情实现源。

**能力范围**：

- 行情：港股 / 美股 / A 股 / 新加坡期货等快照、报价、K 线、分时、盘口、逐笔成交、市场状态
- 衍生品：期权链、到期日、Greeks、窝轮/牛熊证、期货资料
- 资金与市场结构：资金流、资金分布、经纪队列、板块与成分股、条件选股
- 用户数据：账户、资金、持仓、订单、成交、交易流水等只读查询
- 禁止能力：自选股写入、订阅推送、下单、改单、撤单、交易解锁和其他状态变更

**整合原则**：

- `stock-analysis-skill` 只负责意图路由、固定模板和安全边界
- 标准 A 股低 token quote / objective analyze / `/research` A 股与美股深度研报底稿继续优先走 `stock-analysis-api` CLI；`/research` 由 executor 运行时解析绝对 API 命令，避免宿主工作区 cwd 影响
- 港 / 美 / 多市场行情、盘口、期权、账户、持仓、订单等只读查询能力路由到 `futuapi`
- OpenD 安装与连通性问题路由到 `install-futu-opend`
- 禁止 AI 接触交易密码；禁止通过 SDK 或脚本调用交易解锁

**待办**：

- [x] 在 `SKILL.md` 增加 Futu 路由优先级与安全边界
- [x] 在 `references/cli.md` 或新增 reference 中定义统一输出 contract
- [x] 明确 `futuapi` 与 `stock-analysis-api` 的市场 / 能力分工矩阵
- [x] 增加全局只读护栏，禁止任何写入、编辑、下单或交易状态变更行为
- [x] 设计 watchlist 监控场景如何选择 `poll_realtime_quotes.py` vs `futuapi get_stock_quote/get_snapshot`
- [x] 新增 `/research` 单票深度研报 slash command，A 股 / 美股优先复用 `stock_analyze.py --mode full`，港股后置走 Futu/OpenD + HKEX / AKShare / yfinance 降级路径

## Backlog

- [ ] `/cnipo` 从占位升级为 A 股 IPO 池工作流
- [x] `/research` 增加可信度层：`module_status`、`source_freshness`、`data_gaps`
- [x] `/research` 内置风险与反证，并把组合/持仓风险收敛到同入口只读约束
- [x] `/research` 增加历史验证模块边界：只做可复现历史统计，不输出交易建议
- [ ] `/research` 港股数据层从后置 prompt 路由升级为稳定字段矩阵与验证样例
- [ ] `/research` 美股补充 SEC filings / earnings transcript 证据层缓存与引用规范
- [x] 港股 IPO 池工作流增加近 100 个已上市 IPO 首日表现回测 MVP
- [x] 港股 IPO 回测补充评分分桶、排序相关性和高分/低分失配样本
- [x] 港股 IPO 回测支持用 Futu/OpenD 历史日 K 线重算首日涨幅
- [x] 港股 IPO 回测补充绿鞋/基石/暗盘 enrichment 数据源自动抓取
- [x] 港股 IPO 池工作流强制当前日期新鲜度与 Futu/OpenD 优先数据源
- [x] 港股 IPO 池输出压缩为极简结论和单表关键字段
- [x] 港股 IPO 池飞书输出改为窄卡片，避免宽表格横向滚动
- [x] 港股 IPO 池飞书输出去除大标题并加入固定 emoji 信号
- [ ] 港股 IPO 池工作流增加稳定的一手来源核验清单
- [ ] 研究是否接入富途资讯 / 公告 / 研报 / 社区情绪类 skills，补齐文章提到的 Skill Hub 能力
- [ ] 为跨 skill 能力增加最小验证样例，避免只更新说明不验证路由

## 已完成

- 2026-04-23：新增 `/hkipo` 与 `/cnipo` slash command 声明；`/hkipo` 输出港股 IPO 研究 prompt，`/cnipo` 保持占位。
- 2026-04-27：安装并审计富途官方 `futuapi` 与 `install-futu-opend` skills，开始规划统一整合到 `stock-analysis-skill`。
- 2026-04-27：移除旧 `docs/plan.md`，统一使用 `PLANS/`；完成 Futu/OpenD 路由优先级、能力边界和只读安全要求。
- 2026-04-27：新增 `references/futu.md`，定义 Futu/OpenD 路由与输出 Contract。
- 2026-04-27：完成 watchlist 自动选路规则：A 股轻量轮询优先 CLI，混合市场 / 深行情 / 账户联动优先 Futu。
- 2026-04-27：用户完成 OpenD 登录后，港股 IPO 只读查询验证通过；同步 `SKILL.md` / `README.md` / `AGENTS.md` / `references/futu.md` 的全局只读护栏。

- 2026-04-27：新增 `scripts/hkipo_backtest.py`，用 AAStocks Listed IPO 页面进行近 100 个港股 IPO 首日表现回测，验证超购热度分桶。
- 2026-04-28：增强 `scripts/hkipo_backtest.py` 的评分合理性校准，新增评分分桶、评分排序相关性、Top/Bottom 评分分位首日涨幅差和失配样本输出。
- 2026-04-28：`scripts/hkipo_backtest.py` 支持 `--debut-price-source futu-kline`，用 Futu/OpenD 历史日 K 线重算首日收盘涨幅；最近 100 样本实测覆盖 95/100。
- 2026-04-28：`scripts/hkipo_backtest.py` 支持 `--enrichment-source xinguyufu`，通过新股渔夫公开 API 补充绿鞋、基石、暗盘、保荐人和稳价人；最近 100 样本实测补充覆盖 97/100。
- 2026-04-28：`/hkipo` prompt 和 reference 已强制使用北京时间当前日期；当前 IPO 池发现和基础日程字段优先 Futu/OpenD，Futu 缺失字段才允许外部财经源补齐，且过期孖展/暗盘不得用于当前评分。
- 2026-04-28：`/hkipo` 输出模板已压缩为最多 3 条结论、单张评分总览表和 Sources；回测映射、Futu 覆盖、外部热度、发行结构和风险全部进表格。
- 2026-04-28：`/hkipo` 飞书输出模板改为窄卡片列表，避免宽 Markdown 表格横向滚动和裁切；Sources 改为短链接标签。
- 2026-04-28：`/hkipo` 飞书输出模板去除 `#` / `##` 大标题，改为普通加粗标签、短分隔和固定 emoji 信号。
- 2026-04-30：`/hkipo` Futu/OpenD 查询命令改为运行时动态解析当前 skill 安装目录和 `futuapi` 脚本路径，不再依赖用户工作区相对 `.venv` 或固定用户目录。
- 2026-05-01：新增 `/research` 单票深度研报 command 和 `references/research.md`，支持 A 股 / 美股优先、港股后置的统一研报模板与降级规范。
- 2026-05-01：`/research` A 股 / 美股 prompt 已改为运行时解析 `stock-analysis-api` 绝对命令；优先 `STOCK_ANALYSIS_API_ROOT`，再查找 skill 安装目录附近 sibling，缺失时显式预检失败并降级。

- 2026-05-03：`/research` 增加可信度层、风险与反证、历史验证模块；风险不新增独立 `/risk`，组合/持仓风险按同入口只读约束处理。
