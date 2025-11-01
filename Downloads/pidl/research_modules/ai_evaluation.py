"""
AI Kod Değerlendirme Formu
Katılımcıların AI'nın ürettiği kodu değerlendirmesi
"""

import streamlit as st
from typing import Dict, Any


class AIEvaluationForm:
    """AI Kod Değerlendirme Formu"""

    EVALUATION_DIMENSIONS = {
        "code_understandability": {
            "title": "Kod Anlaşılırlığı",
            "question": "AI'nın ürettiği kod ne kadar anlaşılır?",
            "low_label": "Hiç Anlaşılmıyor",
            "high_label": "Çok Anlaşılır"
        },
        "explanation_quality": {
            "title": "Açıklama Kalitesi",
            "question": "AI'nın verdiği açıklamalar ne kadar yeterli?",
            "low_label": "Yetersiz",
            "high_label": "Mükemmel"
        },
        "educational_value": {
            "title": "Öğreticilik",
            "question": "Bu koddan ne kadar şey öğrendiniz?",
            "low_label": "Hiçbir Şey",
            "high_label": "Çok Şey"
        },
        "perceived_code_quality": {
            "title": "Kod Kalitesi (Tahmini)",
            "question": "Kodun kaliteli göründüğünü düşünüyor musunuz?",
            "low_label": "Çok Kötü",
            "high_label": "Çok İyi"
        },
        "perceived_security": {
            "title": "Güvenlik",
            "question": "Kod güvenli görünüyor mu?",
            "low_label": "Güvensiz",
            "high_label": "Çok Güvenli"
        }
    }

    @staticmethod
    def show(ai_type: str = "AI") -> Dict[str, Any]:
        """
        AI değerlendirme formunu göster

        Args:
            ai_type: "Similar" veya "Complementary"

        Returns:
            Değerlendirme sonuçları
        """
        st.markdown(f"### 🤖 {ai_type} AI Değerlendirmesi")
        st.info("Lütfen AI'nın ürettiği kodu değerlendirin:")

        responses = {}

        # Likert skorlar
        for key, dimension in AIEvaluationForm.EVALUATION_DIMENSIONS.items():
            st.markdown(f"#### {dimension['title']}")
            st.markdown(f"*{dimension['question']}*")

            col1, col2, col3 = st.columns([2, 6, 2])

            with col1:
                st.caption(dimension['low_label'])

            with col2:
                score = st.slider(
                    label="",
                    min_value=1,
                    max_value=10,
                    value=5,
                    key=f"ai_eval_{key}",
                    label_visibility="collapsed"
                )
                responses[key] = score

            with col3:
                st.caption(dimension['high_label'])

            st.markdown("---")

        # Açık uçlu sorular
        st.markdown("#### 💭 Açık Uçlu Değerlendirme")

        best_aspect = st.text_area(
            "Bu AI'nın en iyi yönü neydi?",
            placeholder="Örn: Açıklamaları çok detaylıydı, kod çok temizdi, güvenlik konularına dikkat ediyordu...",
            key="ai_eval_best_aspect",
            height=100
        )
        responses['best_aspect'] = best_aspect

        improvement_needed = st.text_area(
            "Bu AI'nın geliştirilmesi gereken yönü neydi?",
            placeholder="Örn: Daha fazla yorum ekleyebilirdi, açıklamaları karmaşıktı, bazı edge case'leri atlıyordu...",
            key="ai_eval_improvement",
            height=100
        )
        responses['improvement_needed'] = improvement_needed

        # Özet metrikler
        st.markdown("### 📊 Değerlendirme Özeti")

        numeric_scores = {k: v for k, v in responses.items() if isinstance(v, int)}
        avg_score = sum(numeric_scores.values()) / len(numeric_scores) if numeric_scores else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Ortalama Puan", f"{avg_score:.1f}/10")

        with col2:
            max_score = max(numeric_scores.items(), key=lambda x: x[1])
            st.metric(
                "En Yüksek",
                AIEvaluationForm.EVALUATION_DIMENSIONS[max_score[0]]['title'][:15]
            )

        with col3:
            min_score = min(numeric_scores.items(), key=lambda x: x[1])
            st.metric(
                "En Düşük",
                AIEvaluationForm.EVALUATION_DIMENSIONS[min_score[0]]['title'][:15]
            )

        return responses

    @staticmethod
    def get_overall_rating(responses: Dict[str, Any]) -> str:
        """Genel değerlendirme"""
        numeric_scores = {k: v for k, v in responses.items() if isinstance(v, int)}
        avg_score = sum(numeric_scores.values()) / len(numeric_scores) if numeric_scores else 0

        if avg_score >= 8:
            return "Mükemmel"
        elif avg_score >= 6:
            return "İyi"
        elif avg_score >= 4:
            return "Orta"
        else:
            return "Geliştirilmeli"
