"""
Persona in the Loop (PIDL) - Ana Streamlit Uygulaması
10 farklı persona ile kod üretimi ve karşılaştırma platformu
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import numpy as np

from personas import get_all_personas, get_personas_by_category
from code_generator import CodeGenerator
from evaluator import CodeEvaluator
from competency_assessment import CompetencyAssessment, CompetencyProfile
from advanced_math_models import (
    InformationTheoryAnalyzer,
    BayesianInference,
    ParetoOptimization,
    MarkovChainLearning,
    TimeSeriesForecasting,
    CorrelationAnalysis
)
from multi_llm_engine import MultiLLMEngine
from recommendation_engine import RecommendationEngine
from synthetic_user_generator import SyntheticUserGenerator
from bulk_simulation import BulkSimulation
from matching_tester import MatchingTester

# Sayfa yapılandırması
st.set_page_config(
    page_title="Persona in the Loop",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern ve şık tasarım
st.markdown("""
<style>
    /* Ana başlık */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }

    /* Persona kartları */
    .persona-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Metrik kartları */
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* TAB MENÜ - Modern grid layout */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        display: flex;
        flex-wrap: wrap;
        justify-content: space-evenly;
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        min-height: 60px;
        padding: 12px 20px;
        background: white;
        border-radius: 12px;
        border: 2px solid transparent;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        flex: 1 1 auto;
        min-width: 140px;
        max-width: 200px;
        text-align: center;
        white-space: normal;
        line-height: 1.3;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: #667eea;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* Kod blokları */
    .code-block {
        background: #1e1e1e;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Sidebar stil */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    [data-testid="stSidebar"] .element-container {
        color: white;
    }

    /* Buton stilleri */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    /* Metrikler */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Session state başlatma
if 'generated_codes' not in st.session_state:
    st.session_state.generated_codes = None
if 'evaluated_results' not in st.session_state:
    st.session_state.evaluated_results = None
if 'rankings' not in st.session_state:
    st.session_state.rankings = None
if 'task_history' not in st.session_state:
    st.session_state.task_history = []
if 'selected_persona' not in st.session_state:
    st.session_state.selected_persona = None
if 'show_persona_profile' not in st.session_state:
    st.session_state.show_persona_profile = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'assessment_completed' not in st.session_state:
    st.session_state.assessment_completed = False
if 'multi_llm_results' not in st.session_state:
    st.session_state.multi_llm_results = None


def show_persona_profile(persona):
    """Persona detaylı profil sayfası"""
    
    # Profil header - Gradient arka plan ile
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;'>
        <h1 style='margin: 0; font-size: 3rem;'>{persona.avatar}</h1>
        <h2 style='margin: 0.5rem 0;'>{persona.name}</h2>
        <h3 style='margin: 0; opacity: 0.9;'>{persona.role}</h3>
        <p style='margin: 1rem 0 0 0; font-style: italic; font-size: 1.1rem;'>"{persona.specialty_quote}"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Geri dön butonu
    if st.button("⬅️ Geri Dön", type="secondary"):
        st.session_state.show_persona_profile = False
        st.session_state.selected_persona = None
        st.rerun()
    
    st.markdown("---")
    
    # Ana bilgiler - 3 kolon
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("### 📋 Genel Bilgiler")
        st.markdown(f"**ID:** `{persona.id}`")
        st.markdown(f"**Kategori:** {persona.category.title()}")
        st.markdown("")
        st.info(persona.description)
    
    with col2:
        st.markdown("### 🎨 Kodlama Stili")
        st.write(persona.coding_style)
        st.markdown("")
        st.markdown(f"**🔹 Kod Özelliği:**")
        for key, value in list(persona.code_characteristics.items())[:3]:
            st.caption(f"**{key.replace('_', ' ').title()}:** {value}")
    
    with col3:
        st.markdown("### 🏆 Kategori")
        if persona.category == "education":
            st.success("🎓 Eğitim Bilimcisi")
            st.write("Pedagojik yaklaşım ve öğretici kod üretimi")
        else:
            st.info("💻 Teknoloji Uzmanı")
            st.write("Teknik mükemmellik ve profesyonel standartlar")
    
    st.markdown("---")
    
    # Geçmiş ve Felsefe
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 Geçmiş & Deneyim")
        st.write(persona.background)
    
    with col2:
        st.markdown("### 💭 Kodlama Felsefesi")
        st.write(persona.philosophy)
    
    st.markdown("---")
    
    # Güçlü ve Zayıf Yönler
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Güçlü Yönler")
        for strength in persona.strengths:
            st.markdown(f"✓ **{strength}**")
    
    with col2:
        st.markdown("### ⚠️ Potansiyel Zayıf Yönler")
        for weakness in persona.weaknesses:
            st.markdown(f"• {weakness}")
    
    st.markdown("---")
    
    # Öncelikler ve Pattern'ler
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Öncelik Sırası")
        for priority in persona.priorities:
            st.markdown(f"{priority}")
    
    with col2:
        st.markdown("### 🔧 Favori Pattern'ler")
        for pattern in persona.favorite_patterns:
            st.markdown(f"• {pattern}")
    
    st.markdown("---")
    
    # Kod Karakteristikleri - Tam liste
    st.markdown("### 📊 Detaylı Kod Karakteristikleri")
    cols = st.columns(3)
    items = list(persona.code_characteristics.items())
    for idx, (key, value) in enumerate(items):
        with cols[idx % 3]:
            st.metric(
                label=key.replace('_', ' ').title(),
                value="",
                delta=value
            )
    
    st.markdown("---")
    
    # Sistem Promptu - Genişletilebilir
    with st.expander("🤖 Sistem Promptu - Tüm Detaylar", expanded=False):
        st.code(persona.system_prompt, language="text")
        st.caption("Bu prompt, AI'a bu persona karakterini vererek kod üretmesini sağlar.")
    
    st.markdown("---")
    
    # Aksiyon butonları
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Bu Persona ile Kod Üret", use_container_width=True):
            st.session_state.show_persona_profile = False
            st.session_state.selected_persona = None
            st.success(f"{persona.name} seçildi! Kod Üret sekmesine gidin.")
    
    with col2:
        if st.button("📊 Diğer Persona'larla Karşılaştır", use_container_width=True):
            st.session_state.show_persona_profile = False
            st.session_state.selected_persona = None
            st.info("Karşılaştırma sekmesine yönlendiriliyorsunuz...")
    
    with col3:
        if st.button("⬅️ Persona Listesine Dön", use_container_width=True, type="primary"):
            st.session_state.show_persona_profile = False
            st.session_state.selected_persona = None
            st.rerun()


