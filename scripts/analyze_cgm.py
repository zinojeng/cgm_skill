#!/usr/bin/env python3
"""
CGM 數據分析工具
計算關鍵血糖指標並生成視覺化報告
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from datetime import datetime, timedelta
import sys
import os
from typing import Dict, Tuple, Optional
import json

# 設置中文顯示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CGMAnalyzer:
    """CGM 數據分析器"""

    def __init__(self, glucose_file: str, event_file: Optional[str] = None):
        """
        初始化分析器

        Args:
            glucose_file: 血糖數據檔案路徑
            event_file: 事件數據檔案路徑（選擇性）
        """
        self.glucose_df = self._load_glucose_data(glucose_file)
        self.event_df = self._load_event_data(event_file) if event_file else None
        self.metrics = {}

    def _load_glucose_data(self, file_path: str) -> pd.DataFrame:
        """載入血糖數據"""
        df = pd.read_csv(file_path)
        df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df['Glucose'] = pd.to_numeric(df['Sensor Glucose (mg/dL)'], errors='coerce')
        df = df.dropna(subset=['Glucose'])
        df = df.sort_values('Timestamp')
        print(f"✓ 載入 {len(df)} 筆血糖數據")
        return df

    def _load_event_data(self, file_path: str) -> pd.DataFrame:
        """載入事件數據"""
        df = pd.read_csv(file_path)
        df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        print(f"✓ 載入 {len(df)} 筆事件數據")
        return df

    def calculate_metrics(self, target_range: Tuple[int, int] = (70, 180)) -> Dict:
        """
        計算所有血糖指標

        Args:
            target_range: 目標血糖範圍 (mg/dL)

        Returns:
            包含所有指標的字典
        """
        low_limit, high_limit = target_range
        glucose_values = self.glucose_df['Glucose'].values

        # 基本統計
        self.metrics['Mean Glucose'] = np.mean(glucose_values)
        self.metrics['Median Glucose'] = np.median(glucose_values)
        self.metrics['SD'] = np.std(glucose_values)
        self.metrics['CV'] = (self.metrics['SD'] / self.metrics['Mean Glucose']) * 100

        # Time in Range 計算
        total_readings = len(glucose_values)
        self.metrics['TIR'] = (np.sum((glucose_values >= low_limit) &
                                      (glucose_values <= high_limit)) / total_readings) * 100
        self.metrics['TAR'] = (np.sum(glucose_values > high_limit) / total_readings) * 100
        self.metrics['TBR'] = (np.sum(glucose_values < low_limit) / total_readings) * 100

        # 詳細範圍
        self.metrics['Very Low (<54)'] = (np.sum(glucose_values < 54) / total_readings) * 100
        self.metrics['Low (54-69)'] = (np.sum((glucose_values >= 54) &
                                              (glucose_values < 70)) / total_readings) * 100
        self.metrics['High (181-250)'] = (np.sum((glucose_values > 180) &
                                                 (glucose_values <= 250)) / total_readings) * 100
        self.metrics['Very High (>250)'] = (np.sum(glucose_values > 250) / total_readings) * 100

        # GMI (Glucose Management Indicator)
        self.metrics['GMI'] = (3.31 + 0.02392 * self.metrics['Mean Glucose'])

        # GRI (Glycemic Risk Index)
        self.metrics['GRI'] = self._calculate_gri()

        # MAGE (Mean Amplitude of Glycemic Excursions)
        self.metrics['MAGE'] = self._calculate_mage()

        # 每日統計
        self._calculate_daily_patterns()

        return self.metrics

    def _calculate_gri(self) -> float:
        """計算 GRI 風險指數"""
        v_low = self.metrics.get('Very Low (<54)', 0)
        low = self.metrics.get('Low (54-69)', 0)
        high = self.metrics.get('High (181-250)', 0)
        v_high = self.metrics.get('Very High (>250)', 0)

        gri = (3.0 * v_low) + (2.4 * low) + (1.6 * v_high) + (0.8 * high)
        return gri

    def _calculate_mage(self) -> float:
        """計算 MAGE（平均血糖波動幅度）"""
        glucose = self.glucose_df['Glucose'].values
        sd = np.std(glucose)

        # 找出所有超過1個標準差的波動
        excursions = []
        direction = 0  # 0: 未定, 1: 上升, -1: 下降

        for i in range(1, len(glucose)):
            diff = glucose[i] - glucose[i-1]

            if abs(diff) > sd:
                if direction == 0:
                    direction = 1 if diff > 0 else -1
                    excursion_start = i-1
                elif (direction == 1 and diff < 0) or (direction == -1 and diff > 0):
                    # 方向改變
                    excursion_amplitude = abs(glucose[i-1] - glucose[excursion_start])
                    if excursion_amplitude > sd:
                        excursions.append(excursion_amplitude)
                    direction = 1 if diff > 0 else -1
                    excursion_start = i-1

        return np.mean(excursions) if excursions else 0

    def _calculate_daily_patterns(self):
        """計算每日血糖模式"""
        df = self.glucose_df.copy()
        df['Hour'] = df['Timestamp'].dt.hour
        df['Date'] = df['Timestamp'].dt.date

        # 每小時平均血糖
        hourly_mean = df.groupby('Hour')['Glucose'].mean()
        self.metrics['Hourly Pattern'] = hourly_mean.to_dict()

        # 每日統計
        daily_stats = df.groupby('Date')['Glucose'].agg(['mean', 'std', 'min', 'max'])
        self.metrics['Daily Stats'] = {
            'Mean of Daily Means': daily_stats['mean'].mean(),
            'Mean of Daily SDs': daily_stats['std'].mean(),
            'Days Analyzed': len(daily_stats)
        }

    def create_agp(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        創建 AGP (Ambulatory Glucose Profile) 圖表

        Args:
            save_path: 儲存路徑

        Returns:
            matplotlib figure
        """
        df = self.glucose_df.copy()
        df['Hour'] = df['Timestamp'].dt.hour + df['Timestamp'].dt.minute / 60

        # 計算百分位數
        percentiles = [10, 25, 50, 75, 90]
        hourly_percentiles = {}

        for hour in range(24):
            hour_data = df[(df['Hour'] >= hour) & (df['Hour'] < hour + 1)]['Glucose']
            if len(hour_data) > 0:
                hourly_percentiles[hour] = np.percentile(hour_data, percentiles)

        # 創建圖表
        fig, ax = plt.subplots(figsize=(12, 6))

        hours = list(hourly_percentiles.keys())
        if hours:
            # 繪製百分位數帶
            p10 = [hourly_percentiles[h][0] for h in hours]
            p25 = [hourly_percentiles[h][1] for h in hours]
            p50 = [hourly_percentiles[h][2] for h in hours]
            p75 = [hourly_percentiles[h][3] for h in hours]
            p90 = [hourly_percentiles[h][4] for h in hours]

            ax.fill_between(hours, p10, p90, alpha=0.2, color='blue', label='10-90%')
            ax.fill_between(hours, p25, p75, alpha=0.3, color='blue', label='25-75%')
            ax.plot(hours, p50, 'b-', linewidth=2, label='Median')

            # 添加目標範圍
            ax.axhspan(70, 180, alpha=0.1, color='green', label='Target Range')
            ax.axhline(y=70, color='green', linestyle='--', alpha=0.5)
            ax.axhline(y=180, color='green', linestyle='--', alpha=0.5)

        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Glucose (mg/dL)')
        ax.set_title('Ambulatory Glucose Profile (AGP)')
        ax.set_xlim(0, 23)
        ax.set_ylim(40, 400)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ AGP 圖表已儲存至：{save_path}")

        return fig

    def create_daily_overlay(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        創建每日血糖疊加圖

        Args:
            save_path: 儲存路徑

        Returns:
            matplotlib figure
        """
        df = self.glucose_df.copy()
        df['Date'] = df['Timestamp'].dt.date
        df['TimeOfDay'] = df['Timestamp'].dt.hour + df['Timestamp'].dt.minute / 60

        fig, ax = plt.subplots(figsize=(12, 6))

        # 繪製每一天的血糖曲線
        for date in df['Date'].unique():
            day_data = df[df['Date'] == date]
            ax.plot(day_data['TimeOfDay'], day_data['Glucose'],
                   alpha=0.3, linewidth=0.5)

        # 添加平均線
        hourly_mean = df.groupby(df['TimeOfDay'].astype(int))['Glucose'].mean()
        ax.plot(hourly_mean.index, hourly_mean.values, 'r-',
               linewidth=2, label='Average')

        # 添加目標範圍
        ax.axhspan(70, 180, alpha=0.1, color='green', label='Target Range')

        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Glucose (mg/dL)')
        ax.set_title('Daily Glucose Overlay')
        ax.set_xlim(0, 24)
        ax.set_ylim(40, 400)
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Daily overlay 圖表已儲存至：{save_path}")

        return fig

    def create_time_in_range_pie(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        創建 Time in Range 圓餅圖

        Args:
            save_path: 儲存路徑

        Returns:
            matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 簡單 TIR/TAR/TBR
        sizes1 = [self.metrics['TBR'], self.metrics['TIR'], self.metrics['TAR']]
        labels1 = [f"TBR\n(<70)\n{sizes1[0]:.1f}%",
                  f"TIR\n(70-180)\n{sizes1[1]:.1f}%",
                  f"TAR\n(>180)\n{sizes1[2]:.1f}%"]
        colors1 = ['#ff9999', '#90ee90', '#ffcc99']

        ax1.pie(sizes1, labels=labels1, colors=colors1, autopct='',
               startangle=90, counterclock=False)
        ax1.set_title('Time in Range Summary')

        # 詳細分類
        sizes2 = [
            self.metrics.get('Very Low (<54)', 0),
            self.metrics.get('Low (54-69)', 0),
            self.metrics['TIR'],
            self.metrics.get('High (181-250)', 0),
            self.metrics.get('Very High (>250)', 0)
        ]
        labels2 = ['Very Low\n<54', 'Low\n54-69', 'In Range\n70-180',
                  'High\n181-250', 'Very High\n>250']
        colors2 = ['#ff6666', '#ff9999', '#90ee90', '#ffcc99', '#ff9966']

        # 過濾掉0值
        non_zero = [(s, l, c) for s, l, c in zip(sizes2, labels2, colors2) if s > 0]
        if non_zero:
            sizes2, labels2, colors2 = zip(*non_zero)
            ax2.pie(sizes2, labels=labels2, colors=colors2,
                   autopct='%1.1f%%', startangle=90, counterclock=False)

        ax2.set_title('Detailed Glucose Ranges')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ TIR 圓餅圖已儲存至：{save_path}")

        return fig

    def generate_report(self, output_dir: str = "./report"):
        """
        生成完整分析報告

        Args:
            output_dir: 輸出目錄
        """
        os.makedirs(output_dir, exist_ok=True)

        # 生成所有圖表
        self.create_agp(os.path.join(output_dir, "agp.png"))
        self.create_daily_overlay(os.path.join(output_dir, "daily_overlay.png"))
        self.create_time_in_range_pie(os.path.join(output_dir, "tir_pie.png"))

        # 儲存指標為 JSON
        metrics_file = os.path.join(output_dir, "metrics.json")
        with open(metrics_file, 'w', encoding='utf-8') as f:
            # 轉換 numpy 類型為標準 Python 類型
            clean_metrics = {}
            for key, value in self.metrics.items():
                if isinstance(value, (np.integer, np.floating)):
                    clean_metrics[key] = float(value)
                elif isinstance(value, np.ndarray):
                    clean_metrics[key] = value.tolist()
                elif isinstance(value, dict):
                    clean_metrics[key] = {k: float(v) if isinstance(v, (np.integer, np.floating))
                                         else v for k, v in value.items()}
                else:
                    clean_metrics[key] = value

            json.dump(clean_metrics, f, indent=2, ensure_ascii=False)
            print(f"✓ 指標已儲存至：{metrics_file}")

        # 生成文字報告
        report_file = os.path.join(output_dir, "report.txt")
        self._generate_text_report(report_file)

        print(f"\n✅ 報告生成完成！所有檔案已儲存至：{output_dir}")

    def _generate_text_report(self, file_path: str):
        """生成文字格式報告"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("CGM 數據分析報告\n")
            f.write(f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            # 數據概要
            f.write("【數據概要】\n")
            f.write(f"分析期間：{self.glucose_df['Timestamp'].min()} 至 {self.glucose_df['Timestamp'].max()}\n")
            f.write(f"總天數：{self.metrics['Daily Stats']['Days Analyzed']} 天\n")
            f.write(f"數據點數：{len(self.glucose_df)} 筆\n\n")

            # 關鍵指標
            f.write("【關鍵指標】\n")
            f.write(f"平均血糖：{self.metrics['Mean Glucose']:.1f} mg/dL\n")
            f.write(f"變異係數 (CV)：{self.metrics['CV']:.1f}%\n")
            f.write(f"GMI：{self.metrics['GMI']:.1f}%\n")
            f.write(f"GRI：{self.metrics['GRI']:.1f}\n\n")

            # Time in Range
            f.write("【Time in Range】\n")
            f.write(f"TIR (70-180)：{self.metrics['TIR']:.1f}%\n")
            f.write(f"TAR (>180)：{self.metrics['TAR']:.1f}%\n")
            f.write(f"TBR (<70)：{self.metrics['TBR']:.1f}%\n")
            f.write(f"  - Very Low (<54)：{self.metrics.get('Very Low (<54)', 0):.1f}%\n")
            f.write(f"  - Low (54-69)：{self.metrics.get('Low (54-69)', 0):.1f}%\n\n")

            # 風險評估
            f.write("【風險評估】\n")
            gri = self.metrics['GRI']
            if gri < 20:
                risk_level = "低風險"
            elif gri < 40:
                risk_level = "中低風險"
            elif gri < 60:
                risk_level = "中度風險"
            elif gri < 80:
                risk_level = "中高風險"
            else:
                risk_level = "高風險"
            f.write(f"GRI 風險等級：{risk_level}\n")

            # 建議
            f.write("\n【建議】\n")
            if self.metrics['TIR'] < 70:
                f.write("- TIR 低於目標 (70%)，建議優化血糖管理\n")
            if self.metrics['CV'] > 36:
                f.write("- 血糖變異性偏高 (CV >36%)，建議評估飲食和胰島素方案\n")
            if self.metrics['TBR'] > 4:
                f.write("- 低血糖時間偏多，建議調整治療避免低血糖\n")
            if self.metrics['TAR'] > 25:
                f.write("- 高血糖時間偏多，可能需要調整胰島素劑量\n")

        print(f"✓ 文字報告已儲存至：{file_path}")

def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方法：python analyze_cgm.py <glucose_file.csv> [event_file.csv]")
        print("範例：python analyze_cgm.py glucose.csv events.csv")
        sys.exit(1)

    glucose_file = sys.argv[1]
    event_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(glucose_file):
        print(f"錯誤：找不到檔案 {glucose_file}")
        sys.exit(1)

    print("=" * 60)
    print("CGM 數據分析工具")
    print("=" * 60)

    # 執行分析
    analyzer = CGMAnalyzer(glucose_file, event_file)
    metrics = analyzer.calculate_metrics()

    # 顯示關鍵指標
    print("\n【關鍵指標】")
    print(f"平均血糖: {metrics['Mean Glucose']:.1f} mg/dL")
    print(f"CV: {metrics['CV']:.1f}%")
    print(f"TIR: {metrics['TIR']:.1f}%")
    print(f"GMI: {metrics['GMI']:.1f}%")
    print(f"GRI: {metrics['GRI']:.1f}")

    # 生成報告
    analyzer.generate_report()

    return 0

if __name__ == "__main__":
    main()