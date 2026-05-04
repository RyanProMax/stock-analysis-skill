# Active Plan

> 本文件是当前复杂任务的单一真相源。一次只允许一个 milestone 处于 `in_progress`。

## Task

把富途 OpenAPI skills 的能力纳入 `stock-analysis-skill` 的统一规划，并建立与 Cli Claw 风格一致的 `PLANS/ROADMAP.md` + `PLANS/ACTIVE.md` 工作流入口。

## Context

- 当前仓库仍是 skill 路由与说明仓库，不承担行情 / 分析实现。
- 已安装外部 skills：`futuapi`、`install-futu-opend`。
- 当前 A 股标准化实时行情和客观分析仍由 `stock-analysis-api` CLI 提供。
- 富途能力覆盖行情、盘口、K 线、期权、账户、持仓、订单、订阅和交易。
- 对用户展示任务时间时，默认使用北京时间（Asia/Shanghai, UTC+8）。

## Milestones

### M21 — /research 英文公司名纠偏与 MiniMax 路由

Status: `done`

Scope:

- `commands/research.py`
- `references/research.md`
- `SKILL.md`
- `tests/test_research_command.py`
- `PLANS/ACTIVE.md`
- `PLANS/ROADMAP.md`

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-04：确认 `/research MINIMAX` 被本地 executor 在上游前按全大写正则归为 `us`，导致 prompt 和标题固定为 `US.MINIMAX`，上游和联网证据没有纠偏空间。
- 2026-05-04：本轮目标是让长英文公司名输入进入“待解析/可纠偏”路径；若公开来源唯一指向港股，最终报告必须切到港股标题和港股数据路径。
- 2026-05-04：已将短裸美股 ticker 与较长英文公司名拆开处理；`MINIMAX` 生成 `待解析` 路由，不再生成 `--market us --symbols MINIMAX` 或 `US.MINIMAX` 固定标题。
- 2026-05-04：已同步 `SKILL.md` 和 `references/research.md`，要求读取上游结构化失败字段后再澄清或改道，不能把美股行情失败包装成有效美股报告。

Validation results:

- passed 2026-05-04：`python3 -m unittest tests/test_research_command.py`
- passed 2026-05-04：`python3 -m py_compile scripts/*.py commands/*.py`
- passed 2026-05-04：`git diff --check`

Handoff:

- 后续若需要把 `MINIMAX` 自动落到 `HK.00100`，应在上游身份解析层增加跨市场唯一匹配能力；本轮 skill executor 负责避免错误预分类，并把纠偏要求明确写入 prompt。

### M1 — 建立计划入口

Status: `done`

Scope:

- 创建 `PLANS/ROADMAP.md`
- 创建 `PLANS/ACTIVE.md`
- 移除旧 `docs/plan.md`，统一使用 `PLANS/`
- 更新 `AGENTS.md`，说明新计划入口与北京时间口径

Validation:

- `test -f PLANS/ROADMAP.md && test -f PLANS/ACTIVE.md`
- `python3 -m py_compile scripts/*.py commands/*.py`
- 人工检查 `AGENTS.md` / `README.md` / `SKILL.md` / `PLANS/*.md` 职责不冲突

### M2 — 设计 Futu 路由矩阵

Status: `done`

Scope:

- 在 `SKILL.md` 增加 Futu/OpenD 路由优先级
- 明确 `stock-analysis-api`、Tushare、Futu 三者边界
- 定义交易 / 账户能力的安全确认要求

Validation:

- 文档一致性检查：`SKILL.md`、`README.md`、`AGENTS.md`、`PLANS/ROADMAP.md`
- 若涉及示例命令，只使用只读行情脚本验证，不触发实盘交易

### M3 — 统一输出 contract

Status: `done`

Scope:

- 定义 quote snapshot、watch alert、option chain、portfolio risk、trade intent 输出模板
- 明确 ratio / percent、时区、数据源降级和异常表达
- 给出 watchlist 全量快照 + 异动 emoji 的固定模板

Validation:

- 用当前 A 股 watchlist 场景复核模板可读性
- 确认不输出主观买卖建议、目标价或交易密码相关内容

### M4 — Watchlist 自动选路

Status: `done`

Scope:

- 设计 `poll_realtime_quotes.py` 与 `futuapi get_stock_quote/get_snapshot` 的选择规则
- 明确混合市场 watchlist 的 batch 拆分和合并输出
- 明确失败、降级和用户要求剔除未纳入标的时的表达

Validation:

- 文档一致性检查：`SKILL.md`、`README.md`、`references/cli.md`、`references/futu.md`、`PLANS/ROADMAP.md`
- 不触发真实 Futu/OpenD 交易或订阅


### M5 — 强化 hkipo 评分与回测工作流

Status: `done`

Scope:

