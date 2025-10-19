---
name: cgm-analyzer
description: Analyzes continuous glucose monitor CSV data, calculates TIR/TAR/TBR metrics, generates AGP charts, and provides AI-powered diabetes management recommendations. Handles Dexcom, FreeStyle Libre, Guardian formats.
---

# CGM 血糖數據分析助手

## 📁 技能檔案結構

```
cgm_skill/
├── skill.md                    # 主要技能文檔
├── config.yaml                 # 配置檔案
├── VERSION                     # 版本號
├── CHANGELOG.md               # 變更日誌
├── README.md                  # 使用說明
├── knowledge/                 # 專業知識庫（模組化）
│   ├── cgm_metrics.md        # 基礎 CGM 指標
│   ├── diabetes_guidelines.md # 糖尿病管理指南
│   ├── metrics/              # 指標詳細文檔
│   │   ├── tir_targets.md   # TIR 目標值
│   │   └── variability.md   # 變異性指標
│   ├── populations/          # 族群特定指南
│   │   └── pregnancy.md     # 妊娠期指南
│   └── treatments/           # 治療相關資訊
├── scripts/                   # 可執行腳本（已設定執行權限）
│   ├── split_csv.py          # CSV 檔案分割工具
│   ├── analyze_cgm.py        # CGM 數據分析工具
│   ├── llm_analysis.py       # LLM 智能分析報告生成器
│   ├── validate.py           # 數據驗證工具
│   ├── setup.py              # 互動式設定精靈
│   ├── batch_process.py      # 批次處理工具
│   ├── test_skill.py         # 自我測試工具
│   └── requirements.txt      # Python 依賴套件
└── examples/                  # 範例數據和文檔
    ├── sample_cgm_data.csv   # 範例 CGM 數據
    └── README.md             # 範例使用說明
```

## 功能概述

這是一個專門處理連續血糖監測（Continuous Glucose Monitor, CGM）數據的智能分析技能。可以從 CSV 格式的原始 CGM 數據中提取關鍵資訊，進行多維度分析，並生成專業的醫療建議報告。

## 核心功能

### 1. 數據處理與解析
- **CSV 文件讀取**：自動解析包含日期、時間、血糖值的 CGM 數據文件
- **數據清理**：處理缺失值、異常值，確保數據品質
- **時間序列轉換**：將原始數據轉換為時間序列格式，便於分析
- **事件提取**：識別並分析用餐、胰島素注射等事件標記

### 2. 血糖指標計算
- **Time in Range (TIR)**：計算血糖在目標範圍內的時間百分比
- **變異係數 (CV)**：評估血糖波動程度
- **平均血糖 (Mean Glucose)**：計算觀察期間的平均血糖值
- **GMI (Glucose Management Indicator)**：估算糖化血紅蛋白 (HbA1c)
- **GRI (Glycemic Risk Index)**：綜合評估血糖風險
- **低血糖/高血糖時間**：統計血糖異常的時間分布

### 3. 進階分析功能

#### AGP (動態血糖曲線) 分析
- 生成 24 小時血糖變化趨勢圖
- 繪製百分位數曲線（10th, 25th, 50th, 75th, 90th）
- 識別每日血糖模式和變化規律
- 分析血糖變異性指標（SD, CV, MAGE）

#### 胰島素藥代動力學分析
- 分析不同類型胰島素（長效、速效、預混）的使用模式
- 計算胰島素劑量統計（平均劑量、注射頻率、劑量範圍）
- 識別常見注射時間和劑量趨勢
- 評估胰島素效力與血糖控制的相關性

#### 飲食影響評估
- 分析餐食對血糖的影響
- 計算餐後血糖峰值和回復時間
- 評估碳水化合物係數和胰島素敏感性

### 4. AI 智能分析與建議

使用先進的語言模型（支援 GPT-4o, GPT-5 等）提供：
- **個人化血糖管理建議**：根據個人數據模式提供客製化建議
- **風險預警**：識別潛在的血糖控制問題
- **治療優化建議**：提供胰島素劑量調整和飲食管理建議
- **趨勢預測**：基於歷史數據預測未來血糖趨勢

### 5. 族群特定分析

支援不同患者族群的目標設定：
- 一般成人糖尿病患者
- 兒童及青少年糖尿病患者
- 老年糖尿病患者
- 妊娠期糖尿病患者
- 重症或高風險患者

## 使用指引

### 輸入要求

1. **CGM 數據文件格式**：
   ```csv
   Date,Time,Sensor Glucose (mg/dL)
   2024-01-01,00:00,120
   2024-01-01,00:05,118
   ...
   ```

2. **事件標記文件（選擇性）**：
   ```csv
   Date,Time,Event Type,Value
   2024-01-01,07:30,Meal,45g
   2024-01-01,07:25,Insulin,8 units
   ...
   ```

### 執行步驟

#### 方法一：使用提供的 Python 腳本

1. **安裝依賴套件**：
   ```bash
   cd scripts/
   pip install -r requirements.txt
   ```

2. **分割原始 CSV 檔案**：
   ```bash
   python split_csv.py original_cgm_data.csv ./output
   # 將生成 glucose.csv 和 events.csv
   ```

3. **執行 CGM 數據分析**：
   ```bash
   python analyze_cgm.py output/glucose.csv output/events.csv
   # 生成分析報告和視覺化圖表
   ```

4. **生成 AI 智能報告**：
   ```bash
   python llm_analysis.py report/metrics.json YOUR_API_KEY gpt-4o
   # 生成個人化建議報告
   ```

#### 方法二：程式化調用

1. **準備數據**：
   - 確保 CSV 文件包含必要的欄位（Date, Time, Sensor Glucose）
   - 檢查數據完整性和時間連續性

