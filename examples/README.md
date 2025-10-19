# CGM 分析範例

這個資料夾包含 CGM 分析的範例檔案和使用案例。

## 📁 範例檔案

### sample_cgm_data.csv
- 簡單的 CGM 數據範例（3 小時）
- 包含典型的血糖波動模式
- 可用於測試基本功能

### sample_events.csv (選擇性)
- 事件標記範例（胰島素注射、用餐）
- 與 sample_cgm_data.csv 對應

## 🚀 快速測試

### 1. 驗證數據
```bash
cd ../scripts
python validate.py ../examples/sample_cgm_data.csv
```

### 2. 分析數據
```bash
python analyze_cgm.py ../examples/sample_cgm_data.csv
```

### 3. 生成 AI 報告
```bash
python llm_analysis.py report/metrics.json YOUR_API_KEY
```

## 📊 預期結果

使用範例數據應該得到類似以下的結果：

### 關鍵指標
- **平均血糖**: ~115 mg/dL
- **TIR (70-180)**: ~75%
- **TAR (>180)**: ~20%
- **TBR (<70)**: ~5%
- **CV**: ~30%

### 圖表輸出
- AGP 動態血糖曲線
- 每日疊加圖
- TIR 圓餅圖

## 🧪 測試案例

### 案例 1: 基本分析
```python
from analyze_cgm import CGMAnalyzer

analyzer = CGMAnalyzer("sample_cgm_data.csv")
metrics = analyzer.calculate_metrics()
print(f"TIR: {metrics['TIR']:.1f}%")
```

### 案例 2: 自訂目標範圍
```python
# 嚴格控制目標
metrics = analyzer.calculate_metrics(target_range=(70, 140))
print(f"嚴格 TIR: {metrics['TIR']:.1f}%")
```

### 案例 3: 批次處理
```bash
python batch_process.py "../examples/*.csv"
```

## 📝 數據格式說明

### CGM 數據格式
```csv
Date,Time,Sensor Glucose (mg/dL)
YYYY-MM-DD,HH:MM,數值
```

### 事件數據格式
```csv
Date,Time,Event Type,Event Subtype,Value
YYYY-MM-DD,HH:MM,類型,子類型,數值
```

## 🔧 常見問題

### Q: 如何生成更長時間的測試數據？
A: 使用 generate_sample_data.py 腳本（如果提供）或複製現有數據並調整日期。

### Q: 如何測試異常情況？
A: 修改範例數據，加入：
- 缺失值（空白）
- 異常值（<40 或 >400）
- 不規則時間間隔

### Q: 如何測試不同的 CGM 設備格式？
A: 參考各設備的數據格式文檔，調整欄位名稱。

## 📚 更多資源

- [CGM 數據標準](https://www.diabetes.org/cgm)
- [測試數據生成工具](https://github.com/example/cgm-test-data)
- [數據品質檢查清單](../knowledge/data_quality.md)

---

*範例數據僅供測試用途，不代表真實患者數據*