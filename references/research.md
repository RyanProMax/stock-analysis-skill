# /research Single-Stock Deep Research Workflow

Use this reference for `/research` single-stock deep reports. The goal is an evidence-based research memo for one listed company, not a buy/sell recommendation, price target, or trading plan.

## Scope

`/research` covers one primary ticker at a time:

- A-share listed stocks.
- US-listed stocks and ADRs.
- HK-listed stocks only when explicitly requested or when A-share / US routing cannot resolve the target.

Do not use this workflow for `/hkipo` current IPO pool ranking. HK IPO scoring and first-day odds belong to `references/hkipo.md`.

## Market Resolution Priority

Resolve the target before collecting data. A-share and US routes have priority; HK is deliberately lower priority.

| Input pattern | Default market | Notes |
| --- | --- | --- |
| 6-digit code such as `300827`, `600000` | A-share | Prefer `stock-analysis-api` CLI contracts. |
| `SH.600000`, `SZ.300827`, `BJ.8xxxxx` | A-share | Preserve explicit exchange if provided. |
| US ticker such as `AAPL`, `MSFT`, `TSLA`, `NVDA` | US | Prefer US route unless user mentions HK/A-share listing. |
| `US.AAPL`, `NASDAQ:AAPL`, `NYSE:KO` | US | Normalize to the provider's supported symbol format. |
| `HK.00700`, `00700.HK`, `港股 00700` | HK | Use HK route only because the user made HK explicit. |
| Chinese company name with multiple listings | Ask or infer A-share first, US ADR second, HK last | If ambiguity can change the company or listing venue, ask a short clarification. |

Rules:

- Do not route to HK only because a company has an HK listing. Use HK only for explicit HK symbols, explicit user intent, or no credible A-share / US match.
- If the same business has multiple listings, keep the selected listing clear in the report and mention other listings only as context.
- If symbol identity remains uncertain after a quick lookup, stop and ask for the exchange or full ticker.

## Data Source Routing

Choose one primary market route, then add source-specific evidence.

| Market | Primary route | Supporting sources |
| --- | --- | --- |
| A-share | `stock-analysis-api` `stock_analyze.py`; `poll_realtime_quotes.py` for current quote | Exchange / company announcements, CNINFO, annual and quarterly reports, Tushare raw interfaces only when explicitly requested. |
| US | `stock-analysis-api` `stock_analyze.py --market us --mode full` | SEC EDGAR, company IR, 10-K / 10-Q / 8-K, earnings releases, investor presentations, Nasdaq / NYSE pages, Futu/OpenD read-only quote/K-line data when available, reputable finance data for consensus or market snapshot. |
| HK | Futu/OpenD read-only market data | HKEXnews, company announcements, annual and interim reports, exchange filings, reputable finance portals for secondary market data. |

Source priority:

1. Official filings, exchange announcements, company IR, regulator records.
2. Structured local contracts already defined by this skill, especially `stock-analysis-api` for A-share / US standard analysis and Futu/OpenD for read-only multi-market quotes.
3. Reputable finance portals for market data, analyst consensus, sector comparison, and news only when primary sources do not expose the field.
4. Search snippets, model memory, unverifiable social posts, forum rumors, stale screenshots, and GitHub repos are not evidence sources.

## Execution Phases

1. **Resolve identity**: confirm ticker, exchange, company name, currency, report date, and source timezone. User-facing time defaults to Beijing time.
2. **Collect market snapshot**: latest price, change, market cap if available, volume / turnover, 52-week context or recent trend. Label market status and source time.
3. **Collect primary evidence**: latest annual / quarterly filings, earnings release, guidance, major announcements, risk factors, and segment data.
4. **Cross-check secondary data**: peer valuation, consensus, news, sector indicators, ownership or capital flows if relevant.
5. **Write the memo**: separate facts, interpretation, uncertainty, and risks. Keep every material claim traceable to a source.
6. **Declare degradation**: if any required source is missing, stale, permission-limited, or unavailable, state it in the memo instead of filling gaps.

## Required Output Structure

Use this shape by default. Keep headings compact and conclusion-first.