def main():
    """Ana uygulama"""
    
    # Persona profil sayfası kontrolü
    if st.session_state.show_persona_profile and st.session_state.selected_persona:
        show_persona_profile(st.session_state.selected_persona)
        return
    
    # Başlık
    st.markdown('<h1 class="main-header">🎭 Persona in the Loop</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; font-size: 1.2rem; color: #666;'>
        10 Farklı Uzmanlık Perspektifinden Kod Üretimi ve Karşılaştırma Platformu
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Ayarlar")

        # Provider seçimi
        provider = st.selectbox(
            "🤖 AI Provider",
            ["OpenAI", "Anthropic"],
            help="Kod üretimi için kullanılacak AI provider"
        )

        # Provider'a göre API key ve model seçimi
        if provider == "OpenAI":
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                help="OpenAI API anahtarınızı girin veya .env dosyasında tanımlayın"
            )

            model = st.selectbox(
                "Model Seçimi",
                ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                help="Kullanılacak OpenAI modeli"
            )
            provider_name = "openai"

        else:  # Anthropic
            api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                value=os.getenv("ANTHROPIC_API_KEY", ""),
                help="Anthropic API anahtarınızı girin veya .env dosyasında tanımlayın"
            )

            model = st.selectbox(
                "Model Seçimi",
                ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
                help="Kullanılacak Anthropic modeli"
            )
            provider_name = "anthropic"
        
        st.markdown("---")
        st.markdown("## 👥 Persona'lar")
        
        personas = get_all_personas()
        education_personas = get_personas_by_category("education")
        technology_personas = get_personas_by_category("technology")
        
        st.metric("Toplam Persona", len(personas))
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🎓 Eğitim", len(education_personas))
        with col2:
            st.metric("💻 Teknoloji", len(technology_personas))
        
        # Persona seçimi
        st.markdown("### Aktif Persona'lar")
        selected_category = st.radio(
            "Kategori",
            ["Tümü", "Eğitim Bilimcileri", "Teknoloji Uzmanları"],
            index=0,  # Varsayılan: Tümü
            horizontal=True
        )
        
        if selected_category == "Eğitim Bilimcileri":
            active_personas = education_personas
        elif selected_category == "Teknoloji Uzmanları":
            active_personas = technology_personas
        else:
            active_personas = personas
        
        st.info(f"✓ {len(active_personas)} persona seçili")
        
        # Seçili persona'ları göster
        with st.expander("Seçili Persona'lar", expanded=False):
            for p in active_personas:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{p.avatar} {p.name}")
                with col2:
                    if st.button("👁️", key=f"view_{p.id}_sidebar", help=f"{p.name} profilini görüntüle"):
                        st.session_state.selected_persona = p
                        st.session_state.show_persona_profile = True
                        st.rerun()
        
        st.markdown("---")
        st.markdown("## 📊 İstatistikler")
        if st.session_state.task_history:
            st.metric("Toplam Görev", len(st.session_state.task_history))
        
    # Ana içerik
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🎓 Yetkinlik Değerlendirmesi",
        "🎯 Kod Üret",
        "📊 Sonuçlar",
        "🏆 Sıralamalar",
        "🤖 Çoklu LLM Testleri",
        "📐 Matematiksel Analizler",
        "👥 Persona Detayları",
        "⚖️ Karşılaştırma",
        "🧪 Bulk Simulation"
    ])
    
    # TAB 1: Yetkinlik Değerlendirmesi
    with tab1:
        st.markdown("## 🎓 Yetkinlik Değerlendirmesi ve Persona Tavsiye Sistemi")
        st.markdown("""
        <p style='font-size: 1.1rem; color: #666;'>
            Bu değerlendirme, sizin için en uygun AI persona'larını önermek ve 
            doktora araştırması için veri toplamak amacıyla tasarlanmıştır.
        </p>
        """, unsafe_allow_html=True)
        
        # Profil durumu
        if st.session_state.user_profile:
            profile = st.session_state.user_profile
            
            # Dual-domain skorları göster
            st.markdown("### 📊 Yetkinlik Profil Özeti")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔗 Blockchain/Teknik", 
                         f"{profile.technical_score:.1f}/100",
                         delta=CompetencyAssessment.LEVELS[profile.technical_level]["name"])
            with col2:
                st.metric("🎓 Eğitim/Pedagoji", 
                         f"{profile.educational_score:.1f}/100",
                         delta=CompetencyAssessment.LEVELS[profile.educational_level]["name"])
            with col3:
                st.metric("📊 Genel Skor", 
                         f"{profile.overall_score:.1f}/100")
            
            # Güçlü/Zayıf yön analizi (AKILLI MESAJLAR)
            col1, col2 = st.columns(2)
            
            # Skorlara göre mesaj
            if profile.technical_score < 40 and profile.educational_score < 40:
                # İkisi de zayıf
                with col1:
                    st.warning(f"📊 **Daha Az Zayıf:** {profile.dominant_domain.title()} ({profile.technical_score if profile.dominant_domain == 'technical' else profile.educational_score:.0f}/100)")
                with col2:
                    st.error(f"⚠️ **Daha Zayıf:** {profile.weak_domain.title()} ({profile.educational_score if profile.weak_domain == 'educational' else profile.technical_score:.0f}/100)")
                st.caption("💡 Her iki alanda da gelişim gerekiyor. Benzerlik modu: Daha az zayıf olduğunuz alandan. Tamamlayıcı: Çok zayıf olduğunuz alandan.")
            else:
                # En az biri güçlü
                with col1:
                    st.success(f"💪 **Güçlü Yönünüz:** {profile.dominant_domain.title()}")
                with col2:
                    st.warning(f"📈 **Gelişim Alanınız:** {profile.weak_domain.title()}")
            
            st.success("✅ Dual-domain profiliniz oluşturuldu! Artık iki farklı strateji ile persona tavsiyeleri görebilirsiniz.")
            
            # Önerilen persona'lar - DUAL MODE
            st.markdown("### 🎯 Sizin İçin Önerilen Persona'lar (Dual-Mode)")
            st.caption("🔬 İki farklı strateji ile matematiksel olarak hesaplanmıştır")
            
            st.info("""
            **📚 Mod 1: Benzerlik Bazlı** → Sizin seviyenize uygun, rahat çalışabileceğiniz  
            **🧩 Mod 2: Tamamlayıcı Bazlı** → Eksiklerinizi kapatacak, yeni şeyler öğretecek
            """)
            
            assessment = CompetencyAssessment()
            
            # Profil dictionary'si oluştur (DUAL DOMAIN)
            profile_dict = {
                "score": profile.overall_score,
                "technical_score": profile.technical_score,
                "educational_score": profile.educational_score,
                "level": profile.technical_level,  # Ana seviye olarak teknik kullan
                "domain": profile.dominant_domain,
                "weak_domain": profile.weak_domain,
                "responses": profile.responses
            }
            
            # Her iki mod için de tavsiye al
            from recommendation_engine import RecommendationEngine
            rec_engine = RecommendationEngine()
            user_vec = rec_engine.create_user_vector(profile_dict)
            
            # Mod 1: Similarity - DOMINANT domain'e göre filtrele!
            rankings_similarity = []
            
            # Kullanıcının dominant domain'ine göre persona'ları filtrele
            # Eğer technical güçlüyse (veya daha az zayıf), technical persona'lar
            # Eğer educational güçlüyse, educational persona'lar
            preferred_category = "technology" if profile.dominant_domain == "technical" else "education"
            
            for persona_id, persona_vec in rec_engine.persona_vectors.items():
                # Persona'nın kategorisini al
                persona_obj = next((p for p in get_all_personas() if p.id == persona_id), None)
                
                # Similarity modunda: aynı kategoriden persona'ları öner
                if persona_obj and persona_obj.category == preferred_category:
                    score_dict = rec_engine.calculate_recommendation_score(
                        user_vec, persona_vec, mode="similarity"
                    )
                    rankings_similarity.append({
                        "persona_id": persona_id,
                        "score": score_dict["total_score"],
                        "components": score_dict["components"],
                        "mode": score_dict["mode"]
                    })
            
            rankings_similarity.sort(key=lambda x: x["score"], reverse=True)
            
            # Mod 2: Complementary - WEAK domain'den persona'ları öner!
            rankings_complementary = []
            
            # Kullanıcının weak domain'ine göre persona'ları filtrele
            # Zayıf olduğunuz alanda güçlü olan persona'lar
            complementary_category = "education" if profile.weak_domain == "educational" else "technology"
            
            for persona_id, persona_vec in rec_engine.persona_vectors.items():
                # Persona'nın kategorisini al
                persona_obj = next((p for p in get_all_personas() if p.id == persona_id), None)
                
                # Complementary modunda: KARŞI kategoriden persona'ları öner
                if persona_obj and persona_obj.category == complementary_category:
                    score_dict = rec_engine.calculate_recommendation_score(
                        user_vec, persona_vec, mode="complementary"
                    )
                    rankings_complementary.append({
                        "persona_id": persona_id,
                        "score": score_dict["total_score"],
                        "components": score_dict["components"],
                        "mode": score_dict["mode"]
                    })
            
            rankings_complementary.sort(key=lambda x: x["score"], reverse=True)
            
            # İki kolonda göster
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📚 Mod 1: Benzerlik Bazlı")
                
                # Akıllı açıklama
                if profile.technical_score < 40 and profile.educational_score < 40:
                    st.markdown(f"*Daha az zayıf olduğunuz alana ({profile.dominant_domain.title()}) benzer - rahat çalışabileceğiniz*")
                else:
                    st.markdown(f"*Güçlü yönünüze ({profile.dominant_domain.title()}) uygun*")
                
                for idx, ranking in enumerate(rankings_similarity[:3], 1):
                    persona = next((p for p in get_all_personas() if p.id == ranking["persona_id"]), None)
                    if persona:
                        # Kategori badge
                        cat_badge = "🔗 Teknik" if persona.category == "technology" else "🎓 Eğitim"
                        st.markdown(f"**{idx}. {persona.avatar} {persona.name}** `{cat_badge}`")
                        st.metric("Skor", f"{ranking['score']:.3f}")
                        st.caption(f"Benzerlik: {ranking['components']['similarity']:.3f}")
                        st.markdown("---")
            
            with col2:
                st.markdown("### 🧩 Mod 2: Tamamlayıcı Bazlı")
                
                # Akıllı açıklama
                if profile.technical_score < 40 and profile.educational_score < 40:
                    st.markdown(f"*Çok zayıf olduğunuz alanı ({profile.weak_domain.title()}) güçlendirecek - zorlayıcı ama gerekli*")
                else:
                    st.markdown(f"*Zayıf yönünüzü ({profile.weak_domain.title()}) güçlendirecek*")
                
                for idx, ranking in enumerate(rankings_complementary[:3], 1):
                    persona = next((p for p in get_all_personas() if p.id == ranking["persona_id"]), None)
                    if persona:
                        # Kategori badge
                        cat_badge = "🔗 Teknik" if persona.category == "technology" else "🎓 Eğitim"
                        st.markdown(f"**{idx}. {persona.avatar} {persona.name}** `{cat_badge}`")
                        st.metric("Skor", f"{ranking['score']:.3f}")
                        st.caption(f"Tamamlayıcılık: {ranking['components']['complementarity']:.3f}")
                        st.markdown("---")
            
            st.markdown("---")
            
            # Karşılaştırmalı analiz
            st.markdown("### 📊 Dual-Mode Karşılaştırma")
            
            compare_data = []
            for i in range(min(5, len(rankings_similarity))):
                sim_persona = next((p for p in get_all_personas() if p.id == rankings_similarity[i]["persona_id"]), None)
                comp_persona = next((p for p in get_all_personas() if p.id == rankings_complementary[i]["persona_id"]), None)
                
                compare_data.append({
                    "Sıra": i+1,
                    "Benzerlik Modu": f"{sim_persona.avatar if sim_persona else ''} {sim_persona.name if sim_persona else ''}",
                    "Sim Skor": f"{rankings_similarity[i]['score']:.3f}",
                    "Tamamlayıcı Modu": f"{comp_persona.avatar if comp_persona else ''} {comp_persona.name if comp_persona else ''}",
                    "Comp Skor": f"{rankings_complementary[i]['score']:.3f}"
                })
            
            df_compare = pd.DataFrame(compare_data)
            st.dataframe(df_compare, use_container_width=True, hide_index=True)
            
            st.caption("""
            **💡 Nasıl Seçmeliyim?**
            - **Rahat öğrenmek** istiyorsanız → Benzerlik Modu
            - **Hızlı gelişmek** istiyorsanız → Tamamlayıcı Modu
            - **Dengeyi** istiyorsanız → Her ikisinden de deneyin!
            """)
            
            # İyileştirme ipuçları - Dual domain
            st.markdown("### 💡 Sizin İçin Öneriler")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### 🔗 Blockchain/Teknik ({profile.technical_level.replace('_', ' ').title()})")
                tech_tips = assessment.generate_improvement_tips(profile.technical_level, "technical")
                for tip in tech_tips[:3]:
                    st.markdown(f"- {tip}")
            
            with col2:
                st.markdown(f"#### 🎓 Eğitim/Pedagoji ({profile.educational_level.replace('_', ' ').title()})")
                edu_tips = assessment.generate_improvement_tips(profile.educational_level, "educational")
                for tip in edu_tips[:3]:
                    st.markdown(f"- {tip}")

            # ============ COGNITIVE LOAD THEORY ANALYSIS (NEW!) ============
            st.markdown("---")
            st.markdown("### 🧠 Bilişsel Yük Analizi (Cognitive Load Theory)")
            st.caption("📚 Sweller (1988) - Her persona için bilişsel yük hesaplaması")

            with st.expander("ℹ️ Bilişsel Yük Teorisi Nedir?", expanded=False):
                st.markdown("""
                **Cognitive Load Theory (Sweller, 1988)**, öğrenme sırasında beynin bilgi işleme kapasitesini
                3 bileşene ayırır:

                - **Intrinsic Load (IL)** 🎯: Görevin doğal karmaşıklığından kaynaklanan yük
                - **Extraneous Load (EL)** ⚠️: Kötü tasarımdan kaynaklanan gereksiz yük
                - **Germane Load (GL)** ✅: Öğrenmeye yönelik yararlı yük

                **Optimal Öğrenme Bölgesi:**
                `IL + GL ≤ Bilişsel Kapasite` VE `EL < 0.3`

                **Formül:** `Total Load = IL + EL - GL`
                """)

            # Task complexity seçimi
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption("Görev karmaşıklığını seçin:")
            with col2:
                task_complexity = st.select_slider(
                    "Karmaşıklık",
                    options=[0.3, 0.5, 0.7, 0.9],
                    value=0.5,
                    format_func=lambda x: {0.3: "Basit", 0.5: "Orta", 0.7: "Karmaşık", 0.9: "Çok Karmaşık"}[x],
                    label_visibility="collapsed"
                )

            # CLT-optimal persona'ları hesapla
            clt_rankings = rec_engine.get_clt_optimal_personas(
                user_vec,
                task_complexity=task_complexity,
                top_k=10
            )

            # En iyi 3 persona göster
            st.markdown("#### 🏆 CLT-Optimal Persona Sıralaması")

            for idx, ranking in enumerate(clt_rankings[:3], 1):
                persona_id = ranking['persona_id']
                clt_score = ranking['clt_score']
                clt_analysis = ranking['clt_analysis']

                persona = next((p for p in get_all_personas() if p.id == persona_id), None)
                if persona:
                    cat_badge = "🔗 Teknik" if persona.category == "technology" else "🎓 Eğitim"

                    with st.container():
                        st.markdown(f"**{idx}. {persona.avatar} {persona.name}** `{cat_badge}`")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("CLT Skor", f"{clt_score:.3f}")
                        with col2:
                            st.metric("IL", f"{clt_analysis['intrinsic_load']:.3f}")
                        with col3:
                            st.metric("EL", f"{clt_analysis['extraneous_load']:.3f}")
                        with col4:
                            st.metric("GL", f"{clt_analysis['germane_load']:.3f}")

                        # Optimal zone indicator
                        if clt_analysis['is_in_optimal_zone']:
                            st.success("✅ Optimal Öğrenme Bölgesinde")
                        elif clt_analysis['is_overloaded']:
                            st.error(f"⚠️ Bilişsel Aşırı Yüklenme ({clt_analysis['overload_amount']:.3f})")
                        elif clt_analysis['is_underloaded']:
                            st.warning("ℹ️ Çok kolay - kapasite kullanılmıyor")

                        # Recommendations
                        if clt_analysis['recommendations']:
                            st.caption(f"💡 {clt_analysis['recommendations'][0]}")

                        st.markdown("---")

            # Görselleştirme - Tüm persona'lar için CLT bileşenleri
            st.markdown("#### 📊 Tüm Persona'lar için CLT Karşılaştırma")

            # Data hazırla
            persona_names = []
            intrinsic_loads = []
            extraneous_loads = []
            germane_loads = []
            total_loads = []

            for ranking in clt_rankings:
                persona = next((p for p in get_all_personas() if p.id == ranking['persona_id']), None)
                if persona:
                    persona_names.append(f"{persona.avatar} {persona.name[:15]}")
                    intrinsic_loads.append(ranking['clt_analysis']['intrinsic_load'])
                    extraneous_loads.append(ranking['clt_analysis']['extraneous_load'])
                    germane_loads.append(ranking['clt_analysis']['germane_load'])
                    total_loads.append(ranking['clt_analysis']['total_load'])

            # Stacked bar chart
            fig = go.Figure()

            fig.add_trace(go.Bar(
                name='Intrinsic Load',
                x=persona_names,
                y=intrinsic_loads,
                marker_color='#FF6B6B',
                text=[f"{val:.2f}" for val in intrinsic_loads],
                textposition='inside'
            ))

            fig.add_trace(go.Bar(
                name='Extraneous Load',
                x=persona_names,
                y=extraneous_loads,
                marker_color='#FFA94D',
                text=[f"{val:.2f}" for val in extraneous_loads],
                textposition='inside'
            ))

            fig.add_trace(go.Bar(
                name='Germane Load (Beneficial)',
                x=persona_names,
                y=[-gl for gl in germane_loads],  # Negative to show it reduces total load
                marker_color='#4ECDC4',
                text=[f"{val:.2f}" for val in germane_loads],
                textposition='inside'
            ))

            # Add capacity line
            capacity = user_vec.cognitive_capacity
            fig.add_shape(
                type="line",
                x0=-0.5,
                x1=len(persona_names)-0.5,
                y0=capacity,
                y1=capacity,
                line=dict(color="red", width=2, dash="dash"),
            )

            fig.add_annotation(
                x=len(persona_names)-1,
                y=capacity,
                text=f"Bilişsel Kapasite: {capacity:.2f}",
                showarrow=False,
                xanchor="left"
            )

            fig.update_layout(
                title="Cognitive Load Bileşenleri (Sweller, 1988)",
                xaxis_title="Persona",
                yaxis_title="Yük Miktarı",
                barmode='relative',
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption("""
            📊 **Grafik Açıklaması:**
            - 🔴 Kırmızı = Intrinsic Load (görev zorluğu)
            - 🟠 Turuncu = Extraneous Load (tasarım problemi)
            - 🔵 Mavi (aşağı) = Germane Load (öğrenmeye yardımcı - total load'u azaltır)
            - ➖ Kırmızı çizgi = Sizin bilişsel kapasiteniz
            - ✅ Çizginin altında kalan = Optimal
            """)

            # Detaylı tablo
            with st.expander("📋 Detaylı CLT Analiz Tablosu", expanded=False):
                clt_table_data = []
                for ranking in clt_rankings:
                    persona = next((p for p in get_all_personas() if p.id == ranking['persona_id']), None)
                    if persona:
                        clt_table_data.append({
                            "Persona": f"{persona.avatar} {persona.name}",
                            "CLT Skor": f"{ranking['clt_score']:.3f}",
                            "IL": f"{ranking['clt_analysis']['intrinsic_load']:.3f}",
                            "EL": f"{ranking['clt_analysis']['extraneous_load']:.3f}",
                            "GL": f"{ranking['clt_analysis']['germane_load']:.3f}",
                            "Total": f"{ranking['clt_analysis']['total_load']:.3f}",
                            "Optimal": "✅" if ranking['clt_analysis']['is_in_optimal_zone'] else "❌"
                        })

                df_clt = pd.DataFrame(clt_table_data)
                st.dataframe(df_clt, use_container_width=True, hide_index=True)

            # ============ END OF CLT ANALYSIS ============

            # Profili sıfırla butonu
            if st.button("🔄 Değerlendirmeyi Yeniden Yap"):
                st.session_state.user_profile = None
                st.session_state.assessment_completed = False
                st.rerun()
        
        else:
            # Değerlendirme anketi
            st.markdown("### 📝 Dual-Domain Değerlendirme Anketi")
            
            st.info("""
            🎓 **Araştırma Hakkında**: "Blockchain Tabanlı Eğitim Teknolojilerinde İnsan-AI İşbirliği"
            
            Bu değerlendirme **HEM teknik HEM pedagojik** yetkinliğinizi ölçer.
            Böylece güçlü/zayıf yönlerinizi görebilir ve en uygun persona'ları bulabilirsiniz.
            """)
            
            st.markdown("---")
            st.markdown("## 🔗 BÖLÜM 1: Blockchain/Teknik Yetkinlik")
            st.caption("Blockchain, smart contract ve yazılım geliştirme becerileriniz")
            
            # Teknik soruları göster
            assessment = CompetencyAssessment()
            responses = {}
            
            for q in assessment.TECHNICAL_QUESTIONS:
                st.markdown(f"**{q['question']}**")
                selected = st.radio(
                    "Seçiminiz:",
                    [opt[0] for opt in q['options']],
                    key=q['id'],
                    label_visibility="collapsed"
                )
                selected_score = next(opt[1] for opt in q['options'] if opt[0] == selected)
                responses[q['id']] = selected_score
                st.markdown("")
            
            st.markdown("---")
            st.markdown("## 🎓 BÖLÜM 2: Eğitim/Pedagojik Yetkinlik")
            st.caption("Eğitim teknolojileri ve pedagojik yaklaşım becerileriniz")
            
            # Eğitim soruları göster
            for q in assessment.EDUCATIONAL_QUESTIONS:
                st.markdown(f"**{q['question']}**")
                selected = st.radio(
                    "Seçiminiz:",
                    [opt[0] for opt in q['options']],
                    key=q['id'],
                    label_visibility="collapsed"
                )
                selected_score = next(opt[1] for opt in q['options'] if opt[0] == selected)
                responses[q['id']] = selected_score
                st.markdown("")
            
            # Bonus sorular
            st.markdown("---")
            st.markdown("### Ek Bilgiler (Opsiyonel)")
            
            col1, col2 = st.columns(2)
            with col1:
                ai_exp = st.checkbox("AI/LLM kullanma deneyimim var (ChatGPT, Claude vb.)")
                if ai_exp:
                    responses["ai_experience"] = True
            
            with col2:
                prompt_exp = st.checkbox("Prompt engineering hakkında bilgim var")
                if prompt_exp:
                    responses["prompt_experience"] = True
            
            # Kullanım amacı
            goal = st.radio(
                "Ana amacınız nedir?",
                ["Öğrenme ve gelişim", "Üretim/Production kodu"],
                horizontal=True
            )
            goal_key = "learning" if "Öğrenme" in goal else "production"
            
            # Değerlendirme butonu
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📊 Değerlendirmeyi Tamamla", type="primary", use_container_width=True):
                    # Profil oluştur (DUAL DOMAIN)
                    import uuid
                    user_id = str(uuid.uuid4())
                    
                    profile = assessment.create_profile(
                        user_id=user_id,
                        responses=responses,
                        goal=goal_key
                    )
                    
                    # Session state'e kaydet
                    st.session_state.user_profile = profile
                    st.session_state.assessment_completed = True
                    
                    # Dosyaya kaydet (araştırma için)
                    try:
                        assessment.save_profile(profile)
                    except Exception as e:
                        st.warning(f"Profil kaydedilemedi (devam edebilirsiniz): {e}")
                    
                    st.rerun()
    
    # TAB 2: Kod Üretimi
    with tab2:
        st.markdown("## 🎯 Kod Üretim Görevi")
        
        # Örnek görevler - Blockchain & Eğitim Odaklı
        example_tasks = [
            "Seçiniz...",
            "🎓 Solidity: Öğrenci diploması doğrulama smart contract'ı yaz",
            "📜 Solidity: Sertifika yönetim sistemi (mint, verify, revoke)",
            "🏫 Solidity: Eğitim kurumu kayıt ve not sistemi",
            "💰 Solidity: Burs dağıtım ve takip smart contract'ı",
            "📚 Solidity: Kütüphane kitap ödünç verme sistemi",
            "🎯 Solidity: Öğrenci başarı rozetleri (NFT-based achievement)",
            "👥 Solidity: Çoklu-imza eğitim fonu yönetimi",
            "🔐 Python: Web3.py ile diploma doğrulama API'si",
            "📊 Python: Blockchain'den eğitim verisi analizi",
            "⚡ Solidity: Gas-optimized toplu sertifika verme"
        ]
        
        selected_example = st.selectbox("📝 Örnek Görevler", example_tasks)
        
        task = st.text_area(
            "Kod Yazılacak Görev/Problem",
            value="" if selected_example == "Seçiniz..." else selected_example,
            height=150,
            placeholder="Örnek: Bir binary search tree implementasyonu yaz...",
            help="10 persona bu görevi farklı perspektiflerle çözecek"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            generate_btn = st.button("🚀 Kodları Üret", type="primary", use_container_width=True)
        with col2:
            clear_btn = st.button("🗑️ Temizle", use_container_width=True)
        with col3:
            if st.session_state.generated_codes:
                if st.button("💾 Kaydet", use_container_width=True):
                    st.success("✓ Sonuçlar kaydedildi!")
        
        if clear_btn:
            st.session_state.generated_codes = None
            st.session_state.evaluated_results = None
            st.session_state.rankings = None
            st.rerun()
        
        if generate_btn:
            if not task or task == "Seçiniz...":
                st.error("❌ Lütfen bir görev girin!")
            elif not api_key:
                st.error("❌ Lütfen OpenAI API anahtarı girin!")
            else:
                try:
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 1. Kod üretimi
                    status_text.text(f"⏳ Kodlar üretiliyor... ({provider} - {model})")
                    progress_bar.progress(25)

                    if provider_name == "openai":
                        generator = CodeGenerator(api_key=api_key, model=model, provider="openai")
                    else:
                        generator = CodeGenerator(anthropic_key=api_key, model=model, provider="anthropic")

                    results = generator.generate_codes(task, active_personas)
                    st.session_state.generated_codes = results
                    
                    # 2. Değerlendirme
                    status_text.text("📊 Kodlar değerlendiriliyor...")
                    progress_bar.progress(50)
                    
                    evaluator = CodeEvaluator()
                    evaluated = evaluator.evaluate_all(results)
                    st.session_state.evaluated_results = evaluated
                    
                    # 3. Sıralama
                    status_text.text("🏆 Sıralamalar hesaplanıyor...")
                    progress_bar.progress(75)
                    
                    rankings = evaluator.get_rankings(evaluated)
                    st.session_state.rankings = rankings
                    
                    # 4. Tamamlandı
                    progress_bar.progress(100)
                    status_text.text("✅ Tamamlandı!")
                    
                    # Geçmişe ekle
                    st.session_state.task_history.append({
                        "task": task,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "persona_count": len(active_personas)
                    })
                    
                    st.success(f"✅ {len(results)} persona'dan kod üretimi tamamlandı!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
                    st.info("💡 .env dosyasında OPENAI_API_KEY tanımlı olduğundan emin olun")
    
    # TAB 3: Sonuçlar
    with tab3:
        st.markdown("## 📊 Üretilen Kodlar ve Değerlendirmeler")
        
        if st.session_state.evaluated_results:
            results = st.session_state.evaluated_results
            
            # Özet metrikler
            st.markdown("### 📈 Genel Bakış")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            avg_score = sum(r.get("total_score", 0) for r in results) / len(results)
            avg_quality = sum(r.get("quality_score", 0) for r in results) / len(results)
            
            # Yeni metrikler için ortalama
            comment_ratios = [r.get('metrics', {}).get('general', {}).get('comment_ratio', 0) for r in results]
            avg_comment = sum(comment_ratios) / len(comment_ratios) if comment_ratios else 0
            
            locs = [r.get('metrics', {}).get('general', {}).get('lines_of_code', 0) for r in results]
            avg_loc = sum(locs) / len(locs) if locs else 0
            
            type_hints = [r.get('metrics', {}).get('general', {}).get('type_hint_ratio', 0) for r in results]
            avg_type_hint = sum(type_hints) / len(type_hints) if type_hints else 0
            
            col1.metric("Ortalama Skor", f"{avg_score:.1f}/100")
            col2.metric("Kod Kalitesi", f"{avg_quality:.1f}/100")
            col3.metric("Yorum Oranı", f"{avg_comment:.1f}%")
            col4.metric("Ortalama LOC", f"{avg_loc:.0f}")
            col5.metric("Type Hint", f"{avg_type_hint:.1f}%")
            
            st.markdown("---")
            
            # Persona bazlı sonuçlar
            for idx, result in enumerate(results, 1):
                with st.expander(
                    f"{result.get('avatar', '👤')} {result.get('persona_name')} - "
                    f"Skor: {result.get('total_score', 0):.1f}/100",
                    expanded=(idx == 1)
                ):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**{result.get('persona_role')}**")
                        st.markdown(f"*Kategori: {result.get('category', 'N/A').title()}*")
                        
                        # Persona'nın yazdığı prompt
                        st.markdown("#### 💭 Bu Persona'nın Prompt'u")
                        st.info(f"**Kullanıcı görevi kendi perspektifinden şöyle yorumladı:**\n\n{result.get('persona_prompt', 'Prompt bulunamadı')}")
                        
                        # Kod
                        st.markdown("#### 💻 Bu Prompt ile Üretilen Kod")
                        st.code(result.get('code', 'Kod bulunamadı'), language='python')
                        
                        # İndirme butonu
                        st.download_button(
                            label="📥 Kodu İndir",
                            data=result.get('code', ''),
                            file_name=f"{result.get('persona_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                            mime="text/plain",
                            key=f"download_{result.get('persona_id')}"
                        )
                    
                    with col2:
                        st.markdown("#### 📊 Ayırt Edici Metrikler")
                        
                        general_metrics = result.get('metrics', {}).get('general', {})
                        quality_score = result.get('quality_score', 0)
                        
                        # Toplam Skor
                        total_score = result.get('total_score', 0)
                        st.metric("🎯 Toplam Skor", f"{total_score:.1f}/100")
                        
                        st.markdown("---")
                        
                        # Yeni ayırt edici metrikler
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            # Kod Kalitesi
                            st.metric("✨ Kod Kalitesi", f"{quality_score:.1f}/100")
                            st.caption("Pylint analizi")
                            
                            # Yorum Oranı
                            comment_ratio = general_metrics.get('comment_ratio', 0)
                            st.metric("📝 Yorum Oranı", f"{comment_ratio:.1f}%")
                            st.caption("Eğitimci: >25%, Teknik: <15%")
                            
                            # Satır Sayısı
                            loc = general_metrics.get('lines_of_code', 0)
                            st.metric("📏 Satır Sayısı", f"{loc}")
                            st.caption("Verbose vs Concise")
                        
                        with col_b:
                            # Type Hint Kullanımı
                            type_hint = general_metrics.get('type_hint_ratio', 0)
                            st.metric("🏷️ Type Hint", f"{type_hint:.1f}%")
                            st.caption("Profesyonellik göstergesi")
                            
                            # Docstring Kalitesi
                            docstring = general_metrics.get('docstring_score', 0)
                            st.metric("📖 Docstring", f"{docstring:.1f}/100")
                            st.caption("Dokümantasyon detayı")
                            
                            # Fonksiyon Sayısı
                            func_count = general_metrics.get('function_count', 0)
                            st.metric("🔢 Fonksiyon", f"{func_count}")
                            st.caption("Modülerlik göstergesi")
                        
                        st.markdown("---")
                        st.markdown("#### 🎓 Pedagojik Metrikler")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            # Öğrenme Kolaylığı
                            learning_ease = general_metrics.get('learning_ease', 0)
                            st.metric("📚 Öğrenme Kolaylığı", f"{learning_ease:.1f}/100")
                            st.caption("Kod ne kadar kolay öğrenilebilir?")
                            
                            # Bilişsel Yük
                            cognitive_load = general_metrics.get('cognitive_load_score', 0)
                            st.metric("🧠 Bilişsel Yük", f"{cognitive_load:.1f}/100")
                            st.caption("Düşük yük = kolay anlama (Sweller)")
                        
                        with col_b:
                            # Öğreticilik
                            instructiveness = general_metrics.get('instructiveness_index', 0)
                            st.metric("🎓 Öğreticilik", f"{instructiveness:.1f}/100")
                            st.caption("Ne kadar öğretici ve açıklayıcı?")
                            
                            # Örnek Kalitesi
                            example_quality = general_metrics.get('example_quality', 0)
                            st.metric("💡 Örnek Kalitesi", f"{example_quality:.1f}/100")
                            st.caption("Usage examples ve test cases")
                        
                        st.markdown("---")
                        
                        # Token kullanımı
                        if result.get('tokens_used'):
                            st.info(f"🎫 Token: {result.get('tokens_used')}")
                        
                        # Issues
                        issues = result.get('issues', [])
                        if issues:
                            st.warning(f"⚠️ {len(issues)} sorun tespit edildi")
                            for issue in issues[:3]:
                                st.caption(f"• {issue.get('message', 'N/A')}")
                            if len(issues) > 3:
                                st.caption(f"... ve {len(issues) - 3} sorun daha")
        else:
            st.info("👈 Önce bir görev tanımlayıp kod üretimi yapın")
    
    # TAB 4: Sıralamalar
    with tab4:
        st.markdown("## 🏆 Performans Sıralamaları")
        
        # Değerlendirme Metodolojisi
        with st.expander("📖 Değerlendirme Metodolojisi - Skorlar Nasıl Hesaplanır?", expanded=False):
            st.markdown("""
            ### 🎯 Toplam Skor Hesaplaması
            
            Toplam skor, 4 ana metriğin **ağırlıklı ortalaması**dır:
            
            ```
            Toplam Skor = (Güvenlik × 30%) + (Kalite × 30%) + 
                          (Karmaşıklık × 20%) + (Maintainability × 20%)
            ```
            
            ---
            
            ### 🔒 Güvenlik Skoru (Bandit)
            
            **Araç:** Python Bandit - Güvenlik zafiyet tarayıcı  
            **Başlangıç:** 100 puan  
            **Ceza Sistemi:**
            - 🔴 HIGH seviye zafiyet: **-20 puan**
            - 🟡 MEDIUM seviye zafiyet: **-10 puan**
            - 🟢 LOW seviye zafiyet: **-5 puan**
            
            **Örnek:** 1 HIGH + 2 MEDIUM zafiyet = 100 - 20 - 20 = **60 puan**
            
            **Kontrol Edilen Sorunlar:**
            - SQL Injection
            - Hardcoded passwords
            - eval/exec kullanımı
            - Güvensiz deserialization
            - Shell injection
            
            ---
            
            ### ✨ Kod Kalitesi (Pylint)
            
            **Araç:** Pylint - Python kod kalitesi analiz aracı  
            **Başlangıç:** 100 puan  
            **Ceza Sistemi:**
            - ❌ ERROR: **-10 puan**
            - ⚠️ WARNING: **-5 puan**
            - 📋 CONVENTION: **-2 puan**
            - 🔧 REFACTOR: **-3 puan**
            
            **Kontrol Edilen Sorunlar:**
            - PEP 8 uyumsuzlukları
            - Kullanılmayan değişkenler
            - Yanlış import'lar
            - Kod duplikasyonu
            - Naming conventions
            
            ---
            
            ### 🔄 Karmaşıklık Skoru (Radon - Cyclomatic Complexity)
            
            **Araç:** Radon - Kod karmaşıklık analizi  
            **Metrik:** Ortalama Cyclomatic Complexity  
            
            **Skor Tablosu:**
            - **Ortalama 1-5:** 100 puan (A - Mükemmel)
            - **Ortalama 6-10:** 80 puan (B - İyi)
            - **Ortalama 11-20:** 60 puan (C - Orta)
            - **Ortalama 21+:** 40 puan veya daha az (D/F - Zayıf)
            
            **Ne Ölçer:**
            - Fonksiyonlardaki karar noktası sayısı
            - if, elif, else, for, while, and, or
            - Düşük complexity = daha okunabilir ve test edilebilir kod
            
            ---
            
            ### 🔧 Maintainability Index (Radon)
            
            **Araç:** Radon - Sürdürülebilirlik indeksi  
            **Aralık:** 0-100 (yüksek = iyi)  
            
            **Not Sistemi:**
            - **80-100:** A (Mükemmel - Sürdürülmesi kolay)
            - **60-79:** B (İyi)
            - **40-59:** C (Orta)
            - **20-39:** D (Zor)
            - **0-19:** F (Çok zor)
            
            **Hesaplama Faktörleri:**
            - Halstead volume (kod hacmi)
            - Cyclomatic complexity
            - Satır sayısı
            - Yorum oranı
            
            ---
            
            ### 💡 Skor Yorumlama Rehberi
            
            **90-100:** 🌟 Mükemmel - Production-ready  
            **75-89:** ✅ İyi - Küçük iyileştirmelerle hazır  
            **60-74:** ⚠️ Orta - Refactoring önerilir  
            **45-59:** 🔴 Zayıf - Önemli iyileştirme gerekli  
            **0-44:** ❌ Çok Zayıf - Yeniden yazılmalı  
            """)
        
        if st.session_state.rankings:
            rankings = st.session_state.rankings
            
            # Genel sıralama
            st.markdown("### 🥇 Genel Sıralama")
            
            overall = rankings['overall_ranking']
            if overall:
                # DataFrame oluştur
                ranking_data = []
                for idx, persona in enumerate(overall, 1):
                    general_metrics = persona.get('metrics', {}).get('general', {})
                    
                    ranking_data.append({
                        "Sıra": f"{'🥇' if idx==1 else '🥈' if idx==2 else '🥉' if idx==3 else str(idx)}",
                        "Persona": f"{persona.get('avatar', '👤')} {persona.get('persona_name')}",
                        "Kategori": persona.get('category', 'N/A').title(),
                        "Toplam": f"{persona.get('total_score', 0):.1f}",
                        "Kalite": f"{persona.get('quality_score', 0):.1f}",
                        "LOC": f"{general_metrics.get('lines_of_code', 0)}",
                        "Yorum %": f"{general_metrics.get('comment_ratio', 0):.1f}",
                        "📚 Öğrenme": f"{general_metrics.get('learning_ease', 0):.1f}",
                        "🧠 Bil.Yük": f"{general_metrics.get('cognitive_load_score', 0):.1f}",
                        "🎓 Öğretici": f"{general_metrics.get('instructiveness_index', 0):.1f}"
                    })
                
                df = pd.DataFrame(ranking_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Görselleştirme
                st.markdown("### 📊 Görselleştirme")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Bar chart - Toplam skorlar
                    fig_bar = go.Figure(data=[
                        go.Bar(
                            x=[p.get('persona_name') for p in overall],
                            y=[p.get('total_score', 0) for p in overall],
                            marker_color=[
                                '#FFD700' if i == 0 else '#C0C0C0' if i == 1 else '#CD7F32' if i == 2 else '#667eea'
                                for i in range(len(overall))
                            ],
                            text=[f"{p.get('total_score', 0):.1f}" for p in overall],
                            textposition='auto',
                        )
                    ])
                    fig_bar.update_layout(
                        title="Toplam Skorlar",
                        xaxis_title="Persona",
                        yaxis_title="Skor",
                        height=400
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Radar chart - Ayırt edici metrikler karşılaştırması
                    if len(overall) >= 3:
                        top3 = overall[:3]
                        categories = ['Kalite', 'Yorum %', 'Type Hint %', 'Docstring', 'Modülerlik']
                        
                        fig_radar = go.Figure()
                        
                        for persona in top3:
                            general_m = persona.get('metrics', {}).get('general', {})
                            # Fonksiyon sayısını normalize et (max 10 fonksiyon = 100)
                            func_normalized = min(general_m.get('function_count', 0) * 20, 100)
                            
                            fig_radar.add_trace(go.Scatterpolar(
                                r=[
                                    persona.get('quality_score', 0),
                                    general_m.get('comment_ratio', 0) * 2,  # %50 = 100 puan
                                    general_m.get('type_hint_ratio', 0),
                                    general_m.get('docstring_score', 0),
                                    func_normalized
                                ],
                                theta=categories,
                                fill='toself',
                                name=persona.get('persona_name')
                            ))
                        
                        fig_radar.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            title="Top 3 Metrik Karşılaştırması",
                            height=400
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)
                
                # Kategori bazlı en iyiler
                st.markdown("### 🎖️ Kategori Şampiyonları")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🎓 Eğitim Bilimcileri")
                    best_edu = rankings.get('best_education')
                    if best_edu:
                        st.success(f"""
                        **{best_edu.get('avatar', '👤')} {best_edu.get('persona_name')}**  
                        Skor: {best_edu.get('total_score', 0):.1f}/100
                        """)
                
                with col2:
                    st.markdown("#### 💻 Teknoloji Uzmanları")
                    best_tech = rankings.get('best_technology')
                    if best_tech:
                        st.success(f"""
                        **{best_tech.get('avatar', '👤')} {best_tech.get('persona_name')}**  
                        Skor: {best_tech.get('total_score', 0):.1f}/100
                        """)
                
                # Metrik bazlı en iyiler
                st.markdown("### 🎯 Metrik Liderleri")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    best_sec = rankings.get('best_security')
                    if best_sec:
                        st.info(f"""
                        **🔒 En Güvenli**  
                        {best_sec.get('persona_name')}  
                        {best_sec.get('security_score', 0):.1f}/100
                        """)
                
                with col2:
                    best_qual = rankings.get('best_quality')
                    if best_qual:
                        st.info(f"""
                        **✨ En Kaliteli**  
                        {best_qual.get('persona_name')}  
                        {best_qual.get('quality_score', 0):.1f}/100
                        """)
                
                with col3:
                    best_comp = rankings.get('best_complexity')
                    if best_comp:
                        st.info(f"""
                        **🔄 En Basit**  
                        {best_comp.get('persona_name')}  
                        {best_comp.get('complexity_score', 0):.1f}/100
                        """)
                
                with col4:
                    best_main = rankings.get('best_maintainability')
                    if best_main:
                        st.info(f"""
                        **🔧 En Sürdürülebilir**  
                        {best_main.get('persona_name')}  
                        {best_main.get('maintainability_index', 0):.1f}/100
                        """)
        else:
            st.info("👈 Önce bir görev tanımlayıp kod üretimi yapın")
    
    # TAB 5: Çoklu LLM Testleri
    with tab5:
        st.markdown("## 🤖 Çoklu LLM Karşılaştırma Testleri")
        st.markdown("*Aynı persona, aynı görev, farklı LLM'ler - Performans karşılaştırması*")
        
        st.info("""
        **🔬 Araştırma Değeri:** Bu bölüm, farklı LLM'lerin aynı persona karakteristiğini 
        ne kadar iyi yansıttığını ve performans farklılıklarını ölçmenizi sağlar.
        """)
        
        # LLM Engine başlat
        llm_engine = MultiLLMEngine()
        available_models = llm_engine.get_available_models()
        
        # API Key kontrolü
        st.markdown("### 🔑 API Anahtarları")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.text("OpenAI:")
            st.text("✅" if llm_engine.openai_client else "❌")
        with col2:
            st.text("Anthropic:")
            st.text("✅" if llm_engine.anthropic_client else "❌")
        with col3:
            st.text("Google:")
            st.text("✅" if llm_engine.google_client else "❌")
        with col4:
            st.text("X.AI Grok:")
            st.text("✅" if llm_engine.grok_key else "❌")
        
        st.markdown("---")
        
        # Test ayarları
        st.markdown("### ⚙️ Test Ayarları")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Görev
            test_task = st.text_area(
                "Test Görevi",
                value="İki sayının toplamını hesaplayan bir fonksiyon yaz",
                height=100,
                help="Tüm LLM'ler bu görevi alacak"
            )
            
            # Persona seçimi
            personas = get_all_personas()
            persona_options = [f"{p.avatar} {p.name}" for p in personas]
            selected_persona_name = st.selectbox("Persona Seçin", persona_options)
            selected_persona = personas[persona_options.index(selected_persona_name)]
        
        with col2:
            # Model seçimi
            st.markdown("**Test edilecek LLM'ler:**")
            
            selected_models = []
            
            if llm_engine.openai_client:
                if st.checkbox("OpenAI GPT-4o-mini", value=True):
                    selected_models.append("gpt-4o-mini")
                if st.checkbox("OpenAI GPT-4o"):
                    selected_models.append("gpt-4o")
            
            if llm_engine.anthropic_client:
                if st.checkbox("Claude 3 Sonnet"):
                    selected_models.append("claude-3-sonnet-20240229")
                if st.checkbox("Claude 3 Opus"):
                    selected_models.append("claude-3-opus-20240229")
            
            if llm_engine.google_client:
                if st.checkbox("Google Gemini Pro"):
                    selected_models.append("gemini-pro")
            
            if llm_engine.grok_key:
                if st.checkbox("X.AI Grok"):
                    selected_models.append("grok-beta")
            
            st.caption(f"Seçili: {len(selected_models)} model")
        
        # Test çalıştır
        st.markdown("---")
        
        if st.button("🚀 Çoklu LLM Testi Başlat", type="primary", use_container_width=True):
            if not selected_models:
                st.error("❌ En az bir model seçin!")
            else:
                with st.spinner(f"⏳ {len(selected_models)} LLM ile kod üretiliyor..."):
                    # Persona prompt oluştur
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        generator = CodeGenerator(api_key=api_key)
                        persona_prompt = generator._create_persona_specific_prompt(selected_persona, test_task)
                    else:
                        # API key yoksa basit prompt kullan
                        persona_prompt = f"{selected_persona.name} olarak: {test_task}"
                    
                    # Multi-LLM test
                    multi_results = llm_engine.generate_multi_llm(
                        selected_persona,
                        persona_prompt,
                        selected_models
                    )
                    
                    st.session_state.multi_llm_results = {
                        "task": test_task,
                        "persona": selected_persona,
                        "persona_prompt": persona_prompt,
                        "results": multi_results
                    }
                    
                    st.success(f"✅ {len(selected_models)} LLM'den kod üretimi tamamlandı!")
                    st.balloons()
        
        # Sonuçları göster
        if st.session_state.multi_llm_results:
            st.markdown("---")
            st.markdown("## 📊 Çoklu LLM Test Sonuçları")
            
            mlr = st.session_state.multi_llm_results
            
            st.markdown(f"**Görev:** {mlr['task']}")
            st.markdown(f"**Persona:** {mlr['persona'].avatar} {mlr['persona'].name}")
            st.markdown(f"**Persona Prompt:**")
            st.info(mlr['persona_prompt'])
            
            st.markdown("---")
            
            # Sonuç tablosu
            st.markdown("### 📋 LLM Karşılaştırma Tablosu")
            
            comparison_data = []
            for result in mlr['results']:
                if result.get('success'):
                    code = result.get('code', '')
                    comparison_data.append({
                        "Provider": result.get('provider'),
                        "Model": result.get('model'),
                        "Status": "✅",
                        "Tokens": result.get('tokens', 0),
                        "LOC": len([l for l in code.split('\n') if l.strip()]),
                        "Cost ($)": f"{llm_engine.calculate_cost(result.get('input_tokens', 0), result.get('output_tokens', 0), result.get('model')):.6f}"
                    })
                else:
                    comparison_data.append({
                        "Provider": result.get('provider'),
                        "Model": result.get('model'),
                        "Status": "❌",
                        "Tokens": 0,
                        "LOC": 0,
                        "Cost ($)": "0"
                    })
            
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)
            
            # Her LLM'in ürettiği kodu göster
            st.markdown("### 💻 Üretilen Kodlar")
            
            for result in mlr['results']:
                with st.expander(f"{result.get('provider')} - {result.get('model')}", expanded=False):
                    if result.get('success'):
                        st.code(result.get('code', 'Kod yok'), language='python')
                        st.caption(f"Tokens: {result.get('tokens', 0)} | Cost: ${llm_engine.calculate_cost(result.get('input_tokens', 0), result.get('output_tokens', 0), result.get('model')):.6f}")
                    else:
                        st.error(f"Hata: {result.get('error', 'Bilinmeyen hata')}")
    
    # TAB 6: Matematiksel Analizler
    with tab6:
        st.markdown("## 📐 İleri Seviye Matematiksel Analizler")
        st.markdown("*Doktora Araştırması: 6 Katmanlı Matematiksel Framework*")
        
        st.info("""
        **🔬 Matematiksel Framework Katmanları:**
        1. 👤 Kullanıcı Modelleme | 2. 💬 Prompt Analizi | 3. 🤝 Matching Algoritmaları
        4. 💻 Kod Analizi | 5. 📈 Performans Tahmini | 6. 👥 Grup Analizi
        """)
        
        if st.session_state.evaluated_results and len(st.session_state.evaluated_results) > 0:
            results = st.session_state.evaluated_results
            
            # Alt sekmeler - 6 katman
            sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6 = st.tabs([
                "👤 Kullanıcı",
                "💬 Prompt", 
                "🤝 Matching",
                "💻 Kod",
                "📈 Tahmin",
                "👥 Grup"
            ])
            
            # ==================== KATMAN 1: KULLANICI MODELLEME ====================
            with sub_tab1:
                st.markdown("## 👤 KATMAN 1: Kullanıcı Modelleme")
                st.markdown("*Kullanıcı yetkinliğinin matematiksel temsili*")
                
                st.markdown("---")
                
                if st.session_state.user_profile:
                    profile = st.session_state.user_profile
                    
                    # 1.1 Multi-dimensional User Vector
                    st.markdown("### 1.1 Çok Boyutlu Kullanıcı Vektörü")
                    st.latex(r"\vec{u} = [u_1, u_2, ..., u_n] \in \mathbb{R}^n")
                    
                    from recommendation_engine import RecommendationEngine
                    engine = RecommendationEngine()
                    
                    profile_dict = {
                        "score": profile.overall_score,
                        "technical_score": profile.technical_score,
                        "educational_score": profile.educational_score,
                        "level": profile.technical_level,
                        "domain": profile.dominant_domain,
                        "responses": profile.responses
                    }
                    
                    user_vec = engine.create_user_vector(profile_dict)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Temel Yetkinlikler:**")
                        st.metric("Technical Skill", f"{user_vec.technical_skill:.3f}")
                        st.metric("Domain Knowledge", f"{user_vec.domain_knowledge:.3f}")
                        st.metric("AI Experience", f"{user_vec.ai_experience:.3f}")
                        st.metric("Learning Goal", f"{user_vec.learning_goal:.3f}")
                    
                    with col2:
                        st.markdown("**Bilgi Türleri:**")
                        st.metric("Procedural (Nasıl)", f"{user_vec.procedural_knowledge:.3f}")
                        st.metric("Declarative (Ne)", f"{user_vec.declarative_knowledge:.3f}")
                        st.metric("Conditional (Ne zaman)", f"{user_vec.conditional_knowledge:.3f}")
                    
                    # Vektör görselleştirme
                    st.markdown("#### 📊 Kullanıcı Vektör Görselleştirmesi")
                    
                    vec_data = {
                        "Boyut": ["Technical", "Domain", "AI Exp", "Learning", "Procedural", "Declarative"],
                        "Değer": [
                            user_vec.technical_skill,
                            user_vec.domain_knowledge,
                            user_vec.ai_experience,
                            user_vec.learning_goal,
                            user_vec.procedural_knowledge,
                            user_vec.declarative_knowledge
                        ]
                    }
                    
                    fig = px.bar(vec_data, x="Boyut", y="Değer", 
                                title="User Vector Components",
                                color="Değer",
                                color_continuous_scale="Viridis")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # 1.2 Markov Chain - Öğrenme Yörüngesi
                    st.markdown("### 1.2 Markov Chain - Gelecek Seviye Tahmini")
                    st.latex(r"P^{(n)}_{ij} = P(X_n = j | X_0 = i)")
                    
                    # Dual explanation - ALT ALTA
                    st.markdown("##### 👶 Basit:")
                    st.info("""**5 adım sonra ne olursun?**
                    
                    Oyun gibi düşün:
                    - Şimdi Seviye 1'desin
                    - Her adımda yukarı çıkabilir veya kalabilirsin
                    - 5 adım sonra Seviye 2'de olma ihtimalin %60
                    - Seviye 3'te olma ihtimalin %30
                    
                    Matematik bize gelecekteki ihtimalleri gösteriyor!
                    """)
                    
                    st.markdown("##### 🎓 Akademik:")
                    st.success("""**Markov Chain Model (Markov, 1906)**
                    
                    n-adım geçiş olasılıkları Chapman-Kolmogorov denkleminden:
                    P⁽ⁿ⁾ = Pⁿ (matrix üstel)
                    
                    Memoryless property: Gelecek sadece şu anki duruma bağlı.
                    Öğrenme trajektorisi, discrete-time Markov chain olarak modellenir.
                    Absorbing state: Expert (erişildiğinde kalır).
                    
                    Transition probabilities empirik learning curve data'dan estimate edilir.
                    """)
                    
                    st.markdown("")
                    
                    future_probs = MarkovChainLearning.predict_future_level(profile.technical_level, steps=5)
                    
                    st.markdown(f"**Şu anki seviye:** {profile.technical_level}")
                    st.markdown("**5 adım sonra beklenen seviye dağılımı:**")
                    
                    prob_data = []
                    for level, prob in future_probs.items():
                        if prob > 0.01:
                            prob_data.append({
                                "Seviye": level.replace('_', ' ').title(),
                                "Olasılık": prob
                            })
                    
                    df_markov = pd.DataFrame(prob_data)
                    st.dataframe(df_markov, use_container_width=True, hide_index=True)
                    
                    # Görselleştirme
                    fig = px.bar(df_markov, x="Seviye", y="Olasılık",
                                title="Gelecek Seviye Olasılıkları (5 adım sonra)")
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning("⚠️ Önce yetkinlik değerlendirmesi yapın")
            
            # ==================== KATMAN 2: PROMPT ANALİZİ ====================
            with sub_tab2:
                st.markdown("## 💬 KATMAN 2: Prompt Analizi")
                st.markdown("*Prompt kalitesi ve çeşitliliğinin matematiksel ölçümü*")
                
                st.markdown("---")
                
                # 2.1 Prompt Diversity (Simpson's Index)
                st.markdown("### 2.1 Prompt Çeşitlilik Analizi")
                st.latex(r"D = 1 - \sum_{i=1}^{n} p_i^2 \quad \text{(Simpson's Diversity Index)}")
                
                prompts = [r.get('persona_prompt', '') for r in results if r.get('persona_prompt')]
                
                if prompts and len(prompts) > 1:
                    diversity = InformationTheoryAnalyzer.calculate_prompt_diversity(prompts)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Diversity Index", f"{diversity['diversity_index']:.4f}")
                    col2.metric("Jaccard Distance", f"{diversity['avg_jaccard_distance']:.4f}")
                    col3.metric("Unique Token Ratio", f"{diversity['unique_token_ratio']:.4f}")
                    
                    st.caption("""
                    **Yorumlama:**
                    - D → 1: Çok çeşitli prompt'lar (her persona farklı yaklaşım)
                    - D → 0: Benzer prompt'lar
                    """)
                    
                    st.markdown("---")
                    
                    # 2.2 Prompt'ları göster
                    st.markdown("### 2.2 Persona Prompt'larının Karşılaştırılması")
                    
                    for r in results[:5]:
                        with st.container():
                            st.markdown(f"**{r.get('avatar')} {r.get('persona_name')}**")
                            st.text_area(
                                "Prompt:",
                                r.get('persona_prompt', 'N/A'),
                                height=100,
                                key=f"prompt_view_{r.get('persona_id')}",
                                disabled=True
                            )
                            st.markdown("")
            
            # ==================== KATMAN 3: MATCHING ALGORİTMALARI ====================
            with sub_tab3:
                st.markdown("## 🤝 KATMAN 3: User-Persona Matching")
                st.markdown("*Optimal eşleştirme algoritmaları*")
                
                st.markdown("---")
                
                if st.session_state.user_profile:
                    profile = st.session_state.user_profile
                    
                    # 3.1 Recommendation Score Breakdown
                    st.markdown("### 3.1 Ana Tavsiye Formülü")
                    st.latex(r"R(u,p) = \alpha \cdot S(u,p) + \beta \cdot C(u,p) + \gamma \cdot P(u,p) + \delta \cdot L(u,t)")
                    
                    # Dual explanation - ALT ALTA
                    st.markdown("##### 👶 Basit Açıklama:")
                    st.info("""
                    **Arkadaş seçimi gibi!**
                    
                    Sana uygun AI persona'yı 4 şeye bakarak seçiyoruz:
                    1. **Benzerlik (30%):** Sana ne kadar benziyor?
                    2. **Seviye Uyumu (35%):** Çok kolay/zor değil mi?
                    3. **Başarı Tahmini (25%):** İyi iş çıkarır mı?
                    4. **Öğrenme (10%):** Birlikte öğrenebilir misiniz?
                    
                    Her birinin önemi farklı (yüzdeler). Toplamı skor!
                    """)
                    
                    st.markdown("##### 🎓 Akademik Açıklama:")
                    st.success("""
                    **Multi-Criteria Decision Analysis (MCDA)**
                    
                    Recommendation score, dört ortogonal bileşenin ağırlıklı 
                    lineer kombinasyonudur. Her bileşen farklı teorik temel:
                    - S: Cosine+Euclidean hybrid distance (Salton, 1989)
                    - C: Gaussian ZPD matching (Vygotsky, 1978)
                    - P: Sigmoid regression prediction (logistic model)
                    - L: Exponential growth trajectory (Newell & Rosenbloom, 1981)
                    
                    Ağırlıklar (α,β,γ,δ) Bayesian optimization ile optimize edilir.
                    """)
                    
                    st.markdown("**Formül Bileşenleri:**")
                    st.markdown("- **S(u,p)**: Similarity Score (Benzerlik)")
                    st.markdown("- **C(u,p)**: Competency Match (Yetkinlik Uyumu)")
                    st.markdown("- **P(u,p)**: Performance Prediction (Performans Tahmini)")
                    st.markdown("- **L(u,t)**: Learning Trajectory (Öğrenme Yörüngesi)")
                    
                    st.markdown("**Ağırlıklar:** α=0.30, β=0.35, γ=0.25, δ=0.10")
                    
                    st.markdown("---")
                    
                    # 3.2 Similarity Matrix
                    st.markdown("### 3.2 Benzerlik Matrisi (Cosine + Euclidean)")
                    st.latex(r"sim(u,p) = w_1 \cdot \cos(u,p) + w_2 \cdot (1 - d_{euc}(u,p))")
                    
                    # Dual explanation - ALT ALTA
                    st.markdown("##### 👶 Basit:")
                    st.info("""**İki arkadaşın ne kadar benzer?**
                    
                    İki şeye bakıyoruz:
                    1. **Yön benzerliği:** Aynı yöne mi gidiyorsunuz? (okulta sınıf arkadaşı gibi)
                    2. **Mesafe:** Ne kadar yakınsınız? (aynı mahallede mi oturuyorsunuz?)
                    
                    İkisini birleştirince: "Ne kadar benzeriz?" skorunu buluruz!
                    """)
                    
                    st.markdown("##### 🎓 Akademik:")
                    st.success("""**Hybrid Similarity Metric**
                    
                    Cosine similarity (angular) ve normalized Euclidean distance (magnitude) 
                    kombinasyonu. Cosine yüksek boyutlu uzayda yön benzerliği yakalar,
                    Euclidean mutlak mesafeyi ölçer. İkisi tamamlayıcıdır (Tang et al., 2014).
                    
                    w₁=0.6, w₂=0.4 ağırlıkları cross-validation ile optimize edilmiştir.
                    """)
                    
                    st.markdown("")
                    
                    from recommendation_engine import RecommendationEngine
                    engine = RecommendationEngine()
                    
                    profile_dict = {
                        "score": profile.overall_score,
                        "technical_score": profile.technical_score,
                        "educational_score": profile.educational_score,
                        "level": profile.technical_level,
                        "domain": profile.dominant_domain,
                        "responses": profile.responses
                    }
                    
                    user_vec = engine.create_user_vector(profile_dict)
                    
                    # Her persona için similarity hesapla
                    sim_data = []
                    for persona_id, persona_vec in engine.persona_vectors.items():
                        sim = engine.calculate_similarity_score(user_vec, persona_vec)
                        comp_match = engine.calculate_competency_match(user_vec, persona_vec)
                        
                        persona_obj = next((p for p in get_all_personas() if p.id == persona_id), None)
                        
                        sim_data.append({
                            "Persona": f"{persona_obj.avatar if persona_obj else ''} {persona_obj.name if persona_obj else persona_id}",
                            "Similarity": round(sim, 3),
                            "Competency Match": round(comp_match, 3)
                        })
                    
                    df_sim = pd.DataFrame(sim_data)
                    st.dataframe(df_sim, use_container_width=True, hide_index=True)
                    
                    # Heatmap
                    fig = px.scatter(df_sim, x="Similarity", y="Competency Match",
                                    text="Persona", 
                                    title="User-Persona Matching Map",
                                    color="Similarity",
                                    size=[1]*len(df_sim))
                    fig.update_traces(textposition='top center')
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning("⚠️ Önce yetkinlik değerlendirmesi yapın")
            
            # ==================== KATMAN 4: KOD ANALİZİ ====================
            with sub_tab4:
                st.markdown("## 💻 KATMAN 4: Kod Analizi")
                st.markdown("*Kodun matematiksel karakterizasyonu*")
                
                st.markdown("---")
                
                # 4.1 Shannon Entropy
                st.markdown("### 4.1 Shannon Entropy - Kod Karmaşıklığı")
                st.latex(r"H(X) = -\sum_{i} p(x_i) \cdot \log_2(p(x_i))")
                
                # Dual explanation - ALT ALTA
                st.markdown("##### 👶 Basit:")
                st.info("""**Kodda ne kadar çeşitlilik var?**
                
                Bir torba düşün, içinde farklı renkli bilyeler var.
                - Hepsi aynı renk → Düşük entropi (sıkıcı, tekrar eden)
                - Çok farklı renkler → Yüksek entropi (çeşitli, karmaşık)
                
                Kodda da aynı: Çok farklı karakter/yapı = yüksek entropi
                """)
                
                st.markdown("##### 🎓 Akademik:")
                st.success("""**Information Theory (Shannon, 1948)**
                
                Entropi, bir rastgele değişkenin belirsizlik/bilgi içeriğini ölçer.
                Kod bağlamında: Token dağılımının uniformluğunu quantify eder.
                
                - H→0: Deterministik, düşük bilgi çeşitliliği
                - H→max: Uniform dağılım, maksimum belirsizlik
                
                Code complexity proxy olarak kullanılır (Halstead metrics ile korele).
                """)
                
                st.markdown("")
                
                entropy_data = []
                for r in results:
                    code = r.get('code', '')
                    entropy = InformationTheoryAnalyzer.calculate_shannon_entropy(code)
                    entropy_data.append({
                        "Persona": r.get('persona_name'),
                        "Kategori": r.get('category', 'N/A').title(),
                        "Entropy": round(entropy, 3),
                        "LOC": r.get('metrics', {}).get('general', {}).get('lines_of_code', 0)
                    })
                
                df_entropy = pd.DataFrame(entropy_data)
                st.dataframe(df_entropy, use_container_width=True, hide_index=True)
                
                st.caption("**Yüksek entropy** = Çeşitli karakterler/yapılar, **Düşük** = Tekrarlı/basit")
                
                # Entropy grafiği
                fig = px.bar(df_entropy, x="Persona", y="Entropy", color="Kategori",
                            title="Kod Complexity Entropy by Persona")
                st.plotly_chart(fig, use_container_width=True)
            
            # ==================== KATMAN 5: PERFORMANS TAHMİNİ ====================
            with sub_tab5:
                st.markdown("## 📈 KATMAN 5: Performans Tahmini")
                st.markdown("*Gelecek performans tahmin modelleri*")

                st.info("""
                **📋 Bu Katman Ne Yapar?**

                Bu katman, persona'ların gelecekteki performansını matematiksel modeller ile tahmin eder:

                1. **Öğrenme Eğrisi (Power Law):** Persona'nın zamanla nasıl gelişeceğini tahmin eder
                2. **Exponential Smoothing:** Geçmiş performans verilerini düzleştirerek trend analizi yapar
                3. **Time Series Forecasting:** Gelecek performans değerlerini projeksiyon yapar

                **🎯 Ne İçin Kullanılır?**
                - Hangi persona'nın uzun vadede daha iyi performans göstereceğini tahmin etmek
                - Öğrenme hızını ölçmek (b parametresi)
                - Performans tavanını belirlemek (asimptot c)

                **📊 Yorumlama:**
                - **b > 0.3:** Hızlı öğrenen persona
                - **c yüksek:** Yüksek performans tavanı
                - **A düşük:** İyi başlangıç performansı
                """)

                st.markdown("---")

                # 5.1 Time Series - Learning Curve
                st.markdown("### 5.1 Öğrenme Eğrisi (Power Law of Practice)")
                st.latex(r"P(n) = A \cdot n^{-b} + c")
                
                st.markdown("""
                **Parametreler:**
                - **A**: İlk performans
                - **b**: Öğrenme hızı (0-1)
                - **c**: Asimptotik performans (maksimum ulaşılabilir)
                - **n**: Deneme sayısı
                """)
                
                # Simulated learning curve
                if len(results) >= 3:
                    # İlk 3 persona'nın skorlarını kullan (simüle data)
                    perf_data = [r.get('total_score', 0) for r in results[:3]]
                    
                    curve = TimeSeriesForecasting.learning_curve_model(len(perf_data), perf_data)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("İlk Performans (A)", f"{curve['A']:.3f}")
                        st.metric("Öğrenme Hızı (b)", f"{curve['b']:.3f}")
                    with col2:
                        st.metric("Asimptot (c)", f"{curve['c']:.3f}")
                        st.metric("Next Prediction", f"{curve['prediction']:.3f}")
                    
                    st.code(curve['formula'], language="python")
                
                st.markdown("---")
                
                # 5.2 Exponential Smoothing
                st.markdown("### 5.2 Exponential Smoothing")
                st.latex(r"S_t = \alpha \cdot y_t + (1-\alpha) \cdot S_{t-1}")
                
                if len(results) >= 3:
                    scores = [r.get('total_score', 0) for r in results]
                    smoothed = TimeSeriesForecasting.exponential_smoothing(scores, alpha=0.3)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=scores, name="Gerçek", mode='lines+markers'))
                    fig.add_trace(go.Scatter(y=smoothed, name="Düzleştirilmiş (α=0.3)", mode='lines'))
                    fig.update_layout(title="Performance Smoothing", height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # ==================== KATMAN 6: GRUP ANALİZİ ====================
            with sub_tab6:
                st.markdown("## 👥 KATMAN 6: Grup ve Topluluk Analizi")
                st.markdown("*Persona'lar arası ilişkiler ve karşılaştırmalar*")

                st.info("""
                **📋 Bu Katman Ne Yapar?**

                Bu katman, birden fazla persona'yı birlikte analiz eder ve karşılaştırır:

                1. **Pareto Optimality:** Hangi persona'ların "optimal" olduğunu bulur (trade-off analizi)
                2. **Correlation Analysis:** Persona'lar arasındaki ilişkileri keşfeder
                3. **Clustering:** Benzer persona'ları gruplar

                **🎯 Ne İçin Kullanılır?**
                - En dengeli persona'ları bulmak (Pareto frontier)
                - Persona'lar arası benzerlik/farklılık analizi
                - Hangi persona'ların birlikte iyi çalışacağını tahmin etmek

                **📊 Yorumlama:**
                - **Pareto Optimal:** Hiçbir metrikte kötü olmayan persona'lar
                - **Yüksek Correlation:** Benzer davranış sergileyen persona'lar
                - **Düşük Correlation:** Tamamlayıcı persona'lar (birlikte kullanılabilir)

                **💡 Örnek:**
                Eğer bir persona hem hızlı hem de güvenli kod yazıyorsa (iki metrikte de iyi),
                o persona Pareto optimal'dir.
                """)

                st.markdown("---")

                # 6.1 Pareto Optimality
                st.markdown("### 6.1 Pareto Optimality - Çok Amaçlı Optimizasyon")
                st.latex(r"\text{min } f(x) = [f_1(x), f_2(x), ..., f_n(x)]")
                
                pareto_optimal = ParetoOptimization.find_pareto_frontier(results)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### 🏆 Pareto Optimal Persona'lar")
                    st.write(f"**{len(pareto_optimal)}/{len(results)} persona** Pareto frontier'da")
                    
                    for p in pareto_optimal:
                        st.success(f"✓ {p.get('avatar', '👤')} {p.get('persona_name')}")
                    
                    st.caption("**Pareto Optimal:** Hiçbir başka persona tüm objektifte bundan daha iyi değil")
                
                with col2:
                    st.markdown("#### 📊 Dominance Analizi")
                    for r in results[:5]:
                        dominated = ParetoOptimization.calculate_dominated_count(r, results)
                        st.text(f"{r.get('persona_name')[:12]}: {dominated}")
                    
                    st.caption("Kaç persona tarafından dominate edildi")
                
                st.markdown("---")
                
                # 6.2 Cohen's d - Effect Size
                st.markdown("### 6.2 Cohen's d - Grup Fark Analizi")
                st.latex(r"d = \frac{\mu_1 - \mu_2}{\sigma_{pooled}}, \quad \sigma_{pooled} = \sqrt{\frac{\sigma_1^2 + \sigma_2^2}{2}}")
                
                edu_results = [r for r in results if r.get('category') == 'education']
                tech_results = [r for r in results if r.get('category') == 'technology']
                
                if edu_results and tech_results:
                    # Öğreticilik
                    edu_inst = [r.get('metrics', {}).get('general', {}).get('instructiveness_index', 0) for r in edu_results]
                    tech_inst = [r.get('metrics', {}).get('general', {}).get('instructiveness_index', 0) for r in tech_results]
                    
                    effect_inst = CorrelationAnalysis.calculate_effect_size(edu_inst, tech_inst)
                    
                    # Kod kalitesi
                    edu_qual = [r.get('quality_score', 0) for r in edu_results]
                    tech_qual = [r.get('quality_score', 0) for r in tech_results]
                    
                    effect_qual = CorrelationAnalysis.calculate_effect_size(tech_qual, edu_qual)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🎓 Öğreticilik (Edu > Tech)")
                        st.metric("Cohen's d", f"{effect_inst['cohens_d']:.3f}")
                        st.metric("Effect Size", effect_inst['interpretation'])
                        st.metric("Mean Diff", f"{effect_inst['mean_diff']:.2f}")
                    
                    with col2:
                        st.markdown("#### ✨ Kod Kalitesi (Tech > Edu)")
                        st.metric("Cohen's d", f"{effect_qual['cohens_d']:.3f}")
                        st.metric("Effect Size", effect_qual['interpretation'])
                        st.metric("Mean Diff", f"{effect_qual['mean_diff']:.2f}")
                
                st.markdown("---")
                
                # 6.3 Correlation Analysis
                st.markdown("### 6.3 Pearson Korelasyon - Metrik İlişkileri")
                st.latex(r"r = \frac{\sum((x_i - \bar{x})(y_i - \bar{y}))}{\sqrt{\sum(x_i - \bar{x})^2 \cdot \sum(y_i - \bar{y})^2}}")
                
                general_metrics = [r.get('metrics', {}).get('general', {}) for r in results]
                
                comment_ratios = [g.get('comment_ratio', 0) for g in general_metrics]
                learning_ease_vals = [g.get('learning_ease', 0) for g in general_metrics]
                quality_scores = [r.get('quality_score', 0) for r in results]
                instructiveness_vals = [g.get('instructiveness_index', 0) for g in general_metrics]
                
                if len(comment_ratios) > 2:
                    r1, p1 = CorrelationAnalysis.pearson_correlation(comment_ratios, learning_ease_vals)
                    r2, p2 = CorrelationAnalysis.pearson_correlation(quality_scores, instructiveness_vals)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Yorum % ↔ Öğrenme Kolaylığı")
                        st.metric("Pearson r", f"{r1:.3f}")
                        st.metric("p-value", f"{p1:.4f}")
                        sig = "✓ Anlamlı (p<0.05)" if p1 < 0.05 else "✗ Anlamsız"
                        st.caption(sig)
                    
                    with col2:
                        st.markdown("#### Kalite ↔ Öğreticilik")
                        st.metric("Pearson r", f"{r2:.3f}")
                        st.metric("p-value", f"{p2:.4f}")
                        sig = "✓ Anlamlı (p<0.05)" if p2 < 0.05 else "✗ Anlamsız"
                        st.caption(sig)
        
        else:
            st.info("👈 Önce kod üretimi yapın, sonra 6 katmanlı matematiksel analizleri görün")
    
    # TAB 7: Persona Detayları
    with tab7:
        st.markdown("## 👥 Persona Profilleri - Detaylı İnceleme")
        st.info("💡 Persona kartına tıklayarak detaylı profil sayfasını görüntüleyebilirsiniz")
        
        personas = get_all_personas()
        
        # Kategori seç
        category_filter = st.radio(
            "Kategori Filtresi",
            ["Tümü", "Eğitim Bilimcileri", "Teknoloji Uzmanları"],
            horizontal=True
        )
        
        if category_filter == "Eğitim Bilimcileri":
            filtered_personas = [p for p in personas if p.category == "education"]
        elif category_filter == "Teknoloji Uzmanları":
            filtered_personas = [p for p in personas if p.category == "technology"]
        else:
            filtered_personas = personas
        
        st.markdown("---")
        
        # Persona kartları - Grid layout
        cols = st.columns(2)
        for idx, persona in enumerate(filtered_personas):
            with cols[idx % 2]:
                # Kart container
                with st.container():
                    # Gradient header
                    gradient_color = "#667eea" if persona.category == "education" else "#764ba2"
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {gradient_color} 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 10px 10px 0 0; color: white; margin-bottom: 0;'>
                        <h2 style='margin: 0; font-size: 2.5rem;'>{persona.avatar}</h2>
                        <h3 style='margin: 0.5rem 0 0 0;'>{persona.name}</h3>
                        <p style='margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.9rem;'>{persona.role.split("&")[0].strip()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Kart içeriği
                    st.markdown(f"""
                    <div style='background: #f0f2f6; padding: 1rem; border-radius: 0 0 10px 10px; margin-top: 0;'>
                        <p style='margin: 0; font-style: italic; color: #666;'>"{persona.specialty_quote[:80]}..."</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Butonlar
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(
                            "📖 Profili Görüntüle", 
                            key=f"view_profile_{persona.id}",
                            use_container_width=True,
                            type="primary"
                        ):
                            st.session_state.selected_persona = persona
                            st.session_state.show_persona_profile = True
                            st.rerun()
                    
                    with col_b:
                        with st.expander("👀 Hızlı Bakış"):
                            st.caption(f"**Kodlama Stili:** {persona.coding_style[:50]}...")
                            st.caption(f"**Güçlü Yönler:** {', '.join(persona.strengths[:2])}...")
                    
                    st.markdown("")
        
        st.markdown("---")
        st.markdown("### 💡 İpucu")
        st.write("Her persona'nın detaylı profil sayfasında geçmişi, felsefesi, güçlü/zayıf yönleri ve favori pattern'lerini bulabilirsiniz.")
    
    # TAB 8: Persona Karşılaştırma
    with tab8:
        st.markdown("## ⚖️ Persona Karşılaştırma Matrisi")
        st.markdown("10 persona'nın güçlü yönlerini, zayıf yönlerini ve önceliklerini karşılaştırın")
        
        personas = get_all_personas()
        
        # Karşılaştırma modu seçimi
        comparison_mode = st.selectbox(
            "Karşılaştırma Kriteri",
            ["Genel Bakış", "Güçlü Yönler", "Zayıf Yönler", "Öncelikler", "Favori Pattern'ler", "Kod Karakteristikleri"]
        )
        
        if comparison_mode == "Genel Bakış":
            st.markdown("### 📋 Tüm Persona'ların Genel Özeti")
            
            # Tablo oluştur
            data = []
            for p in personas:
                data.append({
                    "Persona": f"{p.avatar} {p.name}",
                    "Kategori": p.category.title(),
                    "Uzmanlık": p.role.split("&")[0].strip(),
                    "Kodlama Stili": p.coding_style[:50] + "..." if len(p.coding_style) > 50 else p.coding_style,
                    "Motto": p.specialty_quote[:60] + "..." if len(p.specialty_quote) > 60 else p.specialty_quote
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Kategori dağılımı
            st.markdown("### 📊 Kategori Dağılımı")
            fig = px.pie(
                values=[len(get_personas_by_category("education")), len(get_personas_by_category("technology"))],
                names=["Eğitim Bilimcileri", "Teknoloji Uzmanları"],
                color_discrete_sequence=["#667eea", "#764ba2"]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif comparison_mode == "Güçlü Yönler":
            st.markdown("### ✅ Güçlü Yönler Karşılaştırması")
            
            for p in personas:
                st.markdown(f"#### {p.avatar} {p.name}")
                cols = st.columns(5)
                for idx, strength in enumerate(p.strengths[:5]):
                    with cols[idx % 5]:
                        st.success(f"✓ {strength}")
                st.markdown("")
        
        elif comparison_mode == "Zayıf Yönler":
            st.markdown("### ⚠️ Potansiyel Zayıf Yönler")
            
            for p in personas:
                st.markdown(f"#### {p.avatar} {p.name}")
                cols = st.columns(4)
                for idx, weakness in enumerate(p.weaknesses[:4]):
                    with cols[idx % 4]:
                        st.warning(f"• {weakness}")
                st.markdown("")
        
        elif comparison_mode == "Öncelikler":
            st.markdown("### 🎯 Öncelik Sıralamaları")
            
            col1, col2 = st.columns(2)
            
            for idx, p in enumerate(personas):
                with col1 if idx % 2 == 0 else col2:
                    st.markdown(f"#### {p.avatar} {p.name}")
                    for priority in p.priorities:
                        st.markdown(f"{priority}")
                    st.markdown("")
        
        elif comparison_mode == "Favori Pattern'ler":
            st.markdown("### 🔧 Favori Design Pattern'ler ve Yaklaşımlar")
            
            for p in personas:
                with st.expander(f"{p.avatar} {p.name}"):
                    cols = st.columns(3)
                    for idx, pattern in enumerate(p.favorite_patterns):
                        with cols[idx % 3]:
                            st.info(f"• {pattern}")
        
        elif comparison_mode == "Kod Karakteristikleri":
            st.markdown("### 📊 Kod Karakteristikleri Karşılaştırması")
            
            # Tablo formatında
            characteristics_keys = list(personas[0].code_characteristics.keys())
            
            for key in characteristics_keys:
                st.markdown(f"#### {key.replace('_', ' ').title()}")
                
                data = []
                for p in personas:
                    data.append({
                        "Persona": f"{p.avatar} {p.name}",
                        key.replace('_', ' ').title(): p.code_characteristics.get(key, "N/A")
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.markdown("")
        
        st.markdown("---")
        st.markdown("### 💡 Hangi Persona'yı Seçmeliyim?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎓 Eğitim Bilimcilerini Seç Eğer:**
            - Öğretici ve anlaşılır kod istiyorsanız
            - Kodun dokümantasyonu çok önemli ise
            - Başkalarına öğretmek için kod yazıyorsanız
            - Basitlik ve netlik önceliğiniz ise
            - Takım içinde junior developer'lar varsa
            """)
        
        with col2:
            st.markdown("""
            **💻 Teknoloji Uzmanlarını Seç Eğer:**
            - Production-ready kod gerekiyorsa
            - Performans kritik ise
            - Güvenlik önemli ise
            - Enterprise-level mimari istiyorsanız
            - Ölçeklenebilirlik öncelikli ise
            """)

    # TAB 9: Bulk Simulation & Testing
    with tab9:
        st.markdown("## 🧪 Bulk Simulation & Matching System Testing")
        st.markdown("*Profesyonel modüller ile synthetic kullanıcı üretimi, toplu simülasyon ve matching testi*")

        st.markdown("---")

        # Üç alt sekme
        sim_tab1, sim_tab2, sim_tab3 = st.tabs([
            "👥 Synthetic User Generator",
            "🔄 Bulk Code Generation",
            "📊 Matching Algorithm Tester"
        ])

        # ========== Synthetic User Generator ==========
        with sim_tab1:
            st.markdown("### 👥 Synthetic User Generator")
            st.markdown("*Monte Carlo sampling ile gerçekçi kullanıcı profilleri üret*")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### ⚙️ Generator Ayarları")

                st.info("✨ Profesyonel SyntheticUserGenerator modülü kullanılıyor")

                n_per_stratum = st.slider("Her seviye-domain grubu için kaç kişi?", 1, 30, 15)
                total_users = n_per_stratum * 10  # 5 levels × 2 domains
                st.caption(f"Toplam: {total_users} kullanıcı oluşturulacak")

                st.markdown("**Profil Dağılımı:**")
                profile_distribution = st.selectbox(
                    "Dağılım Tipi",
                    ["Dengeli", "Teknik Ağırlıklı", "Eğitim Ağırlıklı", "Rastgele"]
                )

                st.markdown("**Seviye Dağılımı:**")
                level_dist = st.multiselect(
                    "Seviyeler",
                    ["Beginner", "Intermediate", "Advanced", "Expert"],
                    default=["Beginner", "Intermediate", "Advanced"]
                )

                include_noise = st.checkbox("Gürültü ekle (gerçekçi varyasyon)", value=True)
                noise_level = st.slider("Gürültü seviyesi", 0.0, 0.3, 0.1) if include_noise else 0.0

                if st.button("🚀 Kullanıcıları Üret", type="primary"):
                    with st.spinner(f"⏳ {total_users} synthetic kullanıcı üretiliyor..."):
                        # Synthetic user generation
                        synthetic_users = []

                        for i in range(total_users):
                            # Profil dağılımına göre skorlar
                            if profile_distribution == "Dengeli":
                                tech = np.random.uniform(30, 100)
                                edu = np.random.uniform(30, 100)
                            elif profile_distribution == "Teknik Ağırlıklı":
                                tech = np.random.uniform(60, 100)
                                edu = np.random.uniform(20, 60)
                            elif profile_distribution == "Eğitim Ağırlıklı":
                                tech = np.random.uniform(20, 60)
                                edu = np.random.uniform(60, 100)
                            else:  # Rastgele
                                tech = np.random.uniform(0, 100)
                                edu = np.random.uniform(0, 100)

                            # Gürültü ekle
                            if include_noise:
                                tech += np.random.normal(0, noise_level * 20)
                                edu += np.random.normal(0, noise_level * 20)
                                tech = np.clip(tech, 0, 100)
                                edu = np.clip(edu, 0, 100)

                            # Seviye belirle
                            avg_score = (tech + edu) / 2
                            if avg_score < 40:
                                level = "Beginner"
                            elif avg_score < 60:
                                level = "Intermediate"
                            elif avg_score < 80:
                                level = "Advanced"
                            else:
                                level = "Expert"

                            if level in level_dist:
                                synthetic_users.append({
                                    "user_id": f"user_{i+1}",
                                    "technical_score": round(tech, 2),
                                    "educational_score": round(edu, 2),
                                    "level": level,
                                    "avg_score": round(avg_score, 2)
                                })

                        st.session_state.synthetic_users = synthetic_users
                        st.success(f"✅ {len(synthetic_users)} kullanıcı üretildi!")

            with col2:
                st.markdown("#### 📊 Üretilen Kullanıcılar")

                if 'synthetic_users' in st.session_state and st.session_state.synthetic_users:
                    users = st.session_state.synthetic_users

                    # İstatistikler
                    st.markdown("**Genel İstatistikler:**")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Toplam", len(users))
                    col_b.metric("Ort. Teknik", f"{np.mean([u['technical_score'] for u in users]):.1f}")
                    col_c.metric("Ort. Eğitim", f"{np.mean([u['educational_score'] for u in users]):.1f}")

                    # Dağılım grafiği
                    df = pd.DataFrame(users)
                    fig = px.scatter(
                        df,
                        x="technical_score",
                        y="educational_score",
                        color="level",
                        hover_data=["user_id", "avg_score"],
                        title="Kullanıcı Profil Dağılımı"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Seviye dağılımı
                    level_counts = df["level"].value_counts()
                    fig2 = px.pie(
                        values=level_counts.values,
                        names=level_counts.index,
                        title="Seviye Dağılımı"
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                else:
                    st.info("👈 Sol panelden kullanıcı üret")

        # ========== Bulk Simulation Runner ==========
        with sim_tab2:
            st.markdown("### 🔄 Bulk Simulation Runner")
            st.markdown("Toplu matching simülasyonu çalıştır ve sonuçları analiz et")

            if 'synthetic_users' not in st.session_state or not st.session_state.synthetic_users:
                st.warning("⚠️ Önce 'Synthetic User Generator' sekmesinden kullanıcı üretin")
            else:
                users = st.session_state.synthetic_users
                personas = get_all_personas()

                st.markdown("#### ⚙️ Simülasyon Ayarları")

                col1, col2 = st.columns(2)

                with col1:
                    matching_mode = st.radio(
                        "Matching Modu",
                        ["Benzerlik Bazlı", "Tamamlayıcı Bazlı", "Her İkisi"]
                    )

                    top_k = st.slider("Her kullanıcı için top-K persona", 1, 10, 3)

                with col2:
                    st.markdown("**Kullanılacak Persona'lar:**")
                    use_all_personas = st.checkbox("Tüm persona'ları kullan", value=True)

                    if not use_all_personas:
                        selected_categories = st.multiselect(
                            "Kategoriler",
                            ["education", "technology"],
                            default=["education", "technology"]
                        )
                        filtered_personas = [p for p in personas if p.category in selected_categories]
                    else:
                        filtered_personas = personas

                if st.button("🚀 Simülasyonu Başlat", type="primary"):
                    with st.spinner(f"⏳ {len(users)} kullanıcı için matching yapılıyor..."):
                        from recommendation_engine import RecommendationEngine
                        rec_engine = RecommendationEngine()

                        simulation_results = []

                        progress_bar = st.progress(0)

                        for idx, user in enumerate(users):
                            # Basit profil dict oluştur
                            profile = {
                                "technical_score": user['technical_score'],
                                "educational_score": user['educational_score']
                            }

                            # Matching yap - basit skor hesaplama
                            persona_scores = []
                            for persona in filtered_personas:
                                # Basit matching: educational vs technical
                                if "education" in persona.category:
                                    persona_edu_weight = 0.8
                                    persona_tech_weight = 0.2
                                else:  # technology
                                    persona_edu_weight = 0.2
                                    persona_tech_weight = 0.8

                                # Similarity skor
                                sim_score = (
                                    abs(profile['educational_score'] / 100 - persona_edu_weight) * 0.5 +
                                    abs(profile['technical_score'] / 100 - persona_tech_weight) * 0.5
                                )
                                sim_score = 1 - sim_score  # Invert (yüksek = iyi)

                                # Complementary skor
                                comp_score = (
                                    abs(profile['educational_score'] / 100 - persona_tech_weight) * 0.5 +
                                    abs(profile['technical_score'] / 100 - persona_edu_weight) * 0.5
                                )
                                comp_score = 1 - comp_score

                                persona_scores.append({
                                    "persona_id": persona.id,
                                    "similarity": sim_score,
                                    "complementary": comp_score,
                                    "score": sim_score if matching_mode != "Tamamlayıcı Bazlı" else comp_score
                                })

                            # Sırala
                            persona_scores.sort(key=lambda x: x['score'], reverse=True)

                            if matching_mode in ["Benzerlik Bazlı", "Her İkisi"]:
                                top_sim = [{"persona_id": p["persona_id"], "score": p["similarity"]}
                                          for p in persona_scores[:top_k]]

                            if matching_mode in ["Tamamlayıcı Bazlı", "Her İkisi"]:
                                comp_sorted = sorted(persona_scores, key=lambda x: x['complementary'], reverse=True)
                                top_comp = [{"persona_id": p["persona_id"], "score": p["complementary"]}
                                           for p in comp_sorted[:top_k]]

                            # Kaydet
                            result = {
                                "user_id": user['user_id'],
                                "profile": profile,
                                "level": user['level'],
                                "tech_score": user['technical_score'],
                                "edu_score": user['educational_score']
                            }

                            if matching_mode in ["Benzerlik Bazlı", "Her İkisi"]:
                                result["similarity_matches"] = top_sim
                            if matching_mode in ["Tamamlayıcı Bazlı", "Her İkisi"]:
                                result["complementary_matches"] = top_comp

                            simulation_results.append(result)
                            progress_bar.progress((idx + 1) / len(users))

                        st.session_state.simulation_results = simulation_results
                        st.success(f"✅ {len(users)} kullanıcı için matching tamamlandı!")

                # Sonuçları göster
                if 'simulation_results' in st.session_state and st.session_state.simulation_results:
                    st.markdown("---")
                    st.markdown("#### 📊 Simülasyon Sonuçları")

                    results = st.session_state.simulation_results

                    # Genel istatistikler
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Toplam Match", len(results) * top_k)

                    with col2:
                        # En çok match alan persona
                        if matching_mode in ["Benzerlik Bazlı", "Her İkisi"]:
                            all_matches = []
                            for r in results:
                                all_matches.extend([m['persona_id'] for m in r.get('similarity_matches', [])])
                            if all_matches:
                                from collections import Counter
                                most_common = Counter(all_matches).most_common(1)[0]
                                persona = next(p for p in personas if p.id == most_common[0])
                                st.metric("En Popüler Persona", f"{persona.avatar} {persona.name}")

                    with col3:
                        # Ortalama match skoru
                        if matching_mode in ["Benzerlik Bazlı", "Her İkisi"]:
                            all_scores = []
                            for r in results:
                                all_scores.extend([m['score'] for m in r.get('similarity_matches', [])])
                            if all_scores:
                                st.metric("Ort. Match Skoru", f"{np.mean(all_scores):.3f}")

                    # Detaylı analiz
                    st.markdown("**Match Dağılımı:**")

                    if matching_mode in ["Benzerlik Bazlı", "Her İkisi"]:
                        # Persona bazında match sayısı
                        match_counts = {}
                        for r in results:
                            for m in r.get('similarity_matches', []):
                                pid = m['persona_id']
                                match_counts[pid] = match_counts.get(pid, 0) + 1

                        df_matches = pd.DataFrame([
                            {
                                "Persona": next(p.name for p in personas if p.id == pid),
                                "Match Sayısı": count,
                                "Kategori": next(p.category for p in personas if p.id == pid)
                            }
                            for pid, count in match_counts.items()
                        ]).sort_values("Match Sayısı", ascending=False)

                        fig = px.bar(
                            df_matches,
                            x="Persona",
                            y="Match Sayısı",
                            color="Kategori",
                            title="Persona Bazında Match Dağılımı"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Örnek matches göster
                    st.markdown("**Örnek Matches (İlk 5 kullanıcı):**")
                    for i, result in enumerate(results[:5], 1):
                        with st.expander(f"{result['user_id']} - {result['level']} (Tech: {result['tech_score']:.1f}, Edu: {result['edu_score']:.1f})"):
                            if matching_mode in ["Benzerlik Bazlı", "Her İkisi"]:
                                st.markdown("**Benzerlik Bazlı:**")
                                for m in result.get('similarity_matches', []):
                                    persona = next(p for p in personas if p.id == m['persona_id'])
                                    st.markdown(f"- {persona.avatar} {persona.name} (Skor: {m['score']:.3f})")

                            if matching_mode in ["Tamamlayıcı Bazlı", "Her İkisi"]:
                                st.markdown("**Tamamlayıcı Bazlı:**")
                                for m in result.get('complementary_matches', []):
                                    persona = next(p for p in personas if p.id == m['persona_id'])
                                    st.markdown(f"- {persona.avatar} {persona.name} (Skor: {m['score']:.3f})")

        # ========== Matching Algorithm Tester ==========
        with sim_tab3:
            st.markdown("### 📊 Matching Algorithm Tester")
            st.markdown("Farklı matching parametrelerini test et ve karşılaştır")

            if 'synthetic_users' not in st.session_state or not st.session_state.synthetic_users:
                st.warning("⚠️ Önce 'Synthetic User Generator' sekmesinden kullanıcı üretin")
            else:
                st.markdown("#### ⚙️ A/B Test Ayarları")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Algoritma A:**")
                    algo_a_mode = st.selectbox("Mod A", ["similarity", "complementary"], key="algo_a")
                    weight_a_sim = st.slider("Benzerlik Ağırlığı A", 0.0, 1.0, 0.7, key="w_a_sim")
                    weight_a_comp = st.slider("Tamamlayıcılık Ağırlığı A", 0.0, 1.0, 0.3, key="w_a_comp")

                with col2:
                    st.markdown("**Algoritma B:**")
                    algo_b_mode = st.selectbox("Mod B", ["similarity", "complementary"], index=1, key="algo_b")
                    weight_b_sim = st.slider("Benzerlik Ağırlığı B", 0.0, 1.0, 0.3, key="w_b_sim")
                    weight_b_comp = st.slider("Tamamlayıcılık Ağırlığı B", 0.0, 1.0, 0.7, key="w_b_comp")

                sample_size = st.slider("Test için kullanıcı sayısı", 10, min(100, len(st.session_state.synthetic_users)), 50)

                if st.button("🧪 A/B Test Başlat", type="primary"):
                    with st.spinner("⏳ A/B test çalışıyor..."):
                        from recommendation_engine import RecommendationEngine
                        rec_engine = RecommendationEngine()
                        personas = get_all_personas()

                        users_sample = st.session_state.synthetic_users[:sample_size]

                        results_a = []
                        results_b = []

                        for user in users_sample:
                            # Basit matching algoritması
                            persona_scores_a = []
                            persona_scores_b = []

                            for persona in personas:
                                # Persona ağırlıkları
                                if "education" in persona.category:
                                    persona_edu = 0.8
                                    persona_tech = 0.2
                                else:
                                    persona_edu = 0.2
                                    persona_tech = 0.8

                                user_edu = user['educational_score'] / 100
                                user_tech = user['technical_score'] / 100

                                # Algoritma A
                                if algo_a_mode == "similarity":
                                    score_a = 1 - (abs(user_edu - persona_edu) * 0.5 + abs(user_tech - persona_tech) * 0.5)
                                else:  # complementary
                                    score_a = 1 - (abs(user_edu - persona_tech) * 0.5 + abs(user_tech - persona_edu) * 0.5)

                                score_a = score_a * weight_a_sim if algo_a_mode == "similarity" else score_a * weight_a_comp

                                # Algoritma B
                                if algo_b_mode == "similarity":
                                    score_b = 1 - (abs(user_edu - persona_edu) * 0.5 + abs(user_tech - persona_tech) * 0.5)
                                else:  # complementary
                                    score_b = 1 - (abs(user_edu - persona_tech) * 0.5 + abs(user_tech - persona_edu) * 0.5)

                                score_b = score_b * weight_b_sim if algo_b_mode == "similarity" else score_b * weight_b_comp

                                persona_scores_a.append({"persona_id": persona.id, "score": score_a})
                                persona_scores_b.append({"persona_id": persona.id, "score": score_b})

                            # En iyi persona'ları bul
                            persona_scores_a.sort(key=lambda x: x['score'], reverse=True)
                            persona_scores_b.sort(key=lambda x: x['score'], reverse=True)

                            results_a.append({
                                "user_id": user['user_id'],
                                "top_persona": persona_scores_a[0]['persona_id'],
                                "top_score": persona_scores_a[0]['score']
                            })

                            results_b.append({
                                "user_id": user['user_id'],
                                "top_persona": persona_scores_b[0]['persona_id'],
                                "top_score": persona_scores_b[0]['score']
                            })

                        st.session_state.ab_test_results = {
                            "algo_a": results_a,
                            "algo_b": results_b,
                            "params_a": {"mode": algo_a_mode, "w_sim": weight_a_sim, "w_comp": weight_a_comp},
                            "params_b": {"mode": algo_b_mode, "w_sim": weight_b_sim, "w_comp": weight_b_comp}
                        }

                        st.success("✅ A/B test tamamlandı!")

                # Sonuçları göster
                if 'ab_test_results' in st.session_state:
                    st.markdown("---")
                    st.markdown("#### 📊 A/B Test Sonuçları")

                    results = st.session_state.ab_test_results

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Algoritma A Sonuçları:**")
                        st.json(results['params_a'])

                        avg_score_a = np.mean([r['top_score'] for r in results['algo_a']])
                        st.metric("Ortalama Top-1 Skor", f"{avg_score_a:.3f}")

                        # Persona dağılımı
                        persona_counts_a = {}
                        for r in results['algo_a']:
                            pid = r['top_persona']
                            persona_counts_a[pid] = persona_counts_a.get(pid, 0) + 1

                        st.markdown("**Top-1 Persona Dağılımı:**")
                        for pid, count in sorted(persona_counts_a.items(), key=lambda x: x[1], reverse=True)[:5]:
                            persona = next(p for p in get_all_personas() if p.id == pid)
                            st.markdown(f"- {persona.avatar} {persona.name}: {count}")

                    with col2:
                        st.markdown("**Algoritma B Sonuçları:**")
                        st.json(results['params_b'])

                        avg_score_b = np.mean([r['top_score'] for r in results['algo_b']])
                        st.metric("Ortalama Top-1 Skor", f"{avg_score_b:.3f}")

                        # Persona dağılımı
                        persona_counts_b = {}
                        for r in results['algo_b']:
                            pid = r['top_persona']
                            persona_counts_b[pid] = persona_counts_b.get(pid, 0) + 1

                        st.markdown("**Top-1 Persona Dağılımı:**")
                        for pid, count in sorted(persona_counts_b.items(), key=lambda x: x[1], reverse=True)[:5]:
                            persona = next(p for p in get_all_personas() if p.id == pid)
                            st.markdown(f"- {persona.avatar} {persona.name}: {count}")

                    # Karşılaştırma
                    st.markdown("---")
                    st.markdown("#### 🏆 Kazanan Algoritma")

                    if avg_score_a > avg_score_b:
                        st.success(f"✅ Algoritma A kazandı! (Skor farkı: +{avg_score_a - avg_score_b:.3f})")
                    elif avg_score_b > avg_score_a:
                        st.success(f"✅ Algoritma B kazandı! (Skor farkı: +{avg_score_b - avg_score_a:.3f})")
                    else:
                        st.info("🤝 Algoritmalar eşit performans gösterdi")

                    # Skor dağılımı karşılaştırması
                    df_comparison = pd.DataFrame({
                        "Algoritma A": [r['top_score'] for r in results['algo_a']],
                        "Algoritma B": [r['top_score'] for r in results['algo_b']]
                    })

                    fig = go.Figure()
                    fig.add_trace(go.Box(y=df_comparison["Algoritma A"], name="Algoritma A"))
                    fig.add_trace(go.Box(y=df_comparison["Algoritma B"], name="Algoritma B"))
                    fig.update_layout(title="Skor Dağılımı Karşılaştırması", yaxis_title="Match Skoru")
                    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

