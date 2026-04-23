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

任务范围
- 自动发现当前“可认购”或“已截止认购但未上市”的港股 IPO。
- 不要求用户提供股票代码；你必须先自行整理当前 IPO 池。
- 如果当前没有符合条件的标的，明确写出“当前无符合条件的港股 IPO 池”。

执行要求
- 必须使用联网能力核验当前状态，并使用绝对日期表述关键时间点。
- 优先引用一手或官方来源：HKEX 招股书、配发结果公告、上市文件、公司公告；再用可靠财经站补充公开发售倍数、国际配售热度、中签率 / 一手中签率 / 回拨等公开信息。
- 对每个标的至少覆盖：业务与赛道、商业化阶段、客户/订单、收入利润、亏损/现金流、研发与客户集中度、募资用途、保荐人、基石、估值区间和可比公司。
- 情绪热度必须综合评估：公开发售申购倍数、国际配售或机构超购描述、中签率或一手中签率（若可得）、当前时间窗口（招股中 / 已截止待上市）。
- 若环境里可调用 `stock-analysis-api`、`financial-stock-analysis` 或其他标准化财务资产，只把它们作为财务/估值分析框架使用；港股 IPO 的事实状态、日期和认购数据仍以当前联网获取到的官方/一手来源为准。
- 方法论上借鉴高星仓库里“模块化分解 + 基本面/估值/情绪/赔率分层”的做法，例如 FinanceToolkit、FinGPT、Value-Investing-Agent 一类项目；但不要把这些仓库当成事实来源引用。
- 不输出主观荐股、目标价或确定性承诺；缺失数据明确写“未披露”或“未找到可靠来源”。

输出格式
# 港股 IPO 池跟踪（{today}）

## IPO 池总览
- 先用表格列出：代码 | 公司 | 阶段 | 招股期/截止 | 定价/配发/上市日 | 公开发售倍数 | 中签率/一手中签率 | 情绪热度 | 一句话结论。

## 本期结论
- 用 3 到 6 条扁平 bullet 概括本期更值得重点跟踪、偏情绪博弈、应谨慎回避的标的。

## 逐标的分析
### {{代码}} {{公司名}}
- 标的识别
- 一句话结论
- 发行与上市进度
- 公司状态
- 财务与经营质量
- 估值与可比
- 情绪热度与中签赔率
- 风险与催化
- 打新观察点

## 横向优先级
- 按“更值得重点跟踪 / 更偏情绪博弈 / 更适合回避”分组。

## Sources
- 每个标的至少给出主要来源链接；如果数据来自不同来源，分别标清用途。"""


def main() -> None:
    raw = sys.stdin.read().strip()
    payload = json.loads(raw) if raw else {}
    emit(
        {
            "reply": {
                "type": "assistant_prompt",
                "content": build_prompt(payload),
                "ack": "已开始分析当前可认购与待上市港股 IPO 池，完成后返回结构化报告。",
            }
        }
    )


if __name__ == "__main__":
    main()