2. **啟動分析**：
   ```python
   # 載入 CGM 數據
   cgm_data = read_cgm_file("path/to/cgm_data.csv")

   # 計算血糖指標
   metrics = calculate_metrics(cgm_data, target_range=(70, 180))

   # 生成 AGP 圖表
   agp_plot = create_agp(cgm_data)

   # 執行深度分析
   analysis_result = perform_deep_analysis(
       cgm_data,
       insulin_data,
       meal_data,
       api_key="your-openai-api-key"
   )
   ```

3. **解讀結果**：
   - 查看關鍵血糖指標是否達到目標
   - 分析 AGP 圖表識別血糖模式
   - 參考 AI 建議調整治療方案

## 輸出範例

### 血糖指標報告
```
=== 血糖控制指標 ===
Time in Range (70-180): 75.3%
Time Below Range (<70): 2.1%
Time Above Range (>180): 22.6%
平均血糖: 142 mg/dL
變異係數 (CV): 28.5%
GMI: 6.8%
GRI: 35.2
```

### AGP 分析洞察
```
【AGP 變異性分析】
- 早晨時段 (6-9am) 血糖變異較大，可能與晨曦現象有關
- 午餐後 (12-3pm) 血糖控制良好，維持在目標範圍內
- 晚間 (9pm-12am) 存在低血糖風險，建議調整晚餐胰島素劑量
- 整體變異係數 28.5%，建議目標 <36%，控制尚可
```

### 個人化建議
```
【血糖管理優化建議】
1. 胰島素調整：
   - 建議增加早餐前長效胰島素 2 單位，改善早晨血糖
   - 晚餐速效胰島素可減少 1-2 單位，降低夜間低血糖風險

2. 飲食管理：
   - 早餐建議選擇低 GI 食物，延緩血糖上升
   - 晚餐後適量活動有助於改善餐後血糖

3. 監測重點：
   - 加強凌晨 2-4 點血糖監測
   - 記錄運動對血糖的影響模式
```

## 📚 專業知識庫

### knowledge/ 資料夾內容

此技能包含兩個重要的知識文檔，提供 CGM 分析的專業背景：

1. **cgm_metrics.md** - CGM 關鍵指標參考手冊
   - 各族群的血糖控制目標範圍
   - 血糖變異性指標詳解（SD, CV, MAGE）
   - GRI 風險指數計算方法
   - AGP 解讀指南
   - 胰島素作用時間參考
   - 餐後血糖管理目標
   - 特殊情況處理（晨曦現象、蘇木傑效應）

2. **diabetes_guidelines.md** - 糖尿病管理指南
   - 國際組織（ADA, IDF, EASD）建議標準
   - CGM 使用最佳實踐
   - 胰島素治療策略
   - 飲食與運動管理
   - 併發症預防與監測
   - 特殊族群管理
   - 新技術應用（智慧胰島素筆、閉環系統）

這些知識文檔會被 LLM 分析腳本自動載入，提供專業的醫療背景支援。

## 技術實現細節

### 核心演算法

1. **時間序列分析**：
   - 使用滑動窗口計算動態統計
   - 應用 Savitzky-Golay 濾波平滑數據
   - 使用 FFT 識別週期性模式

2. **統計方法**：
   - 百分位數計算用於 AGP 繪製
   - 核密度估計用於血糖分布分析
   - 迴歸分析評估胰島素-血糖關係

3. **機器學習應用**：
   - 聚類分析識別血糖模式
   - 時間序列預測模型（ARIMA, LSTM）
   - 異常檢測識別數據品質問題

### 依賴套件

```python
# 核心數據處理
import pandas as pd
import numpy as np

# 視覺化
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# 統計分析
from scipy import stats
from sklearn.cluster import KMeans

# AI 整合
import openai
```

## 注意事項與免責聲明

### 使用限制
- 本工具僅供參考，不能替代專業醫療建議
- 所有治療調整應在醫療專業人員指導下進行
- 分析結果準確性依賴於輸入數據品質

### 數據隱私
- 所有數據處理均在本地進行
- AI 分析時會匿名化個人資訊
- 建議定期刪除敏感數據文件

### 更新與維護
- 定期更新血糖管理指南以符合最新醫療標準
- 持續優化 AI 模型以提供更準確的建議
- 收集使用者回饋改進分析演算法

## 延伸應用

### 研究用途
- 大規模 CGM 數據分析
- 血糖控制模式研究
- 治療效果評估

### 臨床應用
- 門診快速評估工具
- 遠程血糖管理平台
- 醫患溝通輔助工具

### 個人健康管理
- 日常血糖追蹤
- 生活方式優化
- 自我管理教育

## 版本歷史

### v1.0.0 (2024-12)
- 初始版本發布
- 支援基本 CGM 數據分析
- 整合 GPT-4 智能分析

### 未來規劃
- 支援更多 CGM 設備格式
- 加入預測性低血糖警報
- 開發行動應用程式界面
- 整合穿戴式設備數據

## 參考資源

- [國際糖尿病聯盟 CGM 使用指南](https://www.idf.org)
- [美國糖尿病協會標準照護指南](https://www.diabetes.org)
- [連續血糖監測技術評論](https://doi.org/example)
- [AI 在糖尿病管理的應用](https://example.com)

## 聯繫與支援

如有任何問題或建議，請透過以下方式聯繫：
- GitHub Issues: [項目頁面](https://github.com/zinojeng/CGM)
- 技術文檔: [Wiki](https://github.com/zinojeng/CGM/wiki)
- 社群討論: [Discord/Forum]

---

*本技能文檔遵循 Claude Code Skills 規範，適用於自動化 CGM 數據分析工作流程。*