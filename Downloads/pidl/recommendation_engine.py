"""
Matematiksel Tavsiye Sistemi (Recommendation Engine)
Doktora Araştırması: İnsan-AI İşbirliği Modellerinde Yetkinlik Transferi

Teorik Temeller:
- Cognitive Load Theory (Sweller, 1988)
- Dreyfus Model of Skill Acquisition
- Multi-Criteria Decision Analysis (MCDA)
- Collaborative Filtering
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

# Scipy yerine numpy ile kendi fonksiyonlarımız
def cosine_similarity(a, b):
    """Cosine similarity hesapla"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def euclidean_distance(a, b):
    """Euclidean distance hesapla"""
    return np.linalg.norm(a - b)


@dataclass
class UserVector:
    """Kullanıcı yetkinlik vektörü - Çok boyutlu representation"""
    # Temel yetkinlik boyutları
    technical_skill: float  # 0-1 arası
    domain_knowledge: float  # 0-1 arası
    ai_experience: float  # 0-1 arası
    learning_goal: float  # 0=production, 1=learning
    
    # Bilgi türleri (Nonaka & Takeuchi, 1995)
    procedural_knowledge: float  # "Nasıl" bilgisi
    declarative_knowledge: float  # "Ne" bilgisi
    conditional_knowledge: float  # "Ne zaman" bilgisi
    
    # Bilişsel faktörler
    cognitive_capacity: float  # İşlem kapasitesi
    pattern_recognition: float  # Pattern tanıma yeteneği
    abstraction_level: float  # Soyutlama seviyesi


@dataclass
class PersonaVector:
    """Persona karakteristik vektörü"""
    persona_id: str
    
    # Kod özellikleri
    code_complexity: float  # Kod karmaşıklığı
    verbosity: float  # Açıklayıcılık
    technical_depth: float  # Teknik derinlik
    pedagogical_focus: float  # Pedagojik odak
    
    # Stil özellikleri
    comment_density: float  # Yorum yoğunluğu
    modularity: float  # Modülerlik
    example_richness: float  # Örnek zenginliği
    
    # Performans karakteristikleri
    learning_support: float  # Öğrenme desteği
    production_readiness: float  # Production hazırlığı
    innovation_factor: float  # Yenilikçilik


