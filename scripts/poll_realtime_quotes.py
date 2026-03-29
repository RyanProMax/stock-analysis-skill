#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量轮询股票 / ETF 的最新日内行情。
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import sys
from typing import Any, Optional

import tushare as ts

from tushare_toolkit import (
    build_legacy_symbol,
    build_ts_code,
    get_tushare_pro,
    infer_exchange,
    infer_security_type,
    normalize_symbol,
    percent_to_ratio,
)

STOCK_INFO_FIELDS = "ts_code,symbol,name,area,industry,market,exchange,list_status,list_date,delist_date"


def normalize_exchange_code(value: Optional[str], fallback: str) -> str:
    normalized = str(value or "").strip().upper()
    mapping = {
        "SSE": "SH",
        "SZSE": "SZ",
        "SH": "SH",
        "SZ": "SZ",
    }
    return mapping.get(normalized, fallback)


def as_optional_str(value) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量查询股票 / ETF 最新日内行情")
    parser.add_argument(
        "--symbols",
        required=True,
        help="逗号分隔的证券代码，例如 600000,510300,159915",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="格式化输出 JSON，便于人工阅读",
    )
    return parser.parse_args()


def emit(payload: dict[str, Any], pretty: bool):
    if pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(json.dumps(payload, ensure_ascii=False))


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_float(value) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_symbols(raw_symbols: str) -> list[str]:
    seen: set[str] = set()
    normalized_symbols: list[str] = []
    for part in str(raw_symbols or "").split(","):
        candidate = part.strip().upper()
        if not candidate:
            continue
        dedupe_key = normalize_symbol(candidate) or candidate
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized_symbols.append(candidate)
    return normalized_symbols


def build_base_info(symbol: str, ts_code: str, security_type: str) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "ts_code": ts_code,
        "security_type": security_type,
        "exchange": infer_exchange(symbol),
        "name": None,
        "full_name": None,
        "list_status": None,
        "list_date": None,
        "delist_date": None,
        "area": None,
        "industry": None,
        "market": None,
        "index_code": None,
        "index_name": None,
        "setup_date": None,
        "manager_name": None,
        "custodian_name": None,
        "management_fee": None,
        "etf_type": None,
    }


def build_stock_info(row, symbol: str, ts_code: str) -> dict[str, Any]:
    info = build_base_info(symbol, ts_code, "stock")
    info.update(
        {
            "exchange": normalize_exchange_code(row.get("exchange"), info["exchange"]),
            "name": as_optional_str(row.get("name")),
            "list_status": as_optional_str(row.get("list_status")),
            "list_date": as_optional_str(row.get("list_date")),
            "delist_date": as_optional_str(row.get("delist_date")),
            "area": as_optional_str(row.get("area")),
            "industry": as_optional_str(row.get("industry")),
            "market": as_optional_str(row.get("market")),
        }
    )
    return info


def build_etf_info(row, symbol: str, ts_code: str) -> dict[str, Any]:
    info = build_base_info(symbol, ts_code, "etf")
    info.update(
        {
            "exchange": normalize_exchange_code(row.get("exchange"), info["exchange"]),
            "name": as_optional_str(row.get("csname")) or as_optional_str(row.get("extname")),
            "full_name": as_optional_str(row.get("cname")) or as_optional_str(row.get("extname")),
            "list_status": as_optional_str(row.get("list_status")),
            "list_date": as_optional_str(row.get("list_date")),
            "setup_date": as_optional_str(row.get("setup_date")),
            "index_code": as_optional_str(row.get("index_code")),
            "index_name": as_optional_str(row.get("index_name")),
            "manager_name": as_optional_str(row.get("mgr_name")),
            "custodian_name": as_optional_str(row.get("custod_name")),
            "management_fee": safe_float(row.get("mgt_fee")),
            "etf_type": as_optional_str(row.get("etf_type")),
        }
    )
    return info


def ensure_info_name(info: Optional[dict[str, Any]], fallback_name: Optional[str]) -> Optional[dict[str, Any]]:
    if not info:
        return info
    if info.get("name"):
        return info
    info["name"] = as_optional_str(fallback_name)
    return info


def fetch_security_info(pro, symbol: str, ts_code: str, security_type: str) -> tuple[dict[str, Any], Optional[str]]:
    base_info = build_base_info(symbol, ts_code, security_type)
    try:
        if security_type == "stock":
            df = pro.stock_basic(ts_code=ts_code, fields=STOCK_INFO_FIELDS)
            if df is not None and not df.empty:
                return build_stock_info(df.iloc[0], symbol, ts_code), None
            return base_info, "stock_basic 返回空结果"

        df = pro.etf_basic(ts_code=ts_code)
        if df is not None and not df.empty:
            return build_etf_info(df.iloc[0], symbol, ts_code), None
        return base_info, "etf_basic 返回空结果"
    except Exception as exc:
        return base_info, f"{security_type}_info 查询失败: {exc}"