- 更新 `SKILL.md` 的 `/hkipo` 边界说明
- 更新 `commands/hkipo.py` 输出的研究 prompt
- 新增 `references/hkipo.md`，沉淀评分、绿鞋与回测校准规则

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/hkipo.py <<< '{}'`
- 人工检查 `SKILL.md` / `commands/hkipo.py` / `references/hkipo.md` 一致

Progress:

- 2026-04-27：根据用户反馈，已将 `/hkipo` 从长报告模板升级为评分卡 + 简报 + 绿鞋/基石 + 首日回测校准工作流。
- 2026-04-27：进一步移除“简评”章节，将维度整合进总览表，并加入融资倍数热度与暗盘修正规则；极端融资/暗盘样本会把首日赔率评分上修。


### M6 — 港股 IPO 近 100 样本回测 MVP

Status: `done`

Scope:

- 新增 `scripts/hkipo_backtest.py`，从公开 IPO 列表抓取近期已上市港股 IPO 样本并输出分桶回测
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md`，说明回测工具的输入、输出和限制
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录本轮进展

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 scripts/hkipo_backtest.py --limit 20 --source aastocks --format markdown`
- 人工检查输出包含样本数、首日胜率、平均/中位涨幅、破发率和热度分桶

Progress:

- 2026-04-27：用户确认开始实现自动回测 MVP；优先使用 AAStocks Listed IPO 页面，因为其公开字段含上市日、发行价、超购倍数、一手中签率和首日涨幅。
- 2026-04-27：100 样本回测已跑通：有效首日涨幅 97 个，胜率 75.3%，中位首日涨幅 16.22%，>=1000x 超购分桶胜率 92.2%、中位首日涨幅 75.53%。


### M7 — 港股 IPO 回测加入行业/估值/结构/暗盘维度

Status: `done`

Scope:

- 扩展 `scripts/hkipo_backtest.py`：加入行业启发式分类、市值/估值分桶、多维评分、enrichment CSV 支持绿鞋/基石/暗盘
- 更新 `README.md` / `references/hkipo.md`，说明 enrichment CSV 和缺失字段处理
- 运行增强版 100 样本回测并记录校准结果

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 scripts/hkipo_backtest.py --limit 20 --source aastocks --format markdown`
- `python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`

Progress:

- 2026-04-27：增强版 100 样本回测已跑通：多维评分相关系数 0.412；市值字段覆盖 47/100；绿鞋/基石/暗盘在 AAStocks 列表源中覆盖 0/100，需要 enrichment CSV 或逐票来源补充。
- 2026-04-27：行业分桶显示 `ai_tech`、`biotech`、`semiconductor` 中位首日涨幅较强；`consumer` 分桶显著偏弱。


### M8 — 安装受控 Futu/OpenD 本地环境

Status: `done`

Scope:

- 确认当前主机默认 Python、`pyenv` 与 `uv` 状态
- 使用独立 `uv` venv 安装并固定 Futu SDK 与数据分析依赖版本
- 安装 macOS GUI 版 Futu OpenD，并写入 futu skill 版本戳
- 验证 SDK import 与 OpenD 只读连接状态
- 为 `stock-analysis-skill` 增加全局只读护栏，禁止任何写入、编辑、下单或交易状态变更行为

Validation:

