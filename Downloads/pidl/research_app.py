"""
PIDL Araştırma Uygulaması - ESKİ SİSTEM ENTEGRE EDİLMİŞ
10 Persona, Dreyfus Model, Tam Yetkinlik Değerlendirmesi
"""

import streamlit as st
import uuid
from datetime import datetime
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

# Eski sistem modülleri
from competency_assessment import CompetencyAssessment, CompetencyProfile
from personas import get_persona_by_id, get_personas_by_level, ALL_PERSONAS, get_persona_details
from recommendation_engine import RecommendationEngine
from content_analyzer import ContentAnalyzer

# Araştırma modülleri
from research_modules import (
    ConsentForm, PrePostTestForm, NASATLXForm,
    AIEvaluationForm, FinalSurveyForm, DataLogger
)
from tasks import get_task_by_number

# .env dosyasını yükle
load_dotenv()

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Sayfa yapılandırması
st.set_page_config(
    page_title="PIDL Araştırma Sistemi",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    .persona-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .persona-card.similar {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .persona-card.complementary {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    .task-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Session State Başlatma
def init_session_state():
    """Session state değişkenlerini başlat"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.phase = 'consent'
        st.session_state.participant_uuid = None
        st.session_state.current_task_number = 1
        st.session_state.current_task_session_id = None
        st.session_state.task_start_time = None
        st.session_state.competency_profile = None  # Eski sistemdeki CompetencyProfile
        st.session_state.similar_persona = None
        st.session_state.complementary_persona = None
        st.session_state.assigned_personas = {}
        st.session_state.session_start_time = datetime.now()


def get_persona_recommendations_from_profile(profile: CompetencyProfile, use_math_engine: bool = True):
    """
    CompetencyProfile'dan Similar ve Complementary persona önerileri al

    İKİ MOD:
    1. Matematiksel Engine (use_math_engine=True): 6 aşamalı hesaplama
    2. Basit Mod (use_math_engine=False): Seviye bazlı eşleştirme

    Similar: Dominant alanınızdan, matematiksel olarak en yüksek skor
    Complementary: Zayıf alanınızdan, eksiklerinizi en iyi tamamlayan
    """

    if use_math_engine:
        # 🔬 MATEMATİKSEL ENGINE - 6 AŞAMALI HESAPLAMA
        try:
            rec_engine = RecommendationEngine()

            # Profile'ı dict'e çevir
            profile_dict = {
                "user_id": str(uuid.uuid4()),
                "technical_score": profile.technical_score,
                "educational_score": profile.educational_score,
                "technical_level": profile.technical_level,
                "educational_level": profile.educational_level,
                "dominant_domain": profile.dominant_domain,
                "weak_domain": profile.weak_domain,
                "learning_goal": 0.7  # Öğrenme odaklı (araştırma için)
            }

            # AŞAMA 1-2: User Vector + Persona Vectors oluştur
            user_vector = rec_engine.create_user_vector(profile_dict)

            # AŞAMA 3-4: Similarity + Competency hesapla
            # AŞAMA 5-6: Performance + Learning hesapla + Rank

            # SIMILAR MOD: Dominant alandan en benzer
            domain_map = {"technical": "technology", "educational": "education"}
            dominant_category = domain_map.get(profile.dominant_domain, "technology")

            similar_candidates = [p for p in ALL_PERSONAS if p.category == dominant_category]
            similar_scores = []

            for persona in similar_candidates:
                persona_vector = rec_engine.persona_vectors.get(persona.id)
                if persona_vector:
                    score_result = rec_engine.calculate_recommendation_score(
                        user_vector, persona_vector,
                        task_complexity=0.5,
                        mode="similarity"
                    )
                    similar_scores.append((persona, score_result))

            similar_scores.sort(key=lambda x: x[1]["total_score"], reverse=True)
            similar_persona = similar_scores[0][0] if similar_scores else ALL_PERSONAS[0]
            similar_score_info = similar_scores[0][1] if similar_scores else None

            # COMPLEMENTARY MOD: Zayıf alandan tamamlayıcı
            weak_category = domain_map.get(profile.weak_domain, "education")

            complementary_candidates = [p for p in ALL_PERSONAS if p.category == weak_category]
            complementary_scores = []

            for persona in complementary_candidates:
                persona_vector = rec_engine.persona_vectors.get(persona.id)
                if persona_vector:
                    score_result = rec_engine.calculate_recommendation_score(
                        user_vector, persona_vector,
                        task_complexity=0.5,
                        mode="complementary"
                    )
                    complementary_scores.append((persona, score_result))

            complementary_scores.sort(key=lambda x: x[1]["total_score"], reverse=True)
            complementary_persona = complementary_scores[0][0] if complementary_scores else similar_persona
            complementary_score_info = complementary_scores[0][1] if complementary_scores else None

            return {
                "similar": similar_persona,
                "complementary": complementary_persona,
                "dominant_domain": profile.dominant_domain,
                "weak_domain": profile.weak_domain,
                "technical_score": profile.technical_score,
                "educational_score": profile.educational_score,
                "math_engine_used": True,
                "similar_score_info": similar_score_info,
                "complementary_score_info": complementary_score_info
            }

        except Exception as e:
            st.warning(f"⚠️ Matematiksel engine hatası: {str(e)}, basit mod'a geçiliyor...")
            use_math_engine = False

    # BASIT MOD - Seviye bazlı eşleştirme (fallback)
    if not use_math_engine:
        domain_map = {
            "technical": "technology",
            "educational": "education"
        }

        dominant_category = domain_map.get(profile.dominant_domain, "technology")
        weak_category = domain_map.get(profile.weak_domain, "education")

        tech_level_str = profile.technical_level
        edu_level_str = profile.educational_level

        # SIMILAR PERSONA
        similar_level = tech_level_str if profile.dominant_domain == "technical" else edu_level_str
        similar_personas = [p for p in ALL_PERSONAS if p.dreyfus_level == similar_level and p.category == dominant_category]
        similar_persona = similar_personas[0] if similar_personas else ALL_PERSONAS[0]

        # COMPLEMENTARY PERSONA
        weak_level = edu_level_str if profile.dominant_domain == "technical" else tech_level_str
        level_order = ["novice", "advanced_beginner", "competent", "proficient", "expert"]
        current_idx = level_order.index(weak_level)
        complementary_level = level_order[min(current_idx + 1, len(level_order) - 1)]

        complementary_personas = [p for p in ALL_PERSONAS if p.dreyfus_level == complementary_level and p.category == weak_category]
        complementary_persona = complementary_personas[0] if complementary_personas else similar_persona

        return {
            "similar": similar_persona,
            "complementary": complementary_persona,
            "dominant_domain": profile.dominant_domain,
            "weak_domain": profile.weak_domain,
            "technical_score": profile.technical_score,
            "educational_score": profile.educational_score,
            "math_engine_used": False
        }


def generate_code_with_persona(persona, task, user_prompt: str) -> tuple:
    """
    Persona'nın system prompt'u ile OpenAI GPT-4 kullanarak kod üret

    Returns:
        (generated_code: str, generation_time: float, messages: dict, full_prompt: str)
    """
    start_time = time.time()

    try:
        # Persona'nın system prompt'unu kullan
        system_prompt = persona.system_prompt

        # Kullanıcı prompt'una görev bilgisini ekle
        full_prompt = f"""Görev: {task.title}

{task.description}

Kullanıcı İsteği:
{user_prompt}

Lütfen Solidity smart contract kodu yaz. Kodu açıklamalarla birlikte sun."""

        # GPT-4'e gönderilecek mesajlar (TAM CONVERSATION)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ]

        # OpenAI API çağrısı
        response = openai_client.chat.completions.create(
            model=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2000"))
        )

        generated_code = response.choices[0].message.content
        generation_time = time.time() - start_time

        # Mesajları ve full prompt'u da return et
        return generated_code, generation_time, messages, full_prompt

    except Exception as e:
        # Hata durumunda fallback
        generation_time = time.time() - start_time
        error_code = f"""// HATA: Kod üretimi başarısız oldu
// Hata mesajı: {str(e)}
// Persona: {persona.name}

pragma solidity ^0.8.0;

// Lütfen tekrar deneyin veya farklı bir prompt kullanın
contract ErrorFallback {{
    // Kod üretilemedi
}}
"""
        # Hata durumunda da mesajları döndür
        error_messages = [
            {"role": "system", "content": persona.system_prompt},
            {"role": "user", "content": f"ERROR: {str(e)}"}
        ]
        return error_code, generation_time, error_messages, f"ERROR: {str(e)}"


def get_persona_balance(persona):
    """
    Personanın teknik/pedagojik dengesini hesapla

    Education domain: Daha pedagojik ağırlıklı
    Technology domain: Daha teknik ağırlıklı
    """
    if persona.category == "education":
        # Eğitim personaları: Pedagojik ağırlıklı
        pedagogical = 70
        technical = 30
    else:  # technology
        # Teknoloji personaları: Teknik ağırlıklı
        technical = 70
        pedagogical = 30

    return {
        "technical": technical,
        "pedagogical": pedagogical
    }


def assign_ai_persona_for_task(task_number: int, similar_persona, complementary_persona):
    """Göreve persona ata: Tek numaralar similar, çift numaralar complementary"""
    ai_type = "Similar" if task_number % 2 == 1 else "Complementary"
    persona = similar_persona if ai_type == "Similar" else complementary_persona

    return {
        "ai_type": ai_type,
        "persona": persona.name,
        "persona_id": persona.id,
        "persona_obj": persona
    }


def show_sidebar():
    """Sidebar - İlerleme göstergesi"""
    with st.sidebar:
        st.markdown("# 🔬 Araştırma İlerlemesi")

        phases = {
            'consent': '📋 Onam',
            'competency': '📊 Yetkinlik',
            'tasks': '💻 Görevler',
            'final': '🎯 Final',
            'complete': '✅ Tamamlandı'
        }

        current_phase = st.session_state.phase

        for phase_key, phase_name in phases.items():
            if phase_key == current_phase:
                st.markdown(f"**→ {phase_name}**")
            elif list(phases.keys()).index(phase_key) < list(phases.keys()).index(current_phase):
                st.markdown(f"✅ {phase_name}")
            else:
                st.markdown(f"⏳ {phase_name}")

        st.markdown("---")

        # Görev ilerlemesi
        if st.session_state.phase == 'tasks':
            st.markdown(f"**Görev:** {st.session_state.current_task_number}/6")
            progress = (st.session_state.current_task_number - 1) / 6
            st.progress(progress)

        # Yetkinlik bilgisi
        if st.session_state.competency_profile:
            st.markdown("---")
            st.markdown("### 👤 Yetkinlik Bilgileriniz")
            profile = st.session_state.competency_profile
            st.markdown(f"**Teknik:** {profile.technical_level}")
            st.markdown(f"**Pedagojik:** {profile.educational_level}")
            st.markdown(f"**Dominant:** {profile.dominant_domain}")


# ============================================================================
# FazFonksiyonları
# ============================================================================

def phase_consent():
    """Faz 1: Onam Formu"""
    st.markdown('<h1 class="main-header">🔬 PIDL Araştırma Sistemi</h1>', unsafe_allow_html=True)
    st.markdown('<div class="phase-badge">1. Bilgilendirilmiş Onam Formu</div>', unsafe_allow_html=True)

    consent_given = ConsentForm.show()

    if consent_given:
        if st.button("✅ Onay Verdim, Devam Et", type="primary", use_container_width=True):
            st.session_state.phase = 'competency'
            st.rerun()


def phase_competency():
    """Faz 2: Yetkinlik Değerlendirmesi - ESKİ SİSTEM"""
    st.markdown('<h1 class="main-header">📊 Yetkinlik Değerlendirmesi</h1>', unsafe_allow_html=True)
    st.markdown('<div class="phase-badge">2. Dreyfus Model Bazlı Yetkinlik Belirleme</div>', unsafe_allow_html=True)

    st.info("🎯 10 sorudan oluşan yetkinlik değerlendirmemiz size özel persona önerileri sunacaktır. "
            "5 teknik + 5 pedagojik soru ile hem yazılım hem eğitim yetkinliğinizi ölçeceğiz.")

    # CompetencyAssessment nesnesi oluştur
    assessment = CompetencyAssessment()

    # Demografik bilgiler
    st.markdown("### 1️⃣ Demografik Bilgiler")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Yaşınız", min_value=18, max_value=100, value=25)
        education = st.selectbox("Eğitim Durumu", [
            "Lise mezunu",
            "Ön lisans mezunu",
            "Lisans mezunu",
            "Yüksek lisans mezunu",
            "Doktora mezunu"
        ])

    with col2:
        gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Diğer", "Belirtmek istemiyorum"])
        work_field = st.selectbox("Çalışma Alanı", [
            "Eğitim",
            "Yazılım/Teknoloji",
            "Akademi/Araştırma",
            "Özel Sektör",
            "Kamu",
            "Öğrenci",
            "Diğer"
        ])

    # TEKNİK SORULAR (eski sistemden)
    st.markdown("---")
    st.markdown("### 2️⃣ Teknik Yetkinlik Soruları (5 soru)")

    tech_responses = {}

    for i, q in enumerate(assessment.TECHNICAL_QUESTIONS, 1):
        st.markdown(f"**Soru {i}:** {q['question']}")
        selected = st.radio(
            f"tech_q{i}",
            options=[opt[0] for opt in q['options']],
            key=f"tech_{q['id']}",
            label_visibility="collapsed"
        )
        # Seçilen cevabın skorunu bul
        score = next((opt[1] for opt in q['options'] if opt[0] == selected), 5)
        tech_responses[q['id']] = score

    # PEDAGOJİK SORULAR (eski sistemden)
    st.markdown("---")
    st.markdown("### 3️⃣ Pedagojik Yetkinlik Soruları (5 soru)")

    edu_responses = {}

    for i, q in enumerate(assessment.EDUCATIONAL_QUESTIONS, 1):
        st.markdown(f"**Soru {i}:** {q['question']}")
        selected = st.radio(
            f"edu_q{i}",
            options=[opt[0] for opt in q['options']],
            key=f"edu_{q['id']}",
            label_visibility="collapsed"
        )
        score = next((opt[1] for opt in q['options'] if opt[0] == selected), 5)
        edu_responses[q['id']] = score

    st.markdown("---")

    # Değerlendirme yap
    if st.button("📊 Yetkinliğimi Değerlendir", type="primary", use_container_width=True):
        # Tüm cevapları birleştir
        all_responses = {**tech_responses, **edu_responses}

        # CompetencyProfile oluştur
        user_id = str(uuid.uuid4())
        profile = assessment.create_profile(
            user_id=user_id,
            responses=all_responses,
            goal="learning"
        )

        # Session state'e kaydet
        st.session_state.competency_profile = profile

        # Persona önerilerini al (Matematiksel Engine ile)
        recommendations = get_persona_recommendations_from_profile(profile, use_math_engine=True)
        st.session_state.similar_persona = recommendations["similar"]
        st.session_state.complementary_persona = recommendations["complementary"]
        st.session_state.recommendations_info = recommendations  # Tam bilgiyi sakla

        # Veritabanına katılımcı kaydet
        participant_uuid = DataLogger.create_participant(
            age=age,
            gender=gender,
            education=education,
            work_field=work_field,
            technical_score=int(profile.technical_score),
            pedagogical_score=int(profile.educational_score),
            competency_level=profile.technical_level  # veya overall level
        )
        st.session_state.participant_uuid = participant_uuid
        st.session_state.competency_evaluated = True  # Flag ekle
        st.rerun()  # Sayfayı yenile

    # Değerlendirme yapıldıysa sonuçları göster
    if st.session_state.get('competency_evaluated', False):
        profile = st.session_state.competency_profile

        # Sonuçları göster
        st.success("✅ Yetkinlik değerlendirmeniz tamamlandı!")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Teknik Yetkinlik", f"{profile.technical_score:.1f}/100",
                     delta=f"{profile.technical_level}")
        with col2:
            st.metric("Pedagojik Yetkinlik", f"{profile.educational_score:.1f}/100",
                     delta=f"{profile.educational_level}")

        st.metric("Dominant Alan", profile.dominant_domain.upper())

        # Persona önerilerini göster
        st.markdown("---")
        st.markdown("## 🤖 Size Önerilen AI Personalar")

        st.info("🎯 Araştırmamızda **iki farklı AI persona tipi** kullanacaksınız:\n"
                "- **Benzer AI (Similar)**: Güçlü alanınızdan, sizin seviyenizde\n"
                "- **Tamamlayıcı AI (Complementary)**: Zayıf alanınızdan, sizi tamamlamak için\n\n"
                "6 görevin 3'ünde Benzer AI, 3'ünde Tamamlayıcı AI kullanacaksınız.")

        # 6 AŞAMALI MATEMATİKSEL HESAPLAMA GÖSTERİMİ
        rec_info = st.session_state.get('recommendations_info', {})
        if rec_info.get('math_engine_used'):
            with st.expander("🔬 6 Aşamalı Matematiksel Hesaplama Süreci", expanded=False):
                st.markdown("""
                ### Persona seçiminiz aşağıdaki 6 adımla bilimsel olarak hesaplandı:

                **AŞAMA 1: User Vector (Kullanıcı Vektörü) Oluşturma** 📊
                - 10 boyutlu vektör: `[technical, domain, AI_exp, learning_goal, procedural, declarative, conditional, cognitive, pattern, abstraction]`
                - Sizin skorlarınız ve Dreyfus seviyeniz bu vektöre dönüştürüldü
                - Formül: `u_tech = φ(level)` - Seviyeden yetkinliğe dönüşüm

                **AŞAMA 2: Persona Vectors (Persona Vektörleri) Eşleştirme** 🎯
                - Her 10 persona için ayrı vektör tanımlandı
                - Vektör bileşenleri: `[complexity, verbosity, technical_depth, pedagogical_focus, comments, modularity, examples, learning_support, production_ready, innovation]`
                - Eğitim personaları: yüksek pedagojik, düşük teknik
                - Teknoloji personaları: yüksek teknik, düşük pedagojik

                **AŞAMA 3: Similarity Score (S) - Benzerlik Hesaplama** 📏
                - **Hybrid Distance:** Cosine Similarity (60%) + Euclidean Distance (40%)
                - Formül: `S = 0.6 × cos(u,p) + 0.4 × (1 - euclidean(u,p)/√10)`
                - Size ne kadar benzediğini ölçer (0-1 arası)

                **AŞAMA 4: Competency Match (C) - Yetkinlik Uyumu** 🎓
                - **Gaussian ZPD (Zone of Proximal Development)**
                - Formül: `C = exp(-λ × |skill_gap|²) × alignment`
                - Vygotsky'nin öğrenme teorisine dayalı
                - Optimal zorluk seviyesini belirler

                **AŞAMA 5: Performance Prediction (P) - Performans Tahmini** 📈
                - **Logistic Regression Modeli**
                - Formül: `P = σ(β₀ + β₁·skill + β₂·quality + β₃·similarity + β₄·task_complexity)`
                - Pilot çalışmadan (N=10) kalibre edilmiş
                - Başarı olasılığınızı tahmin eder

                **AŞAMA 6: Learning Trajectory (L) - Öğrenme Yörüngesi** 🚀
                - **Exponential Growth Model**
                - Formül: `L = L_max × (1 - e^(-k·τ)) × potential`
                - Öğrenme potansiyelinizi modelliyor
                - Uzun vadeli gelişiminizi tahmin eder

                ---

                ### 🎯 Final Recommendation Score:

                **Similar Mode (Benzerlik):**
                ```
                R_similar = 0.30·S + 0.35·C + 0.25·P + 0.10·L
                ```

                **Complementary Mode (Tamamlayıcılık):**
                ```
                R_complementary = 0.30·(1-S) + 0.35·D + 0.25·P + 0.10·L
                ```

                D = Complementarity (eksiklerinizi ne kadar tamamladığı)

                ---

                **📚 Teorik Temel:**
                - Cognitive Load Theory (Sweller, 1988)
                - Dreyfus Model of Skill Acquisition (1980)
                - Zone of Proximal Development (Vygotsky, 1978)
                - Multi-Criteria Decision Analysis (MCDA)
                """)

                st.success("✅ Matematiksel hesaplama tamamlandı! Aşağıda seçilen personalarınızı görebilirsiniz.")

        col1, col2 = st.columns(2)

        with col1:
            similar = st.session_state.similar_persona
            sim_balance = get_persona_balance(similar)
            st.markdown(f"""
            <div class="persona-card similar">
                <h3>{similar.avatar} BENZER AI - {similar.name}</h3>
                <p><strong>Seviye:</strong> {similar.dreyfus_level.upper()}</p>
                <p><strong>Alan:</strong> {similar.category.upper()} (güçlü alanınız)</p>
                <p><strong>Yetkinlik Dengesi:</strong> 💻 Teknik {sim_balance['technical']}% | 🎓 Pedagojik {sim_balance['pedagogical']}%</p>
                <p><strong>Rol:</strong> {similar.role}</p>
                <p>{similar.description}</p>
                <p><em>"{similar.specialty_quote}"</em></p>
                <p><strong>Bu personayı kullanacağınız görevler: 1, 3, 5</strong></p>
            </div>
            """, unsafe_allow_html=True)

            # Matematiksel skor detayları (varsa)
            rec_info = st.session_state.get('recommendations_info', {})
            if rec_info.get('math_engine_used') and rec_info.get('similar_score_info'):
                with st.expander("🔬 Matematiksel Skor Detayları (İleri Düzey)"):
                    score_info = rec_info['similar_score_info']
                    components = score_info['components']
                    st.markdown(f"""
                    **6 Aşamalı Hesaplama Sonuçları:**

                    **Toplam Skor:** {score_info['total_score']:.3f} / 1.000

                    **Bileşenler:**
                    - 📊 Benzerlik (S): {components['similarity']:.3f}
                    - 🎯 Yetkinlik Uyumu (C): {components['competency_match']:.3f}
                    - 📈 Performans Tahmini (P): {components['performance_prediction']:.3f}
                    - 🚀 Öğrenme Yörüngesi (L): {components['learning_trajectory']:.3f}

                    **Formül:** R = α·S + β·C + γ·P + δ·L

                    **Mod:** {score_info['strategy']}

                    **Güven Aralığı (95% CI):** [{score_info['confidence_interval']['lower']:.3f}, {score_info['confidence_interval']['upper']:.3f}]
                    """)

        with col2:
            complementary = st.session_state.complementary_persona
            comp_balance = get_persona_balance(complementary)
            st.markdown(f"""
            <div class="persona-card complementary">
                <h3>{complementary.avatar} TAMAMLAYICI AI - {complementary.name}</h3>
                <p><strong>Seviye:</strong> {complementary.dreyfus_level.upper()}</p>
                <p><strong>Alan:</strong> {complementary.category.upper()} (gelişim alanınız)</p>
                <p><strong>Yetkinlik Dengesi:</strong> 💻 Teknik {comp_balance['technical']}% | 🎓 Pedagojik {comp_balance['pedagogical']}%</p>
                <p><strong>Rol:</strong> {complementary.role}</p>
                <p>{complementary.description}</p>
                <p><em>"{complementary.specialty_quote}"</em></p>
                <p><strong>Bu personayı kullanacağınız görevler: 2, 4, 6</strong></p>
            </div>
            """, unsafe_allow_html=True)

            # Matematiksel skor detayları (varsa)
            rec_info = st.session_state.get('recommendations_info', {})
            if rec_info.get('math_engine_used') and rec_info.get('complementary_score_info'):
                with st.expander("🔬 Matematiksel Skor Detayları (İleri Düzey)"):
                    score_info = rec_info['complementary_score_info']
                    components = score_info['components']
                    st.markdown(f"""
                    **6 Aşamalı Hesaplama Sonuçları:**

                    **Toplam Skor:** {score_info['total_score']:.3f} / 1.000

                    **Bileşenler:**
                    - 🔄 Farklılık (1-S): {components['dissimilarity']:.3f}
                    - 🎯 Tamamlayıcılık (D): {components['complementarity']:.3f}
                    - 📈 Performans Tahmini (P): {components['performance_prediction']:.3f}
                    - 🚀 Öğrenme Yörüngesi (L): {components['learning_trajectory']:.3f}

                    **Formül:** R = α·(1-S) + β·D + γ·P + δ·L

                    **Mod:** {score_info['strategy']}

                    **Güven Aralığı (95% CI):** [{score_info['confidence_interval']['lower']:.3f}, {score_info['confidence_interval']['upper']:.3f}]
                    """)

        st.markdown("---")

        if st.button("▶️ Görevlere Başla", type="primary", use_container_width=True):
            st.session_state.phase = 'tasks'
            st.rerun()


def phase_tasks():
    """Faz 3: 6 Görev"""
    task_number = st.session_state.current_task_number

    if task_number > 6:
        st.session_state.phase = 'final'
        st.rerun()
        return

    st.markdown(f'<h1 class="main-header">💻 Görev {task_number}/6</h1>', unsafe_allow_html=True)

    # Görevi al
    task = get_task_by_number(task_number)

    # Persona ataması yap
    if task_number not in st.session_state.assigned_personas:
        assignment = assign_ai_persona_for_task(
            task_number,
            st.session_state.similar_persona,
            st.session_state.complementary_persona
        )
        st.session_state.assigned_personas[task_number] = assignment

    assigned = st.session_state.assigned_personas[task_number]
    persona_obj = assigned["persona_obj"]
    persona_balance = get_persona_balance(persona_obj)

    # Görev bilgisi
    st.markdown(f"""
    <div class="task-card">
        <h2>{task.title}</h2>
        <p><strong>Zorluk:</strong> {task.difficulty}</p>
        <p><strong>Kullanacağınız AI:</strong> {assigned['ai_type']} - {persona_obj.avatar} {persona_obj.name}</p>
        <p><strong>AI Yetkinlik Dengesi:</strong> 💻 Teknik {persona_balance['technical']}% | 🎓 Pedagojik {persona_balance['pedagogical']}%</p>
        <p>{task.description}</p>
    </div>
    """, unsafe_allow_html=True)

    # Alt görev akışı
    if 'task_substep' not in st.session_state:
        st.session_state.task_substep = 'pre_test'

    substep = st.session_state.task_substep

    if substep == 'pre_test':
        st.markdown("### 📝 Pre-Test (3 soru)")
        st.info("Göreve başlamadan önce mevcut bilginizi ölçelim.")

        pre_test_questions = task.get_pre_test_questions()
        pre_answers = PrePostTestForm.show_test(pre_test_questions, "pre")

        if st.button("✅ Pre-Test Tamamlandı", type="primary"):
            # Task session başlat
            task_session_id = DataLogger.start_task_session(
                participant_uuid=st.session_state.participant_uuid,
                task_number=task_number,
                assigned_ai_type=assigned['ai_type'],
                assigned_persona=persona_obj.name
            )
            st.session_state.current_task_session_id = task_session_id
            st.session_state.task_start_time = datetime.now()

            # Pre-test kaydet
            pre_score = task.calculate_test_score(pre_answers, "pre")
            DataLogger.save_pre_post_test(task_session_id, "pre", pre_answers, pre_score)

            st.session_state.task_substep = 'task_work'
            st.rerun()

    elif substep == 'task_work':
        st.markdown("### 💻 Görev Çalışma Alanı")
        st.markdown(f"**AI Persona:** {persona_obj.avatar} {persona_obj.name} ({assigned['ai_type']})")

        st.info(f"🎯 **Görev Tanımı:**\n\n{task.description}")

        # PERSONA'NIN SYSTEM PROMPT'UNU GÖSTER
        with st.expander(f"🧠 {persona_obj.name}'in Düşünce Sistemi (System Prompt)", expanded=False):
            st.markdown(f"""
            Bu persona şu temel yaklaşımla çalışır:

            **Rol:** {persona_obj.role}

            **Felsefesi:** {persona_obj.philosophy}

            **Güçlü Yönleri:**
            {chr(10).join([f"- {s}" for s in persona_obj.strengths])}

            **Kod Yazma Stili:** {persona_obj.coding_style}

            **Öncelikleri:**
            {chr(10).join([f"- {p}" for p in persona_obj.priorities[:3]])}

            ---

            **Tam System Prompt:**
            """)
            st.code(persona_obj.system_prompt, language="markdown")
            st.caption("👆 Bu prompt, GPT-4'e gönderilecek ve persona'nın karakterini belirleyecek.")

        # Prompt girişi
        user_prompt = st.text_area(
            "📝 AI'a vereceğiniz prompt:",
            height=150,
            placeholder="Örnek: Blockchain tabanlı diploma doğrulama sistemi için smart contract yaz...",
            key=f"prompt_task_{task_number}"
        )

        # GERÇEK AI KOD ÜRETİMİ
        if st.button("🤖 Kod Üret", type="primary"):
            if not user_prompt.strip():
                st.error("❌ Lütfen önce bir prompt girin!")
            else:
                with st.spinner(f"{persona_obj.name} kod yazıyor..."):
                    # OpenAI GPT-4 ile kod üret (TAM mesajları da return eder)
                    generated_code, generation_time, gpt_messages, full_user_prompt = generate_code_with_persona(
                        persona_obj,
                        task,
                        user_prompt
                    )

                    # Kodu kaydet
                    code_id = DataLogger.save_generated_code(
                        task_session_id=st.session_state.current_task_session_id,
                        code_text=generated_code,
                        language="Solidity",
                        prompt_used=user_prompt,
                        ai_persona=persona_obj.name,
                        generation_time_seconds=generation_time
                    )

                    # Session'a kaydet (kalıcı gösterim için)
                    st.session_state.generated_code = generated_code
                    st.session_state.generation_time = generation_time
                    st.session_state.user_prompt = user_prompt  # Kullanıcının ORIJINAL prompt'u
                    st.session_state.full_user_prompt = full_user_prompt  # Görev + kullanıcı prompt BİRLEŞİK
                    st.session_state.gpt_messages = gpt_messages  # GPT-4'e giden TAM CONVERSATION
                    st.session_state.persona_system_prompt = persona_obj.system_prompt  # Persona system prompt
                    st.session_state.code_generated = True
                    st.rerun()

        # Kod üretildiyse göster (kalıcı)
        if st.session_state.get('code_generated', False) and st.session_state.get('generated_code'):
            st.success(f"✅ Kod başarıyla üretildi! (Süre: {st.session_state.generation_time:.1f} saniye)")

            # PROMPT ANALİZİ VE DETAYLARI
            with st.expander("🔍 Kod Üretim Süreci Detayları", expanded=False):
                st.markdown("### 📋 Gönderilen Promptlar:")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**1️⃣ Persona System Prompt (GPT-4'e giden):**")
                    st.code(st.session_state.persona_system_prompt[:500] + "...", language="markdown")
                    st.caption(f"Uzunluk: {len(st.session_state.persona_system_prompt)} karakter")

                with col2:
                    st.markdown("**2️⃣ Sizin Prompt'unuz:**")
                    st.code(st.session_state.user_prompt, language="markdown")
                    st.caption(f"Uzunluk: {len(st.session_state.user_prompt)} karakter")

                st.markdown("---")
                st.markdown("### 🔬 Prompt Analizi:")

                # Prompt kalite metrikleri
                user_prompt_length = len(st.session_state.user_prompt)
                prompt_quality_score = min(100, (user_prompt_length / 200) * 100)  # 200 karakter optimal

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prompt Uzunluğu", f"{user_prompt_length} char")
                with col2:
                    st.metric("Detay Seviyesi", f"{prompt_quality_score:.0f}/100")
                with col3:
                    st.metric("Kod Üretim Süresi", f"{st.session_state.generation_time:.2f}s")

                st.markdown("""
                **Prompt İşleme Akışı:**
                ```
                1. System Prompt → GPT-4 Context
                2. User Prompt + Task Description → User Message
                3. GPT-4 Processing → Code Generation
                4. Output → Solidity Smart Contract
                ```
                """)

                st.info("💡 **Araştırma Notu:** Persona'nın system prompt'u, kod üretim stilini ve yaklaşımını belirler. "
                       "Similar AI daha teknik, Complementary AI daha pedagojik açıklamalar yapar.")

            st.markdown("### 📝 Üretilen Kod:")
            st.code(st.session_state.generated_code, language="solidity")

            # 6 AŞAMALI İÇERİK ANALİZİ
            with st.expander("🔬 6 Aşamalı Matematiksel İçerik Analizi (Prompt + Kod)", expanded=False):
                st.markdown("""
                ### Bu bölümde üretilen **prompt** ve **kod** bilimsel olarak analiz edilir:

                **📊 AŞAMA 1:** Prompt Özellik Çıkarımı
                **🔄 AŞAMA 2:** Prompt Benzerlik Analizi (Cosine Similarity)
                **🏗️ AŞAMA 3:** Kod Yapısı Analizi
                **🔬 AŞAMA 4:** Kod Karmaşıklık Analizi
                **⭐ AŞAMA 5:** Kod Kalite Değerlendirmesi
                **📈 AŞAMA 6:** Komparatif Analiz (Persona Karşılaştırması)

                ---
                """)

                # Content Analyzer oluştur
                analyzer = ContentAnalyzer()

                # FULL ANALYSIS
                full_analysis = analyzer.full_analysis(
                    prompt=st.session_state.user_prompt,
                    code=st.session_state.generated_code
                )

                # AŞAMA 1: PROMPT ANALİZİ
                st.markdown("### 📊 AŞAMA 1: Prompt Özellik Analizi")
                prompt_analysis = full_analysis["stage_1_prompt_analysis"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Kelime Sayısı", prompt_analysis["word_count"])
                    st.metric("Cümle Sayısı", prompt_analysis["sentence_count"])
                with col2:
                    st.metric("Teknik Terim", prompt_analysis["technical_term_count"])
                    st.metric("Ortalama Kelime Uzunluğu", f"{prompt_analysis['avg_word_length']:.1f}")
                with col3:
                    st.metric("Netlik Skoru", f"{prompt_analysis['clarity_score']:.0f}/100")
                    st.metric("Özgüllük Skoru", f"{prompt_analysis['specificity_score']:.0f}/100")

                st.markdown("---")

                # AŞAMA 2: PROMPT BENZERLİK (eğer önceki görev varsa)
                if st.session_state.get('previous_prompt'):
                    st.markdown("### 🔄 AŞAMA 2: Prompt Benzerlik Analizi (Cosine Similarity)")
                    st.caption("Bir önceki görevdeki prompt'unuzla karşılaştırma:")

                    similarity = analyzer.calculate_prompt_similarity(
                        st.session_state.previous_prompt,
                        st.session_state.user_prompt
                    )

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Cosine Similarity", f"{similarity['cosine_similarity']:.3f}")
                    with col2:
                        st.metric("Jaccard Similarity", f"{similarity['jaccard_similarity']:.3f}")
                    with col3:
                        st.metric("Overlap Ratio", f"{similarity['overlap_ratio']:.3f}")

                    st.info(f"💡 **Yorum:** {similarity['interpretation']}")
                    st.markdown("---")
                else:
                    st.info("ℹ️ AŞAMA 2: Prompt benzerlik analizi için birden fazla görev tamamlamanız gerekiyor.")
                    st.markdown("---")

                # Gelecek görevler için bu prompt'u sakla
                st.session_state.previous_prompt = st.session_state.user_prompt

                # AŞAMA 3: KOD YAPISI
                st.markdown("### 🏗️ AŞAMA 3: Kod Yapısı Analizi")
                structure = full_analysis["stage_3_code_structure"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Toplam Satır", structure["total_lines"])
                    st.metric("Kod Satırı", structure["code_lines"])
                with col2:
                    st.metric("Yorum Satırı", structure["comment_lines"])
                    st.metric("Boş Satır", structure["blank_lines"])
                with col3:
                    st.metric("Yorum Oranı", f"{structure['comment_ratio']:.1f}%")
                    st.metric("Fonksiyon Sayısı", structure["function_count"])

                st.markdown("---")

                # AŞAMA 4: KOD KOMPLEKSİTE
                st.markdown("### 🔬 AŞAMA 4: Kod Karmaşıklık Analizi")
                complexity = full_analysis["stage_4_code_complexity"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Cyclomatic Complexity", complexity["cyclomatic_complexity"])
                    st.metric("Nesting Depth", complexity["nesting_depth"])
                with col2:
                    st.metric("Değişken Sayısı", complexity["variable_count"])
                    st.metric("Koşul Sayısı", complexity["conditional_count"])
                with col3:
                    st.metric("Döngü Sayısı", complexity["loop_count"])
                    st.metric("Karmaşıklık Skoru", f"{complexity['complexity_score']:.0f}/100")

                st.info(f"💡 **Karmaşıklık Seviyesi:** {complexity['complexity_level']}")
                st.markdown("---")

                # AŞAMA 5: KOD KALİTESİ
                st.markdown("### ⭐ AŞAMA 5: Kod Kalite Değerlendirmesi")
                quality = full_analysis["stage_5_code_quality"]

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Okunabilirlik", f"{quality['readability_score']:.0f}/100")
                with col2:
                    st.metric("Sürdürülebilirlik", f"{quality['maintainability_score']:.0f}/100")
                with col3:
                    st.metric("Dokümantasyon", f"{quality['documentation_score']:.0f}/100")
                with col4:
                    st.metric("Best Practices", f"{quality['best_practices_score']:.0f}/100")

                st.success(f"⭐ **GENEL KALİTE SKORU:** {quality['overall_quality']:.1f}/100 - {quality['quality_grade']}")
                st.markdown("---")

                # AŞAMA 6: KOMPARATİF ANALİZ (eğer önceki kod varsa)
                if st.session_state.get('previous_code') and st.session_state.get('previous_persona_name'):
                    st.markdown("### 📈 AŞAMA 6: Komparatif Analiz (Persona Karşılaştırması)")
                    st.caption("Bir önceki görevdeki kod ile karşılaştırma:")

                    comparison = analyzer.compare_persona_outputs(
                        persona1_name=st.session_state.previous_persona_name,
                        code1=st.session_state.previous_code,
                        prompt1=st.session_state.get('previous_prompt', ''),
                        persona2_name=persona_obj.name,
                        code2=st.session_state.generated_code,
                        prompt2=st.session_state.user_prompt
                    )

                    st.markdown("**🔄 Prompt Benzerliği:**")
                    st.write(f"Cosine Similarity: **{comparison['prompt_similarity']['cosine_similarity']:.3f}** - {comparison['prompt_similarity']['interpretation']}")

                    st.markdown("**📊 Kalite Karşılaştırması:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        prev_persona_name = st.session_state.previous_persona_name[:20] + "..."
                        prev_quality = comparison['quality_comparison'][st.session_state.previous_persona_name]
                        st.metric(prev_persona_name, f"{prev_quality:.1f}/100")
                    with col2:
                        curr_persona_name = persona_obj.name[:20] + "..."
                        curr_quality = comparison['quality_comparison'][persona_obj.name]
                        st.metric(curr_persona_name, f"{curr_quality:.1f}/100")

                    st.info(f"🏆 **Kalite Kazananı:** {comparison['quality_comparison']['winner']} "
                           f"(Fark: {comparison['quality_comparison']['difference']:.1f} puan)")

                    st.markdown("**🔬 Karmaşıklık Karşılaştırması:**")
                    st.write(f"Daha Basit Kod: **{comparison['complexity_comparison']['simpler']}**")

                    st.markdown("**📝 Dokümantasyon Karşılaştırması:**")
                    st.write(f"Daha İyi Dokümante: **{comparison['documentation_comparison']['better_documented']}**")
                else:
                    st.info("ℹ️ AŞAMA 6: Komparatif analiz için birden fazla görev tamamlamanız gerekiyor.")

                # Gelecek görevler için bu kodu sakla
                st.session_state.previous_code = st.session_state.generated_code
                st.session_state.previous_persona_name = persona_obj.name

                st.markdown("---")
                st.success("✅ 6 Aşamalı Matematiksel İçerik Analizi Tamamlandı!")

                st.markdown("""
                **📚 Kullanılan Metrikler:**
                - **TF-IDF Cosine Similarity:** Metin benzerliği ölçümü
                - **Cyclomatic Complexity:** Kod karmaşıklığı (McCabe, 1976)
                - **Halstead Metrics:** Kod hacmi ve zorluk
                - **Maintainability Index:** Sürdürülebilirlik skoru

                **🎓 Teorik Temel:**
                - Software Quality Metrics (ISO/IEC 25010)
                - Cognitive Complexity Theory
                - Code Readability Research (Buse & Weimer, 2010)
                """)

            st.info("💡 Kodu inceledikten sonra post-test'e geçebilirsiniz.")

        # Post-test'e geçiş (sadece kod üretildiyse aktif)
        if st.session_state.get('code_generated', False):
            if st.button("▶️ Sonraki: Post-Test", type="primary"):
                st.session_state.task_substep = 'post_test'
                st.session_state.code_generated = False  # Bir sonraki görev için sıfırla
                st.rerun()
        else:
            st.button("▶️ Sonraki: Post-Test", type="primary", disabled=True, help="Önce kod üretmelisiniz")

    elif substep == 'post_test':
        st.markdown("### 📝 Post-Test (5 soru)")
        st.info("Görev sonrası öğrenme kazanımınızı ölçelim.")

        post_test_questions = task.get_post_test_questions()
        post_answers = PrePostTestForm.show_test(post_test_questions, "post")

        if st.button("✅ Post-Test Tamamlandı", type="primary"):
            post_score = task.calculate_test_score(post_answers, "post")
            DataLogger.save_pre_post_test(
                st.session_state.current_task_session_id,
                "post",
                post_answers,
                post_score
            )

            st.session_state.task_substep = 'nasa_tlx'
            st.rerun()

    elif substep == 'nasa_tlx':
        st.markdown("### 🧠 Bilişsel Yük Değerlendirmesi (NASA-TLX)")
        st.info("Bu görev sırasındaki zihinsel yükünüzü değerlendirin.")

        nasa_responses = NASATLXForm.show()

        if st.button("✅ Değerlendirme Tamamlandı", type="primary"):
            DataLogger.save_nasa_tlx(st.session_state.current_task_session_id, nasa_responses)
            st.session_state.task_substep = 'ai_evaluation'
            st.rerun()

    elif substep == 'ai_evaluation':
        st.markdown("### ⭐ AI Kod Değerlendirmesi")
        st.info(f"{persona_obj.name}'in ürettiği kodu değerlendirin.")

        ai_eval_responses = AIEvaluationForm.show()

        if st.button("✅ AI Değerlendirmesi Tamamlandı", type="primary"):
            DataLogger.save_ai_evaluation(st.session_state.current_task_session_id, ai_eval_responses)

            # Görevi tamamla
            duration = (datetime.now() - st.session_state.task_start_time).total_seconds() / 60
            DataLogger.complete_task_session(st.session_state.current_task_session_id, int(duration))

            # Sonraki göreve geç
            st.session_state.current_task_number += 1
            st.session_state.task_substep = 'pre_test'
            st.session_state.current_task_session_id = None

            st.success(f"✅ Görev {task_number} tamamlandı!")
            time.sleep(1)
            st.rerun()


def phase_final():
    """Faz 4: Final Değerlendirme"""
    st.markdown('<h1 class="main-header">🎯 Final Değerlendirme</h1>', unsafe_allow_html=True)
    st.markdown('<div class="phase-badge">4. Genel Değerlendirme ve Geri Bildirim</div>', unsafe_allow_html=True)

    st.info("🎉 Tüm görevleri tamamladınız! Son olarak genel deneyiminizi değerlendirin.")

    final_responses = FinalSurveyForm.show()

    if st.button("✅ Araştırmayı Tamamla", type="primary", use_container_width=True):
        DataLogger.save_final_evaluation(st.session_state.participant_uuid, final_responses)

        total_duration = (datetime.now() - st.session_state.session_start_time).total_seconds() / 60
        DataLogger.mark_participant_completed(st.session_state.participant_uuid, int(total_duration))

        st.session_state.phase = 'complete'
        st.rerun()


def phase_complete():
    """Faz 5: Tamamlanma"""
    st.markdown('<h1 class="main-header">🎉 Tebrikler!</h1>', unsafe_allow_html=True)

    st.success("✅ Araştırmayı başarıyla tamamladınız!")

    st.markdown("""
    ### 🙏 Teşekkürler!

    Değerli katılımınız için teşekkür ederiz. Verileriniz anonim olarak saklanmakta ve
    sadece araştırma amaçlı kullanılacaktır.

    #### 📧 Sonuçlar
    Araştırma sonuçları tamamlandığında size e-posta ile bilgilendirme yapılacaktır.

    #### 🎁 Hediye Kartı Çekilişi
    Tüm katılımcılar arasından yapılacak çekilişe dahil edildiniz.

    #### 📜 Katılım Sertifikası
    Katılım sertifikanız e-posta adresinize gönderilecektir.

    ---

    **Katılımcı ID'niz:** `{}`

    Herhangi bir sorunuz varsa: research@pidl.edu
    """.format(st.session_state.participant_uuid[:8] + "..."))


# ============================================================================
# ANA UYGULAMA
# ============================================================================

def main():
    """Ana uygulama"""
    init_session_state()
    show_sidebar()

    phase = st.session_state.phase

    if phase == 'consent':
        phase_consent()
    elif phase == 'competency':
        phase_competency()
    elif phase == 'tasks':
        phase_tasks()
    elif phase == 'final':
        phase_final()
    elif phase == 'complete':
        phase_complete()


if __name__ == "__main__":
    main()
