#!/usr/bin/env python3
"""Skill command executor for /hkipo."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))


def build_prompt(payload: dict) -> str:
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    workspace = payload.get("workspace") or {}
    workspace_name = workspace.get("name") or workspace.get("folder") or "当前工作区"

    return f"""今天是 {today}。这是由 stock-analysis-skill 的 /hkipo 触发的港股 IPO 池研究任务，当前工作区为：{workspace_name}。

任务目标
- 自动发现当前“可认购”或“已截止认购但未上市”的港股 IPO；不要求用户提供代码。
- 输出极简打新优先级：用飞书友好的窄卡片列表展示综合评分、融资倍数/认购热度、绿鞋/基石、首日回测映射。
- 如果当前没有符合条件的标的，明确写出“当前无符合条件的港股 IPO 池”。

执行要求
- 必须联网核验当前状态，并使用绝对日期表述关键时间点。
- 必须按 {today} 重新获取最新数据；不允许把旧日期的孖展、公开认购、暗盘或中签率当作当前数据使用。若只能找到旧数据，必须标注来源日期并写明“过期/仅供趋势参考”，不得用于当前热度主评分。
- 不要解释触发文本、系统日期或取数过程；若用户消息里的日期与 {today} 不一致，直接按 {today} 输出，不写日期差异说明。
- 当前 IPO 池发现、招股状态、上市日、招股截止日、发售价、一手股数和入场费必须优先使用 Futu/OpenD 只读接口：`.venv/bin/python /Users/ryan/.agents/skills/futuapi/scripts/quote/get_ipo_list.py HK --json`。只有当 Futu/OpenD 不可用、返回空值或字段为 N/A 时，才允许用外部数据源补齐，并在 Sources 中标注“Futu 缺字段，外部源补充”。
- 招股书、全球发售、配发结果、上市文件、公司公告等事实层优先使用 HKEX / 公司公告；财经站只用于补充 Futu/OpenD 和一手来源未提供的公开发售倍数、孖展/认购热度、中签率、一手中签率、灰市、首日涨幅等二级数据。
- 必须读取并遵循 stock-analysis-skill 的 `references/hkipo.md`：按 0-100 加权评分，覆盖融资/认购热度、发行结构、回测适配、基本面、估值、证据质量；若已进入暗盘后待上市阶段，暗盘涨幅是最强近端信号。
- 发行结构必须检查绿鞋/超额配股权、稳定价格操作人、基石质量与占比、保荐人、回拨/公众货比例。
- 回测校准只保留关键映射结论，写入每只 IPO 的“回测”字段；不要单列推导过程。
- 不输出目标价、确定性承诺或买卖指令；“推荐”只表达为打新/跟踪优先级。
- 不要使用宽 Markdown 表格；飞书卡片会横向滚动且裁切。每只 IPO 用 5-6 行窄卡片字段展示。
- 输出必须短：除 Sources 外，不写卡片外的逐票解释；结论先行最多 3 条 bullet。

输出格式
# 港股 IPO 池（{today}）

## 结论先行
- 1-3 条 bullet，直接说明最值得跟踪、偏情绪博弈、谨慎/回避。

## 优先级卡片
**1. 代码 公司｜评分｜优先级**
阶段：招股/截止/暗盘/上市日；Futu：发售价/一手/入场费/状态
热度：最新孖展/公开认购/暗盘，标注日期和是否外部补充
结构：绿鞋/基石/保荐/回拨
回测：对应热度分桶和首日赔率映射
风险：一句话最大风险

## Sources
- 只列关键链接；每个标的最多 2-3 个 Markdown 短链接，标明用途、发布日期/更新时间、Futu 当前字段或外部补充字段。"""


def main() -> None:
    raw = sys.stdin.read().strip()
    payload = json.loads(raw) if raw else {}
    emit(
        {
            "reply": {
                "type": "assistant_prompt",
                "content": build_prompt(payload),
                "ack": "已开始按融资热度/绿鞋/回测评分当前港股 IPO 池，完成后返回飞书友好的简明卡片报告。",
            }
        }
    )


if __name__ == "__main__":
    main()
