# stock-analysis-skill

`stock-analysis-skill` 是一个单一 skill 仓库，当前只保留两类能力说明：

- `CLI 使用技能`：直接消费 `stock-analysis-api` 仓库中的内部 CLI
- `Tushare 使用技能`：保留 Tushare 本地工具与接口参考资产

本仓库不是行情 / 分析实现源，不再维护本地 quote / analyze wrapper。

## 仓库结构

- `SKILL.md`: skill 使用说明与约束
- `scripts/tushare_toolkit.py`: `.env` 加载、Tushare 初始化、参考文档生成
- `references/cli.md`: CLI 使用说明、JSON 结构、固定模板
- `references/api_reference.md`: Tushare 接口总表
- `docs/plan.md`: 当前任务与进展
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

## Skill 使用

在本地智能体中加载根目录 [SKILL.md](./SKILL.md) 后：

- 标准化客观分析 / 实时 quote 任务，优先走 `CLI 使用技能`
- 自定义数据研究、接口查阅、文档生成任务，走 `Tushare 使用技能`

## 注意事项

- 本项目仅供学习和研究使用，请勿用于商业用途
- 使用时请遵守 [Tushare 官方文档](https://tushare.pro/document/1?doc_id=290) 与对应使用条款
