# Repository Guidelines

## Project Structure & Module Organization

这是一个根目录单一 `tushare` skill 仓库。核心文件如下：

- `SKILL.md`: skill 元数据与智能体使用说明
- `scripts/poll_realtime_quotes.py`: 对外轮询入口，供外部 Agent 批量查询股票 / ETF 日内行情
- `scripts/tushare_toolkit.py`: 内部工具集，负责 `.env` 加载、Tushare 初始化、代码标准化和文档生成
- `references/`: 接口参考文档目录，`api_reference.md` 是唯一接口总表
- `docs/plan.md`: 每次任务的计划、当前进度、验证结果

当前架构要点：

- 当前仓库只维护根目录单一 `tushare` skill 结构
- 所有对外轮询能力统一收口到 `scripts/poll_realtime_quotes.py`
- 所有辅助能力统一收口到 `scripts/tushare_toolkit.py`
- 接口索引只保留 `references/api_reference.md`，不再维护额外副本

## Task Workflow

每次任务都必须遵循下面的顺序：

1. 开始任务前，先更新 `docs/plan.md`，写清楚任务目标、计划改动和当前进度。
2. 实现过程中持续回填 `docs/plan.md` 的 `Progress` 和 `Validation`。
3. 任务完成后，重新梳理当前项目架构并更新到本文件。
4. 每次完成任务必须提交一次 commit，不把多个已完成任务混在同一个 commit 里。

## Build, Test, and Development Commands

- `python -m venv .venv && source .venv/bin/activate`: 创建本地虚拟环境
- `python -m pip install -r requirements.txt`: 安装运行依赖
- `python scripts/poll_realtime_quotes.py --symbols 600000,510300 --pretty`: 批量轮询最新行情
- `python scripts/tushare_toolkit.py generate-docs`: 根据本地 CSV 重新生成参考文档与唯一接口总表
- `python -m py_compile scripts/*.py`: 快速语法校验

## Testing Guidelines

当前没有单元测试。每次改动至少完成以下验证：

- 运行 `python -m py_compile scripts/*.py`
- 若修改了轮询脚本，使用真实 `.env` 做一次股票 + ETF 的批量查询
- 若修改了文档生成逻辑，运行 `python scripts/tushare_toolkit.py generate-docs`
- 若本地没有 `data/api-doc.csv.csv`，则验证生成器会自动回退到 `references/api_reference.md` 并更新该总表

后续若新增测试，请统一放在顶层 `tests/` 目录，并使用 `test_*.py` 命名。

## Coding Style & Naming Conventions

遵循现有 Python 风格：

- 4 空格缩进
- 函数与变量使用 `snake_case`
- 公共辅助函数保留简短 docstring
- 用户可见文本以中文为主，保持术语一致
- 轮询脚本输出优先返回机器可读 JSON，不返回松散打印文本
- 辅助能力优先集中在 `scripts/tushare_toolkit.py`，避免再拆出低价值小模块

## Commit & Pull Request Guidelines

提交信息保持短而直接，优先中文动宾结构。一次提交只解决一个已完成任务。PR 需要说明：

- 改了什么能力或结构
- 是否更新了 `docs/plan.md`
- 是否影响 `SKILL.md` / `references/` / 轮询输出结构
- 若改了轮询脚本，附一段示例 JSON 输出

## Security & Configuration Tips

不要提交真实 `TUSHARE_TOKEN`、本地导出数据或 IDE/Agent 私有状态。`.env` 只在本地使用，仓库中只保留 `.env.example`。`data/` 视为本地输入目录，不默认提交。
