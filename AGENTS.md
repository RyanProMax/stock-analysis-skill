# Repository Guidelines

## Project Structure & Module Organization

这是一个根目录单一 `stock-analysis-skill` 仓库。当前只保留四类能力说明：

- `CLI 使用技能`：直接消费 `stock-analysis-api` 仓库中的内部 CLI
- `Futu/OpenD 使用技能`：路由到已安装的 `futuapi` / `install-futu-opend` skills
- `Tushare 使用技能`：保留 Tushare 本地工具与接口参考资产
- `Slash Commands`：通过 `commands.json` + `commands/*.py` 暴露单票研报与 IPO 池类命令

核心文件如下：

- `SKILL.md`: skill 元数据与智能体使用说明
- `commands.json`: skill command 声明
- `commands/*.py`: slash command 执行入口
- `scripts/tushare_toolkit.py`: `.env` 加载、Tushare 初始化、代码标准化与参考文档生成
- `references/cli.md`: CLI 使用说明、JSON 结构、汇总规则、固定模板
- `references/research.md`: `/research` 单票深度研报模板、市场路由、降级与 Sources 规范
- `references/api_reference.md`: Tushare 接口总表
- `references/futu.md`: Futu/OpenD 路由与输出 Contract
- `PLANS/ROADMAP.md`: 跨轮次长期跟进项与整合路线
- `PLANS/ACTIVE.md`: 当前复杂任务目标、milestone、验证与 handoff
- `.env.example`: 本地环境变量模板

当前架构要点：

- 当前仓库不是行情 / 分析实现源
- 标准化 quote / analyze 能力统一直接消费 `stock-analysis-api`：
  - `scripts/poll_realtime_quotes.py`
  - `scripts/stock_analyze.py`
- 单票分析、单票研报摘要、A 股标准化实时行情默认先走 CLI，不先走 Futu 或 Tushare
- 港 / 美 / 多市场行情、盘口、期权、账户、持仓、订单等只读查询默认路由到 Futu/OpenD skills
- `/research` 与 IPO 池类命令允许通过 `commands.json` + `commands/*.py` 暴露；复杂研究型 command 优先输出结构化提示词，由宿主 Agent 继续完成联网分析
- 本仓库不再维护对应 wrapper 脚本
- Tushare 本地辅助能力统一收口到 `scripts/tushare_toolkit.py`
- `references/cli.md` 是唯一 CLI 使用说明
- `references/api_reference.md` 是唯一 Tushare 接口总表
- Futu/OpenD 能力只通过已安装 skills 路由，本仓库不复制富途脚本、不保存交易密码；通过本 skill 只允许查询操作，禁止下单、改单、撤单、订阅、交易解锁或任何写入类行为

## Task Workflow

每次任务都必须遵循下面的顺序：

1. 所有任务统一使用 `PLANS/`；先看 `PLANS/ROADMAP.md`，再更新 `PLANS/ACTIVE.md`。
2. 若 `PLANS/ACTIVE.md` 不存在，先创建；不要再使用 `docs/plan.md`。
3. `PLANS/ACTIVE.md` 是复杂任务执行期间的单一真相源；一次只允许一个 milestone 处于 `in_progress`。
4. 实现过程中持续回填 active plan 的 `Progress` 和 `Validation`；未完成但需跨轮次追踪的事项同步回写 `PLANS/ROADMAP.md`。
5. 任务完成后，重新梳理当前项目架构并按需更新到本文件。
6. 每次完成任务必须提交一次 commit，不把多个已完成任务混在同一个 commit 里；若上层执行环境禁止自动提交，则在收尾说明中明确未提交。

## Timezone Convention

- 面向用户展示任务时间、轮询时间、下一次运行时间时，默认使用北京时间（Asia/Shanghai, UTC+8）。
- 若底层调度或数据库存储使用 UTC，回复用户时必须转换为北京时间并标注“北京时间”。

## Build, Test, and Development Commands

- `python -m venv .venv && source .venv/bin/activate`: 创建本地虚拟环境
- `python -m pip install -r requirements.txt`: 安装运行依赖
- `python -m py_compile scripts/*.py commands/*.py`: 快速语法校验
- `python scripts/tushare_toolkit.py generate-docs`: 根据本地 CSV 重新生成 `references/api_reference.md`
- `cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`: 调用 API 仓库 realtime quote CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty`: 调用 API 仓库客观分析 CLI

## Testing Guidelines

当前以 `unittest` 覆盖 slash command / 回测脚本，以 `py_compile` 做快速语法校验。每次改动至少完成以下验证：

- 运行 `python -m py_compile scripts/*.py commands/*.py`
- 若修改了 Tushare 工具脚本，运行 `python scripts/tushare_toolkit.py generate-docs`
- 设置 `STOCK_ANALYSIS_API_ROOT` 后，至少执行一次：
  - `uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`
  - `uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty`
- 检查 `README.md`、`SKILL.md`、`AGENTS.md`、`commands.json` 对命令、字段和固定模板的描述一致

## Coding Style & Naming Conventions

遵循现有 Python 风格：

- 4 空格缩进
- 函数与变量使用 `snake_case`
- 公共辅助函数保留简短 docstring
- 用户可见文本以中文为主，保持术语一致
- 本仓库不新增 CLI wrapper；如需新增本地脚本，优先证明无法直接通过 API 仓库 CLI 满足需求
- 本地辅助能力优先集中在 `scripts/tushare_toolkit.py`

## Commit & Pull Request Guidelines

提交信息保持短而直接，优先中文动宾结构。一次提交只解决一个已完成任务。PR 需要说明：

- 改了什么能力或结构
- 是否更新了 `PLANS/ACTIVE.md` / `PLANS/ROADMAP.md`
- 是否影响 `SKILL.md` / `references/cli.md` / `references/api_reference.md`
- 若改了 CLI 使用说明，附一段对应命令示例

## Security & Configuration Tips

不要提交真实 `TUSHARE_TOKEN`、本地导出数据或 IDE/Agent 私有状态。`.env` 只在本地使用，仓库中只保留 `.env.example`。`data/` 视为本地输入目录，不默认提交。
