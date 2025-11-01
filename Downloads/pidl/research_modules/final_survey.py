"""
Final Değerlendirme Anketi
Tüm görevler tamamlandıktan sonra
"""

import streamlit as st
from typing import Dict, Any


class FinalSurveyForm:
    """Final değerlendirme anketi"""

    @staticmethod
    def show() -> Dict[str, Any]:
        """
        Final anketi göster

        Returns:
            Anket cevapları
        """
        st.markdown("# 🎯 Final Değerlendirme Anketi")
        st.markdown("Tebrikler! Tüm görevleri tamamladınız. Son birkaç soru:")

        responses = {}

        # AI Karşılaştırması
        st.markdown("## 🤖 AI Persona Karşılaştırması")

        responses['preferred_ai'] = st.radio(
            "Hangi AI ile çalışmayı tercih ettiniz?",
            ["Benzer AI (Kendi seviyem)", "Tamamlayıcı AI (Bir üst seviye)", "Duruma göre değişir"],
            key="final_preferred_ai"
        )

        responses['preferred_ai_reason'] = st.text_area(
            "Nedenini açıklayın:",
            placeholder="Tercih nedeninizi buraya yazın...",
            key="final_preferred_reason",
            height=100
        )

        responses['learning_better_ai'] = st.radio(
            "Öğrenme açısından hangi AI daha faydalıydı?",
            ["Benzer AI", "Tamamlayıcı AI", "İkisi de eşit"],
            key="final_learning_ai"
        )

        responses['speed_better_ai'] = st.radio(
            "Hızlı üretim için hangi AI daha uygundu?",
            ["Benzer AI", "Tamamlayıcı AI", "İkisi de eşit"],
            key="final_speed_ai"
        )

        st.markdown("---")

        # Likert Ölçekli Değerlendirmeler
        st.markdown("## 📊 Likert Ölçeği Değerlendirmeleri")
        st.info("Lütfen aşağıdaki ifadelere ne kadar katıldığınızı belirtin (1-5):")

        likert_questions = {
            "comfort_similar": "Benzer AI ile kendimi daha rahat hissettim",
            "development_complementary": "Tamamlayıcı AI beni daha çok geliştirdi",
            "clarity_similar": "Benzer AI'nın açıklamaları daha anlaşılırdı",
            "quality_complementary": "Tamamlayıcı AI'nın kodları daha kaliteliydi",
            "hybrid_ideal": "İki AI türünü birlikte kullanmak idealdir"
        }

        for key, question in likert_questions.items():
            st.markdown(f"**{question}**")
            responses[key] = st.select_slider(
                "",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: ["Kesinlikle Katılmıyorum", "Katılmıyorum", "Kararsızım", "Katılıyorum", "Kesinlikle Katılıyorum"][x-1],
                key=f"final_likert_{key}",
                label_visibility="collapsed"
            )
            st.markdown("")

        st.markdown("---")

        # Genel Deneyim
        st.markdown("## 🌟 Genel Deneyim")

        responses['blockchain_view_change'] = st.select_slider(
            "Blockchain eğitim sistemleri hakkında görüşünüz değişti mi?",
            options=["Çok olumsuz değişti", "Biraz olumsuz değişti", "Değişmedi", "Biraz olumlu değişti", "Çok olumlu değişti"],
            value="Değişmedi",
            key="final_blockchain_view"
        )

        responses['ai_learning_rating'] = st.slider(
            "AI destekli öğrenme deneyiminizi nasıl değerlendirirsiniz?",
            min_value=1,
            max_value=10,
            value=5,
            key="final_ai_rating"
        )
        st.caption("1 = Çok Kötü, 10 = Mükemmel")

        responses['would_recommend'] = st.radio(
            "Bu sistemi başkalarına önerir misiniz?",
            ["Kesinlikle öneririm", "Muhtemelen öneririm", "Kararsızım", "Muhtemelen önermem", "Kesinlikle önermem"],
            key="final_recommend"
        )

        st.markdown("---")

        # Açık Uçlu Sorular
        st.markdown("## 💭 Açık Uçlu Sorular")

        responses['hardest_task'] = st.text_area(
            "En çok hangi görev zorladı ve neden?",
            placeholder="Deneyiminizi paylaşın...",
            key="final_hardest_task",
            height=100
        )

        responses['ai_potential'] = st.text_area(
            "AI'ların eğitim amaçlı kullanımında en büyük potansiyel nedir?",
            placeholder="Düşüncelerinizi paylaşın...",
            key="final_ai_potential",
            height=100
        )

        responses['suggestions'] = st.text_area(
            "Bu çalışmada değiştirilmesini istediğiniz bir şey var mı?",
            placeholder="Önerilerinizi buraya yazın...",
            key="final_suggestions",
            height=100
        )

        responses['blockchain_education_view'] = st.text_area(
            "Blockchain ve eğitimin kesişimi hakkında ne düşünüyorsunuz?",
            placeholder="Görüşlerinizi paylaşın...",
            key="final_blockchain_education",
            height=100
        )

        return responses

    @staticmethod
    def show_completion_message():
        """Tamamlanma mesajı göster"""
        st.success("✅ Araştırma tamamlandı!")
        st.balloons()

        st.markdown("""
        ## 🎉 Tebrikler!

        Araştırmamıza katıldığınız için çok teşekkür ederiz.

        ### 📧 Sonraki Adımlar:

        1. **Katılım sertifikanız** e-posta ile gönderilecektir (5 CPD saati)
        2. **Hediye kartı çekilişi** 1 hafta içinde yapılacaktır
        3. **Araştırma sonuçları** özeti 1 ay içinde paylaşılacaktır

        ### 📊 Katkınız:

        Verdiğiniz cevaplar, blockchain tabanlı eğitim teknolojilerinin geliştirilmesine
        önemli katkı sağlayacaktır.

        ### 📨 İletişim:

        Sorularınız için: research@university.edu

        ---

        **Tekrar teşekkürler! 🙏**
        """)