class RecommendationEngine:
    """
    Matematiksel Tavsiye Motoru
    
    Ana Formül:
    R(u,p) = α·S(u,p) + β·C(u,p) + γ·P(u,p,g) + δ·L(u,t)
    
    Burada:
    - R(u,p): User u için Persona p'nin tavsiye skoru
    - S(u,p): Similarity score (benzerlik)
    - C(u,p): Competency match (yetkinlik uyumu)
    - P(u,p,g): Performance prediction (performans tahmini)
    - L(u,t): Learning trajectory (öğrenme yörüngesi)
    - α, β, γ, δ: Ağırlık katsayıları (Σ = 1)
    """
    
    def __init__(self, alpha=0.30, beta=0.35, gamma=0.25, delta=0.10):
        """
        Recommendation engine başlat
        
        Args:
            alpha: Similarity ağırlığı
            beta: Competency match ağırlığı
            gamma: Performance prediction ağırlığı
            delta: Learning trajectory ağırlığı
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        
        # Persona vektörlerini başlat
        self.persona_vectors = self._initialize_persona_vectors()
    
    def _initialize_persona_vectors(self) -> Dict[str, PersonaVector]:
        """
        Her persona için karakteristik vektörü tanımla - Dreyfus Model

        0.0 = Yok/Düşük
        1.0 = Çok yüksek/Maksimal

        Dreyfus Progression:
        - Novice: Low technical, high verbosity, low complexity
        - Advanced Beginner: Low-medium technical, high verbosity
        - Competent: Medium technical, medium verbosity, deliberate
        - Proficient: High technical, low verbosity, intuitive
        - Expert: Very high technical, low verbosity, innovative
        """
        return {
            # ============ EDUCATION DOMAIN - Dreyfus Levels ============

            "edu_novice": PersonaVector(  # Ayşe Yeni Başlayan (Novice)
                persona_id="edu_novice",
                code_complexity=0.15,  # Çok basit (tek fonksiyon)
                verbosity=0.98,  # Maksimal açıklayıcılık
                technical_depth=0.10,  # Çok düşük (3-6 ay, ChatGPT ile)
                pedagogical_focus=0.95,  # Yüksek (eğitim fakültesi)
                comment_density=0.98,  # Her satırda yorum
                modularity=0.15,  # Çok düşük (modülerlik bilmiyor)
                example_richness=0.85,  # Basit örnekler bol
                learning_support=0.92,  # Yüksek (yeni başlayan için anlaşılır)
                production_readiness=0.10,  # Çok düşük
                innovation_factor=0.08  # Minimal (tutorial takip)
            ),

            "edu_advanced_beginner": PersonaVector(  # Mehmet İlerleyen (Advanced Beginner)
                persona_id="edu_advanced_beginner",
                code_complexity=0.25,  # Basit-orta (pattern'ler var)
                verbosity=0.85,  # Yüksek
                technical_depth=0.25,  # Düşük-orta (1-2 yıl)
                pedagogical_focus=0.90,  # Yüksek
                comment_density=0.80,  # Yüksek (önemli yerlerde)
                modularity=0.35,  # Düşük-orta (modül kullanmaya başladı)
                example_richness=0.80,  # Örnek zengin
                learning_support=0.88,  # Yüksek
                production_readiness=0.25,  # Düşük
                innovation_factor=0.20  # Düşük (pattern takip)
            ),

            "edu_competent": PersonaVector(  # Zeynep Yetkin (Competent)
                persona_id="edu_competent",
                code_complexity=0.45,  # Orta (planlı kod)
                verbosity=0.65,  # Orta
                technical_depth=0.50,  # Orta (3-5 yıl)
                pedagogical_focus=0.85,  # Yüksek
                comment_density=0.60,  # Orta (kritik kararlar)
                modularity=0.60,  # Orta-yüksek
                example_richness=0.70,  # Orta
                learning_support=0.80,  # Yüksek
                production_readiness=0.50,  # Orta
                innovation_factor=0.40  # Orta-düşük (standart çözümler)
            ),

            "edu_proficient": PersonaVector(  # Ali Usta (Proficient)
                persona_id="edu_proficient",
                code_complexity=0.65,  # Orta-yüksek (holistic)
                verbosity=0.50,  # Orta-düşük (self-documenting)
                technical_depth=0.75,  # Yüksek (6-10 yıl)
                pedagogical_focus=0.88,  # Çok yüksek (intuitive pedagoji)
                comment_density=0.40,  # Orta-düşük
                modularity=0.80,  # Yüksek
                example_richness=0.75,  # Yüksek (sophisticated örnekler)
                learning_support=0.85,  # Çok yüksek (adaptive)
                production_readiness=0.70,  # Yüksek
                innovation_factor=0.65  # Orta-yüksek (advanced patterns)
            ),

            "edu_expert": PersonaVector(  # Fatma Uzman (Expert)
                persona_id="edu_expert",
                code_complexity=0.80,  # Yüksek (paradigm-shifting)
                verbosity=0.35,  # Düşük (research referansları)
                technical_depth=0.88,  # Çok yüksek (10+ yıl, doktora)
                pedagogical_focus=0.95,  # Maksimal (research-based)
                comment_density=0.30,  # Düşük (papers'a referans)
                modularity=0.85,  # Çok yüksek (innovative architecture)
                example_richness=0.70,  # Orta-yüksek (cutting-edge)
                learning_support=0.80,  # Yüksek (ama ileri seviye)
                production_readiness=0.75,  # Yüksek (ama experimental)
                innovation_factor=0.95  # Maksimal (paradigm yaratıcı)
            ),

            # ============ TECHNOLOGY DOMAIN - Dreyfus Levels ============

            "tech_novice": PersonaVector(  # Can Acemi (Novice)
                persona_id="tech_novice",
                code_complexity=0.12,  # Çok basit (kopyala-yapıştır)
                verbosity=0.95,  # Çok yüksek (her satırda yorum)
                technical_depth=0.08,  # Minimal (1-3 ay Solidity)
                pedagogical_focus=0.15,  # Çok düşük (pedagoji bilmiyor)
                comment_density=0.95,  # Maksimal
                modularity=0.10,  # Minimal (tek contract)
                example_richness=0.30,  # Düşük (basit örnekler)
                learning_support=0.35,  # Düşük (kendisi öğreniyor)
                production_readiness=0.05,  # Minimal (güvenlik yok)
                innovation_factor=0.05  # Minimal (tutorial takip)
            ),

            "tech_advanced_beginner": PersonaVector(  # Deniz Gelişen (Advanced Beginner)
                persona_id="tech_advanced_beginner",
                code_complexity=0.30,  # Düşük-orta (OpenZeppelin patterns)
                verbosity=0.75,  # Yüksek-orta
                technical_depth=0.35,  # Düşük-orta (6-12 ay)
                pedagogical_focus=0.20,  # Düşük
                comment_density=0.70,  # Orta-yüksek
                modularity=0.40,  # Düşük-orta (modifier kullanıyor)
                example_richness=0.45,  # Orta-düşük
                learning_support=0.48,  # Orta-düşük
                production_readiness=0.35,  # Düşük-orta
                innovation_factor=0.25  # Düşük (pattern adapte)
            ),

            "tech_competent": PersonaVector(  # Elif Yetkin (Competent)
                persona_id="tech_competent",
                code_complexity=0.55,  # Orta (gas optimized)
                verbosity=0.50,  # Orta
                technical_depth=0.65,  # Orta-yüksek (2-4 yıl)
                pedagogical_focus=0.25,  # Düşük-orta
                comment_density=0.50,  # Orta (kritik kararlar)
                modularity=0.70,  # Yüksek (production patterns)
                example_richness=0.50,  # Orta
                learning_support=0.55,  # Orta
                production_readiness=0.75,  # Yüksek (security audit)
                innovation_factor=0.45  # Orta-düşük (proven solutions)
            ),

            "tech_proficient": PersonaVector(  # Burak İleri (Proficient)
                persona_id="tech_proficient",
                code_complexity=0.75,  # Yüksek (holistic DApp)
                verbosity=0.35,  # Düşük-orta (self-documenting)
                technical_depth=0.85,  # Çok yüksek (5-8 yıl)
                pedagogical_focus=0.30,  # Düşük-orta (architecture focus)
                comment_density=0.35,  # Düşük-orta
                modularity=0.90,  # Çok yüksek (enterprise patterns)
                example_richness=0.60,  # Orta-yüksek
                learning_support=0.60,  # Orta
                production_readiness=0.90,  # Çok yüksek
                innovation_factor=0.75  # Yüksek (advanced patterns)
            ),

            "tech_expert": PersonaVector(  # Ahmet Uzman (Expert)
                persona_id="tech_expert",
                code_complexity=0.88,  # Çok yüksek (protocol-level)
                verbosity=0.25,  # Düşük (research papers)
                technical_depth=0.98,  # Maksimal (10+ yıl, EVM mastery)
                pedagogical_focus=0.18,  # Düşük (innovation focus)
                comment_density=0.25,  # Düşük (EIP referansları)
                modularity=0.85,  # Çok yüksek (novel architectures)
                example_richness=0.55,  # Orta (cutting-edge)
                learning_support=0.50,  # Orta (ileri seviye için)
                production_readiness=0.85,  # Çok yüksek (ama experimental)
                innovation_factor=0.98  # Maksimal (paradigm-shifting)
            )
        }
    
    def create_user_vector(self, competency_profile: Dict) -> UserVector:
        """
        Kullanıcı profilinden çok boyutlu vektör oluştur
        
        Args:
            competency_profile: Yetkinlik profil dict'i
            
        Returns:
            UserVector objesi
        """
        score = competency_profile.get('score', 0) / 100  # 0-1 normalize
        domain = competency_profile.get('domain', 'technical')
        level = competency_profile.get('level', 'novice')
        responses = competency_profile.get('responses', {})
        
        # Dreyfus model mapping
        level_mapping = {
            'novice': 0.1,
            'advanced_beginner': 0.3,
            'competent': 0.5,
            'proficient': 0.7,
            'expert': 0.9
        }
        
        technical_skill = level_mapping.get(level, 0.5)
        
        # Domain knowledge
        domain_knowledge = 0.8 if domain == 'technical' else 0.7
        
        # AI experience
        ai_experience = 0.7 if responses.get('ai_experience') else 0.2
        
        # Learning vs production goal
        # Competent ve altı genellikle learning, üstü production
        if level in ['novice', 'advanced_beginner']:
            learning_goal = 0.9
        elif level == 'competent':
            learning_goal = 0.6
        else:
            learning_goal = 0.3
        
        # Bilgi türleri (response pattern'lerinden çıkar)
        procedural = min(1.0, score * 1.2)  # Nasıl yapılır bilgisi
        declarative = score  # Ne olduğu bilgisi
        conditional = max(0.3, score - 0.2)  # Ne zaman bilgisi
        
        # Bilişsel faktörler
        cognitive_capacity = 0.5 + (score * 0.5)  # Skor arttıkça kapasite artar
        pattern_recognition = max(0.3, score - 0.1)
        abstraction_level = score  # Expert'ler daha soyut düşünür
        
        return UserVector(
            technical_skill=technical_skill,
            domain_knowledge=domain_knowledge,
            ai_experience=ai_experience,
            learning_goal=learning_goal,
            procedural_knowledge=procedural,
            declarative_knowledge=declarative,
            conditional_knowledge=conditional,
            cognitive_capacity=cognitive_capacity,
            pattern_recognition=pattern_recognition,
            abstraction_level=abstraction_level
        )
    
    def calculate_similarity_score(self, user: UserVector, persona: PersonaVector, 
                                   focus_dimension: str = "all") -> float:
        """
        S(u,p): Kullanıcı-Persona Benzerlik Skoru
        
        Cosine Similarity + Euclidean Distance'ın hibrit kombinasyonu
        
        Formül:
        S(u,p) = w₁·cos_sim(u,p) + w₂·(1 - norm_euclidean(u,p))
        
        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü
            
        Returns:
            Benzerlik skoru (0-1)
        """
        # User vektörünü numpy array'e çevir
        user_vec = np.array([
            user.technical_skill,
            user.domain_knowledge,
            user.ai_experience,
            user.learning_goal,
            user.cognitive_capacity,
            user.abstraction_level
        ])
        
        # Persona vektörünü numpy array'e çevir
        persona_vec = np.array([
            persona.technical_depth,
            persona.technical_depth,  # Domain proxy
            persona.innovation_factor,  # AI exp proxy
            1 - persona.production_readiness,  # Learning goal inverse
            1 - persona.code_complexity,  # Cognitive capacity inverse
            persona.code_complexity  # Abstraction proxy
        ])
        
        # Cosine similarity (yön benzerliği)
        cos_sim = cosine_similarity(user_vec, persona_vec)
        
        # Normalized Euclidean distance (mesafe benzerliği)
        euclidean_dist = euclidean_distance(user_vec, persona_vec)
        max_dist = np.sqrt(len(user_vec))  # Maksimum olası mesafe
        norm_euclidean = euclidean_dist / max_dist
        euclidean_sim = 1 - norm_euclidean
        
        # Hibrit skor (ağırlıklı ortalama)
        similarity = 0.6 * cos_sim + 0.4 * euclidean_sim
        
        return max(0, min(1, similarity))
    
    def calculate_competency_match(self, user: UserVector, persona: PersonaVector) -> float:
        """
        C(u,p): Yetkinlik Uyum Skoru
        
        Zone of Proximal Development (Vygotsky) bazlı
        Optimal challenge = biraz yukarıda ama ulaşılabilir
        
        Formül:
        C(u,p) = exp(-λ|u_skill - p_difficulty|²) · alignment_factor
        
        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü
            
        Returns:
            Uyum skoru (0-1)
        """
        # Persona difficulty (kod karmaşıklığı ve teknik derinlikten)
        persona_difficulty = (persona.code_complexity + persona.technical_depth) / 2
        
        # Kullanıcı skill seviyesi
        user_skill = (user.technical_skill + user.domain_knowledge) / 2
        
        # ZPD optimal mesafe (Gaussian)
        lambda_param = 2.0  # Hassasiyet parametresi
        skill_diff = abs(user_skill - persona_difficulty)
        
        # Gaussian benzerlik (optimal mesafe: küçük pozitif fark)
        gaussian_match = np.exp(-lambda_param * (skill_diff ** 2))
        
        # Learning goal alignment
        if user.learning_goal > 0.7:  # Öğrenme odaklı
            # Pedagojik persona'ları tercih et
            alignment = persona.pedagogical_focus
        else:  # Production odaklı
            # Production-ready persona'ları tercih et
            alignment = persona.production_readiness
        
        # Bilgi türü uyumu
        knowledge_match = (
            user.procedural_knowledge * persona.modularity * 0.4 +
            user.declarative_knowledge * persona.verbosity * 0.3 +
            user.conditional_knowledge * persona.learning_support * 0.3
        )
        
        # Final competency match
        competency_match = (
            gaussian_match * 0.5 +
            alignment * 0.3 +
            knowledge_match * 0.2
        )
        
        return max(0, min(1, competency_match))
    
    def predict_performance(self, user: UserVector, persona: PersonaVector, 
                          task_complexity: float = 0.5) -> float:
        """
        P(u,p,g): Performans Tahmin Skoru
        
        Regresyon modeli bazlı tahmin
        
        Formül:
        P = σ(β₀ + β₁·u_skill + β₂·p_quality + β₃·match + β₄·task_complexity)
        
        σ: Sigmoid fonksiyonu
        
        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü
            task_complexity: Görev karmaşıklığı (0-1)
            
        Returns:
            Tahmini performans (0-1)
        """
        # Regresyon katsayıları (fitted from pilot data)
        beta_0 = 0.3  # Intercept
        beta_1 = 0.4  # User skill coefficient
        beta_2 = 0.3  # Persona quality coefficient
        beta_3 = 0.25  # Match coefficient
        beta_4 = -0.2  # Task complexity coefficient (negative)
        
        # Feature'lar
        user_skill_feature = (user.technical_skill + user.domain_knowledge) / 2
        persona_quality = (persona.production_readiness + persona.learning_support) / 2
        match_feature = self.calculate_similarity_score(user, persona)
        
        # Linear combination
        z = (beta_0 + 
             beta_1 * user_skill_feature +
             beta_2 * persona_quality +
             beta_3 * match_feature +
             beta_4 * task_complexity)
        
        # Sigmoid activation
        performance = 1 / (1 + np.exp(-z))
        
        return max(0, min(1, performance))
    
    def calculate_learning_trajectory(self, user: UserVector, persona: PersonaVector, 
                                     time_factor: float = 0.5) -> float:
        """
        L(u,t): Öğrenme Yörüngesi Skoru
        
        Zaman içinde beklenen öğrenme gelişimi
        
        Formül:
        L(u,p,t) = L_max · (1 - e^(-k·t)) · potential(u,p)
        
        Power Law of Practice (Newell & Rosenbloom)
        
        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü
            time_factor: Zaman faktörü (0-1)
            
        Returns:
            Öğrenme potansiyeli (0-1)
        """
        # Öğrenme potansiyeli
        L_max = 1.0
        k = 2.0  # Öğrenme hızı parametresi
        
        # Zamanla öğrenme (exponential growth)
        time_learning = L_max * (1 - np.exp(-k * time_factor))
        
        # Persona'nın öğrenme desteği
        learning_support = persona.learning_support
        
        # Kullanıcının öğrenme kapasitesi
        learning_capacity = (
            user.cognitive_capacity * 0.4 +
            user.pattern_recognition * 0.3 +
            (1 - user.abstraction_level) * 0.3  # Başlangıç seviyesi daha çok öğrenir
        )
        
        # Potential function
        potential = learning_support * learning_capacity
        
        # Final trajectory score
        trajectory = time_learning * potential
        
        return max(0, min(1, trajectory))
    
    def calculate_complementarity(self, user: UserVector, persona: PersonaVector) -> float:
        """
        D(u,p): Tamamlayıcılık Skoru
        
        Kullanıcının zayıf olduğu, persona'nın güçlü olduğu alanlar
        
        Formül:
        D(u,p) = Σ max(0, p_strong_i - u_weak_i) / n
        
        Yüksek D = persona kullanıcının eksiklerini tamamlıyor
        
        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü
            
        Returns:
            Tamamlayıcılık skoru (0-1)
        """
        # Kullanıcının zayıf yönleri (düşük skorlar)
        user_weaknesses = {
            'technical': 1 - user.technical_skill,
            'domain': 1 - user.domain_knowledge,
            'ai_experience': 1 - user.ai_experience,
            'abstraction': 1 - user.abstraction_level
        }
        
        # Persona'nın güçlü yönleri
        persona_strengths = {
            'technical': persona.technical_depth,
            'domain': persona.pedagogical_focus if user.learning_goal > 0.5 else persona.production_readiness,
            'ai_experience': persona.innovation_factor,
            'abstraction': persona.code_complexity
        }
        
        # Complementarity: Persona'nın güçlü, user'ın zayıf olduğu alanlar
        complementarity_scores = []
        for key in user_weaknesses:
            # User zayıf VE persona güçlü ise yüksek skor
            comp = persona_strengths.get(key, 0) * user_weaknesses.get(key, 0)
            complementarity_scores.append(comp)
        
        # Ortalama tamamlayıcılık
        avg_complementarity = np.mean(complementarity_scores)

        return max(0, min(1, avg_complementarity))

    # ============================================================================
    # COGNITIVE LOAD THEORY (Sweller, 1988) - Implementation
    # ============================================================================

    def calculate_intrinsic_load(self, user: UserVector, task_complexity: float = 0.5) -> float:
        """
        Intrinsic Load: Görevin doğal karmaşıklığından kaynaklanan yük

        Sweller (1988): Intrinsic load is determined by the complexity of the material
        and the learner's prior knowledge.

        Formül:
        IL(u,t) = task_complexity × (1 - user_expertise)

        Yüksek task complexity + Düşük user expertise = Yüksek intrinsic load

        Args:
            user: Kullanıcı vektörü
            task_complexity: Görev karmaşıklığı (0-1)

        Returns:
            Intrinsic load (0-1)
        """
        # Kullanıcı uzmanlığı (skill + knowledge + experience)
        user_expertise = (
            user.technical_skill * 0.4 +
            user.domain_knowledge * 0.3 +
            user.procedural_knowledge * 0.3
        )

        # Intrinsic load = task difficulty relative to user expertise
        # Novice için karmaşık task → yüksek IL
        # Expert için karmaşık task → düşük IL
        intrinsic_load = task_complexity * (1 - user_expertise)

        return max(0, min(1, intrinsic_load))

    def calculate_extraneous_load(self, persona: PersonaVector) -> float:
        """
        Extraneous Load: Kötü tasarımdan kaynaklanan gereksiz bilişsel yük

        Sweller (1988): Extraneous load is caused by the manner in which information
        is presented to learners and the learning activities required of them.

        Formül:
        EL(p) = w₁·poor_organization + w₂·excessive_verbosity + w₃·code_complexity

        Düşük modularity = Kötü organize
        Çok yüksek verbosity = Aşırı kelime
        Yüksek complexity = Karmaşık yapı

        Args:
            persona: Persona vektörü

        Returns:
            Extraneous load (0-1)
        """
        # Kötü organizasyon (düşük modularity = yüksek yük)
        poor_organization = 1 - persona.modularity

        # Aşırı verbosity (çok fazla yorum/açıklama → bilişsel yük)
        # Optimal verbosity: 0.5-0.7 arası
        # Çok düşük (<0.3) veya çok yüksek (>0.8) = extraneous load
        if persona.verbosity < 0.3:
            excessive_verbosity = 0.3 - persona.verbosity  # Çok az açıklama
        elif persona.verbosity > 0.8:
            excessive_verbosity = persona.verbosity - 0.8  # Çok fazla açıklama
        else:
            excessive_verbosity = 0.0  # Optimal range

        # Kod karmaşıklığı (çok karmaşık = yüksek extraneous load)
        # Optimal complexity: persona seviyesine uygun
        # Çok karmaşık kod = gereksiz yük
        code_complexity_load = persona.code_complexity * 0.5  # Partial contribution

        # Extraneous load hesaplama
        extraneous_load = (
            poor_organization * 0.4 +
            excessive_verbosity * 0.3 +
            code_complexity_load * 0.3
        )

        return max(0, min(1, extraneous_load))

    def calculate_germane_load(self, user: UserVector, persona: PersonaVector) -> float:
        """
        Germane Load: Öğrenmeye yönelik yararlı bilişsel yük

        Sweller (1988): Germane load is the load devoted to the construction and
        automation of schemas - the "good" cognitive load that promotes learning.

        Formül:
        GL(u,p) = learning_support × learning_capacity × pedagogical_alignment

        Yüksek learning support + Yüksek pedagogical focus = Yüksek germane load

        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü

        Returns:
            Germane load (0-1)
        """
        # Persona'nın öğrenme desteği
        learning_support = persona.learning_support

        # Persona'nın pedagojik odağı
        pedagogical_quality = persona.pedagogical_focus

        # Kullanıcının öğrenme kapasitesi
        learning_capacity = (
            user.cognitive_capacity * 0.4 +
            user.pattern_recognition * 0.3 +
            user.learning_goal * 0.3  # Öğrenme motivasyonu
        )

        # Örnek zenginliği (schema construction için)
        example_richness = persona.example_richness

        # Germane load hesaplama
        germane_load = (
            learning_support * 0.35 +
            pedagogical_quality * 0.30 +
            learning_capacity * 0.20 +
            example_richness * 0.15
        )

        return max(0, min(1, germane_load))

    def calculate_total_cognitive_load(self, user: UserVector, persona: PersonaVector,
                                       task_complexity: float = 0.5) -> Dict[str, float]:
        """
        Total Cognitive Load (Sweller, 1988)

        Formül:
        TCL = Intrinsic Load + Extraneous Load - Germane Load

        Optimal Learning Zone:
        IL + GL ≤ Cognitive Capacity
        EL minimized

        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü
            task_complexity: Görev karmaşıklığı

        Returns:
            Dict with all load components and warnings
        """
        # Hesapla 3 load bileşenini
        intrinsic = self.calculate_intrinsic_load(user, task_complexity)
        extraneous = self.calculate_extraneous_load(persona)
        germane = self.calculate_germane_load(user, persona)

        # Total cognitive load
        # Germane pozitif etki (öğrenmeye yardımcı) → çıkar
        total_load = intrinsic + extraneous - germane
        total_load = max(0, min(2, total_load))  # 0-2 arası normalize

        # Cognitive capacity
        capacity = user.cognitive_capacity

        # Optimal Learning Zone check (Sweller)
        # IL + GL ≤ Capacity AND EL minimal
        productive_load = intrinsic + germane
        is_in_optimal_zone = (productive_load <= capacity) and (extraneous < 0.3)

        # Overload detection
        is_overloaded = total_load > capacity
        overload_amount = max(0, total_load - capacity)

        # Underload detection (too easy, not challenging)
        is_underloaded = total_load < (capacity * 0.4)

        # Load efficiency (Germane / Total)
        if total_load > 0:
            load_efficiency = germane / (intrinsic + extraneous + 0.001)
        else:
            load_efficiency = 0

        # Recommendations
        warnings = []
        recommendations = []

        if is_overloaded:
            warnings.append(f"⚠️ Cognitive Overload! ({overload_amount:.2f} over capacity)")
            recommendations.append("Consider easier persona or simpler task")

        if is_underloaded:
            warnings.append("ℹ️ Underutilized capacity - task may be too easy")
            recommendations.append("Consider more challenging persona")

        if extraneous > 0.5:
            warnings.append(f"⚠️ High Extraneous Load ({extraneous:.2f})")
            recommendations.append("Persona may have poor organization or excessive verbosity")

        if germane < 0.3:
            warnings.append(f"ℹ️ Low Germane Load ({germane:.2f})")
            recommendations.append("Limited learning support - consider pedagogical persona")

        if is_in_optimal_zone:
            recommendations.append("✅ Optimal Learning Zone - ideal match!")

        return {
            "intrinsic_load": intrinsic,
            "extraneous_load": extraneous,
            "germane_load": germane,
            "total_load": total_load,
            "productive_load": productive_load,
            "cognitive_capacity": capacity,
            "load_efficiency": load_efficiency,
            "is_in_optimal_zone": is_in_optimal_zone,
            "is_overloaded": is_overloaded,
            "is_underloaded": is_underloaded,
            "overload_amount": overload_amount,
            "warnings": warnings,
            "recommendations": recommendations
        }

    def get_clt_optimal_personas(self, user: UserVector, task_complexity: float = 0.5,
                                  top_k: int = 5) -> List[Dict]:
        """
        CLT bazlı optimal persona tavsiyesi

        Sweller'in teorisine göre en iyi persona'ları seç:
        1. Optimal Learning Zone'da olan
        2. Düşük Extraneous Load
        3. Yüksek Germane Load
        4. Cognitive Overload yaratmayan

        Args:
            user: Kullanıcı vektörü
            task_complexity: Görev karmaşıklığı
            top_k: Kaç tane persona

        Returns:
            CLT skorlarına göre sıralı persona listesi
        """
        clt_rankings = []

        for persona_id, persona_vec in self.persona_vectors.items():
            clt_analysis = self.calculate_total_cognitive_load(user, persona_vec, task_complexity)

            # CLT Score hesaplama
            # Yüksek germane + Düşük extraneous + Optimal zone
            clt_score = (
                clt_analysis["germane_load"] * 0.35 +
                (1 - clt_analysis["extraneous_load"]) * 0.30 +
                clt_analysis["load_efficiency"] * 0.20 +
                (1.0 if clt_analysis["is_in_optimal_zone"] else 0.0) * 0.15
            )

            # Penalty for overload
            if clt_analysis["is_overloaded"]:
                clt_score *= (1 - clt_analysis["overload_amount"] * 0.5)

            clt_rankings.append({
                "persona_id": persona_id,
                "clt_score": clt_score,
                "clt_analysis": clt_analysis
            })

        # CLT score'a göre sırala
        clt_rankings.sort(key=lambda x: x["clt_score"], reverse=True)

        return clt_rankings[:top_k]

    def calculate_recommendation_score(self, user: UserVector, persona: PersonaVector,
                                      task_complexity: float = 0.5,
                                      time_factor: float = 0.5,
                                      mode: str = "adaptive") -> Dict:
        """
        R(u,p): Ana Tavsiye Skoru Hesaplama (DUAL-MODE)
        
        MOD 1 - SIMILARITY (Production/Rahat çalışma):
        R(u,p) = α·S(u,p) + β·C(u,p) + γ·P(u,p) + δ·L(u,t)
        
        MOD 2 - COMPLEMENTARY (Learning/Eksikleri kapatma):
        R(u,p) = α·(1-S) + β·D(u,p) + γ·P(u,p) + δ·L(u,t)
        
        MOD 3 - ADAPTIVE (Otomatik seçim):
        Learning goal > 0.7 → Complementary
        Learning goal < 0.3 → Similarity
        Arası → Hybrid
        
        Args:
            user: Kullanıcı vektörü
            persona: Persona vektörü
            task_complexity: Görev karmaşıklığı
            time_factor: Zaman faktörü
            mode: "similarity", "complementary", veya "adaptive"
            
        Returns:
            Detaylı skor breakdown'u
        """
        # Bileşenleri hesapla
        similarity = self.calculate_similarity_score(user, persona)
        competency = self.calculate_competency_match(user, persona)
        performance = self.predict_performance(user, persona, task_complexity)
        learning = self.calculate_learning_trajectory(user, persona, time_factor)
        complementarity = self.calculate_complementarity(user, persona)
        
        # Mod belirleme
        if mode == "adaptive":
            if user.learning_goal > 0.7:
                actual_mode = "complementary"
            elif user.learning_goal < 0.3:
                actual_mode = "similarity"
            else:
                actual_mode = "hybrid"
        else:
            actual_mode = mode
        
        # Mod'a göre skor hesaplama
        if actual_mode == "similarity":
            # Production/Rahat çalışma modu
            total_score = (
                self.alpha * similarity +
                self.beta * competency +
                self.gamma * performance +
                self.delta * learning
            )
            strategy = "Benzerlik Bazlı (Rahat Çalışma)"
            
        elif actual_mode == "complementary":
            # Learning/Eksik kapatma modu
            dissimilarity = 1 - similarity  # Farklılık
            total_score = (
                self.alpha * dissimilarity +
                self.beta * complementarity +
                self.gamma * performance +
                self.delta * learning
            )
            strategy = "Tamamlayıcı (Eksik Kapatma)"
            
        else:  # hybrid
            # Her ikisinin ortalaması
            similarity_score = (
                self.alpha * similarity +
                self.beta * competency +
                self.gamma * performance +
                self.delta * learning
            )
            
            dissimilarity = 1 - similarity
            complementary_score = (
                self.alpha * dissimilarity +
                self.beta * complementarity +
                self.gamma * performance +
                self.delta * learning
            )
            
            # Ağırlıklı ortalama (learning goal'e göre)
            total_score = (
                user.learning_goal * complementary_score +
                (1 - user.learning_goal) * similarity_score
            )
            strategy = "Hibrit (Adaptif)"
        
        # Confidence interval (95% CI)
        std_dev = 0.05
        ci_lower = max(0, total_score - 1.96 * std_dev)
        ci_upper = min(1, total_score + 1.96 * std_dev)
        
        return {
            "total_score": total_score,
            "mode": actual_mode,
            "strategy": strategy,
            "components": {
                "similarity": similarity,
                "dissimilarity": 1 - similarity,
                "competency_match": competency,
                "complementarity": complementarity,
                "performance_prediction": performance,
                "learning_trajectory": learning
            },
            "weights": {
                "alpha": self.alpha,
                "beta": self.beta,
                "gamma": self.gamma,
                "delta": self.delta
            },
            "confidence_interval": {
                "lower": ci_lower,
                "upper": ci_upper,
                "std_dev": std_dev
            }
        }
    
    def rank_personas(self, user_vector: UserVector, 
                     task_complexity: float = 0.5,
                     top_k: int = 5) -> List[Dict]:
        """
        Tüm persona'ları skorla ve sırala
        
        Multi-Criteria Decision Analysis (MCDA) yaklaşımı
        
        Args:
            user_vector: Kullanıcı vektörü
            task_complexity: Görev karmaşıklığı
            top_k: En iyi K persona
            
        Returns:
            Sıralı persona listesi
        """
        rankings = []
        
        for persona_id, persona_vec in self.persona_vectors.items():
            scores = self.calculate_recommendation_score(
                user_vector, 
                persona_vec,
                task_complexity
            )
            
            rankings.append({
                "persona_id": persona_id,
                "score": scores["total_score"],
                "components": scores["components"],
                "confidence_interval": scores["confidence_interval"]
            })
        
        # Skora göre sırala (descending)
        rankings.sort(key=lambda x: x["score"], reverse=True)
        
        return rankings[:top_k]
    
    def explain_recommendation(self, user_vector: UserVector, persona_id: str) -> str:
        """
        Tavsiye açıklaması üret (Explainable AI)
        
        Args:
            user_vector: Kullanıcı vektörü
            persona_id: Persona ID
            
        Returns:
            Açıklama metni
        """
        persona = self.persona_vectors.get(persona_id)
        if not persona:
            return "Persona bulunamadı"
        
        scores = self.calculate_recommendation_score(user_vector, persona)
        components = scores["components"]
        
        # En yüksek katkıyı bulan bileşen
        max_component = max(components.items(), key=lambda x: x[1])
        
        explanations = {
            "similarity": f"Sizin yetkinlik profilinize çok benziyor (benzerlik: {components['similarity']:.2f})",
            "competency_match": f"Seviyenize tam uygun - optimal challenge (uyum: {components['competency_match']:.2f})",
            "performance_prediction": f"Yüksek performans beklentisi (tahmin: {components['performance_prediction']:.2f})",
            "learning_trajectory": f"Güçlü öğrenme potansiyeli (yörünge: {components['learning_trajectory']:.2f})"
        }
        
        main_reason = explanations.get(max_component[0], "Genel uyumluluk")
        
        return f"{main_reason}. Toplam skor: {scores['total_score']:.2f}"
    
    def optimize_persona_weights(self, user_vector: UserVector, 
                                 feedback_data: Optional[List[Dict]] = None) -> Dict[str, float]:
        """
        Bayesian Optimization ile persona ağırlıklarını optimize et
        
        Kullanıcı feedback'ine göre α, β, γ, δ parametrelerini ayarla
        
        Formül:
        P(θ|D) ∝ P(D|θ) · P(θ)
        
        θ = {α, β, γ, δ}: Parametreler
        D: Feedback data
        
        Args:
            user_vector: Kullanıcı vektörü
            feedback_data: Kullanıcı feedback verileri
            
        Returns:
            Optimize edilmiş ağırlıklar
        """
        if feedback_data is None or len(feedback_data) == 0:
            # Prior: Varsayılan ağırlıklar
            return {
                "alpha": self.alpha,
                "beta": self.beta,
                "gamma": self.gamma,
                "delta": self.delta
            }
        
        # Basit Bayesian update (gerçek uygulamada MCMC kullanılır)
        # Feedback'den learning rate hesapla
        positive_feedback = sum(1 for f in feedback_data if f.get('rating', 0) > 3)
        total_feedback = len(feedback_data)
        
        if total_feedback > 0:
            success_rate = positive_feedback / total_feedback
            
            # Success rate'e göre ağırlıkları ayarla
            if user_vector.learning_goal > 0.7:
                # Learning odaklıysa, similarity ve learning'i artır
                alpha_new = self.alpha + 0.1 * success_rate
                delta_new = self.delta + 0.1 * success_rate
                beta_new = self.beta - 0.05 * success_rate
                gamma_new = self.gamma - 0.05 * success_rate
            else:
                # Production odaklıysa, competency ve performance'ı artır
                beta_new = self.beta + 0.1 * success_rate
                gamma_new = self.gamma + 0.1 * success_rate
                alpha_new = self.alpha - 0.05 * success_rate
                delta_new = self.delta - 0.05 * success_rate
            
            # Normalize et (toplam = 1)
            total = alpha_new + beta_new + gamma_new + delta_new
            
            return {
                "alpha": alpha_new / total,
                "beta": beta_new / total,
                "gamma": gamma_new / total,
                "delta": delta_new / total
            }
        
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "delta": self.delta
        }


# Test için
if __name__ == "__main__":
    engine = RecommendationEngine()
    
    # Test user
    test_profile = {
        "score": 50,
        "level": "competent",
        "domain": "technical",
        "responses": {"ai_experience": True}
    }
    
    user_vec = engine.create_user_vector(test_profile)
    
    # Rank personas
    rankings = engine.rank_personas(user_vec, task_complexity=0.5, top_k=5)
    
    print("🎯 Top 5 Persona Tavsiyeleri:\n")
    for idx, ranking in enumerate(rankings, 1):
        persona_id = ranking["persona_id"]
        score = ranking["score"]
        components = ranking["components"]
        
        print(f"{idx}. {persona_id}: {score:.3f}")
        print(f"   Benzerlik: {components['similarity']:.3f}")
        print(f"   Yetkinlik Uyumu: {components['competency_match']:.3f}")
        print(f"   Performans Tahmini: {components['performance_prediction']:.3f}")
        print(f"   Öğrenme Yörüngesi: {components['learning_trajectory']:.3f}")
        print()

