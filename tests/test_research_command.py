import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "commands"))

import research


class ResearchCommandTest(unittest.TestCase):
    def test_cn_symbol_builds_assistant_prompt_with_full_stock_analyze_cli(self) -> None:
        result = research.build_reply(
            {
                "argsText": "300750",
                "args": ["300750"],
                "workspace": {"name": "研究测试"},
            }
        )

        reply = result["reply"]
        content = reply["content"]

        self.assertEqual(reply["type"], "assistant_prompt")
        self.assertIn("stock-analysis-skill 的 /research", content)
        self.assertIn("当前工作区为：研究测试", content)
        self.assertIn("--market cn --symbols 300750 --mode full --pretty", content)
        self.assertIn("stock-analysis-api", content)
        self.assertIn("references/research.md", content)
        self.assertIn("A 股", content)
        self.assertIn("不输出买卖建议、目标价", content)

    def test_cn_prompt_uses_runtime_resolved_absolute_api_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "developer space" / "stock-analysis-skill"
            api_root = root / "developer space" / "stock-analysis-api"
            script_path = api_root / "scripts" / "stock_analyze.py"
            skill_dir.mkdir(parents=True)
            script_path.parent.mkdir(parents=True)
            script_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")

            result = research.build_reply(
                {
                    "argsText": "300750",
                    "args": ["300750"],
                    "workspace": {"name": "研究测试"},
                },
                skill_dir=skill_dir,
                env={},
            )

        content = result["reply"]["content"]

        self.assertIn(f"cd {research.shlex.quote(str(api_root))}", content)
        self.assertIn("uv run python scripts/stock_analyze.py", content)
        self.assertIn("--market cn --symbols 300750 --mode full --pretty", content)
        self.assertNotIn('cd "$STOCK_ANALYSIS_API_ROOT"', content)

    def test_env_api_root_takes_precedence_over_sibling_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            sibling_root = root / "stock-analysis-api"
            env_root = root / "env stock api"
            skill_dir.mkdir()
            for api_root in (sibling_root, env_root):
                script_path = api_root / "scripts" / "stock_analyze.py"
                script_path.parent.mkdir(parents=True)
                script_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")

            result = research.build_reply(
                {"argsText": "US.AAPL", "args": ["US.AAPL"]},
                skill_dir=skill_dir,
                env={"STOCK_ANALYSIS_API_ROOT": str(env_root)},
            )

        content = result["reply"]["content"]

        self.assertIn(f"cd {research.shlex.quote(str(env_root))}", content)
        self.assertNotIn(f"cd {research.shlex.quote(str(sibling_root))}", content)

    def test_missing_api_root_reports_preflight_instead_of_relative_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            skill_dir.mkdir()

            result = research.build_reply(
                {"argsText": "US.AAPL", "args": ["US.AAPL"]},
                skill_dir=skill_dir,
                env={},
            )

        content = result["reply"]["content"]

        self.assertIn("stock-analysis-api 预检：未找到", content)
        self.assertNotIn('cd "$STOCK_ANALYSIS_API_ROOT"', content)

    def test_empty_env_mapping_does_not_read_process_api_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            process_env_root = root / "process env api"
            script_path = process_env_root / "scripts" / "stock_analyze.py"
            skill_dir.mkdir()
            script_path.parent.mkdir(parents=True)
            script_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")

            with mock.patch.dict(
                os.environ,
                {"STOCK_ANALYSIS_API_ROOT": str(process_env_root)},
            ):
                result = research.build_reply(
                    {"argsText": "300750", "args": ["300750"]},
                    skill_dir=skill_dir,
                    env={},
                )

        content = result["reply"]["content"]

        self.assertIn("stock-analysis-api 预检：未找到", content)
        self.assertNotIn(f"cd {research.shlex.quote(str(process_env_root))}", content)

    def test_api_root_resolution_does_not_guess_from_process_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "installed" / "stock-analysis-skill"
            cwd_api_root = root / "host workspace" / "stock-analysis-api"
            script_path = cwd_api_root / "scripts" / "stock_analyze.py"
            skill_dir.mkdir(parents=True)
            script_path.parent.mkdir(parents=True)
            script_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")

            with mock.patch.object(
                research.Path,
                "cwd",
                return_value=cwd_api_root.parent,
            ):
                result = research.build_reply(
                    {"argsText": "US.AAPL", "args": ["US.AAPL"]},
                    skill_dir=skill_dir,
                    env={},
                )

        content = result["reply"]["content"]

        self.assertIn("stock-analysis-api 预检：未找到", content)
        self.assertNotIn(f"cd {research.shlex.quote(str(cwd_api_root))}", content)

    def test_us_prefixed_symbol_builds_assistant_prompt_with_us_cli(self) -> None:
        result = research.build_reply(
            {
                "argsText": "US.AAPL",
                "args": ["US.AAPL"],
                "workspace": {"folder": "equity"},
            }
        )

        reply = result["reply"]
        content = reply["content"]

        self.assertEqual(reply["type"], "assistant_prompt")
        self.assertIn("当前工作区为：equity", content)
        self.assertIn("--market us --symbols AAPL --mode full --pretty", content)
        self.assertIn("美股", content)
        self.assertIn("SEC", content)
        self.assertIn("earnings transcript", content)

    def test_exchange_prefixed_symbols_are_normalized(self) -> None:
        us_result = research.build_reply(
            {"argsText": "NASDAQ:AAPL", "args": ["NASDAQ:AAPL"]}
        )
        cn_result = research.build_reply(
            {"argsText": "BJ.430047", "args": ["BJ.430047"]}
        )

        self.assertIn(
            "--market us --symbols AAPL --mode full --pretty",
            us_result["reply"]["content"],
        )
        self.assertIn(
            "--market cn --symbols 430047 --mode full --pretty",
            cn_result["reply"]["content"],
        )

    def test_hk_symbol_builds_assistant_prompt_with_hk_deferred_data_path(self) -> None:
        result = research.build_reply(
            {
                "argsText": "HK.00700",
                "args": ["HK.00700"],
                "workspace": {"name": "港股研究"},
            }
        )

        reply = result["reply"]
        content = reply["content"]

        self.assertEqual(reply["type"], "assistant_prompt")
        self.assertIn("HK.00700", content)
        self.assertIn("0700.HK", content)
        self.assertIn("港股", content)
        self.assertIn("后置支持", content)
        self.assertIn("Futu/OpenD", content)
        self.assertIn("HKEX", content)
        self.assertNotIn("uv run python scripts/stock_analyze.py --market hk", content)

    def test_missing_symbol_returns_local_usage_markdown(self) -> None:
        result = research.build_reply({"argsText": "", "args": []})

        reply = result["reply"]

        self.assertEqual(reply["type"], "final_markdown")
        self.assertIn("/research <symbol>", reply["content"])
        self.assertIn("/research 300750", reply["content"])
        self.assertIn("/research US.AAPL", reply["content"])

    def test_multiple_symbols_are_rejected_locally(self) -> None:
        result = research.build_reply(
            {"argsText": "300750 600519", "args": ["300750", "600519"]}
        )

        reply = result["reply"]

        self.assertEqual(reply["type"], "final_markdown")
        self.assertIn("一次只支持一只股票", reply["content"])

    def test_shell_like_symbols_are_rejected_locally(self) -> None:
        dangerous_inputs = [
            ["AAPL;rm", "-rf", "/"],
            ["US.AAPL;rm"],
            ["US.AAPL$(touch pwned)"],
            ["US.AAPL`touch pwned`"],
        ]

        for args in dangerous_inputs:
            with self.subTest(args=args):
                result = research.build_reply(
                    {"argsText": " ".join(args), "args": args}
                )

                self.assertEqual(result["reply"]["type"], "final_markdown")
                self.assertNotIn(
                    "assistant_prompt", json.dumps(result, ensure_ascii=False)
                )

    def test_commands_json_registers_research(self) -> None:
        manifest = json.loads((ROOT / "commands.json").read_text(encoding="utf-8"))
        command = manifest["commands"]["research"]

        self.assertEqual(command["description"], "生成单只股票深度研报")
        self.assertEqual(command["entrypoints"], ["im", "web"])
        self.assertEqual(command["executor"]["command"], "python3")
        self.assertEqual(command["executor"]["args"], ["commands/research.py"])

    def test_main_emits_assistant_prompt_json(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "commands" / "research.py")],
            input=json.dumps(
                {
                    "argsText": "US.AAPL",
                    "args": ["US.AAPL"],
                    "workspace": {"name": "subprocess"},
                }
            ),
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(proc.stdout)

        self.assertEqual(payload["reply"]["type"], "assistant_prompt")
        self.assertIn("US.AAPL", payload["reply"]["content"])
        self.assertTrue(payload["reply"]["ack"])

    def test_main_uses_env_api_root_for_absolute_cli_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            api_root = pathlib.Path(raw_root).resolve() / "api root"
            script_path = api_root / "scripts" / "stock_analyze.py"
            script_path.parent.mkdir(parents=True)
            script_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")
            env = {**os.environ, "STOCK_ANALYSIS_API_ROOT": str(api_root)}

            proc = subprocess.run(
                [sys.executable, str(ROOT / "commands" / "research.py")],
                input=json.dumps({"argsText": "300750", "args": ["300750"]}),
                text=True,
                capture_output=True,
                check=True,
                env=env,
            )

        payload = json.loads(proc.stdout)

        self.assertIn(
            f"cd {research.shlex.quote(str(api_root))}",
            payload["reply"]["content"],
        )

    def test_main_uses_cli_claw_skill_dir_for_sibling_api_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve() / "workspace root"
            skill_dir = root / "stock-analysis-skill"
            api_root = root / "stock-analysis-api"
            script_path = api_root / "scripts" / "stock_analyze.py"
            skill_dir.mkdir(parents=True)
            script_path.parent.mkdir(parents=True)
            script_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")
            env = dict(os.environ)
            env.pop("STOCK_ANALYSIS_API_ROOT", None)
            env["CLI_CLAW_SKILL_DIR"] = str(skill_dir)

            proc = subprocess.run(
                [sys.executable, str(ROOT / "commands" / "research.py")],
                input=json.dumps({"argsText": "US.AAPL", "args": ["US.AAPL"]}),
                text=True,
                capture_output=True,
                check=True,
                env=env,
            )

        payload = json.loads(proc.stdout)

        self.assertIn(
            f"cd {research.shlex.quote(str(api_root))}",
            payload["reply"]["content"],
        )
        self.assertIn(
            "--market us --symbols AAPL --mode full --pretty",
            payload["reply"]["content"],
        )


if __name__ == "__main__":
    unittest.main()
