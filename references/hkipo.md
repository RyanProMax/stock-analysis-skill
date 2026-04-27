# HK IPO Research Workflow

Use this reference only for `/hkipo` reports. The goal is a concise, evidence-based IPO pool ranking, not a long investment memo.

## Lessons Borrowed from Open Skills

- Prefer executable workflows and clear phases: discover → verify → score → rank → report.
- Use explicit weighted scoring, like market-breadth skills, so outputs are repeatable.
- Validate ideas with historical cases, like backtest-focused skills; do not rely on narrative conviction.
- Keep the main skill short and move scoring/rubrics into this reference for progressive disclosure.

## Scope

Discover current Hong Kong IPOs that are either:

1. currently open for subscription; or
2. subscription closed but not yet listed.

If none qualify, state: `当前无符合条件的港股 IPO 池`.

## Source Priority

1. HKEX official listing documents, prospectus, allotment results, listing-date notices.
2. Company announcements and official prospectus appendices.
3. Reliable finance portals for margin data, public-offer multiple, one-lot success rate, grey-market data, and first-day performance.
4. Never use GitHub repos, model outputs, or unverifiable social posts as IPO fact sources.

## Required Data Fields

For each IPO, collect only decision-useful fields:

- identity: code, company, sector, issuer type, stage
- calendar: subscription dates, pricing/allotment/listing dates
- deal: offer price/range, market cap, shares offered, public/international split
- structure: sponsors, cornerstone investors, greenshoe / over-allotment option, stabilizing manager, lock-up where relevant
- fundamentals: revenue, profit/loss, cash flow or cash burn, commercialization stage, top customers/orders, R&D and customer concentration
- valuation: implied market cap/multiple, closest public peers, obvious premium/discount
- sentiment/odds: public-offer multiple, margin heat, international placing language, callback, one-lot success rate if available
- backtest context: recent listed HK IPO first-day performance and similar-deal outcomes

Use `未披露` or `未找到可靠来源` for missing fields.

## Weighted Scorecard

Score each IPO from 0 to 100 as a short-term HK IPO subscription / first-day odds score, not a long-term investment rating. Show the total and compact dimension scores in the overview table.

| Dimension | Weight | What to Evaluate |
|---|---:|---|
| Subscription Heat | 30 | margin financing multiple, public-offer multiple, order-book/placing language, callback, one-lot success rate, grey-market signal if available |
| Deal Structure | 20 | greenshoe, stabilizing manager, cornerstone quality/size, public float, sponsor quality, lock-up, shareholder overhang |
| Backtest Fit | 20 | recent HK IPO first-day win rate, median first-day return, sector/theme match, whether similar deals with similar heat worked |
| Fundamentals | 15 | revenue scale/growth, profitability, cash burn, commercialization, customer concentration |
| Valuation | 10 | valuation vs peers, valuation vs growth quality, downside from aggressive pricing |
| Evidence Quality | 5 | official-source completeness and freshness, cross-source consistency |

### Heat / Financing Tiers

Use margin financing multiple and public-offer multiple as core heat inputs. If sources conflict, cite the range and prefer fresher broker/finance pages.

- margin financing `<10x`: weak heat, usually cap Subscription Heat at 10/30 unless first-day backtest is unusually strong.
- `10-50x`: normal heat, usually 10-16/30.
- `50-200x`: strong heat, usually 16-22/30.
- `200-1000x`: very strong heat, usually 22-26/30.
- `>1000x`: extreme heat, usually 26-30/30; check allocation odds and overpricing risk.
- grey-market `>100%`: treat as a late-stage positive signal; `>250%` usually lifts total score into `90+` unless evidence is unreliable or structure has major selling pressure.

### Phase-Sensitive Score Updates

Update the score as the IPO window advances:

