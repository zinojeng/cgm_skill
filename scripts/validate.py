#!/usr/bin/env python3
"""
CGM 數據驗證工具
檢查輸入檔案格式並提供修復建議
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

class CGMValidator:
    """CGM 數據驗證器"""

    def __init__(self, file_path: str):
        """初始化驗證器"""
        self.file_path = file_path
        self.validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "statistics": {}
        }

    def validate(self) -> Dict:
        """執行完整驗證"""
        print(f"開始驗證檔案：{self.file_path}")

        # 檢查檔案存在
        if not self._check_file_exists():
            return self.validation_results

        # 載入數據
        df = self._load_data()
        if df is None:
            return self.validation_results

        # 執行各項驗證
        self._check_required_columns(df)
        self._check_data_types(df)
        self._check_date_time_format(df)
        self._check_glucose_values(df)
        self._check_data_completeness(df)
        self._check_data_continuity(df)
        self._generate_statistics(df)
        self._provide_suggestions()

        return self.validation_results

    def _check_file_exists(self) -> bool:
        """檢查檔案是否存在"""
        if not os.path.exists(self.file_path):
            self.validation_results["is_valid"] = False
            self.validation_results["errors"].append(f"檔案不存在：{self.file_path}")
            return False

        # 檢查檔案大小
        file_size = os.path.getsize(self.file_path)
        if file_size == 0:
            self.validation_results["is_valid"] = False
            self.validation_results["errors"].append("檔案為空")
            return False

        if file_size > 100 * 1024 * 1024:  # 100MB
            self.validation_results["warnings"].append(f"檔案過大 ({file_size/1024/1024:.1f}MB)，可能影響處理速度")

        return True

    def _load_data(self) -> Optional[pd.DataFrame]:
        """載入數據"""
        try:
            # 嘗試不同的編碼
            encodings = ['utf-8', 'latin1', 'cp1252', 'big5']
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(self.file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                self.validation_results["is_valid"] = False
                self.validation_results["errors"].append("無法讀取檔案，請檢查檔案編碼")
                return None

            if len(df) == 0:
                self.validation_results["is_valid"] = False
                self.validation_results["errors"].append("檔案不包含任何數據")
                return None

            return df

        except Exception as e:
            self.validation_results["is_valid"] = False
            self.validation_results["errors"].append(f"讀取檔案錯誤：{str(e)}")
            return None

    def _check_required_columns(self, df: pd.DataFrame):
        """檢查必要欄位"""
        required_columns = {
            'Date': ['date', 'Date', 'DATE', '日期', 'Timestamp'],
            'Time': ['time', 'Time', 'TIME', '時間', 'Timestamp'],
            'Glucose': ['Sensor Glucose (mg/dL)', 'Glucose', 'glucose', 'Blood Glucose',
                       'BG', '血糖', 'Glucose Value (mg/dL)', 'Historic Glucose mg/dL']
        }

        found_columns = {}
        missing_columns = []

        for key, possible_names in required_columns.items():
            found = False
            for name in possible_names:
                if name in df.columns:
                    found_columns[key] = name
                    found = True
                    break

            if not found:
                missing_columns.append(key)

        if missing_columns:
            self.validation_results["is_valid"] = False
            self.validation_results["errors"].append(f"缺少必要欄位：{', '.join(missing_columns)}")
            self.validation_results["suggestions"].append(
                f"請確保檔案包含以下欄位之一：\n" +
                "\n".join([f"  {k}: {', '.join(v)}" for k, v in required_columns.items()])
            )
        else:
            self.validation_results["statistics"]["columns_found"] = found_columns

    def _check_data_types(self, df: pd.DataFrame):
        """檢查數據類型"""
        if 'Sensor Glucose (mg/dL)' in df.columns:
            glucose_col = 'Sensor Glucose (mg/dL)'
        elif 'Glucose' in df.columns:
            glucose_col = 'Glucose'
        else:
            return

        # 檢查血糖值是否為數字
        non_numeric = df[~df[glucose_col].apply(lambda x: str(x).replace('.', '').replace('-', '').isdigit())]
        if len(non_numeric) > 0:
            self.validation_results["warnings"].append(
                f"發現 {len(non_numeric)} 筆非數字血糖值，將被忽略"
            )

    def _check_date_time_format(self, df: pd.DataFrame):
        """檢查日期時間格式"""
        date_col = None
        time_col = None

        # 找出日期和時間欄位
        for col in df.columns:
            if 'date' in col.lower():
                date_col = col
            if 'time' in col.lower():
                time_col = col

        if date_col and time_col:
            # 嘗試解析日期時間
            try:
                df['Timestamp'] = pd.to_datetime(df[date_col] + ' ' + df[time_col])

                # 檢查時間順序
                if not df['Timestamp'].is_monotonic_increasing:
                    self.validation_results["warnings"].append("數據時間順序不連續，將自動排序")

            except:
                self.validation_results["errors"].append("無法解析日期時間格式")
                self.validation_results["suggestions"].append(
                    "請確保日期格式為 YYYY-MM-DD，時間格式為 HH:MM:SS"
                )

    def _check_glucose_values(self, df: pd.DataFrame):
        """檢查血糖值範圍"""
        glucose_col = None
        for col in df.columns:
            if 'glucose' in col.lower() or 'bg' in col.lower():
                glucose_col = col
                break

        if not glucose_col:
            return

        # 轉換為數值
        df[glucose_col] = pd.to_numeric(df[glucose_col], errors='coerce')

        # 檢查範圍
        valid_range = (20, 600)  # mg/dL
        out_of_range = df[(df[glucose_col] < valid_range[0]) | (df[glucose_col] > valid_range[1])]

        if len(out_of_range) > 0:
            self.validation_results["warnings"].append(
                f"發現 {len(out_of_range)} 筆超出正常範圍 ({valid_range[0]}-{valid_range[1]} mg/dL) 的血糖值"
            )

        # 統計
        valid_glucose = df[glucose_col].dropna()
        if len(valid_glucose) > 0:
            self.validation_results["statistics"]["glucose_stats"] = {
                "mean": float(valid_glucose.mean()),
                "std": float(valid_glucose.std()),
                "min": float(valid_glucose.min()),
                "max": float(valid_glucose.max()),
                "count": len(valid_glucose)
            }

    def _check_data_completeness(self, df: pd.DataFrame):
        """檢查數據完整性"""
        total_rows = len(df)

        # 檢查缺失值
        missing_stats = {}
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_percentage = (missing_count / total_rows) * 100
                missing_stats[col] = {
                    "count": int(missing_count),
                    "percentage": float(missing_percentage)
                }

                if missing_percentage > 30:
                    self.validation_results["warnings"].append(
                        f"欄位 '{col}' 有 {missing_percentage:.1f}% 缺失值"
                    )

        if missing_stats:
            self.validation_results["statistics"]["missing_data"] = missing_stats

    def _check_data_continuity(self, df: pd.DataFrame):
        """檢查數據連續性"""
        try:
            # 創建時間戳
            date_col = time_col = None
            for col in df.columns:
                if 'date' in col.lower():
                    date_col = col
                if 'time' in col.lower():
                    time_col = col

            if date_col and time_col:
                df['Timestamp'] = pd.to_datetime(df[date_col] + ' ' + df[time_col])
                df = df.sort_values('Timestamp')

                # 計算時間間隔
                time_diff = df['Timestamp'].diff()

                # 預期間隔（通常 CGM 每 5 分鐘一筆）
                expected_interval = timedelta(minutes=5)

                # 找出大間隔
                large_gaps = time_diff[time_diff > timedelta(minutes=30)]

                if len(large_gaps) > 0:
                    self.validation_results["warnings"].append(
                        f"發現 {len(large_gaps)} 個超過 30 分鐘的數據間隔"
                    )

                # 計算覆蓋率
                if len(df) > 1:
                    total_duration = df['Timestamp'].iloc[-1] - df['Timestamp'].iloc[0]
                    expected_readings = total_duration / expected_interval
                    coverage = (len(df) / expected_readings) * 100

                    self.validation_results["statistics"]["coverage"] = {
                        "percentage": float(min(coverage, 100)),
                        "duration_days": float(total_duration.days),
                        "total_readings": len(df)
                    }

                    if coverage < 70:
                        self.validation_results["warnings"].append(
                            f"數據覆蓋率偏低 ({coverage:.1f}%)，可能影響分析準確性"
                        )

        except Exception as e:
            self.validation_results["warnings"].append(f"無法檢查數據連續性：{str(e)}")

    def _generate_statistics(self, df: pd.DataFrame):
        """生成統計資訊"""
        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": list(df.columns)
        }

        self.validation_results["statistics"]["basic_info"] = stats

    def _provide_suggestions(self):
        """提供改善建議"""
        if not self.validation_results["is_valid"]:
            self.validation_results["suggestions"].append(
                "請修正以上錯誤後重新執行驗證"
            )

        if self.validation_results["warnings"]:
            self.validation_results["suggestions"].append(
                "建議處理警告項目以獲得最佳分析結果"
            )

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """生成驗證報告"""
        report = []
        report.append("=" * 60)
        report.append("CGM 數據驗證報告")
        report.append(f"檔案：{self.file_path}")
        report.append(f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)

        # 驗證結果
        if self.validation_results["is_valid"]:
            report.append("\n✅ 檔案格式驗證通過")
        else:
            report.append("\n❌ 檔案格式驗證失敗")

        # 錯誤
        if self.validation_results["errors"]:
            report.append("\n【錯誤】")
            for error in self.validation_results["errors"]:
                report.append(f"  ❌ {error}")

        # 警告
        if self.validation_results["warnings"]:
            report.append("\n【警告】")
            for warning in self.validation_results["warnings"]:
                report.append(f"  ⚠️  {warning}")

        # 統計
        if self.validation_results["statistics"]:
            report.append("\n【統計資訊】")

            if "basic_info" in self.validation_results["statistics"]:
                info = self.validation_results["statistics"]["basic_info"]
                report.append(f"  - 總筆數：{info['total_rows']}")
                report.append(f"  - 欄位數：{info['total_columns']}")

            if "glucose_stats" in self.validation_results["statistics"]:
                stats = self.validation_results["statistics"]["glucose_stats"]
                report.append(f"  - 平均血糖：{stats['mean']:.1f} mg/dL")
                report.append(f"  - 標準差：{stats['std']:.1f}")
                report.append(f"  - 範圍：{stats['min']:.0f}-{stats['max']:.0f} mg/dL")

            if "coverage" in self.validation_results["statistics"]:
                cov = self.validation_results["statistics"]["coverage"]
                report.append(f"  - 數據覆蓋率：{cov['percentage']:.1f}%")
                report.append(f"  - 總天數：{cov['duration_days']:.1f} 天")

        # 建議
        if self.validation_results["suggestions"]:
            report.append("\n【建議】")
            for suggestion in self.validation_results["suggestions"]:
                report.append(f"  💡 {suggestion}")

        report_text = "\n".join(report)

        # 儲存報告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)

            # 同時儲存 JSON 格式
            json_file = output_file.replace('.txt', '.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.validation_results, f, indent=2, ensure_ascii=False)

        return report_text


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方法：python validate.py <cgm_file.csv> [output_report.txt]")
        print("範例：python validate.py data.csv validation_report.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # 執行驗證
    validator = CGMValidator(input_file)
    results = validator.validate()

    # 生成報告
    report = validator.generate_report(output_file)
    print(report)

    # 返回狀態碼
    return 0 if results["is_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())