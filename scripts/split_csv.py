#!/usr/bin/env python3
"""
CGM CSV 檔案分割工具
將原始 CGM 數據檔案分割為血糖數據和事件數據兩個檔案
"""

import pandas as pd
import sys
import os
from pathlib import Path
from typing import Tuple, Optional

def split_csv(input_file: str, output_dir: str = "./output") -> Tuple[Optional[str], Optional[str]]:
    """
    分割 CGM CSV 檔案為血糖數據和事件數據

    Args:
        input_file: 輸入的 CSV 檔案路徑
        output_dir: 輸出目錄路徑

    Returns:
        Tuple[event_file_path, glucose_file_path]
    """
    try:
        # 創建輸出目錄
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 讀取原始數據
        df = pd.read_csv(input_file)
        print(f"成功讀取檔案：{input_file}")
        print(f"總共 {len(df)} 筆記錄")

        # 定義血糖數據欄位
        glucose_columns = ['Date', 'Time', 'Sensor Glucose (mg/dL)']

        # 定義事件數據欄位（胰島素注射、用餐等）
        event_columns = ['Date', 'Time', 'Event Type', 'Event Subtype',
                        'Insulin Value (u)', 'Carb Value (g)', 'Duration (hh:mm:ss)']

        # 分離血糖數據
        glucose_df = pd.DataFrame()
        for col in glucose_columns:
            if col in df.columns:
                glucose_df[col] = df[col]

        # 移除空白記錄
        glucose_df = glucose_df.dropna(subset=['Sensor Glucose (mg/dL)'])

        # 分離事件數據
        event_df = pd.DataFrame()
        event_cols_present = [col for col in event_columns if col in df.columns]
        if event_cols_present:
            event_df = df[event_cols_present].copy()
            # 只保留有事件的記錄
            event_df = event_df.dropna(subset=['Event Type'])

        # 生成輸出檔案名稱
        base_name = Path(input_file).stem
        glucose_file = os.path.join(output_dir, f"{base_name}_glucose.csv")
        event_file = os.path.join(output_dir, f"{base_name}_events.csv")

        # 儲存檔案
        if not glucose_df.empty:
            glucose_df.to_csv(glucose_file, index=False)
            print(f"✓ 血糖數據已儲存至：{glucose_file} ({len(glucose_df)} 筆記錄)")
        else:
            print("⚠ 未找到血糖數據")
            glucose_file = None

        if not event_df.empty:
            event_df.to_csv(event_file, index=False)
            print(f"✓ 事件數據已儲存至：{event_file} ({len(event_df)} 筆記錄)")
        else:
            print("⚠ 未找到事件數據")
            event_file = None

        return event_file, glucose_file

    except Exception as e:
        print(f"錯誤：處理檔案時發生錯誤 - {str(e)}")
        return None, None

def validate_glucose_data(file_path: str) -> bool:
    """
    驗證血糖數據檔案的完整性

    Args:
        file_path: 血糖數據檔案路徑

    Returns:
        bool: 數據是否有效
    """
    try:
        df = pd.read_csv(file_path)

        # 檢查必要欄位
        required_cols = ['Date', 'Time', 'Sensor Glucose (mg/dL)']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"⚠ 缺少必要欄位：{missing_cols}")
            return False

        # 檢查數據完整性
        df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df = df.sort_values('Timestamp')

        # 計算數據覆蓋率
        time_diff = df['Timestamp'].diff()
        expected_interval = pd.Timedelta(minutes=5)  # CGM 通常每5分鐘一筆

        large_gaps = time_diff[time_diff > pd.Timedelta(minutes=30)]
        if len(large_gaps) > 0:
            print(f"⚠ 發現 {len(large_gaps)} 個超過30分鐘的數據間隔")

        # 計算數據可用率
        total_duration = df['Timestamp'].iloc[-1] - df['Timestamp'].iloc[0]
        expected_readings = total_duration / expected_interval
        data_availability = len(df) / expected_readings * 100

        print(f"📊 數據統計：")
        print(f"  - 時間範圍：{df['Timestamp'].iloc[0]} 至 {df['Timestamp'].iloc[-1]}")
        print(f"  - 總天數：{total_duration.days} 天")
        print(f"  - 數據可用率：{data_availability:.1f}%")
        print(f"  - 平均血糖：{df['Sensor Glucose (mg/dL)'].mean():.1f} mg/dL")

        return data_availability > 70  # 70%以上視為有效數據

    except Exception as e:
        print(f"驗證錯誤：{str(e)}")
        return False

def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方法：python split_csv.py <input_file.csv> [output_directory]")
        print("範例：python split_csv.py cgm_data.csv ./output")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./output"

    if not os.path.exists(input_file):
        print(f"錯誤：找不到檔案 {input_file}")
        sys.exit(1)

    print("=" * 50)
    print("CGM CSV 檔案分割工具")
    print("=" * 50)

    # 執行分割
    event_file, glucose_file = split_csv(input_file, output_dir)

    if glucose_file:
        print("\n驗證血糖數據...")
        if validate_glucose_data(glucose_file):
            print("✅ 血糖數據驗證通過")
        else:
            print("⚠️ 血糖數據可能不完整，請檢查")

    print("\n分割完成！")
    return 0

if __name__ == "__main__":
    main()