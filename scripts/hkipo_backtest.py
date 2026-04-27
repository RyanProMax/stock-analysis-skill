#!/usr/bin/env python3
"""Backtest recent Hong Kong IPO first-day performance from public IPO tables."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from typing import Iterable

AASTOCKS_LISTED_IPO_URL = "https://aastocks.com/en/stocks/market/ipo/listedipo.aspx"
USER_AGENT = "Mozilla/5.0 (compatible; stock-analysis-skill/1.0)"


@dataclass
class IpoSample:
    name: str
    code: str
    listing_date: str
    offer_price: float | None
    listing_price: float | None
    oversub_rate: float | None
    applied_lots_for_one_lot: int | None
    one_lot_success_rate: float | None
    last_price: float | None
    debut_return_pct: float | None
    accumulated_return_pct: float | None
    heat_bucket: str
    odds_score: int | None


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table_stack = 0
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._table_stack += 1
            if self._table_stack == 1:
                self._current_table = []
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            text = data.strip()
            if text:
                self._current_cell.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._current_cell is not None:
            self._current_row.append(" ".join(self._current_cell))
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None:
            if any(cell for cell in self._current_row):
                self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._current_table is not None:
            self._table_stack -= 1
            if self._table_stack == 0:
                self.tables.append(self._current_table)
                self._current_table = None


def fetch_url(url: str, timeout: int = 30) -> str:
    completed = subprocess.run(
        ["curl", "-L", "--max-time", str(timeout), "-A", USER_AGENT, "-sS", url],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout + 5,
    )
    if completed.returncode != 0 and not completed.stdout:
        raise RuntimeError(completed.stderr.strip() or f"curl exit {completed.returncode}")
    return completed.stdout


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip().replace(",", "")
    if not text or text.upper() == "N/A":
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def parse_int(value: str | None) -> int | None:
    number = parse_number(value)
    return int(number) if number is not None else None


def parse_pct(value: str | None) -> float | None:
    return parse_number(value)


def split_name_code(value: str) -> tuple[str, str]:
    match = re.search(r"(\d{5}\.HK)", value)
    if not match:
        return value.strip(), ""
    return value[: match.start()].strip(), match.group(1)


def heat_bucket(oversub_rate: float | None) -> str:
    if oversub_rate is None:
        return "unknown"
    if oversub_rate < 10:
        return "<10x"
    if oversub_rate < 50:
        return "10-50x"
    if oversub_rate < 200:
        return "50-200x"
    if oversub_rate < 1000:
        return "200-1000x"
    return ">=1000x"


def score_from_heat(oversub_rate: float | None) -> int | None:
    if oversub_rate is None:
        return None
    if oversub_rate < 10:
        return 50
    if oversub_rate < 50:
        return 62
    if oversub_rate < 200:
        return 72
    if oversub_rate < 1000:
        return 84
    return 94


def find_ipo_table(html: str) -> list[list[str]]:
    parser = TableParser()
    parser.feed(html)
    for table in parser.tables:
        flat = " ".join(" ".join(row) for row in table[:3])
        if "Over-sub" in flat and "Debut" in flat and "Listing Date" in flat:
            return table
    return []


def parse_samples_from_html(html: str) -> list[IpoSample]:
    table = find_ipo_table(html)
    samples: list[IpoSample] = []
    for row in table[1:]:
        if len(row) < 13 or not re.search(r"\d{5}\.HK", row[1]):
            continue
        name, code = split_name_code(row[1])
        oversub = parse_number(row[7])
        samples.append(
            IpoSample(
                name=name,
                code=code,
                listing_date=row[2],
                offer_price=parse_number(row[5]),
                listing_price=parse_number(row[6]),
                oversub_rate=oversub,
                applied_lots_for_one_lot=parse_int(row[8]),
                one_lot_success_rate=parse_pct(row[9]),
                last_price=parse_number(row[10]),
                debut_return_pct=parse_pct(row[11]),
                accumulated_return_pct=parse_pct(row[12]),
                heat_bucket=heat_bucket(oversub),
                odds_score=score_from_heat(oversub),
            )
        )
    return samples


def load_aastocks_samples(limit: int, delay: float = 0.2) -> list[IpoSample]:
    samples: list[IpoSample] = []
    page = 1
    while len(samples) < limit:
        url = AASTOCKS_LISTED_IPO_URL if page == 1 else f"{AASTOCKS_LISTED_IPO_URL}?s=3&o=0&page={page}"
        page_samples = parse_samples_from_html(fetch_url(url))
        if not page_samples:
            break
        existing_codes = {sample.code for sample in samples}
        samples.extend(sample for sample in page_samples if sample.code not in existing_codes)
        page += 1
        if delay > 0:
            time.sleep(delay)
    return samples[:limit]


def mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def summarize(samples: list[IpoSample]) -> dict:
    valid = [sample for sample in samples if sample.debut_return_pct is not None]
    returns = [sample.debut_return_pct for sample in valid if sample.debut_return_pct is not None]
    scored = [sample for sample in valid if sample.odds_score is not None]
    by_bucket = []
    for bucket in ["<10x", "10-50x", "50-200x", "200-1000x", ">=1000x", "unknown"]:
        bucket_samples = [sample for sample in valid if sample.heat_bucket == bucket]
        bucket_returns = [sample.debut_return_pct for sample in bucket_samples if sample.debut_return_pct is not None]
        if not bucket_samples:
            continue
        wins = [value for value in bucket_returns if value > 0]
        breaks = [value for value in bucket_returns if value < 0]
        by_bucket.append(
            {
                "bucket": bucket,
                "count": len(bucket_samples),
                "win_rate": len(wins) / len(bucket_returns) if bucket_returns else None,
                "avg_return_pct": mean(bucket_returns),
                "median_return_pct": median(bucket_returns),
                "break_rate": len(breaks) / len(bucket_returns) if bucket_returns else None,
            }
        )
    xs = [float(sample.odds_score) for sample in scored]
    ys = [sample.debut_return_pct for sample in scored if sample.debut_return_pct is not None]
    return {
        "sample_count": len(samples),
        "valid_debut_return_count": len(valid),
        "win_rate": len([value for value in returns if value > 0]) / len(returns) if returns else None,
        "avg_return_pct": mean(returns),
        "median_return_pct": median(returns),
        "break_rate": len([value for value in returns if value < 0]) / len(returns) if returns else None,
        "score_return_correlation": pearson(xs, ys),
        "by_heat_bucket": by_bucket,
        "top_debut_returns": [asdict(sample) for sample in sorted(valid, key=lambda item: item.debut_return_pct or -999, reverse=True)[:10]],
        "worst_debut_returns": [asdict(sample) for sample in sorted(valid, key=lambda item: item.debut_return_pct or 999)[:10]],
    }


def fmt_pct(value: float | None, digits: int = 1) -> str:
    return "N/A" if value is None else f"{value * 100:.{digits}f}%"


def fmt_num(value: float | None, digits: int = 2) -> str:
    return "N/A" if value is None else f"{value:.{digits}f}"


def render_markdown(summary: dict) -> str:
    lines = [
        "# 港股 IPO 首日回测 MVP",
        "",
        "## 总览",
        f"- 样本数：{summary['sample_count']}；有效首日涨幅样本：{summary['valid_debut_return_count']}",
        f"- 首日胜率：{fmt_pct(summary['win_rate'])}；破发率：{fmt_pct(summary['break_rate'])}",
        f"- 平均首日涨幅：{fmt_num(summary['avg_return_pct'])}%；中位首日涨幅：{fmt_num(summary['median_return_pct'])}%",
        f"- 简化热度评分与首日涨幅相关系数：{fmt_num(summary['score_return_correlation'], 3)}",
        "",
        "## 融资/认购热度分桶",
        "| 热度分桶 | 样本数 | 胜率 | 平均首日涨幅 | 中位首日涨幅 | 破发率 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for bucket in summary["by_heat_bucket"]:
        lines.append(
            "| {bucket} | {count} | {win_rate} | {avg} | {median} | {break_rate} |".format(
                bucket=bucket["bucket"],
                count=bucket["count"],
                win_rate=fmt_pct(bucket["win_rate"]),
                avg=fmt_num(bucket["avg_return_pct"]),
                median=fmt_num(bucket["median_return_pct"]),
                break_rate=fmt_pct(bucket["break_rate"]),
            )
        )
    lines += ["", "## Top 10 首日涨幅", "| 代码 | 公司 | 上市日 | 超购倍数 | 一手中签率 | 首日涨幅 |", "|---|---|---|---:|---:|---:|"]
    for sample in summary["top_debut_returns"]:
        lines.append(f"| {sample['code']} | {sample['name']} | {sample['listing_date']} | {fmt_num(sample['oversub_rate'], 1)}x | {fmt_num(sample['one_lot_success_rate'], 1)}% | {fmt_num(sample['debut_return_pct'])}% |")
    lines += ["", "## Worst 10 首日涨幅", "| 代码 | 公司 | 上市日 | 超购倍数 | 一手中签率 | 首日涨幅 |", "|---|---|---|---:|---:|---:|"]
    for sample in summary["worst_debut_returns"]:
        lines.append(f"| {sample['code']} | {sample['name']} | {sample['listing_date']} | {fmt_num(sample['oversub_rate'], 1)}x | {fmt_num(sample['one_lot_success_rate'], 1)}% | {fmt_num(sample['debut_return_pct'])}% |")
    lines += [
        "",
        "## 校准建议",
        "- 当前 MVP 用公开超购倍数近似融资/认购热度，尚未纳入绿鞋、基石、暗盘和行业标签。",
        "- 若 >=1000x 分桶显著跑赢，应保留极端热度加权；若 200-1000x 与 >=1000x 分化不大，应降低边际加分。",
        "- 破发样本需单独复盘行业、估值和发行结构，避免只按热度打分。",
        "",
        "数据源：AAStocks Listed IPO 页面；字段定义以页面备注为准。",
    ]
    return "\n".join(lines)


def write_csv(samples: Iterable[IpoSample], path: str) -> None:
    rows = [asdict(sample) for sample in samples]
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backtest recent HK IPO debut returns.")
    parser.add_argument("--limit", type=int, default=100, help="number of recent listed IPOs to fetch")
    parser.add_argument("--source", choices=["aastocks"], default="aastocks")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--csv", help="optional CSV output path for raw samples")
    args = parser.parse_args()
    try:
        samples = load_aastocks_samples(args.limit)
    except Exception as exc:
        print(f"回测数据抓取失败：{exc}", file=sys.stderr)
        return 1
    summary = summarize(samples)
    if args.csv:
        write_csv(samples, args.csv)
    if args.format == "json":
        print(json.dumps({"samples": [asdict(sample) for sample in samples], "summary": summary}, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
