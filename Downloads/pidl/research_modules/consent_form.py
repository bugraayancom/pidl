"""
Bilgilendirilmiş Onam Formu
KVKK/GDPR uyumlu katılımcı onay formu
"""

import streamlit as st
from typing import Dict, Any


class ConsentForm:
    """Bilgilendirilmiş onam formu"""

    @staticmethod
    def show() -> bool:
        """
        Onam formunu göster

        Returns:
            True if consent given, False otherwise
        """
        st.markdown("# 📋 KATILIMCI BİLGİLENDİRME VE ONAM FORMU")

        st.markdown("""
        ### ARAŞTIRMANIN ADI
        **İnsan-AI İşbirliği Modellerinde Yetkinlik Transferi ve Performans Optimizasyonu**

        ---

        ### 🎯 ARAŞTIRMANIN AMACI
        Bu araştırma, blockchain tabanlı eğitim sistemleri geliştirmede, farklı yetkinlik
        seviyelerindeki kullanıcılar için en uygun AI yardımını belirlemeyi amaçlamaktadır.

        ### ⏱️ KATILIM SÜRECİ
        Araştırmaya katılmayı kabul ederseniz:
        - **Oturum 1 (2 saat):** Online yetkinlik değerlendirmesi ve 3 görev
        - **Oturum 2 (2 saat, 1-2 gün sonra):** 3 görev ve anket
        - **Toplam süre:** 4-5 saat

        ### 📝 NE YAPACAKSINIZ
        1. Yetkinlik anketi dolduracaksınız (10 soru)
        2. AI yardımıyla blockchain kod üretimi görevleri (6 görev)
        3. Her görev sonrası kısa anket (NASA-TLX, 2 dakika)
        4. Final değerlendirme anketi (5 dakika)

        ### ⚠️ RİSKLER
        - Minimal risk: Zihinsel yorgunluk olabilir
        - Ara verme imkanı tanınacaktır
        - İstediğiniz zaman araştırmadan çekilebilirsiniz

        ### ✅ FAYDALAR
        - Kendi yetkinlik profilinizi öğrenme
        - AI ile etkili çalışma deneyimi
        - Blockchain eğitim sistemleri hakkında bilgi
        - Katılım sertifikası (5 CPD saati)
        - Hediye kartı çekilişi şansı (%10, 500₺)

        ### 🔒 GİZLİLİK
        - Verileriniz anonim olarak saklanacaktır (UUID ile)
        - Kimlik bilgileriniz kaydedilmeyecektir
        - KVKK/GDPR uyumlu veri saklama
        - Sadece araştırmacı erişebilir

        ### 🤝 HAKLARINIZ
        - ✓ Gönüllü katılım (zorunluluk yok)
        - ✓ İstediğiniz zaman çekilme (ceza yok)
        - ✓ Soru sorma ve bilgi alma
        - ✓ Verilerinizi silme talebi
        - ✓ Sonuçlara erişim (özet rapor)

        ### 📧 İLETİŞİM
        Sorularınız için: research@university.edu
        Etik Kurul: ethics@university.edu

        ---
        """)

        st.markdown("### 📋 ONAM")

        col1, col2 = st.columns([1, 10])

        consents = []

        with col1:
            c1 = st.checkbox("", key="consent1")
        with col2:
            st.markdown("Yukarıdaki bilgileri okudum ve anladım")
        consents.append(c1)

        with col1:
            c2 = st.checkbox("", key="consent2")
        with col2:
            st.markdown("Sorularım yanıtlandı veya sormak istediğim soru yok")
        consents.append(c2)

        with col1:
            c3 = st.checkbox("", key="consent3")
        with col2:
            st.markdown("Gönüllü olarak katılıyorum")
        consents.append(c3)

        with col1:
            c4 = st.checkbox("", key="consent4")
        with col2:
            st.markdown("Verilerimin araştırmada kullanılmasına izin veriyorum")
        consents.append(c4)

        with col1:
            c5 = st.checkbox("", key="consent5")
        with col2:
            st.markdown("İstersem çekilebileceğimi biliyorum")
        consents.append(c5)

        st.markdown("---")

        # Tüm onaylar verildi mi?
        all_consents_given = all(consents)

        if all_consents_given:
            st.success("✅ Tüm onaylar verildi. Araştırmaya başlayabilirsiniz.")
        else:
            st.warning("⚠️ Devam etmek için lütfen tüm onayları işaretleyin.")

        return all_consents_given

    @staticmethod
    def get_consent_data() -> Dict[str, Any]:
        """Onam verilerini döndür"""
        return {
            "consent_given": True,
            "consent_timestamp": st.session_state.get('consent_timestamp'),
            "participant_uuid": st.session_state.get('participant_uuid')
        }
