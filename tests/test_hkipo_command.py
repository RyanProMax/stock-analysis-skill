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

    def test_prompt_removes_subscription_conflict_section_and_uses_dates_in_rank_title(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            skill_dir.mkdir()

            prompt = hkipo.build_prompt(
                {"workspace": {"name": "测试工作区"}},
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn("个股标题末尾必须写申购截止日和开奖/配发结果日", prompt)
        self.assertIn("5/6截止 | 5/7开奖", prompt)
        self.assertIn("**🟢 1｜代码 公司｜评分｜M/D截止 | M/D开奖**", prompt)
        self.assertNotIn("**⏱ 申购冲突**", prompt)
        self.assertNotIn("申购冲突：", prompt)
        self.assertNotIn("同批次资金冲突", prompt)
        self.assertNotIn("高优先级跟踪", prompt)
        self.assertNotIn("重点跟踪", prompt)
        self.assertNotIn("投资建议", prompt)

    def test_prompt_uses_compact_report_body_without_blank_empty_lines(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = pathlib.Path(raw_root).resolve()
            skill_dir = root / "stock-analysis-skill"
            skill_dir.mkdir()

            prompt = hkipo.build_prompt(
                {"workspace": {"name": "测试工作区"}},
                skill_dir=skill_dir,
                home_dir=root,
            )

        self.assertIn("**💡 关键结论**\n- 🟢", prompt)
        self.assertIn("**📌 优先级**\n**🟢 1", prompt)
        self.assertIn("⚠️ 风险：一句话最大风险\n**🔗 来源**", prompt)
        self.assertIn(
            "正文不要插入空白空行；顶层小节标题、bullet、个股标题和个股字段都用单换行连续排列",
            prompt,
        )
        self.assertIn("📍 阶段：招股/截止/暗盘/上市日", prompt)
        self.assertIn("\n💰 热度：最新孖展/公开认购/暗盘", prompt)
        self.assertNotIn("\n\n**💡 关键结论**", prompt)
        self.assertNotIn("\n\n**📌 优先级**", prompt)
        self.assertNotIn("\n\n**🔗 来源**", prompt)
        self.assertNotIn("\n\n💰 热度：最新孖展/公开认购/暗盘", prompt)
        self.assertNotIn("\n\n🛡 结构：绿鞋/基石/保荐/回拨", prompt)
        self.assertNotIn("\n\n📈 回测：对应热度分桶", prompt)
        self.assertNotIn("每条 emoji 字段上方都保留一个空行", prompt)
        self.assertIn("报告正文", prompt)
        self.assertNotIn("飞书卡片", prompt)
        self.assertNotIn("thinking", prompt.lower())
        self.assertNotIn("tool steps", prompt.lower())

    def test_reference_uses_compact_sections_and_date_title_contract(self) -> None:
        reference = (ROOT / "references" / "hkipo.md").read_text(encoding="utf-8")

        self.assertIn("deadline and allotment/result date", reference)
        self.assertIn("**🟢 1｜代码 公司｜评分｜M/D截止 | M/D开奖**", reference)
        self.assertIn("Do not insert blank empty lines", reference)
        self.assertIn("fixed source order", reference)
        self.assertNotIn("**⏱ 申购冲突**", reference)
        self.assertNotIn("⏱ 申购冲突：", reference)
        self.assertNotIn("each emoji field", reference)
        self.assertNotIn("inside every IPO block", reference)
        self.assertNotIn("thinking", reference.lower())
        self.assertNotIn("tool steps", reference.lower())

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