- `python3 --version`
- `pyenv --version`
- `uv --version`
- `.venv/bin/python -c 'import sys, futu, google.protobuf; ...'`
- `.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- `grep -R "模拟/实盘交易\|实盘下单 / 撤单 / 改单\|trade_intent\|确认执行" -n SKILL.md README.md AGENTS.md references/futu.md`

Progress:

- 2026-04-27 20:08 北京时间：确认默认 `python3` 是 Homebrew `3.14.3`；主机同时安装了 `pyenv 2.6.26` 与 `uv 0.10.12`。
- 2026-04-27 20:08 北京时间：已用 `uv` 创建 `.venv`，Python 版本为 `3.12.12`，并安装 `futu-api==10.4.6408`、`backtrader==1.9.78.123`、`matplotlib==3.10.9`、`pandas==3.0.2`、`numpy==2.4.4`。
- 2026-04-27 20:08 北京时间：已新增 `requirements-futu.txt` 与 `requirements-futu.lock` 记录固定版本，并在 `.gitignore` 忽略 `.venv`。
- 2026-04-27 20:08 北京时间：已下载并安装 GUI 版 `/Applications/Futu_OpenD.app`，版本 `10.4.6408`，并写入 `/Users/ryan/.futu_skill_version=0.1.1`。
- 2026-04-27 23:49 北京时间：用户完成 OpenD 登录后，`get_ipo_list.py HK --json` 已只读查询成功，返回 5 条港股 IPO 记录。
- 2026-04-27 23:49 北京时间：已在 `SKILL.md` 增加全局只读护栏，并同步 `README.md` / `AGENTS.md` / `references/futu.md`，明确禁止下单、改单、撤单、订阅、交易解锁和其他写入类行为。

Blockers:

- 无。


### M9 — 优化 skill md 说明

Status: `done`

Scope:

- 优化 `SKILL.md` 的 frontmatter description，使其只描述触发条件，不复述执行流程
- 收敛 `SKILL.md` / `README.md` / `AGENTS.md` / `references/*.md` 中只读边界、订阅和导出表述
- 保留 CLI、Futu/OpenD、Tushare、Slash Commands 四类路由，但减少重复说明并改为引用 owner reference

Validation:

- `python3 -m py_compile scripts/*.py commands/*.py`
- 人工检查 `SKILL.md` / `README.md` / `AGENTS.md` / `references/cli.md` / `references/futu.md` 的路由和只读约束一致

Progress:

- 2026-04-28 00:38 北京时间：开始按 skill 编写要求优化 md 说明，优先处理 description、重复说明和只读边界冲突。
- 2026-04-28 00:38 北京时间：已完成 `SKILL.md` 精简、frontmatter description 调整，并同步 `README.md` / `AGENTS.md` / `references/cli.md` / `references/futu.md` 的只读边界表述。

### M10 — 回测评分合理性校准

Status: `done`

Scope:

- 扩展 `scripts/hkipo_backtest.py`：按评分分桶、排序相关性和失配样本评估评分与首日涨幅的一致性
- 新增最小回归测试覆盖评分校准摘要
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md` 的回测输出说明
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录 100 样本校准结论

Validation:

- `python3 -m unittest tests/test_hkipo_backtest.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：开始按用户要求评估最近 100 个港股新股的评分与首日涨幅是否匹配；当前缺口是只有相关系数和 Top/Worst 首日表现，缺少评分分桶与高分破发/低分大涨失配样本。
- 2026-04-28 北京时间：已新增评分分桶、评分排序相关性、Top/Bottom 评分分位首日涨幅差和高分破发 / 低分大涨失配样本。
- 2026-04-28 北京时间：100 样本回测结果显示评分方向基本合理：评分排序相关系数 0.561；Top 20% 评分中位首日涨幅 88.78%，Bottom 20% 为 0.00%；80-89 分桶胜率 95.8%、中位首日涨幅 95.34%，<50 分桶胜率 41.7%、中位首日涨幅 -2.21%。
- 2026-04-28 北京时间：限制仍明确保留：绿鞋 / 基石 / 暗盘覆盖为 0/100，行业分是同源样本内启发式，不等同于样本外预测。

Validation status:

- passed

Review status:

- passed

### M11 — Futu K 线校验港股 IPO 首日回测

Status: `done`

Scope:

- 扩展 `scripts/hkipo_backtest.py`：支持用 Futu/OpenD 历史日 K 线重算首日涨幅
- 保留 AAStocks 作为最近 100 个已上市 IPO 样本清单来源，明确 Futu `get_ipo_list` 只覆盖当前 IPO 列表
- 新增最小回归测试覆盖 Futu 首日收益写回逻辑
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md` 的 Futu 回测命令与数据边界
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录 Futu/OpenD 实测结果

Validation:

- `.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- `.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_history_kl_quota.py --json`
- `python3 -m unittest tests/test_hkipo_backtest.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --debut-price-source futu-kline --format markdown`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户明确要求用已登录的 Futu/OpenD 拉数据并回测；已确认 `get_ipo_list(HK)` 只返回当前 IPO 列表且不含绿鞋 / 基石 / 暗盘字段。
- 2026-04-28 北京时间：已用 Futu 历史日 K 线接口成功读取 `HK.02635` 上市日 K 线，可用于重算首日收盘涨幅。
- 2026-04-28 北京时间：首次用系统 `python3` 跑 Futu 模式失败，原因是 Futu SDK 安装在项目 `.venv`；已将 Futu 模式验证命令改为 `.venv/bin/python`。
- 2026-04-28 北京时间：Futu/OpenD 100 样本回测跑通，上市日 K 线覆盖 95/100；报告中 `首日涨幅来源` 显示 `futu_kline 95`。
- 2026-04-28 北京时间：Futu K 线重算后的结果与表格首日涨幅基本一致：评分排序相关系数 0.561，Top 20% 评分中位首日涨幅 88.78%，80-89 分桶中位首日涨幅 95.34%。

Validation status:

- passed

Review status:

- passed

### M12 — 补全绿鞋/基石/暗盘 enrichment 并回测

Status: `done`

Scope:

- 参考 AKShare 的公开网页数据接口实现方式，新增可选公开数据源 enrichment
- 扩展 `scripts/hkipo_backtest.py`：支持按代码从新股渔夫公开 API 补绿鞋、基石、暗盘、保荐人和稳价人字段
- 保持 AAStocks 作为样本清单，Futu/OpenD 作为首日 K 线来源
- 新增最小回归测试覆盖 enrichment 字段映射
- 更新 `README.md` / `SKILL.md` / `references/hkipo.md` 的命令和数据源边界
- 更新 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`，记录补全覆盖率和回测结果

Validation:

- `python3 -m unittest tests/test_hkipo_backtest.py`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --enrichment-source xinguyufu --debut-price-source futu-kline --format markdown`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：开始按用户要求参考开源实现补全数据源。已确认 AKShare `stock_ipo_hk_ths` 的模式是带浏览器 UA 抓公开页面并抽取表格；新股渔夫公开页面暴露 `/api/ipo` JSON 字段，可按单个代码查询绿鞋、基石、暗盘等字段。
- 2026-04-28 北京时间：已新增 `--enrichment-source xinguyufu`，逐票按代码补充绿鞋、基石、辉立暗盘、富途暗盘、保荐人、稳价人、回拨和行业字段。
- 2026-04-28 北京时间：100 样本实测：新股渔夫补充字段覆盖 97/100；Futu/OpenD 首日 K 线覆盖 95/100。
- 2026-04-28 北京时间：补全字段后的评分校准结果：评分排序相关系数 0.579；Top 20% 评分中位首日涨幅 87.26%，Bottom 20% 为 -0.12%；80-89 分桶胜率 95.0%、中位首日涨幅 88.02%。

Validation status:

- passed

Review status:

- passed

### M13 — 约束 hkipo 当前数据源优先级与新鲜度

Status: `done`

Scope:

- 强化 `SKILL.md` 的 `/hkipo` 规则：当前 IPO 池发现和上市/招股状态必须先走 Futu/OpenD 只读 `get_ipo_list(HK)`。
- 强化 `references/hkipo.md` 的数据源优先级：Futu 当前 IPO 基础字段优先；Futu 缺失的孖展、公开认购、暗盘、中签率等字段才允许使用外部财经源。
- 强化 `/hkipo` prompt：必须按当前日期重新获取最新数据，禁止把过期孖展/暗盘数据当作当前数据使用。
- 同步 `README.md` 的 slash command 说明。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "Futu/OpenD|过期|孖展|当前日期|get_ipo_list|外部财经" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户指出天星医疗孖展数据使用了过期的 2026-04-24 口径；本轮目标是把“当前日期最新数据 + Futu 优先 + 外部源兜底”写成硬约束。
- 2026-04-28 北京时间：`/hkipo` prompt 已改用北京时间日期，避免美国本地时区导致报告日期落后一天。
- 2026-04-28 北京时间：已将当前 IPO 池发现和基础日程字段约束为优先使用 Futu/OpenD `get_ipo_list(HK)`；孖展、暗盘、中签率等 Futu 缺失字段才允许用外部财经源补齐。

Validation status:

- passed

Review status:

- passed

### M14 — 压缩 hkipo 输出为关键表格

Status: `done`

Scope:

- 收紧 `/hkipo` prompt，禁止解释触发文本日期差异、推导过程和冗长回测段落。
- 将关键结论、数据源新鲜度、Futu 覆盖/外部补充、回测映射都整合进评分总览表。
- 更新 `references/hkipo.md` / `SKILL.md` / `README.md` 的输出 contract。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "触发文本|推导过程|废话|只保留|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户反馈 `/hkipo` 输出废话太多，并指出不应写死或解释旧触发文本日期；本轮目标是把报告压缩为极短结论 + 单表 + Sources。
- 2026-04-28 北京时间：已将 `/hkipo` 输出模板改为最多 3 条结论 + 单张评分总览表 + Sources；移除单独回测校准段落，回测映射和数据源覆盖全部进表格。
- 2026-04-28 北京时间：prompt 已明确禁止解释触发文本、系统日期或取数过程；若用户消息日期与当前北京时间日期不一致，直接按当前日期输出，不写差异说明。

Validation status:

- passed

Review status:

- passed

### M15 — 优化 hkipo 飞书卡片排版

Status: `done`

Scope:

- 将 `/hkipo` 从宽 Markdown 表格改为飞书友好的窄卡片列表，避免横向滚动和长表格裁切。
- 保留关键必要信息：结论、每只 IPO 的评分/阶段/热度/结构/回测/风险、关键 Sources。
- 更新 `commands/hkipo.py`、`references/hkipo.md`、`SKILL.md`、`README.md`。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "Markdown 表格|窄卡片|横向滚动|评分卡片|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户反馈飞书消息卡片里的宽表格排版太差；本轮目标是改成正式、优雅、可读的窄卡片列表。
- 2026-04-28 北京时间：`/hkipo` prompt 已禁止宽 Markdown 表格，改为最多 3 条结论 + 每只 IPO 5-6 行窄卡片 + 短链接 Sources。

Validation status:

- passed

Review status:

- passed

### M16 — 细化 hkipo 飞书视觉层级

Status: `done`

Scope:

- 去除 `/hkipo` 输出中的 `#` / `##` Markdown 大标题，改为普通加粗标签和短分隔。
- 为结论、热度、结构、回测、风险、来源加入固定 emoji 信号。
- 更新 `commands/hkipo.py`、`references/hkipo.md`、`SKILL.md`、`README.md`。

Validation:

- `python3 commands/hkipo.py <<< '{}'`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `rg -n "# 港股|## 结论|## Sources|emoji|🟢|💰|⚠️" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- `git diff --check`

Progress:

- 2026-04-28 北京时间：用户反馈飞书卡片中“结论先行 / 优先级卡片 / Sources”标题过大且重点不明显；本轮目标是去 Markdown 大标题，并用少量 emoji 强化关键信息。
- 2026-04-28 北京时间：`/hkipo` 输出模板已改为普通加粗标题、短分隔和固定 emoji 信号，不再使用 `#` / `##` 大标题。

Validation status:

- passed

Review status:

- passed

### M17 — 修复 hkipo Futu 命令跨目录兼容

Status: `done`

Scope:

- 修复 `/hkipo` prompt 中的 Futu/OpenD 查询命令，不再使用当前工作区相对 `.venv/bin/python` 或用户机器硬编码路径。
- 在 command executor 运行时解析当前 `stock-analysis-skill` 安装目录、可用 venv Python 和已安装 `futuapi` skill 脚本路径。
- 增加回归测试，覆盖任意安装目录下生成的 prompt 不会依赖 `/Users/ryan` 或工作区 `.venv`。

Validation:

- `python3 -m unittest tests/test_hkipo_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/hkipo.py <<< '{}'`
- `cd /Users/ryan/projects/stock-analysis-skill && /Users/ryan/projects/stock-analysis-skill/.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- `git diff --check`

Progress:

- 2026-04-30 北京时间：已确认 `/hkipo` 提示 Futu 不可用的根因是 prompt 使用相对 `.venv/bin/python`，而宿主 Agent 在工作区 cwd `/Users/ryan/projects/cli-claw` 下执行，找不到 `stock-analysis-skill` 的 Futu SDK venv。
- 2026-04-30 北京时间：已将 `/hkipo` Futu 命令改为由 executor 运行时解析当前 skill 安装目录、venv Python 和 `futuapi` 脚本；若缺失则明确预检失败，不再让 Agent 猜工作区 `.venv`。
- 2026-04-30 北京时间：已增加回归测试覆盖任意安装目录、venv symlink 保留、`futuapi` skill 自带 venv fallback 和缺失预检提示。

Validation status:

- passed

Review status:

- passed

### M18 — 新增 /research 单票深度研报命令

Status: `done`

Scope:

- 新增 `/research` skill command，沿用 `/hkipo` 的 thin executor + `assistant_prompt` 模式。
- 第一版支持单只股票参数解析：A 股 6 位代码、`cn/us/hk` 显式市场、`US.AAPL` / `HK.00700` / `0700.HK` 等常见前缀格式。
- A 股 / 美股优先复用 `stock-analysis-api/scripts/stock_analyze.py --mode full`；港股先作为后置支持，要求 Futu/OpenD + HKEX / AKShare / yfinance 降级路径。
- 新增 `references/research.md`，沉淀统一研报模板、数据源路由、禁止事项、降级与来源规范。
- 更新 `SKILL.md`、`README.md`、`commands.json` 与测试，确保 `/help` 可展示新命令且 command 输出 contract 一致。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/research.py <<< '{"argsText":"300750","args":["300750"],"workspace":{"name":"test"}}'`
- `python3 commands/research.py <<< '{"argsText":"US.AAPL","args":["US.AAPL"],"workspace":{"name":"test"}}'`
- `python3 commands/research.py <<< '{"argsText":"HK.00700","args":["HK.00700"],"workspace":{"name":"test"}}'`
- `git diff --check`

Progress:

- 2026-05-01 北京时间：用户确认新增 `/research` 并要求 subagents 协作；已派生 reader 检查测试模式、implementer 草拟 `references/research.md`。
- 2026-05-01 北京时间：本轮实现采用 TDD；先新增失败测试覆盖参数解析、assistant prompt、单票限制、A 股/美股 CLI 指令与港股后置数据层提示。
- 2026-05-01 北京时间：已新增 `commands/research.py`、`references/research.md`、`tests/test_research_command.py`，并在 `commands.json` 注册 `/research`。
- 2026-05-01 北京时间：review 发现 `US.` 前缀路径可能绕过 ticker 校验；已补安全回归测试、统一美股 symbol 校验并对可复制 CLI 参数使用 `shlex.quote`。

Validation status:

- passed

Review status:

- passed

### M19 — /research 动态解析 stock-analysis-api 命令

Status: `done`

Scope:

- 让 `/research` executor 运行时解析可用的 `stock-analysis-api` 根目录，不再只在 prompt 中依赖 `$STOCK_ANALYSIS_API_ROOT`。
- 搜索顺序优先环境变量，其次当前 skill 安装目录附近的 sibling `stock-analysis-api`；找到时输出可直接复制执行的绝对 `cd ... && uv run python scripts/stock_analyze.py ...` 命令。
- 找不到 API 根目录时，在 prompt 中明确预检失败原因，并提示才允许按数据源不可用处理。
- 增加回归测试覆盖 sibling root、环境变量优先、缺失预检和 shell-safe 命令参数。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `python3 commands/research.py <<< '{"argsText":"300750","args":["300750"],"workspace":{"name":"test"}}'`
- `python3 commands/research.py <<< '{"argsText":"US.AAPL","args":["US.AAPL"],"workspace":{"name":"test"}}'`
- `git diff --check`

Progress:

- 2026-05-01 北京时间：用户要求继续下一轮开发；本轮聚焦 `/research` 的 API CLI 命令可执行性，避免宿主 Agent 在不同 cwd 下猜环境变量或相对路径。
- 2026-05-01 北京时间：已为 `/research` 增加 `stock-analysis-api` 根目录解析：`STOCK_ANALYSIS_API_ROOT` 优先，随后查找当前 skill 安装目录附近的 sibling `stock-analysis-api`；生成 shell-safe 绝对 `cd ... && uv run python scripts/stock_analyze.py ...` 命令。
- 2026-05-01 北京时间：已补充回归测试，覆盖 sibling root、环境变量优先、空 env 不读取进程环境、缺失预检、不从宿主 cwd 猜 API 仓库、subprocess 入口和 `CLI_CLAW_SKILL_DIR` 驱动的宿主路径解析。
- 2026-05-01 北京时间：已同步 `SKILL.md` / `README.md` / `AGENTS.md` / `references/research.md`，明确找不到 API 仓库时必须显式降级，不能猜相对路径或虚构 `$STOCK_ANALYSIS_API_ROOT`。

Validation status:

- passed

Review status:

- passed

### M20 — /research 可信度、风险与历史验证模块

Status: `done`

Scope:

- 在 `/research` prompt 和 `references/research.md` 中固定可信度层：`module_status`、`source_freshness`、`data_gaps`。
- 将风险评估整合进 `/research`，覆盖单票风险、组合/持仓只读风险和反证信号，不新增独立 `/risk` 指令。
- 增加“历史验证”模块边界：只做可复现历史统计、样本数、窗口、假设和限制，不输出买卖建议或策略执行指令。
- 补充回归测试，确保 `/research` executor prompt 强制包含以上模块。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-03 北京时间：用户确认按 Vibe-Trading 对比后的方向优化，但要求风险不新增指令，统一整合到 `/research`；历史验证也作为 `/research` 模块而不是独立 `/backtest`。
- 2026-05-03 北京时间：已在 `/research` prompt 和 `references/research.md` 固定 `module_status`、`source_freshness`、`data_gaps` 可信度层。
- 2026-05-03 北京时间：已把风险评估收敛为 `/research` 内的“风险与反证”，并把组合/持仓风险定义为同入口只读约束，不新增 `/risk`。
- 2026-05-03 北京时间：已新增“历史验证”模块边界：只做可复现历史统计，必须说明样本数、窗口、条件、指标和限制，不给交易指令。

Validation status:

- passed

Review status:

- passed

### M21 — /research 飞书短版与最终回复清洗

Status: `done`

Scope:

- 约束 `/research` 最终回复不得混入执行过程日志、工具尝试过程或调试错误堆栈。
- 将 IM/飞书默认输出改为短版研报：结论摘要、数据可信度、关键风险与反证、降级说明、Sources。
- 深度章节仅在用户明确要求详细/完整/深度时展开；历史验证默认压缩，无法验证时一行说明。
- 维护 debug 细节边界：函数名、异常栈、环境排查细节只进入降级摘要，不进入用户版正文。

Validation:

- `python3 -m unittest tests/test_research_command.py`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-03 北京时间：用户要求优化实际研报输出；本轮聚焦可读性和最终消息清洁度，不改数据采集实现。
- 2026-05-03 北京时间：已约束最终回复必须直接从 `**/research｜...**` 标题开始，不得混入执行过程日志、工具尝试、调试细节或异常堆栈。
- 2026-05-03 北京时间：已将 IM/飞书默认输出改为 2500-3500 字短版，只保留结论摘要、数据可信度、关键风险与反证、降级说明和 Sources。
- 2026-05-03 北京时间：已明确调试细节只压缩为用户可理解的降级原因，内部函数名/堆栈/本地路径不进用户版报告。

Validation status:

- passed

Review status:

- passed


### M22 — /research 股票名交由上游 CLI 识别

Status: `done`

Scope:

- `/research` 支持输入股票名 / 公司名，并将原始输入传给 `stock-analysis-api` CLI
- executor 不读取 SQLite / 本地缓存、不硬编码匹配、不生成下游标的识别模板
- `stock-analysis-api` 在 CLI 入口解析唯一市场和代码后再调用分析链路
- 上游返回 `identity_conflict` / `identity_not_found` 时，agent 先向用户澄清，不自行猜测代码
- 同步 README / SKILL / research reference，并验证 slash command 行为

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`
- `STOCK_ANALYSIS_API_ROOT=/Users/ryan/projects/stock-analysis-api python3 commands/research.py <<< '{"argsText":"宁德时代","args":["宁德时代"]}'`

