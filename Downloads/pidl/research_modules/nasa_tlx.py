"""
NASA-TLX Bilişsel Yük Ölçeği
Her görev sonrası bilişsel yükü ölçmek için
"""

import streamlit as st
from typing import Dict, Any


class NASATLXForm:
    """NASA-TLX Bilişsel Yük Ölçeği"""

    DIMENSIONS = {
        "mental_demand": {
            "title": "Zihinsel Talep (Mental Demand)",
            "question": "Bu görevi yapmak ne kadar zihinsel çaba gerektirdi?",
            "low_label": "Çok Az",
            "high_label": "Çok Fazla"
        },
        "physical_demand": {
            "title": "Fiziksel Talep (Physical Demand)",
            "question": "Bu görev ne kadar fiziksel aktivite gerektirdi?",
            "low_label": "Çok Az",
            "high_label": "Çok Fazla"
        },
        "temporal_demand": {
            "title": "Zamansal Talep (Temporal Demand)",
            "question": "Zaman baskısı ne kadar hissettiniz?",
            "low_label": "Çok Az",
            "high_label": "Çok Fazla"
        },
        "performance": {
            "title": "Performans (Performance)",
            "question": "Görevi ne kadar başarılı tamamladığınızı düşünüyorsunuz?",
            "low_label": "Başarısız",
            "high_label": "Mükemmel"
        },
        "effort": {
            "title": "Çaba (Effort)",
            "question": "Bu görevi başarmak için ne kadar çaba harcadınız?",
            "low_label": "Çok Az",
            "high_label": "Çok Fazla"
        },
        "frustration": {
            "title": "Hayal Kırıklığı (Frustration)",
            "question": "Görev sırasında ne kadar sinirli, stresli veya hayal kırıklığı yaşadınız?",
            "low_label": "Çok Az",
            "high_label": "Çok Fazla"
        }
    }

    @staticmethod
    def show() -> Dict[str, int]:
        """
        NASA-TLX formunu göster

        Returns:
            Boyut skorları {dimension: score (1-10)}
        """
        st.markdown("### 🧠 Bilişsel Yük Değerlendirmesi (NASA-TLX)")
        st.info("Lütfen aşağıdaki boyutları 1-10 arasında değerlendirin:")

        responses = {}

        for key, dimension in NASATLXForm.DIMENSIONS.items():
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
                    key=f"nasa_tlx_{key}",
                    label_visibility="collapsed"
                )
                responses[key] = score

            with col3:
                st.caption(dimension['high_label'])

            st.markdown("---")

        # Toplam bilişsel yük hesapla
        total_load = sum(responses.values())
        responses['total_cognitive_load'] = total_load

        # Görselleştirme
        st.markdown("### 📊 Bilişsel Yük Özeti")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Toplam Yük", f"{total_load}/60")

        with col2:
            avg_load = total_load / 6
            load_level = "Düşük" if avg_load < 4 else "Orta" if avg_load < 7 else "Yüksek"
            st.metric("Ortalama", f"{avg_load:.1f}/10", delta=load_level)

        with col3:
            max_dimension = max(responses.items(), key=lambda x: x[1] if x[0] != 'total_cognitive_load' else 0)
            if max_dimension[0] != 'total_cognitive_load':
                st.metric("En Yüksek", NASATLXForm.DIMENSIONS[max_dimension[0]]['title'].split('(')[0].strip()[:20])

        return responses

    @staticmethod
    def get_load_interpretation(total_load: int) -> str:
        """Bilişsel yük yorumlama"""
        if total_load < 20:
            return "Düşük bilişsel yük - Görev kolaydı"
        elif total_load < 35:
            return "Orta bilişsel yük - Görev uygun zorlukta"
        elif total_load < 50:
            return "Yüksek bilişsel yük - Görev zorlayıcıydı"
        else:
            return "Çok yüksek bilişsel yük - Görev aşırı zorlayıcıydı"
