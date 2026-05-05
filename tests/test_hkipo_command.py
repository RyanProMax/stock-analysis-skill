import pathlib
import os
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "commands"))

import hkipo


class HkipoFutuCommandTest(unittest.TestCase):
    def test_prompt_excludes_closed_ipo_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            skill_dir.mkdir()

            prompt = hkipo.build_prompt(
                {
                    "argsText": "",
                    "args": [],
                    "workspace": {"name": "测试工作区"},
                },
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn("默认只输出当前仍可认购的港股 IPO", prompt)
        self.assertIn("过滤 `is_subscribe_status=false`", prompt)
        self.assertIn("/hkipo --all", prompt)
        self.assertNotIn("--include" + "-closed", prompt)
        self.assertNotIn("自动发现当前“可认购”或“已截止认购但未上市”", prompt)

    def test_prompt_can_include_closed_ipo_with_all_flag(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            skill_dir.mkdir()

            prompt = hkipo.build_prompt(
                {
                    "argsText": "--all",
                    "args": ["--all"],
                    "workspace": {"name": "测试工作区"},
                },
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn("输出当前仍可认购 + 已截止认购但未上市的港股 IPO", prompt)
        self.assertIn("用户已显式传入 `--all`", prompt)
        self.assertIn("保留 `is_subscribe_status=false` 且上市日未到的标的", prompt)
        self.assertNotIn("--include" + "-closed", prompt)

    def test_prompt_requires_subscription_conflict_field(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            skill_dir.mkdir()

            prompt = hkipo.build_prompt(
                {"workspace": {"name": "测试工作区"}},
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn("申购冲突", prompt)
        self.assertIn("同批次资金冲突", prompt)
        self.assertIn("可等上批次结果后再申购", prompt)
        self.assertIn("⏱ 冲突：", prompt)

    def test_prompt_uses_runtime_resolved_absolute_futu_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "developer space" / "stock-analysis-skill"
            python_path = skill_dir / ".venv" / "bin" / "python"
            futu_script = (
                root
                / ".agents"
                / "skills"
                / "futuapi"
                / "scripts"
                / "quote"
                / "get_ipo_list.py"
            )
            python_path.parent.mkdir(parents=True)
            target_python = root / "python-real"
            target_python.write_text("#!/usr/bin/env python\n", encoding="utf-8")
            if hasattr(os, "symlink"):
                python_path.symlink_to(target_python)
            else:
                python_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")
            futu_script.parent.mkdir(parents=True)
            futu_script.write_text("#!/usr/bin/env python\n", encoding="utf-8")

            prompt = hkipo.build_prompt(
                {"workspace": {"name": "测试工作区"}},
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn(str(python_path), prompt)
        self.assertNotIn(str(target_python), prompt)
        self.assertIn(str(futu_script), prompt)
        self.assertIn(f"{futu_script.resolve()} HK --json", prompt)
        self.assertNotIn("`.venv/bin/python ", prompt)
        self.assertNotIn("/Users/ryan", prompt)

    def test_prompt_reports_missing_futu_preflight_without_relative_venv(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            skill_dir.mkdir()

            prompt = hkipo.build_prompt(
                {"workspace": {"name": "测试工作区"}},
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn("Futu/OpenD 预检：未找到", prompt)
        self.assertNotIn("`.venv/bin/python ", prompt)
        self.assertNotIn("/Users/ryan", prompt)

    def test_prompt_can_use_futuapi_skill_venv_when_stock_skill_venv_is_missing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            futuapi_dir = root / ".agents" / "skills" / "futuapi"
            futuapi_python = futuapi_dir / ".venv" / "bin" / "python"
            futu_script = futuapi_dir / "scripts" / "quote" / "get_ipo_list.py"
            skill_dir.mkdir()
            futuapi_python.parent.mkdir(parents=True)
            futuapi_python.write_text("#!/usr/bin/env python\n", encoding="utf-8")
            futu_script.parent.mkdir(parents=True)
            futu_script.write_text("#!/usr/bin/env python\n", encoding="utf-8")

            prompt = hkipo.build_prompt(
                {"workspace": {"name": "测试工作区"}},
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn(str(futuapi_python), prompt)
        self.assertIn(f"{futu_script.resolve()} HK --json", prompt)
        self.assertNotIn("Futu/OpenD 预检：未找到", prompt)


if __name__ == "__main__":
    unittest.main()