Progress:

- 2026-05-03 北京时间：已按用户反馈补 `/research 宁德时代`、`/research cn 宁德时代`、API root 缺失场景单测。
- 2026-05-04 北京时间：已撤掉下游 agent 标的识别流程，股票名输入现在生成 `--symbols 原始输入`，由上游 CLI 解析。
- 2026-05-04 北京时间：已同步 README / SKILL / research reference，明确 executor 不硬匹配、上游 CLI 识别、多候选先澄清。

Validation status:

- passed

Review status:

- passed


### M23 — /research 增加行业与研报维度

Status: `done`

Scope:

- `/research` prompt 强制补充行业整体趋势和市场热度
- 强制给出同类公司平均 PE，并说明可比公司样本、PE 口径、异常值处理和数据日期
- 强制汇总权威机构研报，列机构、研报发布日期、核心观点、共识与分歧
- 数据不可得时写入 `data_gaps` / 降级说明，不伪造，不把评级或目标价作为建议

Validation:

- `python3 -m unittest tests/test_research_command.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 -m py_compile scripts/*.py commands/*.py`
- `git diff --check`

Progress:

- 2026-05-04 北京时间：已补 prompt/reference 单测，锁定行业整体趋势、市场热度、同类公司平均 PE、权威机构研报汇总四个必备模块。
- 2026-05-04 北京时间：已更新 `/research` prompt 和 `references/research.md`，要求写清来源日期、样本口径、异常 PE 处理、机构观点共识与分歧。
- 2026-05-04 北京时间：已同步 README / SKILL，飞书短版也必须压缩纳入四个模块；不可得时写入可信度或降级说明。

