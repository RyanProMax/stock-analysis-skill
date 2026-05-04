#!/usr/bin/env python3
"""Skill command executor for /research."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Mapping
from zoneinfo import ZoneInfo


MARKET_ALIASES = {
    "a": "cn",
    "ashare": "cn",
    "cn": "cn",
    "china": "cn",
    "a股": "cn",
    "us": "us",
    "usa": "us",
    "美股": "us",
    "hk": "hk",
    "hkg": "hk",
    "港股": "hk",
}
US_SYMBOL_PATTERN = re.compile(r"[A-Z][A-Z0-9.-]{0,9}")
SHORT_BARE_US_SYMBOL_PATTERN = re.compile(r"[A-Z][A-Z0-9.-]{0,4}")
BARE_ENGLISH_COMPANY_PATTERN = re.compile(r"[A-Z][A-Z0-9&'.-]{5,79}")


@dataclass(frozen=True)
class ResearchTarget:
    market: str
    input_symbol: str
    normalized_symbol: str
    display_symbol: str
    yahoo_symbol: str | None = None


@dataclass(frozen=True)
class StockAnalyzeCommand:
    command: str | None
    api_root: Path | None
    reason: str | None
    uv_path: Path | None = None


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))


def usage(content: str | None = None) -> dict:
    message = content or "请提供一只股票代码。"
    return {
        "reply": {
            "type": "final_markdown",
            "content": (
                f"{message}\n\n"
                "用法：`/research <symbol>`\n\n"
                "示例：\n"
                "- `/research 宁德时代`\n"
                "- `/research 300750`\n"
                "- `/research cn 300750`\n"
                "- `/research US.AAPL`\n"
                "- `/research AAPL`\n"
                "- `/research HK.00700`\n"
                "- `/research 0700.HK`"
            ),
        }
    }


def _args_from_payload(payload: dict) -> list[str]:
    raw_args = payload.get("args")
    if isinstance(raw_args, list):
        return [str(arg).strip() for arg in raw_args if str(arg).strip()]
    args_text = str(payload.get("argsText") or "").strip()
    return [part for part in args_text.split() if part]


def _extract_market_and_symbol(args: list[str]) -> tuple[str | None, list[str]]:
    market: str | None = None
    symbols: list[str] = []
    skip_next = False
    for index, raw_arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue

        arg = raw_arg.strip()
        if not arg:
            continue
        if arg.startswith("--"):
            if arg in {"--mode", "--market"} and index + 1 < len(args):
                skip_next = True
            continue

        alias = MARKET_ALIASES.get(arg.lower())
        if alias:
            market = alias
            continue
        symbols.append(arg)
    return market, symbols


def resolve_skill_dir(
    skill_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    if skill_dir:
        return Path(skill_dir).expanduser().resolve()
    resolved_env = os.environ if env is None else env
    env_skill_dir = resolved_env.get("CLI_CLAW_SKILL_DIR")
    if env_skill_dir:
        return Path(env_skill_dir).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _valid_api_root(path: Path) -> Path | None:
    root = path.expanduser()
    if not root.is_absolute():
        root = Path.cwd() / root
    root = root.resolve()
    if (root / "scripts" / "stock_analyze.py").is_file():
        return root
    return None


def _path_from_env_executable(value: str, env: Mapping[str, str] | None) -> Path | None:
    raw_value = str(value or "").strip()
    if not raw_value:
        return None

    path_env = None if env is None else env.get("PATH", "")
    if os.sep not in raw_value and not (os.altsep and os.altsep in raw_value):
        resolved = shutil.which(raw_value, path=path_env)
        if resolved:
            return Path(resolved).expanduser().resolve()

    candidate = Path(raw_value).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    candidate = candidate.resolve()
    if candidate.is_file():
        return candidate
    return None


def candidate_uv_paths(env: Mapping[str, str] | None = None) -> list[Path]:
    resolved_env = os.environ if env is None else env
    candidates: list[Path] = []

    for env_name in ("STOCK_ANALYSIS_UV", "UV_BIN", "UV"):
        uv_path = _path_from_env_executable(resolved_env.get(env_name, ""), env)
        if uv_path:
            candidates.append(uv_path)

    path_uv = shutil.which("uv", path=None if env is None else resolved_env.get("PATH", ""))
    if path_uv:
        candidates.append(Path(path_uv).expanduser().resolve())

    home_value = resolved_env.get("HOME") or str(Path.home())
    if home_value:
        home = Path(home_value).expanduser()
        candidates.extend([home / ".local" / "bin" / "uv", home / ".cargo" / "bin" / "uv"])

    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        if resolved in seen or not resolved.is_file():
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def resolve_uv_path(env: Mapping[str, str] | None = None) -> Path | None:
    candidates = candidate_uv_paths(env=env)
    return candidates[0] if candidates else None


def candidate_api_roots(
    skill_dir: Path,
    env: Mapping[str, str] | None = None,
) -> list[Path]:
    resolved_env = os.environ if env is None else env
    candidates: list[Path] = []
    env_root = resolved_env.get("STOCK_ANALYSIS_API_ROOT")
    if env_root:
        candidates.append(Path(env_root))

    candidates.extend(
        [
            skill_dir.parent / "stock-analysis-api",
            skill_dir.parent.parent / "stock-analysis-api",
        ]
    )

    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique



def resolve_stock_analyze_command(
    target: ResearchTarget,
    *,
    skill_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> StockAnalyzeCommand:
    resolved_skill_dir = resolve_skill_dir(skill_dir=skill_dir, env=env)
    uv_path = resolve_uv_path(env=env)
    for candidate in candidate_api_roots(resolved_skill_dir, env=env):
        api_root = _valid_api_root(candidate)
        if not api_root:
            continue
        if not uv_path:
            return StockAnalyzeCommand(
                command=None,
                api_root=api_root,
                uv_path=None,
                reason=(
                    "找到 stock-analysis-api，但未找到 uv 可执行文件；"
                    "请设置 STOCK_ANALYSIS_UV 或 UV_BIN 为绝对路径，"
                    "或确保 skill 运行环境 HOME 下存在 .local/bin/uv / .cargo/bin/uv"
                ),
            )

        command = (
            f"cd {shlex.quote(str(api_root))} && "
            f"{shlex.quote(str(uv_path))} run python scripts/stock_analyze.py "
            f"--market {shlex.quote(target.market)} "
            f"--symbols {shlex.quote(target.normalized_symbol)} "
            "--mode full --pretty"
        )
        return StockAnalyzeCommand(
            command=command,
            api_root=api_root,
            reason=None,
            uv_path=uv_path,
        )

    return StockAnalyzeCommand(
        command=None,
        api_root=None,
        uv_path=uv_path,
        reason=(
            "未找到 STOCK_ANALYSIS_API_ROOT 指向的有效仓库，"
            "也未在当前 skill 安装目录附近找到含 scripts/stock_analyze.py 的 stock-analysis-api"
        ),
    )


def _hk_symbols(raw_symbol: str) -> tuple[str, str]:
    symbol = raw_symbol.strip().upper()
    if symbol.startswith("HK."):
        digits = re.sub(r"\D", "", symbol.split(".", 1)[1])
    elif symbol.endswith(".HK"):
        digits = re.sub(r"\D", "", symbol.rsplit(".", 1)[0])
    else:
        digits = re.sub(r"\D", "", symbol)
    if not digits:
        raise ValueError("无法识别港股代码。")
    futu_symbol = f"HK.{int(digits):05d}"
    yahoo_symbol = f"{int(digits):04d}.HK"
    return futu_symbol, yahoo_symbol



def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in str(text or ""))


def parse_target(
    payload: dict,
    *,
    skill_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> ResearchTarget | str:
    del skill_dir, env
    market_hint, symbols = _extract_market_and_symbol(_args_from_payload(payload))
    if not symbols:
        return "请提供一只股票代码。"
    if len(symbols) != 1:
        return "一次只支持一只股票；请拆成多次 `/research` 请求。"

    raw_input = symbols[0].strip()
    raw_symbol = raw_input.upper()
    if not raw_symbol:
        return "请提供一只股票代码。"

    if market_hint == "cn":
        digits = re.sub(r"\D", "", raw_symbol)
        if len(digits) == 6:
            return ResearchTarget("cn", raw_symbol, digits, digits)
        if _contains_cjk(raw_input):
            return ResearchTarget("cn", raw_input, raw_input, raw_input)
        return "A 股代码需要是 6 位数字，例如 `/research 300750`。"

    if market_hint == "us":
        symbol = raw_symbol[3:] if raw_symbol.startswith("US.") else raw_symbol
        if not US_SYMBOL_PATTERN.fullmatch(symbol):
            if _contains_cjk(raw_input):
                return ResearchTarget("us", raw_input, raw_input, raw_input)
            return "美股代码格式无法识别，例如 `/research US.AAPL`。"
        return ResearchTarget("us", raw_symbol, symbol, f"US.{symbol}")

    if market_hint == "hk":
        try:
            futu_symbol, yahoo_symbol = _hk_symbols(raw_symbol)
        except ValueError as exc:
            return str(exc)
        return ResearchTarget("hk", raw_symbol, futu_symbol, futu_symbol, yahoo_symbol)

    if re.fullmatch(r"\d{6}", raw_symbol):
        return ResearchTarget("cn", raw_symbol, raw_symbol, raw_symbol)
    if raw_symbol.startswith(("SH.", "SZ.", "BJ.")):
        digits = re.sub(r"\D", "", raw_symbol)
        if len(digits) == 6:
            return ResearchTarget("cn", raw_symbol, digits, digits)
    if raw_symbol.endswith((".SH", ".SZ", ".BJ")):
        digits = re.sub(r"\D", "", raw_symbol)
        if len(digits) == 6:
            return ResearchTarget("cn", raw_symbol, digits, digits)
    if raw_symbol.startswith("US."):
        symbol = raw_symbol[3:]
        if not US_SYMBOL_PATTERN.fullmatch(symbol):
            return "美股代码格式无法识别，例如 `/research US.AAPL`。"
        return ResearchTarget("us", raw_symbol, symbol, raw_symbol)
    us_exchange_match = re.fullmatch(
        r"(NASDAQ|NYSE|AMEX):([A-Z][A-Z0-9.-]{0,9})",
        raw_symbol,
    )
    if us_exchange_match:
        symbol = us_exchange_match.group(2)
        return ResearchTarget("us", raw_symbol, symbol, f"US.{symbol}")
    if raw_symbol.startswith("HK.") or raw_symbol.endswith(".HK"):
        try:
            futu_symbol, yahoo_symbol = _hk_symbols(raw_symbol)
        except ValueError as exc:
            return str(exc)
        return ResearchTarget("hk", raw_symbol, futu_symbol, futu_symbol, yahoo_symbol)
    if SHORT_BARE_US_SYMBOL_PATTERN.fullmatch(raw_symbol):
        return ResearchTarget("us", raw_symbol, raw_symbol, f"US.{raw_symbol}")
    if _contains_cjk(raw_input):
        return ResearchTarget("cn", raw_input, raw_input, raw_input)
    if BARE_ENGLISH_COMPANY_PATTERN.fullmatch(raw_symbol):
        return ResearchTarget("auto", raw_input, raw_input, raw_input)

    return "无法判断市场；请使用 `/research 宁德时代`、`/research cn 300750`、`/research US.AAPL` 或 `/research HK.00700`。"


def _stock_analyze_instruction(command: StockAnalyzeCommand) -> str:
    if command.command:
        return (
            f"`{command.command}`。这条命令由 /research executor 运行时解析，"
            "必须直接复制执行；不要改用当前工作区相对路径。"
        )

    return (
        f"stock-analysis-api 预检：{command.reason}。不要在当前工作区猜测 "
        "`$STOCK_ANALYSIS_API_ROOT` 或相对路径；此时必须把标准化 CLI 标为不可用，"
        "再按 `references/research.md` 的降级规则继续。"
    )



def _market_execution_requirements(
    target: ResearchTarget,
    *,
    skill_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    if target.market == "auto":
        return f"""市场路由：待解析（英文公司名 / 非标准短 ticker）
