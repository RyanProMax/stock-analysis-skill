# Tushare Skill

[Tushare Pro](https://tushare.pro) 金融数据获取 Skill，当前是单一根目录 skill，保留一个外部 Agent 可调用的轮询入口，以及一个内部工具脚本用于环境初始化和文档生成。

## 仓库结构

- `SKILL.md`: 根目录 skill 说明与智能体使用约束
- `scripts/poll_realtime_quotes.py`: 批量查询股票 / ETF 日内最新行情
- `scripts/tushare_toolkit.py`: `.env` 加载、Tushare 初始化、代码标准化、文档生成
- `references/api_reference.md`: 唯一接口总表与参考文档入口
- `docs/plan.md`: 每次任务的计划与当前进度

## 安装

### 1. 安装依赖

- 安装 Python 依赖

```bash
python -m pip install -r requirements.txt
```

### 2. 安装 Tushare Skill

当前仓库就是单一 `tushare` skill。将仓库保存在本地后，直接使用根目录的 [SKILL.md](./SKILL.md) 和 `scripts/` 即可，无需再从其他源码仓库安装镜像包。

### 3. 配置 `.env`

到 [Tushare 官网](https://tushare.pro) 注册账号并获取 API token，然后复制环境变量模板：

```bash
cp .env.example .env
```

在 `.env` 中填写：

```bash
TUSHARE_TOKEN="your_token_here"
TUSHARE_HTTP_URL=""
```

其中 `TUSHARE_HTTP_URL` 为可选项，用于覆盖默认的 Tushare 接口地址。

## 批量轮询脚本

用于给外部 Agent 做低 token 的定时轮询调用：

```bash
python scripts/poll_realtime_quotes.py --symbols 600000,510300,159915 --pretty
```

默认输出单个 JSON 对象，包含：

- `computed_at`: 本次计算时间
- `request`: 输入的 symbol 列表和数量
- `summary`: 成功 / 失败统计
- `items`: 每个 symbol 的查询结果，含 `requested_symbol`、`status`、`error`、`info`、`quote_data`

`info` 里包含证券基础信息，股票和 ETF 会统一返回以下通用字段：

- `symbol`
- `ts_code`
- `security_type`
- `exchange`
- `name`
- `full_name`
- `list_status`
- `list_date`

股票额外会补充 `area`、`industry`、`market`，ETF 额外会补充 `index_code`、`index_name`、`setup_date`、`manager_name`、`custodian_name`、`management_fee`、`etf_type`。

`quote_data` 里统一返回：

- `price`
- `change_pct`
- `change_amount`
- `open`
- `high`
- `low`
- `pre_close`
- `volume`
- `amount`
- `volume_ratio`
- `turnover_rate`
- `amplitude`
- `as_of`
- `source`
- `mode`

其中 `change_pct` / `turnover_rate` / `amplitude` 统一为 ratio，例如 `0.0123` 表示 `1.23%`。

## 文档生成

文档生成现在统一走内部工具脚本：

```bash
python scripts/tushare_toolkit.py generate-docs
```

生成顺序如下：

- 优先使用本地未跟踪的 `data/api-doc.csv.csv`，生成 `references/` 下的详细文档，并更新 `references/api_reference.md`
- 如果本地没有 CSV，则自动回退到已有的 `references/api_reference.md`，重新规范化该总表

## Skill 使用

在本地智能体中加载根目录 `SKILL.md` 后，即可通过自然语言完成股票、ETF、财务、板块、资金流与宏观数据查询。

支持 claude code、openclaw、trae 等通用智能体。

## API 限制说明

[Tushare 官方文档](https://tushare.pro/document/1?doc_id=290)

**注意**: 本项目仅供学习和研究使用，请勿用于商业用途。使用时请遵守 Tushare 的使用条款。
