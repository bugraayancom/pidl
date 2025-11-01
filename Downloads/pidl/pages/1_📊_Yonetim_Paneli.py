"""
PIDL Araştırma Yönetim Paneli
Admin dashboard - Veri analizi ve raporlama
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
sys.path.insert(0, '..')

from database.database import DatabaseSession
from database.models import (
    Participant, TaskSession, PrePostTest, GeneratedCode,
    NASATLXResponse, AICodeEvaluation, FinalEvaluation,
    TaskStatus, AIType
)
from content_analyzer import ContentAnalyzer

# Sayfa yapılandırması
st.set_page_config(
    page_title="PIDL Yönetim Paneli",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
    }
    .metric-card p {
        color: white;
        font-size: 1.2rem;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 📊 PIDL Araştırma Yönetim Paneli")
st.markdown("---")

# Veri yükleme fonksiyonları
@st.cache_data(ttl=60)  # 60 saniye cache
def load_dashboard_data():
    """Tüm dashboard verilerini yükle"""
    with DatabaseSession() as session:
        # Katılımcılar
        participants = session.query(Participant).all()

        # Task sessions
        task_sessions = session.query(TaskSession).all()

        # Pre/Post tests
        tests = session.query(PrePostTest).all()

        # Generated codes
        codes = session.query(GeneratedCode).all()

        # NASA-TLX responses
        nasa_responses = session.query(NASATLXResponse).all()

        # AI evaluations
        ai_evals = session.query(AICodeEvaluation).all()

        # Final evaluations
        final_evals = session.query(FinalEvaluation).all()

        return {
            "participants": participants,
            "task_sessions": task_sessions,
            "tests": tests,
            "codes": codes,
            "nasa_responses": nasa_responses,
            "ai_evals": ai_evals,
            "final_evals": final_evals
        }


# Veriyi yükle
data = load_dashboard_data()

# 1. GENEL İSTATİSTİKLER
st.markdown("## 📈 Genel İstatistikler")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_participants = len(data["participants"])
    completed_participants = len([p for p in data["participants"] if p.completed])
    st.markdown(f"""
    <div class="metric-card">
        <h1>{total_participants}</h1>
        <p>Toplam Katılımcı</p>
        <p style="font-size: 0.9rem;">({completed_participants} tamamlandı)</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_tasks = len(data["task_sessions"])
    completed_tasks = len([t for t in data["task_sessions"] if t.status == TaskStatus.COMPLETED])
    st.markdown(f"""
    <div class="metric-card">
        <h1>{total_tasks}</h1>
        <p>Toplam Görev Oturumu</p>
        <p style="font-size: 0.9rem;">({completed_tasks} tamamlandı)</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_codes = len(data["codes"])
    avg_generation_time = sum([c.generation_time_seconds for c in data["codes"]]) / len(data["codes"]) if data["codes"] else 0
    st.markdown(f"""
    <div class="metric-card">
        <h1>{total_codes}</h1>
        <p>Üretilen Kod Sayısı</p>
        <p style="font-size: 0.9rem;">(Ort: {avg_generation_time:.1f}s)</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_nasa = len(data["nasa_responses"])
    avg_cognitive_load = sum([n.total_cognitive_load for n in data["nasa_responses"]]) / len(data["nasa_responses"]) if data["nasa_responses"] else 0
    st.markdown(f"""
    <div class="metric-card">
        <h1>{total_nasa}</h1>
        <p>NASA-TLX Ölçümü</p>
        <p style="font-size: 0.9rem;">(Ort Yük: {avg_cognitive_load:.1f}/60)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 2. KATILIMCI ANALİZİ
st.markdown("## 👥 Katılımcı Analizi")

if data["participants"]:
    # Yetkinlik dağılımı
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Yetkinlik Seviyesi Dağılımı")
        level_counts = {}
        for p in data["participants"]:
            level = p.competency_level.value if hasattr(p.competency_level, 'value') else str(p.competency_level)
            level_counts[level] = level_counts.get(level, 0) + 1

        fig = px.pie(
            values=list(level_counts.values()),
            names=list(level_counts.keys()),
            title="Dreyfus Seviye Dağılımı"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🎯 Teknik vs Pedagojik Skorlar")
        participants_df = pd.DataFrame([{
            "Teknik": p.technical_score,
            "Pedagojik": p.pedagogical_score,
            "Seviye": p.competency_level.value if hasattr(p.competency_level, 'value') else str(p.competency_level)
        } for p in data["participants"]])

        fig = px.scatter(
            participants_df,
            x="Teknik",
            y="Pedagojik",
            color="Seviye",
            title="Teknik-Pedagojik Skor Dağılımı",
            labels={"Teknik": "Teknik Skor (0-300)", "Pedagojik": "Pedagojik Skor (0-300)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Demografik bilgiler
    st.markdown("### 📋 Demografik Dağılım")
    col1, col2, col3 = st.columns(3)

    with col1:
        gender_counts = {}
        for p in data["participants"]:
            gender_counts[p.gender] = gender_counts.get(p.gender, 0) + 1
        fig = px.bar(x=list(gender_counts.keys()), y=list(gender_counts.values()), title="Cinsiyet Dağılımı")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        edu_counts = {}
        for p in data["participants"]:
            edu_counts[p.education] = edu_counts.get(p.education, 0) + 1
        fig = px.bar(x=list(edu_counts.keys()), y=list(edu_counts.values()), title="Eğitim Durumu")
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        work_counts = {}
        for p in data["participants"]:
            work_counts[p.work_field] = work_counts.get(p.work_field, 0) + 1
        fig = px.bar(x=list(work_counts.keys()), y=list(work_counts.values()), title="Çalışma Alanı")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Henüz katılımcı verisi yok.")

st.markdown("---")

# 3. GÖREV ANALİZİ
st.markdown("## 💻 Görev Performans Analizi")

if data["task_sessions"]:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Görev Tamamlanma Durumu")
        task_counts = {}
        for t in data["task_sessions"]:
            status = t.status.value if hasattr(t.status, 'value') else str(t.status)
            task_counts[status] = task_counts.get(status, 0) + 1

        fig = px.pie(
            values=list(task_counts.values()),
            names=list(task_counts.keys()),
            title="Görev Durumu Dağılımı"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🤖 AI Persona Kullanımı")
        ai_counts = {}
        for t in data["task_sessions"]:
            ai_type = t.assigned_ai_type.value if hasattr(t.assigned_ai_type, 'value') else str(t.assigned_ai_type)
            ai_counts[ai_type] = ai_counts.get(ai_type, 0) + 1

        fig = px.bar(
            x=list(ai_counts.keys()),
            y=list(ai_counts.values()),
            title="Similar vs Complementary AI",
            labels={"x": "AI Tipi", "y": "Kullanım Sayısı"}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Görev bazlı süre analizi
    st.markdown("### ⏱️ Görev Süreleri")
    completed_sessions = [t for t in data["task_sessions"] if t.duration_minutes and t.duration_minutes > 0]
    if completed_sessions:
        task_durations = {}
        for t in completed_sessions:
            task_num = f"Görev {t.task_number}"
            if task_num not in task_durations:
                task_durations[task_num] = []
            task_durations[task_num].append(t.duration_minutes)

        avg_durations = {k: sum(v)/len(v) for k, v in task_durations.items()}

        fig = px.bar(
            x=list(avg_durations.keys()),
            y=list(avg_durations.values()),
            title="Ortalama Görev Tamamlanma Süreleri",
            labels={"x": "Görev", "y": "Süre (dakika)"}
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Henüz görev verisi yok.")

st.markdown("---")

# 4. ÖĞRENME KAZANIMI ANALİZİ
st.markdown("## 📚 Öğrenme Kazanımı Analizi (Pre-test vs Post-test)")

if data["tests"]:
    # Pre vs Post skorları
    pre_tests = [t for t in data["tests"] if t.test_type.value == "PRE" or str(t.test_type) == "PRE"]
    post_tests = [t for t in data["tests"] if t.test_type.value == "POST" or str(t.test_type) == "POST"]

    if pre_tests and post_tests:
        col1, col2, col3 = st.columns(3)

        pre_avg = sum([t.score for t in pre_tests]) / len(pre_tests)
        post_avg = sum([t.score for t in post_tests]) / len(post_tests)
        improvement = post_avg - pre_avg

        with col1:
            st.metric("Pre-test Ortalama", f"{pre_avg:.1f}/100")
        with col2:
            st.metric("Post-test Ortalama", f"{post_avg:.1f}/100")
        with col3:
            st.metric("Öğrenme Kazanımı", f"+{improvement:.1f} puan", delta=f"{(improvement/pre_avg*100):.1f}%")

        # Görev bazlı kazanım
        st.markdown("### 📈 Görev Bazlı Öğrenme Kazanımı")

        # Task session ID'ye göre grupla
        learning_gains = {}
        with DatabaseSession() as session:
            for task_session in data["task_sessions"]:
                pre = session.query(PrePostTest).filter_by(
                    task_session_id=task_session.id,
                    test_type="PRE"
                ).first()
                post = session.query(PrePostTest).filter_by(
                    task_session_id=task_session.id,
                    test_type="POST"
                ).first()

                if pre and post:
                    task_key = f"Görev {task_session.task_number}"
                    if task_key not in learning_gains:
                        learning_gains[task_key] = []
                    learning_gains[task_key].append(post.score - pre.score)

        if learning_gains:
            avg_gains = {k: sum(v)/len(v) for k, v in learning_gains.items()}
            fig = px.bar(
                x=list(avg_gains.keys()),
                y=list(avg_gains.values()),
                title="Ortalama Öğrenme Kazanımı (Post - Pre)",
                labels={"x": "Görev", "y": "Kazanım (puan)"}
            )
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Henüz test verisi yok.")

st.markdown("---")

# 5. BİLİŞSEL YÜK ANALİZİ (NASA-TLX)
st.markdown("## 🧠 Bilişsel Yük Analizi")

if data["nasa_responses"]:
    st.markdown("### 📊 NASA-TLX Boyutları")

    dimensions = ["mental_demand", "physical_demand", "temporal_demand", "performance", "effort", "frustration"]
    dim_names = {
        "mental_demand": "Zihinsel Talep",
        "physical_demand": "Fiziksel Talep",
        "temporal_demand": "Zamansal Baskı",
        "performance": "Performans",
        "effort": "Çaba",
        "frustration": "Hayal Kırıklığı"
    }

    avg_scores = {}
    for dim in dimensions:
        scores = [getattr(n, dim) for n in data["nasa_responses"]]
        avg_scores[dim_names[dim]] = sum(scores) / len(scores)

    fig = go.Figure(data=[
        go.Bar(
            x=list(avg_scores.keys()),
            y=list(avg_scores.values()),
            marker_color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        )
    ])
    fig.update_layout(
        title="Ortalama NASA-TLX Boyut Skorları",
        yaxis_title="Skor (1-10)",
        xaxis_title="Boyut"
    )
    st.plotly_chart(fig, use_container_width=True)

    # AI tipi bazlı bilişsel yük
    st.markdown("### 🤖 AI Tipi Bazlı Bilişsel Yük")

    with DatabaseSession() as session:
        similar_loads = []
        complementary_loads = []

        for nasa in data["nasa_responses"]:
            task_session = session.query(TaskSession).filter_by(id=nasa.task_session_id).first()
            if task_session:
                ai_type = task_session.assigned_ai_type.value if hasattr(task_session.assigned_ai_type, 'value') else str(task_session.assigned_ai_type)
                if "SIMILAR" in ai_type.upper():
                    similar_loads.append(nasa.total_cognitive_load)
                else:
                    complementary_loads.append(nasa.total_cognitive_load)

        if similar_loads and complementary_loads:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Similar AI - Ort Yük", f"{sum(similar_loads)/len(similar_loads):.1f}/60")
            with col2:
                st.metric("Complementary AI - Ort Yük", f"{sum(complementary_loads)/len(complementary_loads):.1f}/60")

else:
    st.info("Henüz NASA-TLX verisi yok.")

st.markdown("---")

# 6. AI DEĞERLENDİRME ANALİZİ
st.markdown("## ⭐ AI Kod Değerlendirme Analizi")

if data["ai_evals"]:
    st.markdown("### 📊 AI Değerlendirme Boyutları")

    dimensions = {
        "code_understandability": "Kod Anlaşılırlığı",
        "explanation_quality": "Açıklama Kalitesi",
        "educational_value": "Eğitsel Değer",
        "perceived_code_quality": "Algılanan Kod Kalitesi",
        "perceived_security": "Algılanan Güvenlik"
    }

    avg_ratings = {}
    for key, name in dimensions.items():
        ratings = [getattr(e, key) for e in data["ai_evals"]]
        avg_ratings[name] = sum(ratings) / len(ratings)

    fig = go.Figure(data=[
        go.Scatterpolar(
            r=list(avg_ratings.values()),
            theta=list(avg_ratings.keys()),
            fill='toself',
            name='Ortalama Değerlendirme'
        )
    ])
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title="AI Kod Değerlendirme - Radar Chart"
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Henüz AI değerlendirme verisi yok.")

st.markdown("---")

# 7. DETAYLI VERİ TABLOSU
st.markdown("## 📋 Detaylı Veri Tabloları")

tab1, tab2, tab3, tab4 = st.tabs(["Katılımcılar", "Görev Oturumları", "Üretilen Kodlar", "Test Sonuçları"])

with tab1:
    if data["participants"]:
        participants_data = []
        for p in data["participants"]:
            participants_data.append({
                "UUID": p.uuid[:8] + "...",
                "Yaş": p.age,
                "Cinsiyet": p.gender,
                "Eğitim": p.education,
                "Teknik": p.technical_score,
                "Pedagojik": p.pedagogical_score,
                "Seviye": p.competency_level.value if hasattr(p.competency_level, 'value') else str(p.competency_level),
                "Tamamlandı": "✅" if p.completed else "⏳",
                "Süre (dk)": p.total_duration_minutes or 0
            })
        st.dataframe(pd.DataFrame(participants_data), use_container_width=True)

with tab2:
    if data["task_sessions"]:
        sessions_data = []
        for t in data["task_sessions"]:
            sessions_data.append({
                "ID": t.id,
                "Görev": t.task_number,
                "AI Tipi": t.assigned_ai_type.value if hasattr(t.assigned_ai_type, 'value') else str(t.assigned_ai_type),
                "Persona": t.assigned_persona,
                "Durum": t.status.value if hasattr(t.status, 'value') else str(t.status),
                "Süre (dk)": t.duration_minutes or 0
            })
        st.dataframe(pd.DataFrame(sessions_data), use_container_width=True)

with tab3:
    if data["codes"]:
        codes_data = []
        for c in data["codes"]:
            codes_data.append({
                "ID": c.id,
                "Session": c.task_session_id,
                "Persona": c.ai_persona,
                "Dil": c.language,
                "Süre (s)": f"{c.generation_time_seconds:.1f}",
                "Satır": len(c.code_text.split('\n')),
                "Prompt": c.prompt_used[:50] + "..." if len(c.prompt_used) > 50 else c.prompt_used
            })
        st.dataframe(pd.DataFrame(codes_data), use_container_width=True)

with tab4:
    if data["tests"]:
        tests_data = []
        for t in data["tests"]:
            tests_data.append({
                "ID": t.id,
                "Session": t.task_session_id,
                "Tip": t.test_type.value if hasattr(t.test_type, 'value') else str(t.test_type),
                "Skor": t.score
            })
        st.dataframe(pd.DataFrame(tests_data), use_container_width=True)

st.markdown("---")

# 8. EXPORT İŞLEMLERİ
st.markdown("## 💾 Veri Dışa Aktarma")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Katılımcı Verisini İndir (CSV)", use_container_width=True):
        if data["participants"]:
            df = pd.DataFrame([{
                "uuid": p.uuid,
                "age": p.age,
                "gender": p.gender,
                "education": p.education,
                "work_field": p.work_field,
                "technical_score": p.technical_score,
                "pedagogical_score": p.pedagogical_score,
                "competency_level": p.competency_level.value if hasattr(p.competency_level, 'value') else str(p.competency_level),
                "completed": p.completed,
                "total_duration_minutes": p.total_duration_minutes
            } for p in data["participants"]])

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 CSV İndir",
                csv,
                "participants.csv",
                "text/csv",
                key='download-participants-csv'
            )

with col2:
    if st.button("📥 Görev Verisini İndir (CSV)", use_container_width=True):
        if data["task_sessions"]:
            df = pd.DataFrame([{
                "id": t.id,
                "participant_uuid": t.participant_uuid,
                "task_number": t.task_number,
                "assigned_ai_type": t.assigned_ai_type.value if hasattr(t.assigned_ai_type, 'value') else str(t.assigned_ai_type),
                "assigned_persona": t.assigned_persona,
                "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                "duration_minutes": t.duration_minutes
            } for t in data["task_sessions"]])

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 CSV İndir",
                csv,
                "task_sessions.csv",
                "text/csv",
                key='download-tasks-csv'
            )

with col3:
    if st.button("📥 Tüm Veriyi İndir (Excel)", use_container_width=True):
        st.info("Excel export özelliği yakında eklenecek!")

# 8. 🔬 İÇERİK ANALİZİ - 6 AŞAMALI MATEMATİKSEL ANALİZ
st.markdown("---")
st.markdown("## 🔬 İçerik Analizi - 6 Aşamalı Matematiksel Model")

# İçerik analizi aktif - Tüm prompt ve kodlar analiz edilir
if len(data["codes"]) > 0:
    st.info(f"📊 Toplam {len(data['codes'])} kod analiz edilebilir durumda.")

    # Content Analyzer'ı başlat
    analyzer = ContentAnalyzer()

    # Tüm kodları analiz et
    all_analyses = []

    with st.spinner("Tüm kodlar analiz ediliyor..."):
        for code_obj in data["codes"]:
            if code_obj.code_text and code_obj.prompt_used:
                try:
                    analysis = analyzer.full_analysis(
                        prompt=code_obj.prompt_used,
                        code=code_obj.code_text
                    )

                    all_analyses.append({
                        "code_id": code_obj.id,
                        "task_session_id": code_obj.task_session_id,
                        "ai_persona": code_obj.ai_persona,
                        "generation_time": code_obj.generation_time_seconds,
                        "created_at": code_obj.created_at,
                        "analysis": analysis
                    })
                except Exception as e:
                    st.warning(f"Kod ID {code_obj.id} analiz edilemedi: {str(e)}")

    if len(all_analyses) == 0:
        st.warning("⚠️ Analiz yapılabilecek geçerli kod bulunamadı. Kodların hem prompt hem de kod metni içermesi gerekir.")
    else:
        st.success(f"✅ {len(all_analyses)} kod başarıyla analiz edildi!")

        # TAB'lar ile organize et
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 AŞAMA 1: Prompt Analizi",
            "🏗️ AŞAMA 3: Kod Yapısı",
            "🔬 AŞAMA 4: Karmaşıklık",
            "⭐ AŞAMA 5: Kalite",
            "📈 Persona Karşılaştırması"
        ])

        # ========================================================================
        # TAB 1: PROMPT ANALİZİ
        # ========================================================================
        with tab1:
            st.markdown("### 📊 AŞAMA 1: Prompt Özellik Analizi")

            # DataFrame oluştur
            prompt_data = []
            for item in all_analyses:
                pa = item["analysis"]["stage_1_prompt_analysis"]
                prompt_data.append({
                    "Code ID": item["code_id"],
                    "AI Persona": item["ai_persona"],
                    "Kelime Sayısı": pa["word_count"],
                    "Cümle Sayısı": pa["sentence_count"],
                    "Teknik Terim": pa["technical_term_count"],
                    "Netlik Skoru": pa["clarity_score"],
                    "Özgüllük Skoru": pa["specificity_score"],
                    "Ort. Kelime Uzunluğu": pa["avg_word_length"]
                })

            df_prompt = pd.DataFrame(prompt_data)

            if len(df_prompt) > 0 and 'Kelime Sayısı' in df_prompt.columns:
                # Ortalama metrikler
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Ort. Kelime Sayısı", f"{df_prompt['Kelime Sayısı'].mean():.1f}")
                with col2:
                    st.metric("Ort. Teknik Terim", f"{df_prompt['Teknik Terim'].mean():.1f}")
                with col3:
                    st.metric("Ort. Netlik Skoru", f"{df_prompt['Netlik Skoru'].mean():.1f}/100")
                with col4:
                    st.metric("Ort. Özgüllük", f"{df_prompt['Özgüllük Skoru'].mean():.1f}/100")

                st.markdown("---")

                # Tablo göster
                st.dataframe(df_prompt, use_container_width=True)

                # Grafik: Netlik vs Özgüllük
                fig = px.scatter(df_prompt,
                                x="Netlik Skoru",
                                y="Özgüllük Skoru",
                                color="AI Persona",
                                size="Teknik Terim",
                                hover_data=["Code ID", "Kelime Sayısı"],
                                title="Prompt Netlik vs Özgüllük (Teknik Terim Sayısına Göre Boyut)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Henüz analiz edilecek veri yok.")

        # ========================================================================
        # TAB 2: KOD YAPISI
        # ========================================================================
        with tab2:
            st.markdown("### 🏗️ AŞAMA 3: Kod Yapısı Analizi")

            structure_data = []
            for item in all_analyses:
                struct = item["analysis"]["stage_3_code_structure"]
                structure_data.append({
                    "Code ID": item["code_id"],
                    "AI Persona": item["ai_persona"],
                    "Toplam Satır": struct["total_lines"],
                    "Kod Satırı": struct["code_lines"],
                    "Yorum Satırı": struct["comment_lines"],
                    "Yorum Oranı (%)": struct["comment_ratio"],
                    "Fonksiyon Sayısı": struct["function_count"],
                    "Ort. Satır Uzunluğu": struct["avg_line_length"]
                })

            df_structure = pd.DataFrame(structure_data)

            if len(df_structure) > 0 and 'Toplam Satır' in df_structure.columns:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Ort. Toplam Satır", f"{df_structure['Toplam Satır'].mean():.0f}")
                with col2:
                    st.metric("Ort. Kod Satırı", f"{df_structure['Kod Satırı'].mean():.0f}")
                with col3:
                    st.metric("Ort. Yorum Oranı", f"{df_structure['Yorum Oranı (%)'].mean():.1f}%")
                with col4:
                    st.metric("Ort. Fonksiyon", f"{df_structure['Fonksiyon Sayısı'].mean():.1f}")

                st.markdown("---")
                st.dataframe(df_structure, use_container_width=True)

                # Grafik: Yorum Oranı Karşılaştırması
                fig = px.bar(df_structure,
                            x="Code ID",
                            y="Yorum Oranı (%)",
                            color="AI Persona",
                            title="Yorum Oranı - Persona Karşılaştırması",
                            text="Yorum Oranı (%)")
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Henüz analiz edilecek veri yok.")

        # ========================================================================
        # TAB 3: KARMAŞIKLIK
        # ========================================================================
        with tab3:
            st.markdown("### 🔬 AŞAMA 4: Kod Karmaşıklık Analizi")

            complexity_data = []
            for item in all_analyses:
                comp = item["analysis"]["stage_4_code_complexity"]
                complexity_data.append({
                    "Code ID": item["code_id"],
                    "AI Persona": item["ai_persona"],
                    "Cyclomatic Complexity": comp["cyclomatic_complexity"],
                    "Nesting Depth": comp["nesting_depth"],
                    "Değişken Sayısı": comp["variable_count"],
                    "Koşul Sayısı": comp["conditional_count"],
                    "Döngü Sayısı": comp["loop_count"],
                    "Karmaşıklık Skoru": comp["complexity_score"],
                    "Seviye": comp["complexity_level"]
                })

            df_complexity = pd.DataFrame(complexity_data)

            if len(df_complexity) > 0 and 'Cyclomatic Complexity' in df_complexity.columns:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Ort. Cyclomatic", f"{df_complexity['Cyclomatic Complexity'].mean():.1f}")
                with col2:
                    st.metric("Ort. Nesting Depth", f"{df_complexity['Nesting Depth'].mean():.1f}")
                with col3:
                    st.metric("Ort. Karmaşıklık", f"{df_complexity['Karmaşıklık Skoru'].mean():.1f}/100")
                with col4:
                    # En basit persona
                    simplest = df_complexity.groupby("AI Persona")["Karmaşıklık Skoru"].mean().idxmin()
                    st.metric("En Basit Kod", simplest)

                st.markdown("---")
                st.dataframe(df_complexity, use_container_width=True)

                # Grafik: Karmaşıklık Dağılımı
                fig = px.box(df_complexity,
                            x="AI Persona",
                            y="Karmaşıklık Skoru",
                            color="AI Persona",
                            title="Karmaşıklık Skoru Dağılımı - Persona Bazlı")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Henüz analiz edilecek veri yok.")

        # ========================================================================
        # TAB 4: KALİTE
        # ========================================================================
        with tab4:
            st.markdown("### ⭐ AŞAMA 5: Kod Kalite Değerlendirmesi")

            quality_data = []
            for item in all_analyses:
                qual = item["analysis"]["stage_5_code_quality"]
                quality_data.append({
                    "Code ID": item["code_id"],
                    "AI Persona": item["ai_persona"],
                    "Okunabilirlik": qual["readability_score"],
                    "Sürdürülebilirlik": qual["maintainability_score"],
                    "Dokümantasyon": qual["documentation_score"],
                    "Best Practices": qual["best_practices_score"],
                    "⭐ Genel Kalite": qual["overall_quality"],
                    "Not": qual["quality_grade"]
                })

            df_quality = pd.DataFrame(quality_data)

            if len(df_quality) > 0 and '⭐ Genel Kalite' in df_quality.columns:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Ort. Genel Kalite", f"{df_quality['⭐ Genel Kalite'].mean():.1f}/100")
                with col2:
                    st.metric("Ort. Okunabilirlik", f"{df_quality['Okunabilirlik'].mean():.1f}/100")
                with col3:
                    st.metric("Ort. Dokümantasyon", f"{df_quality['Dokümantasyon'].mean():.1f}/100")
                with col4:
                    # En yüksek kalite
                    best_persona = df_quality.groupby("AI Persona")["⭐ Genel Kalite"].mean().idxmax()
                    st.metric("En İyi Kalite", best_persona)

                st.markdown("---")
                st.dataframe(df_quality, use_container_width=True)

                # Radar Chart: Kalite Boyutları
                persona_avg = df_quality.groupby("AI Persona").mean()

                fig = go.Figure()

                for persona in persona_avg.index:
                    fig.add_trace(go.Scatterpolar(
                        r=[
                            persona_avg.loc[persona, "Okunabilirlik"],
                            persona_avg.loc[persona, "Sürdürülebilirlik"],
                            persona_avg.loc[persona, "Dokümantasyon"],
                            persona_avg.loc[persona, "Best Practices"]
                        ],
                        theta=["Okunabilirlik", "Sürdürülebilirlik", "Dokümantasyon", "Best Practices"],
                        fill='toself',
                        name=persona
                    ))

                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title="Kalite Boyutları - Persona Karşılaştırması (Radar Chart)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Henüz analiz edilecek veri yok.")

        # ========================================================================
        # TAB 5: PERSONA KARŞILAŞTIRMASI
        # ========================================================================
        with tab5:
            st.markdown("### 📈 Persona Karşılaştırmalı Analiz")

            # Persona bazında toplu karşılaştırma
            if len(all_analyses) >= 2:
                personas = list(set([item["ai_persona"] for item in all_analyses]))

                st.markdown("#### 🏆 Persona Performans Tablosu")

                comparison_data = []
                for persona in personas:
                    persona_items = [item for item in all_analyses if item["ai_persona"] == persona]

                    if len(persona_items) > 0:
                        # Ortalama metrikler
                        avg_quality = sum([item["analysis"]["stage_5_code_quality"]["overall_quality"]
                                          for item in persona_items]) / len(persona_items)
                        avg_complexity = sum([item["analysis"]["stage_4_code_complexity"]["complexity_score"]
                                             for item in persona_items]) / len(persona_items)
                        avg_comment_ratio = sum([item["analysis"]["stage_3_code_structure"]["comment_ratio"]
                                                for item in persona_items]) / len(persona_items)
                        avg_generation_time = sum([item["generation_time"]
                                                   for item in persona_items]) / len(persona_items)

                        comparison_data.append({
                            "Persona": persona,
                            "Kod Sayısı": len(persona_items),
                            "⭐ Ort. Kalite": round(avg_quality, 1),
                            "🔬 Ort. Karmaşıklık": round(avg_complexity, 1),
                            "📝 Ort. Yorum Oranı (%)": round(avg_comment_ratio, 1),
                            "⏱️ Ort. Üretim Süresi (s)": round(avg_generation_time, 2)
                        })

                df_comparison = pd.DataFrame(comparison_data)
                df_comparison = df_comparison.sort_values("⭐ Ort. Kalite", ascending=False)

                st.dataframe(df_comparison, use_container_width=True)

                # En iyi persona
                best = df_comparison.iloc[0]
                st.success(f"🏆 **En İyi Persona:** {best['Persona']} - "
                          f"Kalite: {best['⭐ Ort. Kalite']}/100, "
                          f"Karmaşıklık: {best['🔬 Ort. Karmaşıklık']}/100")

                # Karşılaştırmalı bar chart
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    name='Kalite',
                    x=df_comparison['Persona'],
                    y=df_comparison['⭐ Ort. Kalite'],
                    marker_color='lightgreen'
                ))

                fig.add_trace(go.Bar(
                    name='Karmaşıklık (Ters)',
                    x=df_comparison['Persona'],
                    y=100 - df_comparison['🔬 Ort. Karmaşıklık'],  # Ters çevir (düşük = iyi)
                    marker_color='lightcoral'
                ))

                fig.update_layout(
                    title="Persona Performans Karşılaştırması (Yüksek = Daha İyi)",
                    xaxis_title="Persona",
                    yaxis_title="Skor (0-100)",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Karşılaştırma için en az 2 kod gerekli.")

else:
    st.warning("⚠️ Henüz analiz edilebilecek kod bulunmuyor. Katılımcılar görevleri tamamladıkça bu bölüm dolacaktır.")

# Footer
st.markdown("---")
st.markdown("**Son Güncelleme:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
st.markdown("**PIDL Araştırma Sistemi** | Persona in the Loop - Admin Panel")
