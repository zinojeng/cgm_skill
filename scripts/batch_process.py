#!/usr/bin/env python3
"""
CGM 批次處理工具
處理多個 CGM 檔案並生成比較報告
"""

import os
import sys
import glob
import json
import yaml
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from tqdm import tqdm

# 匯入其他模組
sys.path.append(os.path.dirname(__file__))
from analyze_cgm import CGMAnalyzer
from validate import CGMValidator


class BatchProcessor:
    """批次處理器"""

    def __init__(self, config_file: Optional[str] = None):
        """初始化批次處理器"""
        self.config = self._load_config(config_file)
        self.results = []
        self.errors = []

    def _load_config(self, config_file: Optional[str]) -> Dict:
        """載入配置"""
        default_config = {
            "max_parallel": 4,
            "batch_size": 10,
            "output_dir": "./batch_output",
            "validate_first": True,
            "generate_comparison": True
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    if config_file.endswith('.yaml'):
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)

                # 合併配置
                if "batch_processing" in user_config:
                    default_config.update(user_config["batch_processing"])

            except Exception as e:
                print(f"⚠️ 無法載入配置檔案：{e}")

        return default_config

    def process_files(self, file_pattern: str) -> Dict:
        """處理多個檔案"""
        # 尋找匹配的檔案
        files = glob.glob(file_pattern)

        if not files:
            print(f"❌ 找不到匹配的檔案：{file_pattern}")
            return {"status": "error", "message": "No files found"}

        print(f"找到 {len(files)} 個檔案待處理")

        # 創建輸出目錄
        os.makedirs(self.config["output_dir"], exist_ok=True)

        # 驗證檔案（如果啟用）
        if self.config["validate_first"]:
            print("\n📋 驗證檔案...")
            valid_files = self._validate_files(files)

            if not valid_files:
                print("❌ 沒有有效的檔案可處理")
                return {"status": "error", "message": "No valid files"}

            files = valid_files

        # 批次處理
        print(f"\n🔄 開始批次處理（最大並行：{self.config['max_parallel']}）...")

        with ProcessPoolExecutor(max_workers=self.config["max_parallel"]) as executor:
            # 提交任務
            futures = {}
            for file_path in files:
                future = executor.submit(self._process_single_file, file_path)
                futures[future] = file_path

            # 處理結果
            with tqdm(total=len(files), desc="處理進度") as pbar:
                for future in as_completed(futures):
                    file_path = futures[future]

                    try:
                        result = future.result(timeout=300)  # 5 分鐘超時
                        self.results.append(result)
                    except Exception as e:
                        error = {
                            "file": file_path,
                            "error": str(e)
                        }
                        self.errors.append(error)
                        print(f"\n❌ 處理失敗：{file_path} - {e}")

                    pbar.update(1)

        # 生成比較報告
        if self.config["generate_comparison"] and len(self.results) > 1:
            print("\n📊 生成比較報告...")
            self._generate_comparison_report()

        # 生成總結報告
        summary = self._generate_summary()

        print("\n✅ 批次處理完成！")
        print(f"成功：{len(self.results)} 個檔案")
        print(f"失敗：{len(self.errors)} 個檔案")

        return summary

    def _validate_files(self, files: List[str]) -> List[str]:
        """驗證檔案"""
        valid_files = []

        for file_path in files:
            validator = CGMValidator(file_path)
            result = validator.validate()

            if result["is_valid"]:
                valid_files.append(file_path)
                print(f"  ✓ {os.path.basename(file_path)} - 驗證通過")
            else:
                print(f"  ✗ {os.path.basename(file_path)} - 驗證失敗")
                for error in result["errors"]:
                    print(f"    - {error}")

        return valid_files

    def _process_single_file(self, file_path: str) -> Dict:
        """處理單個檔案"""
        try:
            # 創建分析器
            analyzer = CGMAnalyzer(file_path)

            # 計算指標
            metrics = analyzer.calculate_metrics()

            # 生成個人報告目錄
            file_name = Path(file_path).stem
            output_dir = os.path.join(self.config["output_dir"], file_name)
            os.makedirs(output_dir, exist_ok=True)

            # 生成報告
            analyzer.generate_report(output_dir)

            # 返回結果
            return {
                "file": file_path,
                "name": file_name,
                "status": "success",
                "metrics": metrics,
                "output_dir": output_dir
            }

        except Exception as e:
            return {
                "file": file_path,
                "status": "error",
                "error": str(e)
            }

    def _generate_comparison_report(self):
        """生成比較報告"""
        comparison_data = []

        # 收集所有成功處理的結果
        for result in self.results:
            if result["status"] == "success":
                row = {
                    "File": result["name"],
                    "Mean Glucose": result["metrics"].get("Mean Glucose", np.nan),
                    "TIR (%)": result["metrics"].get("TIR", np.nan),
                    "TAR (%)": result["metrics"].get("TAR", np.nan),
                    "TBR (%)": result["metrics"].get("TBR", np.nan),
                    "CV (%)": result["metrics"].get("CV", np.nan),
                    "GMI": result["metrics"].get("GMI", np.nan),
                    "GRI": result["metrics"].get("GRI", np.nan)
                }
                comparison_data.append(row)

        if not comparison_data:
            return

        # 創建 DataFrame
        df = pd.DataFrame(comparison_data)

        # 計算統計
        summary_stats = df.describe()

        # 生成 Markdown 報告
        report_file = os.path.join(self.config["output_dir"], "comparison_report.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# CGM 批次分析比較報告\n\n")
            f.write(f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"分析檔案數：{len(comparison_data)}\n\n")

            # 詳細數據表
            f.write("## 詳細數據\n\n")
            f.write(df.to_markdown(index=False, floatfmt=".1f"))
            f.write("\n\n")

            # 統計摘要
            f.write("## 統計摘要\n\n")
            f.write(summary_stats.to_markdown(floatfmt=".1f"))
            f.write("\n\n")

            # 最佳和最差表現
            f.write("## 表現分析\n\n")

            if "TIR (%)" in df.columns:
                best_tir = df.nlargest(1, "TIR (%)")
                worst_tir = df.nsmallest(1, "TIR (%)")

                f.write(f"**最佳 TIR：** {best_tir['File'].values[0]} ")
                f.write(f"({best_tir['TIR (%)'].values[0]:.1f}%)\n\n")

                f.write(f"**最差 TIR：** {worst_tir['File'].values[0]} ")
                f.write(f"({worst_tir['TIR (%)'].values[0]:.1f}%)\n\n")

            if "CV (%)" in df.columns:
                best_cv = df.nsmallest(1, "CV (%)")
                worst_cv = df.nlargest(1, "CV (%)")

                f.write(f"**最穩定（最低 CV）：** {best_cv['File'].values[0]} ")
                f.write(f"({best_cv['CV (%)'].values[0]:.1f}%)\n\n")

                f.write(f"**最不穩定（最高 CV）：** {worst_cv['File'].values[0]} ")
                f.write(f"({worst_cv['CV (%)'].values[0]:.1f}%)\n\n")

            # 建議
            f.write("## 建議\n\n")

            # 找出需要改善的檔案
            need_improvement = []

            for _, row in df.iterrows():
                issues = []

                if row.get("TIR (%)", 100) < 70:
                    issues.append("TIR 低於目標")
                if row.get("TBR (%)", 0) > 4:
                    issues.append("低血糖時間過多")
                if row.get("CV (%)", 0) > 36:
                    issues.append("血糖變異性過高")

                if issues:
                    need_improvement.append({
                        "file": row["File"],
                        "issues": issues
                    })

            if need_improvement:
                f.write("### 需要關注的檔案：\n\n")
                for item in need_improvement:
                    f.write(f"- **{item['file']}**\n")
                    for issue in item["issues"]:
                        f.write(f"  - {issue}\n")
                    f.write("\n")

        # 儲存 CSV 格式
        csv_file = os.path.join(self.config["output_dir"], "comparison_data.csv")
        df.to_csv(csv_file, index=False, encoding='utf-8')

        print(f"  ✓ 比較報告已生成：{report_file}")

    def _generate_summary(self) -> Dict:
        """生成總結"""
        summary = {
            "total_files": len(self.results) + len(self.errors),
            "successful": len(self.results),
            "failed": len(self.errors),
            "output_directory": self.config["output_dir"],
            "timestamp": datetime.now().isoformat()
        }

        # 計算整體統計
        if self.results:
            all_metrics = []
            for result in self.results:
                if result["status"] == "success":
                    all_metrics.append(result["metrics"])

            if all_metrics:
                # 計算平均值
                avg_metrics = {}
                keys = ["Mean Glucose", "TIR", "TAR", "TBR", "CV", "GMI", "GRI"]

                for key in keys:
                    values = [m.get(key, np.nan) for m in all_metrics]
                    values = [v for v in values if not np.isnan(v)]
                    if values:
                        avg_metrics[key] = float(np.mean(values))

                summary["average_metrics"] = avg_metrics

        # 儲存總結
        summary_file = os.path.join(self.config["output_dir"], "batch_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        return summary


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python batch_process.py <file_pattern> [config.yaml]")
        print("\n範例：")
        print("  python batch_process.py '*.csv'")
        print("  python batch_process.py 'data/*.csv' config.yaml")
        print("  python batch_process.py '/path/to/cgm_*.csv'")
        sys.exit(1)

    file_pattern = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 60)
    print("CGM 批次處理工具")
    print("=" * 60)

    # 創建處理器
    processor = BatchProcessor(config_file)

    # 執行批次處理
    result = processor.process_files(file_pattern)

    # 顯示總結
    if result.get("average_metrics"):
        print("\n📊 整體平均指標：")
        for key, value in result["average_metrics"].items():
            print(f"  - {key}: {value:.1f}")

    print(f"\n所有報告已儲存至：{result['output_directory']}")

    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())