Validation status:

- passed

Review status:

- passed

## Progress

- 2026-05-04：`/research` 已新增行业整体趋势、市场热度、同类公司平均 PE、权威机构研报汇总四个强制模块；数据不可得时进入可信度/降级说明。
- 2026-05-04：`/research` 股票名输入已改为上游 CLI 识别；executor 只传原始输入，不查本地缓存、不硬编码匹配、不生成下游识别模板。
- 2026-04-27：移除旧 `docs/plan.md`，统一使用 `PLANS/`。
- 2026-04-27：确认用户要求后续任务时间改用北京时间展示。
- 2026-04-27：开始创建 `PLANS/ROADMAP.md` 与 `PLANS/ACTIVE.md`，并把富途整合纳入长期 roadmap。
- 2026-04-27：已在 `SKILL.md` / `README.md` / `AGENTS.md` 增加 Futu/OpenD 路由优先级、边界和交易安全要求。
- 2026-04-27：新增 `references/futu.md`，定义 quote snapshot、watch alert、option chain、portfolio risk、trade intent contract。
- 2026-04-27：补充 watchlist 自动选路规则：A 股轻量轮询走 `poll_realtime_quotes.py`，混合市场 / 盘口 / 订阅 / 持仓联动走 `futuapi`。

## Validation

