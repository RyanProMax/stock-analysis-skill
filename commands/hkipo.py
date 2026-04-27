#!/usr/bin/env python3
"""Skill command executor for /hkipo."""

from __future__ import annotations

import json
import sys
from datetime import date


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))


def build_prompt(payload: dict) -> str:
    today = date.today().isoformat()
    workspace = payload.get("workspace") or {}
    workspace_name = workspace.get("name") or workspace.get("folder") or "当前工作区"

    return f"""今天是 {today}。这是由 stock-analysis-skill 的 /hkipo 触发的港股 IPO 池研究任务，当前工作区为：{workspace_name}。

任务目标
- 自动发现当前“可认购”或“已截止认购但未上市”的港股 IPO；不要求用户提供代码。
- 输出简明打新优先级：综合评分、融资倍数/认购热度、绿鞋/基石、首日回测映射。
- 如果当前没有符合条件的标的，明确写出“当前无符合条件的港股 IPO 池”。

执行要求
- 必须联网核验当前状态，并使用绝对日期表述关键时间点。
- 优先使用一手来源：HKEX 招股书/全球发售文件、配发结果、上市文件、公司公告；财经站只用于补充公开发售倍数、孖展/认购热度、中签率、一手中签率、灰市、首日涨幅等二级数据。
- 必须读取并遵循 stock-analysis-skill 的 `references/hkipo.md`：按 0-100 加权评分，覆盖融资/认购热度、发行结构、回测适配、基本面、估值、证据质量；若已进入暗盘后待上市阶段，暗盘涨幅是最强近端信号。
- 发行结构必须检查绿鞋/超额配股权、稳定价格操作人、基石质量与占比、保荐人、回拨/公众货比例。
- 回测校准：尽量选取最近 1-3 个月或同赛道 5-10 只已上市港股 IPO，统计首日胜率、中位首日涨幅，并说明样本限制；结合融资倍数/暗盘/首日涨幅反向检查评分是否偏保守或偏激进。
- 不输出目标价、确定性承诺或买卖指令；“推荐”只表达为打新/跟踪优先级。

输出格式
# 港股 IPO 池（{today}）

## 结论先行
- 3-5 条 bullet，直接说明最值得跟踪、偏情绪博弈、谨慎/回避。

## 评分总览
| 代码 | 公司 | 阶段/上市日 | 评分/优先级 | 融资/认购热度 | 首日回测映射 | 绿鞋/基石/保荐 | 基本面/估值 | 最大风险 |
|---|---|---|---:|---|---|---|---|---|

## 回测校准
- 用 3-5 条 bullet 说明样本、首日胜率、中位首日涨幅、可借鉴模式和限制。

## Sources
- 按标的/回测样本分组列链接，并标明每个链接用途。"""


def main() -> None:
    raw = sys.stdin.read().strip()
    payload = json.loads(raw) if raw else {}
    emit(
        {
            "reply": {
                "type": "assistant_prompt",
                "content": build_prompt(payload),
                "ack": "已开始按融资热度/绿鞋/回测评分当前港股 IPO 池，完成后返回单表简明报告。",
            }
        }
    )


if __name__ == "__main__":
    main()