def build_failed_item(
    requested_symbol: str,
    error: str,
    info: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    return {
        "requested_symbol": requested_symbol,
        "status": "failed",
        "error": error,
        "info": info,
        "quote_data": None,
    }


def build_quote_from_quotation(row, computed_at: str) -> dict[str, Any]:
    return {
        "price": safe_float(row.get("price")),
        "change_pct": percent_to_ratio(row.get("pct_chg")),
        "change_amount": safe_float(row.get("change")),
        "open": safe_float(row.get("open")),
        "high": safe_float(row.get("high")),
        "low": safe_float(row.get("low")),
        "pre_close": safe_float(row.get("pre_close")),
        "volume": safe_int(row.get("vol")),
        "amount": safe_float(row.get("amount")),
        "volume_ratio": safe_float(row.get("volume_ratio")),
        "turnover_rate": percent_to_ratio(row.get("turnover_ratio", row.get("turnover_rate"))),
        "amplitude": percent_to_ratio(row.get("amplitude")),
        "as_of": computed_at,
        "source": "tushare",
        "mode": "realtime",
    }


def build_quote_from_legacy(row, computed_at: str) -> dict[str, Any]:
    price = safe_float(row.get("price"))
    pre_close = safe_float(row.get("pre_close"))
    change_amount = None
    change_pct = None
    if price is not None and pre_close not in (None, 0):
        change_amount = round(price - float(pre_close), 4)
        change_pct = round(change_amount / float(pre_close), 6)

    volume = safe_int(row.get("volume"))
    if volume is not None:
        volume = volume // 100

    return {
        "price": price,
        "change_pct": change_pct,
        "change_amount": change_amount,
        "open": safe_float(row.get("open")),
        "high": safe_float(row.get("high")),
        "low": safe_float(row.get("low")),
        "pre_close": pre_close,
        "volume": volume,
        "amount": safe_float(row.get("amount")),
        "volume_ratio": None,
        "turnover_rate": None,
        "amplitude": None,
        "as_of": computed_at,
        "source": "tushare",
        "mode": "legacy_realtime",
    }


def fetch_item(pro, requested_symbol: str, computed_at: str) -> dict[str, Any]:
    symbol = normalize_symbol(requested_symbol)
    if not symbol:
        return build_failed_item(requested_symbol, f"非法证券代码: {requested_symbol}")

    try:
        ts_code = build_ts_code(symbol)
        security_type = infer_security_type(symbol)
    except ValueError as exc:
        return build_failed_item(requested_symbol, str(exc))

    info, info_error = fetch_security_info(pro, symbol, ts_code, security_type)

    errors: list[str] = []
    quote_data = None
    quote_name = None

    try:
        df = pro.quotation(ts_code=ts_code)
        if df is not None and not df.empty:
            row = df.iloc[0]
            quote_name = str(row.get("name", "") or "")
            quote_data = build_quote_from_quotation(row, computed_at)
        else:
            errors.append("quotation 返回空结果")
    except Exception as exc:
        errors.append(f"quotation 查询失败: {exc}")

    if quote_data is None:
        try:
            legacy_symbol = build_legacy_symbol(symbol)
            df = ts.get_realtime_quotes(legacy_symbol)
            if df is not None and not df.empty:
                row = df.iloc[0]
                quote_name = str(row.get("name", "") or quote_name or "")
                quote_data = build_quote_from_legacy(row, computed_at)
            else:
                errors.append("legacy realtime 返回空结果")
        except Exception as exc:
            errors.append(f"legacy realtime 查询失败: {exc}")

    info = ensure_info_name(info, quote_name)

    if quote_data is not None:
        return {
            "requested_symbol": requested_symbol,
            "status": "ok",
            "error": None,
            "info": info,
            "quote_data": quote_data,
        }

    if info_error:
        errors.insert(0, info_error)

    return build_failed_item(requested_symbol, "；".join(errors), info=info)


def main() -> int:
    args = parse_args()
    requested_symbols = parse_symbols(args.symbols)
    if not requested_symbols:
        emit(
            {
                "status": "failed",
                "error": "--symbols 不能为空",
                "request": {"symbols": [], "count": 0},
            },
            args.pretty,
        )
        return 2

    try:
        pro = get_tushare_pro()
    except RuntimeError as exc:
        emit(
            {
                "status": "failed",
                "error": str(exc),
                "request": {
                    "symbols": requested_symbols,
                    "count": len(requested_symbols),
                },
            },
            args.pretty,
        )
        return 3

    computed_at = now_iso()
    items = [fetch_item(pro, symbol, computed_at) for symbol in requested_symbols]
    success_count = sum(1 for item in items if item["status"] == "ok")
    failed_count = len(items) - success_count

    payload = {
        "status": "ok" if failed_count == 0 else "partial",
        "computed_at": computed_at,
        "source": "tushare",
        "request": {
            "symbols": requested_symbols,
            "count": len(requested_symbols),
        },
        "summary": {
            "ok": success_count,
            "failed": failed_count,
        },
        "items": items,
    }
    emit(payload, args.pretty)
    return 0


if __name__ == "__main__":
    sys.exit(main())
