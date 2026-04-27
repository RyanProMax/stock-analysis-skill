# Futu/OpenD 路由与输出 Contract

> 本文件记录 `stock-analysis-skill` 对已安装 `futuapi` / `install-futu-opend` skills 的统一路由、输出模板和安全边界。本仓库不复制富途脚本，不直接实现行情、账户或交易逻辑；通过本 skill 使用 Futu/OpenD 时只允许查询操作。

## 全局只读护栏

- 只允许调用行情、盘口、逐笔、分时、K 线、IPO、期权链、账户、资金、持仓、订单、成交、流水等查询能力。
- 禁止下单、改单、撤单、交易解锁、订阅推送、创建 / 修改价格提醒、写入 watchlist、修改配置、导出文件或任何其他状态变更。
- 用户请求写入 / 编辑 / 下单 / 订阅 / 解锁时，必须拒绝执行；不得用模拟账户、已登录 OpenD 或用户二次确认作为绕过理由。

## 能力边界

| 场景 | 默认路由 | 说明 |
| --- | --- | --- |
| A 股标准化客观分析 | `stock-analysis-api` / `scripts/stock_analyze.py` | 保持固定 objective analyze contract |
| A 股股票 / ETF 低 token 行情轮询 | `stock-analysis-api` / `scripts/poll_realtime_quotes.py` | 适合简单 watchlist 与飞书推送 |
| 港股 / 美股 / 多市场行情、盘口、逐笔、分时、K 线 | `futuapi` | 需要 OpenD 与 `futu-api` SDK |
| 期权链、到期日、Greeks、窝轮 / 牛熊证、期货资料 | `futuapi` | 使用富途多市场衍生品能力 |
| 资金流、经纪队列、板块、条件选股 | `futuapi` | 用于市场结构与筛选 |
| 账户、资金、持仓、订单、成交、流水 | `futuapi` | 仅限只读查询；敏感信息最小化展示 |
| OpenD 安装、启动、升级、SDK 环境检查 | `install-futu-opend` | 不在本 skill 内实现安装脚本 |
| 原始 Tushare 接口、自定义字段、接口文档 | `Tushare 使用技能` | 保留原始数据研究能力 |

## 通用字段规则

- 时间：面向用户统一展示北京时间（Asia/Shanghai, UTC+8）；源数据时间保留在 `source_time`。
- 百分比：内部 ratio 字段保持小数；面向用户展示为百分比，例如 `0.021` -> `+2.10%`。
- 数据源：必须标注 `source`，例如 `stock-analysis-api`、`futuapi`、`tushare`。
- 降级：源端不可用时输出 `status=degraded` 或 `status=failed`，不要伪造行情或账户数据。
- 建议边界：不输出买卖建议、目标价、主观 conviction；只输出事实、触发原因和风险提示。


## Watchlist 选路规则

watchlist 监控必须先按标的、市场和所需数据粒度拆分，不要把所有场景都塞给同一个数据源。

### 默认路由

| 输入特征 | 默认路由 | 原因 |
| --- | --- | --- |
| 全部是 A 股股票 / ETF 的 6 位代码，且只需要现价、涨跌幅、全量快照、简单异动提醒 | `stock-analysis-api` / `scripts/poll_realtime_quotes.py` | 低 token、稳定 JSON、适合 IM 定时推送 |
| 标的包含 `HK.` / `US.` / `SG.` / `JP.` / `AU.` / `CA.` 等市场前缀 | `futuapi` | 需要 Futu 多市场代码体系 |
| 用户明确说“富途”“OpenD”“牛牛”“Futu” | `futuapi` 或 `install-futu-opend` | 尊重用户指定数据源 |
| 需要盘口、逐笔、分时、K 线、盘前盘后、市场状态查询 | `futuapi` | 超出轻量 quote CLI 范围 |
| 需要账户、持仓、订单、成交、流水查询 | `futuapi` | 仅限只读查询，禁止交易状态变更 |
| 用户明确要原始 Tushare 字段、接口清单或自定义时间窗 | `Tushare 使用技能` | 保留原始数据研究路径 |

### 混合 watchlist

- 若 watchlist 同时包含 A 股 6 位代码和 `HK.` / `US.` 等前缀代码，先拆成多个 source batch。
- A 股低 token batch 走 `poll_realtime_quotes.py`；多市场 batch 走 `futuapi`。
- 合并输出时统一成 `watch_alert` contract，每个 item 保留 `source`。
- 任一 batch 失败时，只把该 batch 标记为 `degraded` 或 `failed`，不要影响其他 batch 的成功结果。

