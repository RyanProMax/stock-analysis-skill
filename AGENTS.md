# Repository Guidelines

## Project Structure & Module Organization

这是一个根目录单一 `stock-analysis-skill` 仓库。当前只保留两类能力说明：

- `CLI 使用技能`：直接消费 `stock-analysis-api` 仓库中的内部 CLI
- `Tushare 使用技能`：保留 Tushare 本地工具与接口参考资产

核心文件如下：

- `SKILL.md`: skill 元数据与智能体使用说明
- `scripts/tushare_toolkit.py`: `.env` 加载、Tushare 初始化、代码标准化与参考文档生成
- `references/cli.md`: CLI 使用说明、JSON 结构、汇总规则、固定模板
- `references/api_reference.md`: Tushare 接口总表
- `docs/plan.md`: 当前任务、进展、验证结果
- `.env.example`: 本地环境变量模板

当前架构要点：

- 当前仓库不是行情 / 分析实现源
- 标准化 quote / analyze 能力统一直接消费 `stock-analysis-api`：
  - `scripts/poll_realtime_quotes.py`
  - `scripts/stock_analyze.py`
- 单票分析、单票研报摘要、标准化实时行情默认先走 CLI，不先走 Tushare
- 本仓库不再维护对应 wrapper 脚本
- Tushare 本地辅助能力统一收口到 `scripts/tushare_toolkit.py`
- `references/cli.md` 是唯一 CLI 使用说明
- `references/api_reference.md` 是唯一 Tushare 接口总表

## Task Workflow

每次任务都必须遵循下面的顺序：

1. 开始任务前，先更新 `docs/plan.md`，写清楚任务目标、计划改动和当前进度。
2. 实现过程中持续回填 `docs/plan.md` 的 `Progress` 和 `Validation`。
3. 任务完成后，重新梳理当前项目架构并更新到本文件。
4. 每次完成任务必须提交一次 commit，不把多个已完成任务混在同一个 commit 里。

## Build, Test, and Development Commands

- `python -m venv .venv && source .venv/bin/activate`: 创建本地虚拟环境
- `python -m pip install -r requirements.txt`: 安装运行依赖
- `python scripts/tushare_toolkit.py generate-docs`: 根据本地 CSV 重新生成 `references/api_reference.md`
- `python -m py_compile scripts/*.py`: 快速语法校验
- `cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`: 调用 API 仓库 realtime quote CLI
- `cd "$STOCK_ANALYSIS_API_ROOT" && uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty`: 调用 API 仓库客观分析 CLI

## Testing Guidelines

当前没有单元测试。每次改动至少完成以下验证：

- 运行 `python -m py_compile scripts/*.py`
- 若修改了 Tushare 工具脚本，运行 `python scripts/tushare_toolkit.py generate-docs`
- 设置 `STOCK_ANALYSIS_API_ROOT` 后，至少执行一次：
  - `uv run python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`
  - `uv run python scripts/stock_analyze.py --market cn --symbols 300827 --mode base --pretty`
- 检查 `references/cli.md`、`SKILL.md`、`README.md` 对命令、字段和固定模板的描述一致

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
- 是否更新了 `docs/plan.md`
- 是否影响 `SKILL.md` / `references/cli.md` / `references/api_reference.md`
- 若改了 CLI 使用说明，附一段对应命令示例

## Security & Configuration Tips

不要提交真实 `TUSHARE_TOKEN`、本地导出数据或 IDE/Agent 私有状态。`.env` 只在本地使用，仓库中只保留 `.env.example`。`data/` 视为本地输入目录，不默认提交。