- 必须先检查 `STOCK_ANALYSIS_API_ROOT` 与 `uv` 是否可用，但不要把 `{target.input_symbol}` 直接当作美股普通股代码。
- 先用上游 CLI 返回字段和公开权威来源核验唯一上市市场与标准代码；若唯一核验为 A 股或美股，再按 `stock-analysis-api` 标准 CLI 继续；若唯一核验为港股，切换到港股路径，使用 Futu/OpenD + HKEX / 公司公告 / AKShare / yfinance 降级规则。
- 若标准 CLI 返回 `identity_conflict` / `identity_not_found`，或 `data.items[0].status` 为 `failed` / `not_supported` 且 `error.code` 指向 quote、core module、security type 或 identity 问题，必须解析 `data.items[0].error`、`data.items[0].info`、`data.items[0].meta.modules`、`meta.partial_reasons` 后再决定是否澄清或改道。
- 若唯一核验为港股，最终报告标题和 Sources 必须使用港股标准代码，例如 `HK.00100` / `hk`，不得沿用待解析输入或错误的 `US.*` 标题。
- 若无法唯一核验上市市场或存在同名歧义，必须先向用户澄清交易所或完整代码，不要用热度、记忆或单一搜索结果猜测。"""

    if target.market == "cn":
        command = resolve_stock_analyze_command(target, skill_dir=skill_dir, env=env)
        instruction = _stock_analyze_instruction(command)
        return f"""市场路由：A 股
