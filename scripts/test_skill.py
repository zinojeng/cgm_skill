#!/usr/bin/env python3
"""
CGM 技能自我測試工具
驗證所有功能是否正常運作
"""

import os
import sys
import json
import yaml
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple


class SkillTester:
    """技能測試器"""

    def __init__(self):
        """初始化測試器"""
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.skill_root = Path(__file__).parent.parent

    def run_all_tests(self) -> bool:
        """執行所有測試"""
        print("=" * 60)
        print("🧪 CGM 技能自我測試")
        print("=" * 60)

        # 測試項目
        tests = [
            ("檔案結構", self.test_file_structure),
            ("Python 依賴", self.test_dependencies),
            ("腳本可執行性", self.test_scripts),
            ("配置檔案", self.test_config),
            ("知識庫", self.test_knowledge),
            ("範例數據", self.test_examples),
            ("版本資訊", self.test_version)
        ]

        # 執行測試
        for test_name, test_func in tests:
            print(f"\n測試 {test_name}...")
            try:
                success, message = test_func()
                if success:
                    self.test_results["passed"].append(test_name)
                    print(f"  ✅ {message}")
                else:
                    self.test_results["failed"].append(test_name)
                    print(f"  ❌ {message}")
            except Exception as e:
                self.test_results["failed"].append(test_name)
                print(f"  ❌ 測試失敗：{str(e)}")

        # 顯示總結
        self._show_summary()

        return len(self.test_results["failed"]) == 0

    def test_file_structure(self) -> Tuple[bool, str]:
        """測試檔案結構"""
        required_files = [
            "skill.md",
            "config.yaml",
            "README.md",
            "CHANGELOG.md",
            "VERSION",
            "scripts/split_csv.py",
            "scripts/analyze_cgm.py",
            "scripts/llm_analysis.py",
            "scripts/validate.py",
            "scripts/setup.py",
            "scripts/batch_process.py",
            "scripts/requirements.txt",
            "knowledge/cgm_metrics.md",
            "knowledge/diabetes_guidelines.md",
            "examples/sample_cgm_data.csv"
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.skill_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            return False, f"缺少檔案：{', '.join(missing_files)}"

        return True, f"所有必要檔案都存在 ({len(required_files)} 個)"

    def test_dependencies(self) -> Tuple[bool, str]:
        """測試 Python 依賴"""
        required_modules = [
            "pandas",
            "numpy",
            "matplotlib",
            "yaml",
            "openai"
        ]

        missing_modules = []
        for module in required_modules:
            spec = importlib.util.find_spec(module)
            if spec is None:
                missing_modules.append(module)

        if missing_modules:
            self.test_results["warnings"].append(
                f"缺少 Python 模組：{', '.join(missing_modules)}。"
                f"請執行：pip install -r scripts/requirements.txt"
            )
            return False, f"缺少 {len(missing_modules)} 個必要模組"

        return True, f"所有必要模組都已安裝 ({len(required_modules)} 個)"

    def test_scripts(self) -> Tuple[bool, str]:
        """測試腳本可執行性"""
        scripts_dir = self.skill_root / "scripts"
        python_scripts = list(scripts_dir.glob("*.py"))

        non_executable = []
        for script in python_scripts:
            if not os.access(script, os.X_OK):
                non_executable.append(script.name)

        if non_executable:
            self.test_results["warnings"].append(
                f"以下腳本沒有執行權限：{', '.join(non_executable)}。"
                f"請執行：chmod +x scripts/*.py"
            )
            return False, f"{len(non_executable)} 個腳本沒有執行權限"

        # 測試腳本語法
        syntax_errors = []
        for script in python_scripts:
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    compile(f.read(), script.name, 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{script.name}: {e}")

        if syntax_errors:
            return False, f"語法錯誤：{'; '.join(syntax_errors)}"

        return True, f"所有腳本都可執行且語法正確 ({len(python_scripts)} 個)"

    def test_config(self) -> Tuple[bool, str]:
        """測試配置檔案"""
        config_file = self.skill_root / "config.yaml"

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 檢查必要的配置項
            required_keys = ["defaults", "ai_models", "output", "data_processing"]
            missing_keys = [key for key in required_keys if key not in config]

            if missing_keys:
                return False, f"配置檔案缺少：{', '.join(missing_keys)}"

            # 檢查配置值
            if "defaults" in config:
                if "target_range" in config["defaults"]:
                    low = config["defaults"]["target_range"].get("low", 70)
                    high = config["defaults"]["target_range"].get("high", 180)

                    if low >= high:
                        return False, f"目標範圍設定錯誤：{low}-{high}"

            return True, "配置檔案格式正確且包含所有必要項目"

        except Exception as e:
            return False, f"無法讀取配置檔案：{str(e)}"

    def test_knowledge(self) -> Tuple[bool, str]:
        """測試知識庫"""
        knowledge_dir = self.skill_root / "knowledge"

        if not knowledge_dir.exists():
            return False, "知識庫目錄不存在"

        # 統計知識檔案
        md_files = list(knowledge_dir.rglob("*.md"))

        if len(md_files) < 2:
            return False, f"知識庫檔案不足（找到 {len(md_files)} 個）"

        # 檢查檔案大小
        total_size = sum(f.stat().st_size for f in md_files)

        if total_size < 1000:  # 至少 1KB
            return False, "知識庫內容太少"

        return True, f"知識庫包含 {len(md_files)} 個檔案，總大小 {total_size/1024:.1f}KB"

    def test_examples(self) -> Tuple[bool, str]:
        """測試範例數據"""
        examples_dir = self.skill_root / "examples"
        sample_file = examples_dir / "sample_cgm_data.csv"

        if not sample_file.exists():
            return False, "範例數據檔案不存在"

        try:
            # 嘗試讀取範例數據
            import pandas as pd
            df = pd.read_csv(sample_file)

            # 檢查必要欄位
            required_columns = ["Date", "Time", "Sensor Glucose (mg/dL)"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return False, f"範例數據缺少欄位：{', '.join(missing_columns)}"

            if len(df) < 10:
                return False, f"範例數據太少（只有 {len(df)} 筆）"

            return True, f"範例數據格式正確（{len(df)} 筆記錄）"

        except Exception as e:
            return False, f"無法讀取範例數據：{str(e)}"

    def test_version(self) -> Tuple[bool, str]:
        """測試版本資訊"""
        version_file = self.skill_root / "VERSION"

        if not version_file.exists():
            return False, "VERSION 檔案不存在"

        try:
            with open(version_file, 'r') as f:
                version = f.read().strip()

            # 檢查版本格式 (主版本.次版本.修訂號)
            parts = version.split('.')
            if len(parts) != 3:
                return False, f"版本格式錯誤：{version}"

            for part in parts:
                if not part.isdigit():
                    return False, f"版本號必須是數字：{version}"

            # 檢查 skill.md 中的版本
            skill_file = self.skill_root / "skill.md"
            with open(skill_file, 'r', encoding='utf-8') as f:
                skill_content = f.read()

            if f"version: {version}" not in skill_content:
                self.test_results["warnings"].append(
                    f"skill.md 中的版本號與 VERSION 檔案不符"
                )

            return True, f"版本號：{version}"

        except Exception as e:
            return False, f"無法讀取版本資訊：{str(e)}"

    def _show_summary(self):
        """顯示測試總結"""
        print("\n" + "=" * 60)
        print("測試總結")
        print("=" * 60)

        total_tests = len(self.test_results["passed"]) + len(self.test_results["failed"])

        print(f"\n總測試數：{total_tests}")
        print(f"✅ 通過：{len(self.test_results['passed'])}")
        print(f"❌ 失敗：{len(self.test_results['failed'])}")

        if self.test_results["failed"]:
            print("\n失敗的測試：")
            for test_name in self.test_results["failed"]:
                print(f"  - {test_name}")

        if self.test_results["warnings"]:
            print("\n⚠️ 警告：")
            for warning in self.test_results["warnings"]:
                print(f"  - {warning}")

        # 生成報告檔案
        report = {
            "timestamp": str(Path.cwd()),
            "total_tests": total_tests,
            "passed": self.test_results["passed"],
            "failed": self.test_results["failed"],
            "warnings": self.test_results["warnings"],
            "success_rate": (len(self.test_results["passed"]) / total_tests * 100)
                           if total_tests > 0 else 0
        }

        report_file = self.skill_root / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 測試報告已儲存至：{report_file}")

        # 最終結果
        if len(self.test_results["failed"]) == 0:
            print("\n🎉 所有測試都通過！技能已準備就緒。")
        else:
            print("\n❌ 有測試失敗，請修復後再試。")


def main():
    """主函數"""
    print("開始 CGM 技能自我測試...\n")

    tester = SkillTester()
    success = tester.run_all_tests()

    # 提供修復建議
    if not success:
        print("\n💡 修復建議：")
        print("1. 安裝依賴：pip install -r scripts/requirements.txt")
        print("2. 設定權限：chmod +x scripts/*.py")
        print("3. 執行設定：python scripts/setup.py")
        print("4. 檢查檔案：確認所有必要檔案都存在")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())