1. **招股中**: rely on fundamentals, valuation, deal structure, margin financing progress, and recent backtest fit.
2. **截止待配发**: add public-offer multiple, international placing language, callback, one-lot success rate.
3. **暗盘后待上市**: grey-market return becomes the strongest near-term signal; explain whether first-day score is upgraded or whether dark-pool overheating raises reversal risk.

If an IPO has verified margin financing above 1000x and verified grey-market gain of 300%-400%, the old scoring that puts it only in the high-70s is too conservative for first-day odds. It should normally be `90-95` for打新/首日优先级, while still flagging long-term fundamental risk separately.

### Scoring Rules

- `90-100`: 极高优先级 — extreme heat / grey-market confirmation / supportive structure; still disclose reversal risk.
- `80-89`: 重点跟踪 — strong combined setup, but one key uncertainty remains.
- `65-79`: 可观察/可小仓博弈 — has a clear edge but at least one material weakness.
- `50-64`: 中性 — facts are mixed or valuation/odds are not attractive enough.
- `<50`: 谨慎/回避 — poor odds, weak fundamentals, stretched valuation, or unreliable evidence.

Do not call the score a buy/sell recommendation. Phrase it as `打新优先级` or `首日赔率评分`. Keep long-term quality separate from first-day odds.

## Greenshoe / Stabilization Checks

For every IPO, explicitly check:

- whether an over-allotment option / greenshoe exists;
- maximum over-allotment size if disclosed;
- stabilizing manager if disclosed;
- whether lack of greenshoe weakens early aftermarket support;
- whether the deal has cornerstone investors and their approximate share of offering/market cap.

Score effect:

- confirmed greenshoe + credible stabilizing manager: positive Deal Structure factor;
- no greenshoe or not disclosed: neutral-to-negative unless sentiment/float structure compensates;
- cornerstone is not automatically positive: assess quality, lock-up, and whether valuation still leaves upside.

## Backtest Calibration

### Automated Backtest MVP

Run this command before or during `/hkipo` calibration when network access is available:

```bash
python3 scripts/hkipo_backtest.py --limit 100 --source aastocks --format markdown
```

The MVP uses AAStocks Listed IPO fields: listing date, offer/listing price, public over-subscription rate, applied lots for one lot, one-lot success rate, last price, first-day return and accumulated return. It reports total win rate, average/median first-day return, break rate, heat buckets and simple heat-score correlation.

Limitations: it does not yet parse greenshoe, cornerstone investors, grey-market returns, sectors, or sponsors. Use it to calibrate the heat/odds weights, not as a complete scoring replacement.


Before ranking current IPOs, collect a small recent sample of already listed HK IPOs, ideally 5-10 names from the last 1-3 months or the same sector/deal type.

For each sample, capture:

- code/company, listing date, offer price, first-day close or first-day return;
- public-offer multiple / one-lot success rate if available;
- greenshoe / cornerstone status if available;
- sector/deal type similarity.

Summarize only:

- sample size;
- first-day win rate;
- median first-day return;
- observed pattern: e.g. high subscription + greenshoe + reasonable valuation worked better/worse;
- limitations: small sample, missing grey-market data, sector mismatch.

If reliable recent first-day data cannot be found quickly, do not invent it; set Backtest Fit to neutral and say why.

## Concise Output Contract

Use this report shape by default. Do **not** include separate per-name narrative sections; integrate dimension details into the table.

```markdown
# 港股 IPO 池（YYYY-MM-DD）

## 结论先行
- 3-5 bullets only.

## 评分总览
| 代码 | 公司 | 阶段/上市日 | 评分/优先级 | 融资/认购热度 | 首日回测映射 | 绿鞋/基石/保荐 | 基本面/估值 | 最大风险 |
|---|---|---|---:|---|---|---|---|---|

## 回测校准
- 样本、胜率、中位数、可借鉴模式、限制。

## Sources
- Group links by IPO/sample; label each link's purpose.
```

Keep the whole report concise. Avoid long company introductions. Do not repeat the same fact in multiple sections.