- 必须先检查 `STOCK_ANALYSIS_API_ROOT`、`uv`、`TUSHARE_TOKEN` / `TUSHARE_HTTP_URL` 是否可用。
- 首选执行：{instruction}
- 上游 CLI 负责股票名 / 公司名解析；若返回 `identity_conflict` / `identity_not_found`，必须先向用户澄清，不要自行猜测代码。
- `stock-analysis-api` JSON 是主事实底稿；只读取 `data.items[0]`、`summary.research_strategy`、`summary.*`、`meta.modules` 和原始 records 摘要。
- 若 Tushare 权限不足、研报/公告/新闻为空或模块状态为 `partial` / `permission_denied` / `not_supported`，必须进入“数据质量与降级”章节。
- 不直接改走原始 Tushare，除非用户明确要求原始接口或当前 CLI 无法覆盖。"""

    if target.market == "us":
        command = resolve_stock_analyze_command(target, skill_dir=skill_dir, env=env)
        instruction = _stock_analyze_instruction(command)
        return f"""市场路由：美股
- 必须先检查 `STOCK_ANALYSIS_API_ROOT` 与 `uv` 是否可用。
- 首选执行：{instruction}
- 上游 CLI 负责股票名 / 公司名解析；若返回 `identity_conflict` / `identity_not_found`，必须先向用户澄清，不要自行猜测代码。
- `stock-analysis-api` JSON 是主事实底稿；重点消费 technical、earnings、dcf、comps、three_statement、competitive、sector_overview、summary.research_strategy。
- 允许联网补充 SEC filings、公司 IR、earnings transcript、最新财报电话会、重大新闻和行业数据；所有联网事实必须标注来源日期。
- 若 FMP / yfinance / SEC / 新闻源不可用，必须明确写入“数据质量与降级”，不能补编财务或估值数据。"""

    yahoo_symbol = target.yahoo_symbol or target.normalized_symbol
    return f"""市场路由：港股（后置支持）
