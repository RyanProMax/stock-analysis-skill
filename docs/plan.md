# Task Plan

## Task

为 `stock-analysis-skill` 增加 skill command 声明与 IPO 研究入口：先实现 `/hkipo`，自动发现当前“可认购 + 已截止认购但未上市”的港股 IPO 池，并输出给宿主 Agent 的结构化分析提示；同时预留 `/cnipo` 指令位。

## Goal

- 新增 `commands.json`，声明 `/hkipo` 与 `/cnipo`
- 为 `/hkipo` 提供可执行的 command 脚本，输出结构化 `assistant_prompt`
- 为 `/cnipo` 提供占位脚本，明确“暂未实现”
- 更新 `SKILL.md` / `README.md` / `AGENTS.md`，同步 slash command 约定与 IPO 分析边界
- 完成基础语法校验与文档一致性检查

## Planned Changes

- [x] 更新当前任务计划与执行进度
- [x] 新增 `commands.json`
- [x] 新增 `commands/hkipo.py`
- [x] 新增 `commands/cnipo.py`
- [x] 更新 `SKILL.md`
- [x] 更新 `README.md`
- [x] 更新 `AGENTS.md`
- [x] 运行语法检查与一致性验证
- [x] 提交一次独立 commit

## Progress

- 2026-04-23: 已确认 `/hkipo` 走 skill-native IPO 池工作流，不耦合到 `cli-claw` 的股票业务逻辑。
- 2026-04-23: 已新增 `commands.json`，声明 `/hkipo` 与 `/cnipo` 的 entrypoint/executor。
- 2026-04-23: 已新增 `/hkipo` command 脚本，输出面向宿主 Agent 的结构化分析 prompt，要求自动发现当前港股 IPO 池、联网核验日期和认购数据，并按固定模板出报告。
- 2026-04-23: 已新增 `/cnipo` 占位脚本，当前只返回“已预留，暂未实现”。
- 2026-04-23: 已更新 `SKILL.md` / `README.md` / `AGENTS.md`，同步 slash command 与 IPO 分析边界。
- 2026-04-23: 已执行 `python3 -m py_compile scripts/*.py commands/*.py`，语法校验通过。
- 2026-04-23: 已复查 `README.md` / `SKILL.md` / `AGENTS.md` / `commands.json`，slash command 与 IPO 工作流描述一致。

## Validation

- 已执行 `python3 -m py_compile scripts/*.py commands/*.py`
- 已检查 `README.md` / `SKILL.md` / `AGENTS.md` / `commands.json` 对 slash command 和 IPO 工作流的描述一致

## Completion Notes

- `stock-analysis-skill` 现已具备 slash command 声明能力，`/hkipo` 会向宿主 Agent 输出固定结构的港股 IPO 分析 prompt，`/cnipo` 保持预留占位。
- 真实 IPO 事实核验仍由宿主 Agent 联网完成；本仓库只负责 command 契约与研究框架提示，不在本地硬编码港股 IPO 数据源。