```markdown
**/research｜{ticker} {company}｜{market}｜YYYY-MM-DD**

**结论摘要**
- 数据状态：ok / partial / degraded / failed；关键来源截至时间。
- 核心观察：1-3 条，只写可被证据支持的事实判断。
- 最大不确定性：1-2 条。

**标的识别**
- 代码 / 交易所 / 公司名 / 币种 / 行业。
- 是否存在多地上市、ADR、ETF 或同名歧义。

**市场快照**
- 最新价格、涨跌幅、成交量 / 成交额、市场状态、数据时间。
- 近期走势只做事实描述，不写交易指令。

**业务与行业**
- 主营业务、收入结构、行业位置、竞争格局。
- 行业周期、政策、需求或技术变化的证据。

**财务质量**
- 收入、利润、现金流、毛利率 / 费用率、资产负债、资本开支。
- 同比 / 环比变化和源自管理层披露的解释。

**估值上下文**
- 市值、主要倍数、可比公司或历史区间。
- 只说明相对位置和关键假设，不输出目标价。

**催化剂与验证路径**
- 未来 1-4 个可验证事件：财报、产品、订单、政策、监管、指数、资本动作。
- 每个催化剂写清验证信号和反证信号。

**风险清单**
- 基本面、估值、流动性、监管、财务、治理、地缘或执行风险。
- 区分已经发生的风险和需要跟踪的风险。

**降级说明**
- 列出缺失模块、不可用来源、过期数据或权限限制。

**Sources**
- 按本文件 Sources 规范列出。
```

## Analysis Rules

- State what the data says before interpreting why it matters.
- Separate long-term business quality from short-term price action.
- For A-share reports, consume `stock_analyze.py` summary fields first when available, then supplement with filings and current web evidence.
- For US reports, filings and company IR are the anchor. Quote / chart data is context, not the main evidence.
- For HK reports, do not reuse IPO first-day scoring. Treat listed HK stocks as normal single-stock research.
- If valuation is requested, use ranges, peer context, historical multiples, and explicit assumptions. Do not convert the result into a target price or trade instruction.
- If the user asks "能不能买", answer with factual pros / cons, suitability caveats, and follow-up checks; do not provide a buy/sell/hold call.

## Degradation Contract

Use a visible status in the report:

- `ok`: required identity, market snapshot, primary filings, and key financial facts are available.
- `partial`: core report is useful, but one or more secondary modules are missing.
- `degraded`: primary evidence or current market data is missing, stale, permission-denied, or conflicting.
- `failed`: ticker identity cannot be resolved or no reliable source can support the report.

Common degradation reasons:

- `identity_conflict`: multiple tickers or listings could match the request.
- `market_data_unavailable`: quote source failed, market source is down, or OpenD is unavailable.
- `primary_filing_missing`: latest annual / quarterly filing cannot be found.
- `permission_denied`: data provider requires entitlement or login not available.
- `stale_data`: latest source is older than the report context requires.
- `unsupported_market`: requested market is outside A-share / US / HK scope.
- `source_conflict`: two credible sources disagree materially; show both and avoid overclaiming.

When degraded:

- Keep the report if enough evidence remains for a useful factual memo.
- Put missing or unreliable items in `降级说明`.
- Never fabricate current prices, financial values, filing dates, analyst views, or management statements.
- Do not hide failed modules just because the final narrative still reads smoothly.

## Forbidden Output

Do not output or imply:

- Buy / sell / hold recommendations.
- Target prices, stop-losses, take-profit levels, position sizing, allocation advice, or exact trade timing.
- `recommendation`, `confidence`, `price_target`, `conviction`, `thesis` as formal fields.
- Guarantees about returns, "确定", "必涨", "稳赚", or similar certainty language.
- Unverified rumors, social-media claims, search snippets, model memory, or stale cached data as facts.
- Any write action: orders, order changes, cancellation, subscription, watchlist edits, alerts, exports, config changes, or local file writes.
- Account, position, or order details unless the user explicitly asked for a read-only account/portfolio check and the source is allowed by `references/futu.md`.

## Sources Section Rules

The final report must include `Sources` unless the task failed before any reliable source was found.

Format each source as a short bullet:

```markdown
- [Source title](url) — publisher, publication/update date, accessed YYYY-MM-DD, purpose.
```

Rules:

- Put primary sources first, then market data providers, then reputable secondary sources.
- Include source date and accessed date for all web sources.
- For local CLI / tool output, cite the command or tool name, request parameters, and `computed_at` / source time instead of a URL.
- Use a source only for the claim it actually supports. Do not cite an annual report for current price or a finance portal for audited financials unless no better source exists and the limitation is stated.
- If a source is not current enough for market data or recent catalysts, label it `历史参考` or exclude it from current-state claims.
- If sources conflict, keep both in Sources and describe the conflict in `降级说明`.
- Keep Sources concise: prefer the most authoritative 5-10 sources for a full memo, fewer for a short memo.