- 港股当前不走 `stock_analyze.py --market hk`；不要虚构该 CLI。
- 优先用 Futu/OpenD 只读能力获取行情快照、K 线、估值快照和市场状态，Futu 代码：`{target.normalized_symbol}`。
- 用 HKEX / 公司公告补充年报、中报、公告、上市文件和公司行动；用 AKShare / yfinance 作为财务与历史行情补充，Yahoo 格式：`{yahoo_symbol}`。
- 港股字段缺失、延迟行情、HKEX PDF 无法抽取或 Futu/OpenD 不可用时，必须明确标注“港股数据层降级”；港股结论只能基于已核验事实。"""


def build_prompt(
    payload: dict,
    target: ResearchTarget,
    *,
    skill_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    workspace = payload.get("workspace") or {}
    workspace_name = workspace.get("name") or workspace.get("folder") or "当前工作区"
    execution_requirements = _market_execution_requirements(
        target,
        skill_dir=skill_dir,
        env=env,
    )

    market_label = "待解析" if target.market == "auto" else target.market
    if target.market == "auto":
        title_instruction = (
            f"核验后的 `**/research｜{{标准代码}}｜{{market}}｜{today}**`；"
            "若唯一核验为港股，必须使用港股标准代码和 `hk` 市场"
        )
    else:
        title_instruction = (
            f"`**/research｜{target.display_symbol}｜{target.market}｜{today}**`"
        )

    target_block = (
        f"- 用户输入：`{target.input_symbol}`\n"
        f"- 识别市场：`{market_label}`\n"
        f"- 标准代码：`{target.display_symbol}`"
    )

    return f"""今天是 {today}。这是由 stock-analysis-skill 的 /research 触发的单只股票深度研报任务，当前工作区为：{workspace_name}。