- 已通过：M23 `python3 -m unittest discover -s tests -v`、`python3 -m py_compile scripts/*.py commands/*.py`、`git diff --check`
- 已通过：`python3 -m unittest tests/test_research_command.py -v`
- 已通过：`python3 -m unittest discover -s tests -v`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/research.py` 抽样验证 `/research 宁德时代` 生成 `--symbols 宁德时代` 并声明上游 CLI 负责解析
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 20 --source aastocks --format markdown`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`
- 已通过：人工检查 `SKILL.md` / `README.md` / `commands/hkipo.py` / `references/hkipo.md` 的 `/hkipo` 评分、绿鞋、回测和简明输出规则一致
- 已通过：`test ! -e docs/plan.md && test -f PLANS/ROADMAP.md && test -f PLANS/ACTIVE.md && test -f references/futu.md`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：人工检查 `AGENTS.md` / `README.md` / `SKILL.md` / `PLANS/*.md` / `references/futu.md` 职责不冲突
- 已通过：确认 `PLANS/ACTIVE.md` 中没有进行中的 milestone
- 已通过：`.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- 已通过：人工检查 `SKILL.md` / `README.md` / `AGENTS.md` / `references/futu.md` 的 Futu/OpenD 说明已统一为只读查询，且不再保留实盘/模拟交易执行路径
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "订阅默认|订阅推送见|自定义导出|文档生成任务|三类能力|价格提醒联动|原始 Tushare 字段或导出" SKILL.md README.md AGENTS.md references/*.md PLANS/*.md` 无命中
- 已通过：`git diff --check`
- 已通过：`python3 -m unittest tests/test_hkipo_backtest.py`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown`
- 已通过：`git diff --check`
- 已通过：`.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`
- 已通过：`.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_history_kl_quota.py --json`
- 已通过：`python3 -m unittest tests/test_hkipo_backtest.py`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --debut-price-source futu-kline --format markdown`
- 已通过：`git diff --check`
- 已通过：`python3 -m unittest tests/test_hkipo_backtest.py`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`.venv/bin/python scripts/hkipo_backtest.py --limit 100 --source aastocks --enrichment-source xinguyufu --debut-price-source futu-kline --format markdown`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "Futu/OpenD|过期|孖展|当前日期|get_ipo_list|外部财经" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "触发文本|推导过程|废话|只保留|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "Markdown 表格|窄卡片|横向滚动|评分卡片|评分总览" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`
- 已通过：`python3 commands/hkipo.py <<< '{}'`
- 已通过：`python3 -m py_compile scripts/*.py commands/*.py`
- 已通过：`rg -n "# 港股|## 结论|## Sources|emoji|🟢|💰|⚠️" SKILL.md README.md references/hkipo.md commands/hkipo.py`
- 已通过：`git diff --check`

## Handoff

- M1 已完成：计划入口、北京时间口径与富途整合 roadmap 均已落盘。
- 2026-04-27：用户要求移除 `docs/plan.md`，后续统一使用 `PLANS/`。
- 2026-04-27：M2 已完成：`SKILL.md` / `README.md` / `AGENTS.md` 已同步 Futu/OpenD 路由矩阵与安全边界。
- M3 已完成：统一输出 contract 已落到 `references/futu.md`。
- M4 已完成：watchlist 自动选路规则已落到 `references/futu.md`，并同步 `SKILL.md` / `README.md` / `references/cli.md`。
- M5 已完成：`/hkipo` 已升级为评分卡 + 简明报告 + 绿鞋/基石 + 首日回测校准工作流，并新增 `references/hkipo.md`。
- M6 已完成：新增 `scripts/hkipo_backtest.py`，可抓取 AAStocks 近期已上市港股 IPO 并输出首日表现分桶回测。
- M7 已完成：回测加入行业启发式分类、市值/估值分桶，并支持通过 enrichment CSV 补充绿鞋、基石、暗盘。
- M8 已完成：Futu/OpenD 登录后只读 IPO 查询验证通过；`stock-analysis-skill` 已增加全局只读护栏，禁止任何写入、编辑、下单、订阅或交易解锁行为。
- 下一轮可在只读边界内继续补 quote / IPO / 持仓查询类封装或输出模板。
- M9 已完成：`SKILL.md` 按 skill 编写要求精简为路由规范；description 改为触发条件描述；只读边界、订阅、导出和文档生成表述已同步。
- M10 已完成：`hkipo_backtest.py` 已能按评分分桶、评分排序相关性和失配样本评估评分与首日涨幅的一致性；最近 100 样本验证显示评分方向基本合理，但绿鞋 / 基石 / 暗盘仍需 enrichment 数据源补齐。
- M11 已完成：`hkipo_backtest.py` 已支持 Futu/OpenD 历史日 K 线重算首日收盘涨幅；最近 100 样本实测覆盖 95/100，Futu 重算后评分方向仍基本合理。
- M12 已完成：`hkipo_backtest.py` 已支持新股渔夫公开 API enrichment；最近 100 样本补充字段覆盖 97/100，绿鞋 80/100、基石 97/100、辉立暗盘 97/100、富途暗盘 95/100，结合 Futu K 线后的评分排序相关系数 0.579。
- M13 已完成：`/hkipo` 已强制按北京时间当前日期取数；当前 IPO 池和基础日程字段优先 Futu/OpenD，Futu 缺失的孖展、暗盘、中签率等字段才允许外部财经源补充，且过期数据不得用于当前热度主评分。
- M14 已完成：`/hkipo` 输出已压缩为最多 3 条结论 + 单张评分总览表 + Sources；不再解释触发文本日期差异、取数过程或评分推导。
- M15 已完成：`/hkipo` 输出改为飞书友好的窄卡片列表，避免宽 Markdown 表格横向滚动和裁切；Sources 要求短链接和用途/日期标签。
- M16 已完成：`/hkipo` 去除 `#` / `##` 大标题，改用普通加粗标签、短分隔和 🟢/🟡/⚪/💰/🛡/📈/⚠️/🔗 固定信号。
- M19 已完成：`/research` A 股 / 美股 prompt 已改为运行时解析 `stock-analysis-api` 绝对命令；找不到 API 仓库时显式预检失败并按研报降级规则继续。
- M20 已完成：`/research` 已增加可信度层、风险与反证、历史验证模块；风险不新增独立指令，组合/持仓风险纳入同入口只读约束。
- M21 已完成：`/research` 默认飞书短版和最终回复清洗已落地；最终正文直接从标题开始，过程日志和 debug 细节不进入用户版报告。