### A 股是否改走 Futu

A 股默认仍走 `stock-analysis-api` CLI。只有以下情况才把 A 股 watchlist 改走 Futu/OpenD：

- 用户明确指定“用富途 / OpenD 查 A 股”；
- 需要盘口、逐笔、分时、K 线查询；
- 需要和富途账户持仓、订单等只读信息联动；
- `poll_realtime_quotes.py` 明确不支持该标的，且可以确定对应 Futu 代码（例如 `SH.600000` / `SZ.000001`）。

### 失败与降级

- Futu 路由需要 OpenD；如果 OpenD 未启动或 SDK 不满足要求，转入 `install-futu-opend` 提示修复，不要伪造行情。
- `poll_realtime_quotes.py` 返回 `partial` 时，成功 item 正常展示，失败 item 进入异常区或按用户要求剔除。
- 用户要求“全量标的都返回”时，输出所有成功 item；异动 item 加 emoji 和原因。
- 用户要求“不说明未纳入”时，只展示成功监控集合，不输出剔除列表。

## `quote_snapshot`

用于单标的或多标的现价快照。

```json
{
  "type": "quote_snapshot",
  "status": "ok",
  "source": "futuapi",
  "market": "HK",
  "symbol": "HK.00700",
  "name": "腾讯控股",
  "price": 0.0,
  "change_pct": 0.0,
  "change_amount": 0.0,
  "source_time": "2026-04-27T10:30:00+08:00",
  "display_time": "2026-04-27 10:30 北京时间",
  "extra": {
    "volume": null,
    "turnover": null,
    "market_state": null
  }
}
```

用户展示模板：

```text
{symbol} {name} {price} {change_pct_display}
```

## `watch_alert`

用于 watchlist 全量快照和异动提醒。

```json
{
  "type": "watch_alert",
  "status": "ok",
  "display_time": "2026-04-27 10:30 北京时间",
  "summary": {"total": 15, "ok": 15, "alert_count": 2},
  "items": [
    {
      "symbol": "603228",
      "name": "景旺电子",
      "price": 75.35,
      "change_pct": 0.1,
      "is_alert": true,
      "emoji": "🚨",
      "reason": ["涨跌幅 +10.00%", "接近/达到涨停"]
    }
  ]
}
```

用户展示模板：

```text
盯盘全量快照：成功 {ok}/{total}，异动 {alert_count}
- 🚨 603228 景旺电子 75.35 +10.00%：涨跌幅 +10.00%；接近/达到涨停
- 300033 同花顺 230.75 +0.98%
```

## `option_chain`

用于期权链与期权筛选结果。

```json
{
  "type": "option_chain",
  "status": "ok",
  "source": "futuapi",
  "underlying": "US.AAPL",
  "expiration": "2026-05-15",
  "items": [
    {
      "code": "US.AAPL260515C200000",
      "option_type": "CALL",
      "strike": 200.0,
      "last_price": 0.0,
      "implied_volatility": null,
      "delta": null,
      "volume": null,
      "open_interest": null
    }
  ]
}
```

用户展示优先字段：到期日、Call/Put、行权价、最新价、IV、Delta、成交量、未平仓量。

## `portfolio_risk`

用于账户、持仓、资金、订单的只读汇总。

```json
{
  "type": "portfolio_risk",
  "status": "ok",
  "source": "futuapi",
  "environment": "SIMULATE",
  "display_time": "2026-04-27 10:30 北京时间",
  "account_summary": {
    "cash": null,
    "market_value": null,
    "total_assets": null,
    "currency": null
  },
  "positions": [
    {
      "symbol": "US.AAPL",
      "name": "Apple",
      "quantity": 0,
      "market_value": null,
      "unrealized_pnl": null,
      "weight": null
    }
  ],
  "risk_flags": []
}
```

安全要求：账户号、资金、持仓等敏感字段按最小必要原则展示；不得把账户信息用于非用户请求场景。

## 写入请求拒绝模板

遇到下单、改单、撤单、订阅、交易解锁、写入自选股、创建 / 修改提醒、导出文件或修改配置等请求时，直接拒绝执行。

```text
我不能执行这个操作。stock-analysis-skill 只允许查询操作，禁止任何写入、编辑、下单、订阅、交易解锁或账户 / 订单 / 配置状态变更。可以继续帮你查询行情、盘口、K 线、IPO、期权链、账户、资金、持仓、订单、成交或流水等只读信息。
```
