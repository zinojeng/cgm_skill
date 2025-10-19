#!/usr/bin/env python3
"""
CGM LLM 智能分析報告生成器
使用 OpenAI API 生成個人化的血糖管理建議
"""

import json
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from openai import OpenAI

class CGMLLMAnalyzer:
    """CGM LLM 分析器"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        初始化 LLM 分析器

        Args:
            api_key: OpenAI API 金鑰
            model: 使用的模型名稱
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.analysis_results = {}

    def load_metrics(self, metrics_file: str) -> Dict:
        """載入分析指標"""
        with open(metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_knowledge(self, knowledge_dir: str = "../knowledge") -> str:
        """載入專業知識庫"""
        knowledge_content = ""

        # 載入 CGM 指標參考
        metrics_file = os.path.join(knowledge_dir, "cgm_metrics.md")
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r', encoding='utf-8') as f:
                knowledge_content += f"【CGM 指標參考】\n{f.read()}\n\n"

        # 載入糖尿病管理指南
        guidelines_file = os.path.join(knowledge_dir, "diabetes_guidelines.md")
        if os.path.exists(guidelines_file):
            with open(guidelines_file, 'r', encoding='utf-8') as f:
                knowledge_content += f"【糖尿病管理指南】\n{f.read()}\n\n"

        return knowledge_content

    def analyze_agp_pattern(self, metrics: Dict) -> str:
        """分析 AGP 模式"""
        prompt = f"""
        根據以下 CGM 數據的每小時血糖模式，分析血糖控制的特徵和問題：

        每小時平均血糖（mg/dL）：
        {json.dumps(metrics.get('Hourly Pattern', {}), indent=2)}

        整體指標：
        - 平均血糖：{metrics.get('Mean Glucose', 0):.1f} mg/dL
        - CV：{metrics.get('CV', 0):.1f}%
        - SD：{metrics.get('SD', 0):.1f} mg/dL

        請分析：
        1. 識別血糖模式（晨曦現象、夜間低血糖風險等）
        2. 找出血糖控制的問題時段
        3. 評估血糖變異性
        4. 提供具體的改善建議

        請用繁體中文回答，並使用專業但易懂的語言。
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位專業的糖尿病管理專家，擅長分析 CGM 數據並提供個人化建議。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def analyze_time_in_range(self, metrics: Dict) -> str:
        """分析 Time in Range"""
        prompt = f"""
        請分析以下 CGM Time in Range 數據：

        - TIR (70-180 mg/dL): {metrics.get('TIR', 0):.1f}%
        - TAR (>180 mg/dL): {metrics.get('TAR', 0):.1f}%
        - TBR (<70 mg/dL): {metrics.get('TBR', 0):.1f}%
        - Very Low (<54 mg/dL): {metrics.get('Very Low (<54)', 0):.1f}%
        - Very High (>250 mg/dL): {metrics.get('Very High (>250)', 0):.1f}%

        GMI: {metrics.get('GMI', 0):.1f}%
        GRI: {metrics.get('GRI', 0):.1f}

        國際目標：
        - TIR >70%
        - TBR <4%
        - TAR <25%

        請提供：
        1. 與國際標準的比較
        2. 優先改善的項目
        3. 具體的調整建議
        4. 風險評估

        請用繁體中文回答。
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位經驗豐富的內分泌科醫師，專精於糖尿病管理。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def generate_personalized_recommendations(self, metrics: Dict, patient_profile: Optional[Dict] = None) -> str:
        """生成個人化建議"""
        profile_info = ""
        if patient_profile:
            profile_info = f"""
            患者資料：
            - 糖尿病類型：{patient_profile.get('diabetes_type', '未指定')}
            - 年齡組：{patient_profile.get('age_group', '成人')}
            - 治療方案：{patient_profile.get('treatment', '未指定')}
            """

        prompt = f"""
        基於以下 CGM 分析結果，提供個人化的血糖管理建議：

        {profile_info}

        關鍵指標：
        - 平均血糖：{metrics.get('Mean Glucose', 0):.1f} mg/dL
        - CV：{metrics.get('CV', 0):.1f}%
        - TIR：{metrics.get('TIR', 0):.1f}%
        - GMI：{metrics.get('GMI', 0):.1f}%
        - GRI：{metrics.get('GRI', 0):.1f}

        請提供以下方面的具體建議：

        1. 【胰島素調整】
           - 基礎胰島素調整建議
           - 餐時胰島素優化
           - 校正劑量策略

        2. 【飲食管理】
           - 碳水化合物攝取建議
           - 用餐時間安排
           - 特定食物選擇

        3. 【生活方式】
           - 運動時機和類型
           - 睡眠對血糖的影響
           - 壓力管理

        4. 【監測重點】
           - 需要加強監測的時段
           - 特殊情況的處理
           - CGM 使用優化

        5. 【風險預防】
           - 低血糖預防措施
           - 高血糖處理方案
           - 緊急情況準備

        請提供實用、具體、可執行的建議，使用繁體中文。
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位資深的糖尿病照護團隊成員，包含醫師、營養師和衛教師的專業知識。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content

    def generate_comprehensive_report(self, metrics: Dict, output_file: str = "llm_report.md"):
        """生成完整的 LLM 分析報告"""
        print("正在生成 AI 分析報告...")

        # 載入專業知識（如果存在）
        knowledge = self.load_knowledge()

        # 執行各項分析
        print("  分析 AGP 模式...")
        agp_analysis = self.analyze_agp_pattern(metrics)

        print("  分析 Time in Range...")
        tir_analysis = self.analyze_time_in_range(metrics)

        print("  生成個人化建議...")
        recommendations = self.generate_personalized_recommendations(metrics)

        # 組合報告
        report = f"""# CGM 智能分析報告

生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析模型：{self.model}

---

## 📊 數據摘要

- **平均血糖**：{metrics.get('Mean Glucose', 0):.1f} mg/dL
- **變異係數 (CV)**：{metrics.get('CV', 0):.1f}%
- **Time in Range**：{metrics.get('TIR', 0):.1f}%
- **GMI**：{metrics.get('GMI', 0):.1f}%
- **GRI**：{metrics.get('GRI', 0):.1f}

---

## 🔍 AGP 模式分析

{agp_analysis}

---

## 📈 Time in Range 評估

{tir_analysis}

---

## 💡 個人化管理建議

{recommendations}

---

## ⚠️ 重要提醒

1. **醫療諮詢**：本報告僅供參考，所有治療調整應在醫療專業人員指導下進行
2. **持續監測**：建議定期（每2-4週）重新評估血糖控制情況
3. **個體差異**：每個人對治療的反應不同，需要個體化調整
4. **安全第一**：優先處理低血糖風險，再優化高血糖控制

---

## 📚 參考資源

- [美國糖尿病協會 (ADA) 標準](https://www.diabetes.org)
- [國際糖尿病聯盟 (IDF)](https://www.idf.org)
- [CGM 使用共識聲明](https://doi.org/10.2337/dci19-0062)

---

*本報告由 AI 輔助生成，結合了最新的糖尿病管理指南和 CGM 數據分析最佳實踐。*
"""

        # 儲存報告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✓ AI 分析報告已儲存至：{output_file}")

        # 同時儲存為 JSON 格式
        json_file = output_file.replace('.md', '.json')
        analysis_json = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "metrics": metrics,
            "analysis": {
                "agp_pattern": agp_analysis,
                "time_in_range": tir_analysis,
                "recommendations": recommendations
            }
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_json, f, indent=2, ensure_ascii=False)

        print(f"✓ JSON 格式報告已儲存至：{json_file}")

        return report

    def analyze_insulin_patterns(self, insulin_data: pd.DataFrame, metrics: Dict) -> str:
        """分析胰島素使用模式（如果有數據）"""
        if insulin_data is None or insulin_data.empty:
            return "無胰島素數據可供分析"

        # 統計胰島素使用
        insulin_summary = {
            "total_injections": len(insulin_data),
            "daily_average": len(insulin_data) / metrics.get('Daily Stats', {}).get('Days Analyzed', 1),
            "types": insulin_data['Event Subtype'].value_counts().to_dict() if 'Event Subtype' in insulin_data.columns else {}
        }

        prompt = f"""
        分析以下胰島素使用數據並提供優化建議：

        胰島素使用統計：
        {json.dumps(insulin_summary, indent=2, ensure_ascii=False)}

        血糖控制結果：
        - TIR: {metrics.get('TIR', 0):.1f}%
        - 平均血糖: {metrics.get('Mean Glucose', 0):.1f} mg/dL
        - CV: {metrics.get('CV', 0):.1f}%

        請分析：
        1. 胰島素使用模式是否合理
        2. 與血糖控制的相關性
        3. 可能的優化方向
        4. 具體調整建議

        使用繁體中文回答。
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位胰島素治療專家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content

def main():
    """主函數"""
    if len(sys.argv) < 3:
        print("使用方法：python llm_analysis.py <metrics.json> <api_key> [model]")
        print("範例：python llm_analysis.py metrics.json sk-xxx gpt-4o")
        sys.exit(1)

    metrics_file = sys.argv[1]
    api_key = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "gpt-4o"

    if not os.path.exists(metrics_file):
        print(f"錯誤：找不到檔案 {metrics_file}")
        sys.exit(1)

    print("=" * 60)
    print("CGM LLM 智能分析")
    print("=" * 60)

    try:
        # 初始化分析器
        analyzer = CGMLLMAnalyzer(api_key, model)

        # 載入指標
        print("載入分析指標...")
        metrics = analyzer.load_metrics(metrics_file)

        # 生成報告
        print("開始 AI 分析...")
        report = analyzer.generate_comprehensive_report(metrics)

        print("\n✅ AI 分析完成！")

    except Exception as e:
        print(f"錯誤：{str(e)}")
        sys.exit(1)

    return 0

if __name__ == "__main__":
    main()