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
- 标准 A 股低 token quote / objective analyze 继续优先走 `stock-analysis-api` CLI
- 港 / 美 / 多市场行情、盘口、期权、账户、持仓、订单等只读查询能力路由到 `futuapi`
- OpenD 安装与连通性问题路由到 `install-futu-opend`
- 禁止 AI 接触交易密码；禁止通过 SDK 或脚本调用交易解锁

**待办**：

- [x] 在 `SKILL.md` 增加 Futu 路由优先级与安全边界
- [x] 在 `references/cli.md` 或新增 reference 中定义统一输出 contract
- [x] 明确 `futuapi` 与 `stock-analysis-api` 的市场 / 能力分工矩阵
- [x] 增加全局只读护栏，禁止任何写入、编辑、下单或交易状态变更行为
- [x] 设计 watchlist 监控场景如何选择 `poll_realtime_quotes.py` vs `futuapi get_stock_quote/get_snapshot`

## Backlog

- [ ] `/cnipo` 从占位升级为 A 股 IPO 池工作流
- [x] 港股 IPO 池工作流增加近 100 个已上市 IPO 首日表现回测 MVP
- [x] 港股 IPO 回测补充评分分桶、排序相关性和高分/低分失配样本
- [ ] 港股 IPO 回测补充绿鞋/基石/暗盘 enrichment 数据源自动抓取
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
