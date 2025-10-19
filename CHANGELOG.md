# 變更日誌

所有 CGM 血糖數據分析技能的重要變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [1.1.0] - 2024-12-19

### 新增
- ✨ 增強的技能描述，包含具體觸發詞彙
- 📁 模組化知識庫結構
  - metrics/ - 指標相關知識
  - populations/ - 族群特定指南
  - treatments/ - 治療相關資訊
- ⚙️ 配置系統 (config.yaml)
- 🔧 驗證工具 (validate.py)
- 🎯 互動式設定精靈 (setup.py)
- 🔄 批次處理功能 (batch_process.py)
- 📊 範例數據和文檔
- 📝 完整的 README 文檔

### 改進
- 🚀 更好的 Progressive Disclosure 支援
- 🔒 增強的安全設定（限制工具權限）
- 📈 更詳細的錯誤處理和建議
- 🌐 支援多種 CGM 設備格式

### 修復
- 🐛 改善中文字元顯示
- 🐛 修正日期時間解析問題
- 🐛 處理缺失值的邏輯優化

## [1.0.0] - 2024-12-18

### 初始發布
- 📊 基本 CGM 數據分析功能
  - TIR/TAR/TBR 計算
  - CV、GMI、GRI 指標
  - AGP 圖表生成
- 🤖 LLM 智能分析整合
  - 支援 GPT-4o、GPT-4o-mini
  - 個人化建議生成
- 📁 基礎檔案結構
  - skill.md 主文檔
  - Python 分析腳本
  - 知識庫文檔

## 未來規劃

### [1.2.0] - 計劃中
- [ ] 支援更多 CGM 設備格式（Abbott、Medtronic）
- [ ] 即時數據流處理
- [ ] 網頁界面 (Web UI)
- [ ] 多語言支援擴展

### [1.3.0] - 規劃中
- [ ] 機器學習預測模型
- [ ] 與醫療系統整合 (FHIR)
- [ ] 行動應用程式支援
- [ ] 雲端同步功能

### [2.0.0] - 長期目標
- [ ] 完整的 MCP 服務器實現
- [ ] AI 自動調參建議
- [ ] 多患者管理系統
- [ ] 臨床決策支援系統

## 版本說明

### 版本號規則
- **主版本號 (Major)**: 不相容的 API 變更
- **次版本號 (Minor)**: 向下相容的功能新增
- **修訂號 (Patch)**: 向下相容的錯誤修復

### 支援政策
- 最新的主版本：完整支援
- 前一個主版本：安全更新支援 6 個月
- 更早版本：不再支援

## 貢獻者

- 主要開發者：CGM Analysis Team
- 特別感謝：Claude Code Skills 社群

## 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

---

如有問題或建議，請提交 [GitHub Issue](https://github.com/zinojeng/CGM/issues)