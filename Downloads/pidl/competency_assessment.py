"""
Yetkinlik Değerlendirme ve Tavsiye Sistemi
Dreyfus Model of Skill Acquisition bazlı

Matematiksel recommendation engine ile entegre
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime
import json

try:
    from recommendation_engine import RecommendationEngine, UserVector
    RECOMMENDATION_ENGINE_AVAILABLE = True
except ImportError:
    RECOMMENDATION_ENGINE_AVAILABLE = False


@dataclass
class CompetencyProfile:
    """Kullanıcı yetkinlik profili - DUAL DOMAIN"""
    user_id: str
    # Dual domain scores
    technical_score: float  # Blockchain/teknik (0-100)
    educational_score: float  # Eğitim/pedagoji (0-100)
    technical_level: str  # Teknik yetkinlik seviyesi
    educational_level: str  # Eğitimsel yetkinlik seviyesi
    # Genel
    overall_score: float  # Ortalama skor
    dominant_domain: str  # "technical" veya "educational" (hangisi güçlü)
    weak_domain: str  # Zayıf olan domain
    assessment_date: str
    responses: Dict
    recommended_personas_similarity: List[str]  # Benzerlik bazlı
    recommended_personas_complementary: List[str]  # Tamamlayıcı bazlı


class CompetencyAssessment:
    """Yetkinlik değerlendirme sistemi"""
    
    # Dreyfus Modeli Seviyeleri
    LEVELS = {
        "novice": {"min": 0, "max": 20, "name": "Novice (Acemi)"},
        "advanced_beginner": {"min": 21, "max": 40, "name": "Advanced Beginner (İleri Başlangıç)"},
        "competent": {"min": 41, "max": 60, "name": "Competent (Yetkin)"},
        "proficient": {"min": 61, "max": 80, "name": "Proficient (Usta)"},
        "expert": {"min": 81, "max": 100, "name": "Expert (Uzman)"}
    }
    
    # Teknik Domain Soruları
    TECHNICAL_QUESTIONS = [
        {
            "id": "tech_1",
            "question": "Python programlama deneyiminiz ne kadar?",
            "options": [
                ("Hiç yok veya çok az (0-6 ay)", 5),
                ("Temel seviye (6 ay - 2 yıl)", 15),
                ("Orta seviye (2-5 yıl)", 30),
                ("İleri seviye (5-10 yıl)", 45),
                ("Uzman seviye (10+ yıl)", 60)
            ]
        },
        {
            "id": "tech_2",
            "question": "Kod yazmada hangi yaklaşımı kullanırsınız?",
            "options": [
                ("Stack Overflow'dan kopyala-yapıştır yaparım", 5),
                ("Örneklere bakarak anlamaya çalışırım", 15),
                ("Belgeleri okur ve uygularım", 30),
                ("Best practices'e göre tasarlarım", 45),
                ("Mimari desenler ve optimizasyon yaparım", 60)
            ]
        },
        {
            "id": "tech_3",
            "question": "Algoritma ve veri yapıları bilginiz?",
            "options": [
                ("Temel list, dict biliyorum", 5),
                ("For döngüsü, if-else rahat kullanırım", 15),
                ("Big-O kavramını biliyorum", 30),
                ("Karmaşık veri yapıları uygulayabilirim", 45),
                ("Optimal algoritma seçimi ve analizi yaparım", 60)
            ]
        },
        {
            "id": "tech_4",
            "question": "Clean code ve design patterns hakkında bilginiz?",
            "options": [
                ("Hiç duymadım", 5),
                ("İsimlerini duydum", 15),
                ("Bazılarını kullanmaya çalışırım", 30),
                ("Çoğunu uygulayabilirim", 45),
                ("Hangi durumda hangisini kullanacağımı bilirim", 60)
            ]
        },
        {
            "id": "tech_5",
            "question": "Kod review ve refactoring deneyiminiz?",
            "options": [
                ("Hiç yapmadım", 5),
                ("Kendi kodumu gözden geçiririm", 15),
                ("Başkalarının kodunu anlayabilirim", 30),
                ("Düzenli review ve refactor yaparım", 45),
                ("Mentorluk yapar, mimari kararlar veririm", 60)
            ]
        }
    ]
    
    # Eğitim Domain Soruları
    EDUCATIONAL_QUESTIONS = [
        {
            "id": "edu_1",
            "question": "Eğitim teknolojileri deneyiminiz ne kadar?",
            "options": [
                ("Yok veya çok az (0-6 ay)", 5),
                ("Temel seviye (6 ay - 2 yıl)", 15),
                ("Orta seviye (2-5 yıl)", 30),
                ("İleri seviye (5-10 yıl)", 45),
                ("Uzman seviye (10+ yıl)", 60)
            ]
        },
        {
            "id": "edu_2",
            "question": "Pedagojik yaklaşımlar hakkında bilginiz?",
            "options": [
                ("Bilmiyorum", 5),
                ("Temel kavramları duydum", 15),
                ("Bazı yöntemleri uygulayabilirim", 30),
                ("Farklı yaklaşımları karşılaştırabilirim", 45),
                ("Duruma özel strateji geliştirebilirim", 60)
            ]
        },
        {
            "id": "edu_3",
            "question": "Öğrenme hedefleri ve değerlendirme tasarlama?",
            "options": [
                ("Hiç yapmadım", 5),
                ("Hazır şablonları kullanabilirim", 15),
                ("Basit hedefler yazabilirim", 30),
                ("SMART hedefler ve rubric tasarlarım", 45),
                ("Bloom taksonomisi ile sentezlerim", 60)
            ]
        },
        {
            "id": "edu_4",
            "question": "Dijital araçlar ve platformlar kullanımı?",
            "options": [
                ("Sadece temel ofis programları", 5),
                ("LMS ve video konferans", 15),
                ("Etkileşimli içerik araçları", 30),
                ("Çeşitli edtech araçları entegre ederim", 45),
                ("Yeni teknolojileri değerlendirir ve seçerim", 60)
            ]
        },
        {
            "id": "edu_5",
            "question": "Eğitim programı tasarlama ve geliştirme?",
            "options": [
                ("Hiç yapmadım", 5),
                ("Hazır programları takip ederim", 15),
                ("Modüller tasarlayabilirim", 30),
                ("Tam program geliştirebilirim", 45),
                ("Kurumsal müfredat ve strateji oluştururum", 60)
            ]
        }
    ]
    
    def __init__(self):
        """Assessment sistemini başlat"""
        self.rec_engine = RecommendationEngine() if RECOMMENDATION_ENGINE_AVAILABLE else None
    
    def _recommend_with_math_engine(self, competency_profile: Dict) -> List[Dict]:
        """
        Matematiksel recommendation engine ile tavsiye üret
        
        Args:
            competency_profile: Kullanıcı profil dictionary
            
        Returns:
            Matematiksel olarak optimize edilmiş tavsiyeler
        """
        if not self.rec_engine:
            return []
        
        # User vector oluştur
        user_vector = self.rec_engine.create_user_vector(competency_profile)
        
        # Task complexity tahmin et (orta seviye varsayalım)
        task_complexity = 0.5
        
        # Persona'ları rank'le
        rankings = self.rec_engine.rank_personas(
            user_vector, 
            task_complexity=task_complexity,
            top_k=5
        )
        
        # Formata dönüştür
        recommendations = []
        for idx, ranking in enumerate(rankings, 1):
            persona_id = ranking["persona_id"]
            score = ranking["score"]
            components = ranking["components"]
            ci = ranking["confidence_interval"]
            
            # Açıklama üret
            explanation = self.rec_engine.explain_recommendation(user_vector, persona_id)
            
            # Matematiksel detaylar ekle
            math_details = f"""