请求标的
{target_block}

任务目标
- 只分析这一只股票，输出中文深度研报。
- A 股 / 美股优先复用 `stock-analysis-api` 的标准化 objective analyze full mode；港股是后置支持，按 Futu/OpenD + HKEX / AKShare / yfinance 降级路径执行。
- 必须读取并遵循 stock-analysis-skill 的 `references/research.md`，按统一研报模板输出。

执行要求
{execution_requirements}
- 需要联网核验最新公开事实时，必须使用绝对日期；不要把旧新闻、旧公告或旧财报当成当前事实。
- 报告只能基于结构化 JSON、公告/财报/交易所/公司 IR 等可核验来源；所有关键判断必须能追溯到模块或链接。
- 必须输出数据可信度层：`module_status`（各模块 ok/partial/degraded/failed）、`source_freshness`（行情/财报/公告/研报等截至时间）、`data_gaps`（缺失、过期、冲突或无权限数据）。
- 必须补充行业与市场维度：行业整体趋势（景气度、供需、政策、技术周期或竞争格局变化）、市场热度（板块表现、成交/资金、新闻/搜索/社媒热度等可得 proxy）、同类公司平均 PE（说明可比公司口径、样本、剔除负 PE/异常值、截至日期）和权威机构研报汇总（机构名、研报发布日期、核心观点、分歧点；不得把单一机构观点当成市场共识，不输出评级或目标价作为建议）。
- 风险评估必须整合在 `/research` 内，不新增独立 /risk；单票报告输出“风险与反证”，组合/持仓问题也按 `/research` 的只读风险约束处理。
- 历史验证只作为 `/research` 的可选模块：仅在有可复现条件和足够数据时输出历史统计，必须写清样本数、时间窗口、筛选条件、指标和限制，不得转成交易指令。
- 不输出买卖建议、目标价、确定性承诺、主观 conviction、`recommendation`、`confidence`、`price_target`、`thesis`。
- 可以输出“重点跟踪 / 证据较强 / 风险偏高 / 数据不足”，但必须把它们解释为研究优先级或证据强度，不是交易建议。
- 缺失数据直接写“未披露 / 未找到可靠来源 / 当前接口无权限”，不要伪造。
- 最终回复必须直接从标题开始，即第一行必须是 `**/research｜...**`；不得包含执行过程日志、工具调用尝试、思考过程、调试细节、异常堆栈或“我先检查/我找到/接下来”这类过程性文字。
- 调试细节只压缩进“降级说明”：保留用户能理解的原因，例如“标准 CLI 失败 / Tushare token 不可用”；不要暴露内部函数名、堆栈或本地路径，除非用户明确要求排障。

输出格式
- 以 `references/research.md` 的 Required Output Structure 为完整结构；默认输出飞书短版，控制在 2500-3500 字。
- 标题使用：{title_instruction}。
- 飞书短版必须包含：结论摘要、数据可信度、关键风险与反证、降级说明、Sources。
- 飞书短版也必须压缩纳入：行业整体趋势、市场热度、同类公司平均 PE、权威机构研报汇总；若数据不可得，写入数据可信度或降级说明，不要省略。
- 业务与行业、财务质量、估值上下文、催化剂与验证路径、历史验证默认压缩进结论/风险；只有用户明确要求“详细 / 完整 / 深度 / 展开”时才展开为独立长章节。
- Sources 只列关键来源链接或模块名；外部链接要标明用途和发布日期/更新时间。"""


def build_reply(
    payload: dict,
    *,
    skill_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> dict:
    target_or_error = parse_target(payload, skill_dir=skill_dir, env=env)
    if isinstance(target_or_error, str):
        return usage(target_or_error)

    return {
        "reply": {
            "type": "assistant_prompt",
            "content": build_prompt(
                payload,
                target_or_error,
                skill_dir=skill_dir,
                env=env,
            ),
            "ack": f"已开始生成 {target_or_error.display_symbol} 的单票深度研报。",
        }
    }


def main() -> None:
    raw = sys.stdin.read().strip()
    payload = json.loads(raw) if raw else {}
    emit(build_reply(payload))


if __name__ == "__main__":
    main()
