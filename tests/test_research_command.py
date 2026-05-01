import json
import pathlib
import subprocess
import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