**Matematiksel Skor Detayları:**
- Toplam Skor: {score:.3f}
- Benzerlik (S): {components['similarity']:.3f}
- Yetkinlik Uyumu (C): {components['competency_match']:.3f}
- Performans Tahmini (P): {components['performance_prediction']:.3f}
- Öğrenme Yörüngesi (L): {components['learning_trajectory']:.3f}
- 95% CI: [{ci['lower']:.3f}, {ci['upper']:.3f}]

Formül: R = {self.rec_engine.alpha}·S + {self.rec_engine.beta}·C + {self.rec_engine.gamma}·P + {self.rec_engine.delta}·L
"""
            
            recommendations.append({
                "persona_id": persona_id,
                "reason": explanation,
                "priority": idx,
                "mathematical_score": score,
                "components": components,
                "confidence_interval": ci,
                "math_details": math_details
            })
        
        return recommendations
    
    def calculate_score(self, responses: Dict[str, int], domain: str) -> float:
        """
        Toplam skoru hesapla
        
        Args:
            responses: Soru ID ve seçilen puan dictionary'si
            domain: "technical" veya "educational"
            
        Returns:
            0-100 arası skor
        """
        if not responses:
            return 0
        
        # Bonus faktörler (isteğe bağlı sorular için)
        bonus = 0
        
        # AI/LLM deneyimi varsa bonus
        if responses.get("ai_experience"):
            bonus += 10
        
        # Prompt engineering deneyimi varsa bonus
        if responses.get("prompt_experience"):
            bonus += 10
        
        # Temel sorulardan ortalama
        base_scores = [v for k, v in responses.items() if k.startswith(domain[:3])]
        if not base_scores:
            return 0
        
        avg_score = sum(base_scores) / len(base_scores)
        
        # Bonus ekle ama 100'ü geçme
        total = min(avg_score + bonus, 100)
        
        return round(total, 2)
    
    def determine_level(self, score: float) -> str:
        """
        Skordan yetkinlik seviyesini belirle
        
        Args:
            score: 0-100 arası skor
            
        Returns:
            Seviye anahtarı
        """
        for level, ranges in self.LEVELS.items():
            if ranges["min"] <= score <= ranges["max"]:
                return level
        return "novice"
    
    def recommend_personas(self, level: str, domain: str, goal: str = "learning", 
                          use_mathematical_engine: bool = True,
                          competency_profile: Dict = None) -> List[Dict]:
        """
        Yetkinlik seviyesine göre persona öner
        
        İki mod:
        1. Matematiksel Engine (Araştırma için önerilen)
        2. Rule-based Basit (Fallback)
        
        Args:
            level: Yetkinlik seviyesi
            domain: Domain türü
            goal: "learning" (öğrenme) veya "production" (üretim)
            use_mathematical_engine: Matematiksel model kullan mı?
            competency_profile: Tam profil (engine için)
            
        Returns:
            Önerilen persona'lar ve açıklamaları
        """
        # Matematiksel engine kullan (eğer mevcut ve istenmişse)
        if use_mathematical_engine and RECOMMENDATION_ENGINE_AVAILABLE and competency_profile:
            return self._recommend_with_math_engine(competency_profile)
        
        # Basit rule-based tavsiye (fallback)
        recommendations = []
        
        # Domain seçimi
        category = "education" if domain == "educational" else "technology"
        
        # Seviye bazlı tavsiyeler
        if level == "novice":
            # Acemiler için öğretici persona'lar
            recommendations = [
                {
                    "persona_id": "edu_1",
                    "reason": "Çok açıklayıcı ve bol yorumlu kod yazar - öğrenmeniz için ideal",
                    "priority": 1
                },
                {
                    "persona_id": "edu_2", 
                    "reason": "Adım adım yaklaşımı sayesinde kodu takip etmek kolay",
                    "priority": 2
                },
                {
                    "persona_id": "edu_4",
                    "reason": "Modüler yapısı ile kodun parçalarını ayrı ayrı anlayabilirsiniz",
                    "priority": 3
                }
            ]
        
        elif level == "advanced_beginner":
            # İleri başlangıç için dengeli
            recommendations = [
                {
                    "persona_id": "edu_2",
                    "reason": "Yapılandırılmış yaklaşımı seviyenize uygun",
                    "priority": 1
                },
                {
                    "persona_id": "edu_4",
                    "reason": "Takım çalışması prensipleri öğrenmenize yardımcı olur",
                    "priority": 2
                },
                {
                    "persona_id": "tech_1",
                    "reason": "Clean code prensiplerini öğrenmeye başlayabilirsiniz",
                    "priority": 3
                }
            ]
        
        elif level == "competent":
            # Yetkin seviye için profesyonel
            if goal == "learning":
                recommendations = [
                    {
                        "persona_id": "tech_1",
                        "reason": "Clean code ve SOLID prensiplerini mükemmel uygular",
                        "priority": 1
                    },
                    {
                        "persona_id": "edu_3",
                        "reason": "Problem çözme yaklaşımları görmeniz için iyi",
                        "priority": 2
                    },
                    {
                        "persona_id": "tech_4",
                        "reason": "Mimari düşünme becerisi kazanırsınız",
                        "priority": 3
                    }
                ]
            else:
                recommendations = [
                    {
                        "persona_id": "tech_1",
                        "reason": "Production-ready, maintainable kod",
                        "priority": 1
                    },
                    {
                        "persona_id": "tech_2",
                        "reason": "Performans odaklı çözümler",
                        "priority": 2
                    }
                ]
        
        elif level == "proficient":
            # Usta seviye için optimizasyon odaklı
            recommendations = [
                {
                    "persona_id": "tech_2",
                    "reason": "Performans optimizasyonu uzmanlığınızla uyumlu",
                    "priority": 1
                },
                {
                    "persona_id": "tech_3",
                    "reason": "Güvenlik konusunda derinleşmeniz için",
                    "priority": 2
                },
                {
                    "persona_id": "tech_5",
                    "reason": "Algoritma optimizasyonu seviyenize uygun",
                    "priority": 3
                }
            ]
        
        else:  # expert
            # Uzman seviye için tüm spektrum
            recommendations = [
                {
                    "persona_id": "tech_5",
                    "reason": "Algoritma uzmanlığınızla eşleşir",
                    "priority": 1
                },
                {
                    "persona_id": "tech_4",
                    "reason": "Mimari tasarım seviyenize uygun",
                    "priority": 2
                },
                {
                    "persona_id": "tech_3",
                    "reason": "Güvenlik best practices",
                    "priority": 3
                },
                {
                    "persona_id": "edu_3",
                    "reason": "Farklı perspektifler için - alternatif yaklaşımlar",
                    "priority": 4
                }
            ]
        
        return recommendations
    
    def generate_improvement_tips(self, level: str, domain: str) -> List[str]:
        """
        Seviye için iyileştirme önerileri
        
        Args:
            level: Yetkinlik seviyesi
            domain: Domain türü
            
        Returns:
            İyileştirme ipuçları listesi
        """
        tips = {
            "novice": [
                "🎯 Basit görevlerle başlayın (örn: 'İki sayının toplamı')",
                "📚 Üretilen kodları satır satır okuyun ve anlamaya çalışın",
                "💡 Yorumları dikkatlice inceleyin - öğretici bilgiler içerir",
                "🔄 Aynı görevi farklı persona'larla deneyin ve karşılaştırın",
                "📖 Dr. Ayşe Öğretmen'in kodlarından başlayın - en öğretici"
            ],
            "advanced_beginner": [
                "🎯 Orta karmaşıklıkta görevler seçin",
                "🔍 Kod organizasyonuna dikkat edin (fonksiyon yapıları)",
                "💭 Prof. Mehmet'in adım adım yaklaşımını inceleyin",
                "🛠️ Doç. Ali'nin modüler tasarımlarını öğrenin",
                "📊 Farklı persona'ların yaklaşımlarını karşılaştırın"
            ],
            "competent": [
                "🎯 Kompleks problemlere geçin",
                "⚡ Ahmet Senior Developer'dan clean code öğrenin",
                "🏗️ Deniz Architect'in mimari yaklaşımlarını inceleyin",
                "🔒 Elif Security Expert'ten güvenlik prensiplerine bakın",
                "📈 Performans metriklerini karşılaştırın"
            ],
            "proficient": [
                "🎯 Production-ready kod için tech persona'ları kullanın",
                "⚙️ Can DevOps'tan performans optimizasyonu öğrenin",
                "🤖 Burak AI Specialist'in algoritma yaklaşımlarını inceleyin",
                "🔐 Güvenlik zafiyet analizlerini detaylı inceleyin",
                "🏛️ Enterprise pattern'leri keşfedin"
            ],
            "expert": [
                "🎯 Tüm persona'ları deneyin - farklı perspektifler kazanın",
                "🔬 Persona'ların yaklaşımlarını kritik edin",
                "📊 Metrik farklılıklarının nedenlerini analiz edin",
                "🎓 Kendi prompt pattern'lerinizi geliştirin",
                "🤝 Farklı persona kombinasyonlarını test edin"
            ]
        }
        
        return tips.get(level, tips["novice"])
    
    def create_profile(self, user_id: str, responses: Dict[str, int], 
                      goal: str = "learning") -> CompetencyProfile:
        """
        Kullanıcı profili oluştur - DUAL DOMAIN
        
        Args:
            user_id: Kullanıcı ID
            responses: Anket yanıtları (tech_ ve edu_ soruları)
            goal: Amaç
            
        Returns:
            CompetencyProfile objesi (dual domain)
        """
        # Technical ve Educational skorları ayrı hesapla
        tech_score = self.calculate_score(responses, "technical")
        edu_score = self.calculate_score(responses, "educational")
        
        # Seviyeleri belirle
        tech_level = self.determine_level(tech_score)
        edu_level = self.determine_level(edu_score)
        
        # Genel skor (ortalama)
        overall_score = (tech_score + edu_score) / 2
        
        # Dominant ve weak domain (AKILLI LOGIC)
        # Mutlak skorlara da bak, sadece relative değil
        
        if tech_score >= 40 and edu_score >= 40:
            # İkisi de güçlü - hangisi daha güçlü?
            if tech_score > edu_score:
                dominant = "technical"
                weak = "educational"
                strength_level = "both_strong"
            else:
                dominant = "educational"
                weak = "technical"
                strength_level = "both_strong"
        elif tech_score < 40 and edu_score < 40:
            # İkisi de zayıf - hangisi daha az zayıf?
            if tech_score > edu_score:
                dominant = "technical"  # Daha az zayıf
                weak = "educational"  # Daha zayıf
                strength_level = "both_weak"
            else:
                dominant = "educational"  # Daha az zayıf
                weak = "technical"  # Daha zayıf
                strength_level = "both_weak"
        else:
            # Biri güçlü biri zayıf
            if tech_score >= 40:
                dominant = "technical"
                weak = "educational"
                strength_level = "mixed"
            else:
                dominant = "educational"
                weak = "technical"
                strength_level = "mixed"
        
        # Similarity ve Complementary tavsiyeleri
        # (Şimdilik basit, matematiksel engine kullanacak)
        sim_personas = []
        comp_personas = []
        
        profile = CompetencyProfile(
            user_id=user_id,
            technical_score=tech_score,
            educational_score=edu_score,
            technical_level=tech_level,
            educational_level=edu_level,
            overall_score=overall_score,
            dominant_domain=dominant,
            weak_domain=weak,
            assessment_date=datetime.now().isoformat(),
            responses=responses,
            recommended_personas_similarity=sim_personas,
            recommended_personas_complementary=comp_personas
        )
        
        return profile
    
    def save_profile(self, profile: CompetencyProfile, filepath: str = "data/user_profiles.json"):
        """
        Profili dosyaya kaydet
        
        Args:
            profile: CompetencyProfile objesi
            filepath: Kayıt dosyası yolu
        """
        import os
        
        # data klasörünü oluştur
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Mevcut profilleri oku
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            profiles = []
        
        # Yeni profili ekle
        profile_dict = {
            "user_id": profile.user_id,
            "domain": profile.domain,
            "level": profile.level,
            "score": profile.score,
            "assessment_date": profile.assessment_date,
            "responses": profile.responses,
            "recommended_personas": profile.recommended_personas
        }
        
        profiles.append(profile_dict)
        
        # Kaydet
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)


# Test için
if __name__ == "__main__":
    assessment = CompetencyAssessment()
    
    # Test responses
    test_responses = {
        "tech_1": 30,
        "tech_2": 30,
        "tech_3": 30,
        "tech_4": 30,
        "tech_5": 30
    }
    
    profile = assessment.create_profile(
        user_id="test_user",
        domain="technical",
        responses=test_responses
    )
    
    print(f"Seviye: {profile.level}")
    print(f"Skor: {profile.score}")
    print(f"Öneriler: {profile.recommended_personas}")

