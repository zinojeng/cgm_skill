#!/usr/bin/env python3
"""
CGM 分析技能設定精靈
互動式設定工具，協助使用者配置分析參數
"""

import os
import sys
import json
import yaml
from typing import Dict, Optional
from pathlib import Path


class CGMSetupWizard:
    """CGM 設定精靈"""

    def __init__(self):
        """初始化設定精靈"""
        self.config = {}
        self.config_file = "../config.yaml"

    def run(self):
        """執行設定精靈"""
        print("=" * 60)
        print("🎯 CGM 分析技能設定精靈")
        print("=" * 60)
        print("\n此精靈將協助您設定 CGM 分析參數\n")

        # 基本設定
        self._setup_basic()

        # API 設定
        self._setup_api()

        # 目標值設定
        self._setup_targets()

        # 輸出設定
        self._setup_output()

        # 進階設定
        if self._ask_yes_no("是否要設定進階選項？"):
            self._setup_advanced()

        # 儲存設定
        self._save_config()

        print("\n✅ 設定完成！")
        print(f"設定已儲存至：{self.config_file}")

    def _setup_basic(self):
        """基本設定"""
        print("\n【基本設定】")

        # 語言設定
        languages = {
            "1": ("zh-TW", "繁體中文"),
            "2": ("zh-CN", "簡體中文"),
            "3": ("en", "English")
        }

        print("\n選擇輸出語言：")
        for key, (code, name) in languages.items():
            print(f"  {key}. {name}")

        choice = input("請選擇 (預設: 1): ").strip() or "1"
        self.config["language"] = languages.get(choice, languages["1"])[0]

        # 分析期間
        days = input("\n預設分析天數 (預設: 14): ").strip()
        self.config["analysis_days"] = int(days) if days.isdigit() else 14

    def _setup_api(self):
        """API 設定"""
        print("\n【API 設定】")

        # OpenAI API Key
        print("\nOpenAI API Key 設定：")
        print("  1. 環境變數 (OPENAI_API_KEY)")
        print("  2. 設定檔案")
        print("  3. 每次輸入")

        choice = input("請選擇 (預設: 1): ").strip() or "1"

        if choice == "2":
            api_key = input("請輸入您的 OpenAI API Key: ").strip()
            if api_key:
                self.config["openai_api_key"] = api_key
                print("⚠️  API Key 將以明文儲存，請確保檔案安全")
        elif choice == "1":
            self.config["api_key_source"] = "environment"
            print("✓ 將從環境變數 OPENAI_API_KEY 讀取")
        else:
            self.config["api_key_source"] = "prompt"
            print("✓ 每次執行時輸入")

        # 模型選擇
        print("\n預設 AI 模型：")
        models = {
            "1": "gpt-4o",
            "2": "gpt-4o-mini",
            "3": "gpt-4-turbo",
            "4": "gpt-3.5-turbo"
        }

        for key, model in models.items():
            print(f"  {key}. {model}")

        choice = input("請選擇 (預設: 1): ").strip() or "1"
        self.config["default_model"] = models.get(choice, "gpt-4o")

    def _setup_targets(self):
        """目標值設定"""
        print("\n【血糖目標設定】")

        print("\n選擇預設族群：")
        populations = {
            "1": ("adult", "一般成人 (TIR >70%, 範圍 70-180)"),
            "2": ("pediatric", "兒童青少年 (TIR >60%, 範圍 70-180)"),
            "3": ("elderly", "老年患者 (TIR >50%, 範圍 70-180)"),
            "4": ("pregnancy", "妊娠期 (TIR >90%, 範圍 63-140)"),
            "5": ("custom", "自訂")
        }

        for key, (code, desc) in populations.items():
            print(f"  {key}. {desc}")

        choice = input("請選擇 (預設: 1): ").strip() or "1"
        population = populations.get(choice, populations["1"])[0]

        if population == "custom":
            # 自訂目標
            print("\n自訂血糖目標：")

            low = input("目標範圍下限 (mg/dL, 預設: 70): ").strip()
            self.config["target_low"] = int(low) if low.isdigit() else 70

            high = input("目標範圍上限 (mg/dL, 預設: 180): ").strip()
            self.config["target_high"] = int(high) if high.isdigit() else 180

            tir = input("TIR 目標 (%, 預設: 70): ").strip()
            self.config["tir_goal"] = int(tir) if tir.isdigit() else 70

            cv = input("CV 目標 (%, 預設: 36): ").strip()
            self.config["cv_target"] = int(cv) if cv.isdigit() else 36
        else:
            self.config["default_population"] = population

    def _setup_output(self):
        """輸出設定"""
        print("\n【輸出設定】")

        # 輸出格式
        print("\n選擇預設輸出格式（可多選，用逗號分隔）：")
        print("  1. Markdown (.md)")
        print("  2. HTML (.html)")
        print("  3. PDF (.pdf)")
        print("  4. JSON (.json)")

        choices = input("請選擇 (預設: 1,2): ").strip() or "1,2"
        format_map = {"1": "markdown", "2": "html", "3": "pdf", "4": "json"}

        formats = []
        for choice in choices.split(","):
            choice = choice.strip()
            if choice in format_map:
                formats.append(format_map[choice])

        self.config["output_formats"] = formats if formats else ["markdown"]

        # 圖表設定
        if self._ask_yes_no("\n是否生成圖表？"):
            print("\n選擇要生成的圖表（可多選，用逗號分隔）：")
            print("  1. AGP 動態血糖曲線")
            print("  2. 每日疊加圖")
            print("  3. TIR 圓餅圖")
            print("  4. 每小時模式圖")
            print("  5. 變異性分析圖")

            choices = input("請選擇 (預設: 1,2,3): ").strip() or "1,2,3"
            chart_map = {
                "1": "agp",
                "2": "daily_overlay",
                "3": "tir_pie",
                "4": "hourly_pattern",
                "5": "variability"
            }

            charts = []
            for choice in choices.split(","):
                choice = choice.strip()
                if choice in chart_map:
                    charts.append(chart_map[choice])

            self.config["charts"] = charts if charts else ["agp", "tir_pie"]

        # 輸出目錄
        output_dir = input("\n輸出目錄 (預設: ./output): ").strip()
        self.config["output_dir"] = output_dir or "./output"

    def _setup_advanced(self):
        """進階設定"""
        print("\n【進階設定】")

        # 數據處理
        print("\n數據處理設定：")

        coverage = input("最小數據覆蓋率 (%, 預設: 70): ").strip()
        self.config["min_coverage"] = int(coverage) if coverage.isdigit() else 70

        if self._ask_yes_no("\n啟用異常值檢測？"):
            self.config["outlier_detection"] = True

            print("\n異常值檢測方法：")
            print("  1. IQR (四分位距)")
            print("  2. Z-Score (標準分數)")

            choice = input("請選擇 (預設: 1): ").strip() or "1"
            self.config["outlier_method"] = "iqr" if choice == "1" else "zscore"

        # 批次處理
        if self._ask_yes_no("\n啟用批次處理？"):
            self.config["batch_processing"] = True

            parallel = input("最大並行數 (預設: 4): ").strip()
            self.config["max_parallel"] = int(parallel) if parallel.isdigit() else 4

        # 安全設定
        print("\n安全設定：")

        if self._ask_yes_no("是否匿名化數據？"):
            self.config["anonymize_data"] = True

        if self._ask_yes_no("是否移除個人識別資訊？"):
            self.config["remove_pii"] = True

        # 開發設定
        if self._ask_yes_no("\n啟用除錯模式？"):
            self.config["debug"] = True
            self.config["verbose"] = True

    def _ask_yes_no(self, question: str) -> bool:
        """詢問是/否問題"""
        while True:
            answer = input(f"{question} (y/n, 預設: y): ").strip().lower()
            if answer in ["", "y", "yes", "是"]:
                return True
            elif answer in ["n", "no", "否"]:
                return False
            else:
                print("請輸入 y 或 n")

    def _save_config(self):
        """儲存設定"""
        # 建立完整的設定結構
        full_config = {
            "defaults": {
                "language": self.config.get("language", "zh-TW"),
                "analysis_period": self.config.get("analysis_days", 14),
                "target_range": {
                    "low": self.config.get("target_low", 70),
                    "high": self.config.get("target_high", 180)
                }
            },
            "ai_models": {
                "preferred": self.config.get("default_model", "gpt-4o"),
                "api_key_source": self.config.get("api_key_source", "environment")
            },
            "output": {
                "formats": self.config.get("output_formats", ["markdown"]),
                "charts": self.config.get("charts", ["agp", "tir_pie"]),
                "output_dir": self.config.get("output_dir", "./output")
            },
            "data_processing": {
                "min_coverage": self.config.get("min_coverage", 70),
                "outlier_detection": {
                    "enabled": self.config.get("outlier_detection", False),
                    "method": self.config.get("outlier_method", "iqr")
                }
            },
            "security": {
                "anonymize_data": self.config.get("anonymize_data", False),
                "remove_pii": self.config.get("remove_pii", False)
            },
            "development": {
                "debug": self.config.get("debug", False),
                "verbose": self.config.get("verbose", False)
            }
        }

        # 如果有 API Key，單獨儲存
        if "openai_api_key" in self.config:
            full_config["ai_models"]["api_key"] = self.config["openai_api_key"]

        # 如果選擇了預設族群
        if "default_population" in self.config:
            full_config["defaults"]["population"] = self.config["default_population"]

        # 批次處理設定
        if self.config.get("batch_processing"):
            full_config["batch_processing"] = {
                "enabled": True,
                "max_parallel": self.config.get("max_parallel", 4)
            }

        # 儲存為 YAML
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(full_config, f, default_flow_style=False,
                         allow_unicode=True, sort_keys=False)

            # 同時儲存為 JSON（備份）
            json_path = str(config_path).replace('.yaml', '.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"\n❌ 儲存設定失敗：{e}")
            return

    def load_existing_config(self) -> bool:
        """載入現有設定"""
        if os.path.exists(self.config_file):
            print(f"\n發現現有設定檔案：{self.config_file}")

            if self._ask_yes_no("是否要載入現有設定並修改？"):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        existing = yaml.safe_load(f)

                    # 將現有設定轉換為簡單格式
                    if existing.get("defaults"):
                        self.config["language"] = existing["defaults"].get("language", "zh-TW")
                        self.config["analysis_days"] = existing["defaults"].get("analysis_period", 14)

                        if "target_range" in existing["defaults"]:
                            self.config["target_low"] = existing["defaults"]["target_range"].get("low", 70)
                            self.config["target_high"] = existing["defaults"]["target_range"].get("high", 180)

                    if existing.get("ai_models"):
                        self.config["default_model"] = existing["ai_models"].get("preferred", "gpt-4o")
                        self.config["api_key_source"] = existing["ai_models"].get("api_key_source", "environment")

                    print("✓ 已載入現有設定")
                    return True

                except Exception as e:
                    print(f"❌ 載入設定失敗：{e}")

        return False


def main():
    """主函數"""
    print("歡迎使用 CGM 分析技能設定精靈！")

    wizard = CGMSetupWizard()

    # 檢查現有設定
    wizard.load_existing_config()

    # 執行設定精靈
    wizard.run()

    print("\n您現在可以開始使用 CGM 分析技能了！")
    print("執行範例：python analyze_cgm.py your_data.csv")

    return 0


if __name__ == "__main__":
    sys.exit(main())