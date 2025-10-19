# CGM 血糖數據分析技能

這是一個專為 Claude Code 設計的 CGM (連續血糖監測) 數據分析技能，能夠自動處理和分析血糖數據，生成專業的分析報告。

## 🚀 快速開始

### 1. 安裝技能

將整個 `cgm_skill` 資料夾複製到 Claude Code 技能目錄：

```bash
# 個人技能
cp -r cgm_skill ~/.claude/skills/

# 或專案技能
cp -r cgm_skill .claude/skills/
```

### 2. 安裝依賴

```bash
cd cgm_skill/scripts
pip install -r requirements.txt
```

### 3. 執行分析

```bash
# 步驟 1: 分割原始 CSV
python scripts/split_csv.py your_cgm_data.csv ./output

# 步驟 2: 分析血糖數據
python scripts/analyze_cgm.py output/*_glucose.csv output/*_events.csv

# 步驟 3: 生成 AI 報告（需要 OpenAI API Key）
python scripts/llm_analysis.py report/metrics.json YOUR_API_KEY
```

## 📁 檔案結構

```
cgm_skill/
├── skill.md                    # 技能主文檔
├── README.md                   # 本說明檔案
├── knowledge/                   # 專業知識庫
│   ├── cgm_metrics.md          # CGM 指標參考
│   └── diabetes_guidelines.md  # 糖尿病管理指南
└── scripts/                     # 可執行腳本
    ├── split_csv.py            # CSV 分割工具
    ├── analyze_cgm.py          # 數據分析工具
    ├── llm_analysis.py         # AI 報告生成器
    └── requirements.txt        # Python 依賴
```

## 📊 功能特色

### 核心分析功能
- ✅ Time in Range (TIR) 計算
- ✅ 血糖變異性分析 (CV, SD, MAGE)
- ✅ GMI 和 GRI 風險評估
- ✅ AGP 動態血糖曲線生成
- ✅ 每日血糖模式識別

### AI 智能分析
- 🤖 個人化血糖管理建議
- 🤖 胰島素劑量優化建議
- 🤖 飲食和運動建議
- 🤖 風險預警和趨勢預測

### 視覺化報告
- 📈 AGP 百分位數圖表
- 📈 每日血糖疊加圖
- 📈 Time in Range 圓餅圖
- 📈 趨勢分析圖表

## 🔧 進階使用

### 自訂目標範圍

在 `analyze_cgm.py` 中修改目標範圍：

```python
# 預設目標範圍
metrics = analyzer.calculate_metrics(target_range=(70, 180))

# 嚴格控制目標
metrics = analyzer.calculate_metrics(target_range=(70, 140))

# 妊娠期目標
metrics = analyzer.calculate_metrics(target_range=(63, 140))
```

### 選擇 AI 模型

支援多種 OpenAI 模型：

```bash
# 使用 GPT-4o (預設)
python llm_analysis.py metrics.json API_KEY gpt-4o

# 使用 GPT-4o-mini (較經濟)
python llm_analysis.py metrics.json API_KEY gpt-4o-mini

# 使用 GPT-5 (如有權限)
python llm_analysis.py metrics.json API_KEY gpt-5
```

### 批次處理

處理多個檔案：

```bash
#!/bin/bash
for file in data/*.csv; do
    python scripts/split_csv.py "$file" "./output/$(basename $file .csv)"
    python scripts/analyze_cgm.py "./output/$(basename $file .csv)"/*_glucose.csv
done
```

## 📝 數據格式要求

### CGM 數據格式

```csv
Date,Time,Sensor Glucose (mg/dL)
2024-01-01,00:00,120
2024-01-01,00:05,118
2024-01-01,00:10,115
...
```

### 事件數據格式（選擇性）

```csv
Date,Time,Event Type,Event Subtype,Insulin Value (u),Carb Value (g)
2024-01-01,07:30,Meal,Breakfast,,45
2024-01-01,07:25,Insulin,Rapid,8,
...
```

## 🎯 使用案例

### 案例 1: 基本分析
```bash
# 只分析血糖數據，不含事件
python scripts/analyze_cgm.py glucose_only.csv
```

### 案例 2: 完整分析
```bash
# 包含胰島素和餐食事件
python scripts/analyze_cgm.py glucose.csv events.csv
```

### 案例 3: 自動化每日報告
```python
# daily_report.py
import schedule
import time
from analyze_cgm import CGMAnalyzer
from llm_analysis import CGMLLMAnalyzer

def daily_analysis():
    analyzer = CGMAnalyzer("today_glucose.csv")
    metrics = analyzer.calculate_metrics()
    analyzer.generate_report("./daily_reports/")

    llm = CGMLLMAnalyzer(api_key="YOUR_KEY")
    llm.generate_comprehensive_report(metrics)

schedule.every().day.at("20:00").do(daily_analysis)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🛠️ 故障排除

### 常見問題

1. **找不到模組錯誤**
   ```bash
   pip install --upgrade -r scripts/requirements.txt
   ```

2. **中文顯示問題**
   ```python
   # 在腳本開頭加入
   plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
   plt.rcParams['axes.unicode_minus'] = False
   ```

3. **API 額度不足**
   - 使用 gpt-4o-mini 代替 gpt-4o
   - 減少分析頻率
   - 檢查 OpenAI 帳戶餘額

4. **數據格式錯誤**
   - 確認 CSV 包含必要欄位
   - 檢查日期時間格式
   - 移除空白行和無效數據

## 📖 參考資源

- [Claude Code Skills 文檔](https://docs.claude.com/en/docs/claude-code/skills)
- [CGM 數據標準](https://www.diabetes.org/cgm)
- [OpenAI API 文檔](https://platform.openai.com/docs)
- [項目 GitHub](https://github.com/zinojeng/CGM)

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設置
```bash
git clone https://github.com/zinojeng/CGM.git
cd CGM
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 測試
```bash
python -m pytest tests/
```

## 📄 授權

MIT License - 詳見 LICENSE 檔案

## ⚠️ 免責聲明

本工具僅供教育和研究用途。所有醫療決策應諮詢專業醫療人員。作者不對使用本工具造成的任何後果負責。

---

**版本**: 1.0.0
**更新日期**: 2024-12
**作者**: CGM Analysis Team
**聯絡**: [GitHub Issues](https://github.com/zinojeng/CGM/issues)