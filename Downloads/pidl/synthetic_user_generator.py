"""
Synthetic User Profile Generator
Monte Carlo sampling ile 150 gerçekçi kullanıcı profili oluşturur

Araştırma için: 5 seviye × 2 domain × 15 kişi = 150 user
"""

import numpy as np
import json
from datetime import datetime
from typing import List, Dict
import uuid


class SyntheticUserGenerator:
    """Sentetik kullanıcı profili üreteci"""
    
    # Dreyfus seviyeleri
    LEVELS = ['novice', 'advanced_beginner', 'competent', 'proficient', 'expert']
    DOMAINS = ['technical', 'educational']
    
    def __init__(self, seed=42):
        """
        Generator başlat
        
        Args:
            seed: Random seed (reproducibility için)
        """
        np.random.seed(seed)
        self.users = []
    
    def generate_users(self, n_per_stratum=15) -> List[Dict]:
        """
        Stratified sampling ile N users oluştur
        
        Args:
            n_per_stratum: Her strata'da kaç kişi
            
        Returns:
            List of user dicts
        """
        user_id = 0
        
        for level in self.LEVELS:
            for domain in self.DOMAINS:
                
                # Bu strata için n_per_stratum kişi
                for i in range(n_per_stratum):
                    
                    user = self._generate_single_user(
                        user_id=user_id,
                        level=level,
                        domain=domain
                    )
                    
                    self.users.append(user)
                    user_id += 1
        
        return self.users
    
    def _generate_single_user(self, user_id: int, level: str, domain: str) -> Dict:
        """
        Tek bir user profili oluştur
        
        Args:
            user_id: User ID
            level: Yetkinlik seviyesi
            domain: Dominant domain
            
        Returns:
            User profile dict
        """
        # Seviyeye göre score mean ve SD
        level_params = {
            'novice': (10, 5),
            'advanced_beginner': (30, 8),
            'competent': (50, 7),
            'proficient': (70, 8),
            'expert': (90, 5)
        }
        
        score_mean, score_sd = level_params[level]
        
        # Dominant domain için yüksek skor
        if domain == 'technical':
            # Technical yüksek
            technical_score = np.random.normal(score_mean, score_sd)
            # Educational düşük (zayıf taraf)
            educational_score = np.random.beta(2, 3) * 50  # Beta dist, sola çarpık
            
        else:  # educational
            # Educational yüksek
            educational_score = np.random.normal(score_mean, score_sd)
            # Technical düşük
            technical_score = np.random.beta(2, 3) * 50
        
        # Weak negative correlation enforce (r≈-0.20)
        # Bazen her ikisi de yüksek olabilir (multi-skilled, %8)
        if np.random.rand() < 0.08:  # %8 şans
            # Multi-skilled user
            if domain == 'technical':
                educational_score += 30
            else:
                technical_score += 30
        
        # Clip to [0, 100]
        technical_score = np.clip(technical_score, 0, 100)
        educational_score = np.clip(educational_score, 0, 100)
        
        # Demografik bilgiler (realistic)
        age = self._generate_age(level)
        experience_years = self._generate_experience(level)
        education_level = self._generate_education(level)
        sector = domain  # Basitleştirilmiş
        
        # Learning goal (seviyeye göre)
        if level in ['novice', 'advanced_beginner']:
            learning_goal = np.random.beta(8, 2)  # Yüksek (0.7-0.9)
        elif level == 'competent':
            learning_goal = np.random.beta(4, 4)  # Orta (0.4-0.6)
        else:
            learning_goal = np.random.beta(2, 8)  # Düşük (0.1-0.3)
        
        # User dict
        user = {
            'id': f'synthetic_user_{user_id:03d}',
            'uuid': str(uuid.uuid4()),
            'level': level,
            'dominant_domain': domain,
            'technical_score': round(technical_score, 1),
            'educational_score': round(educational_score, 1),
            'overall_score': round((technical_score + educational_score) / 2, 1),
            'learning_goal': round(learning_goal, 3),
            'age': age,
            'experience_years': experience_years,
            'education_level': education_level,
            'sector': sector,
            'ai_experience': np.random.rand() > 0.5,
            'prompt_experience': np.random.rand() > 0.7,
            'generated_at': datetime.now().isoformat()
        }
        
        return user
    
    def _generate_age(self, level: str) -> int:
        """Seviyeye göre realistic yaş"""
        age_params = {
            'novice': (23, 3),  # M=23, SD=3
            'advanced_beginner': (26, 4),
            'competent': (32, 5),
            'proficient': (38, 6),
            'expert': (45, 8)
        }
        mean, sd = age_params[level]
        age = int(np.random.normal(mean, sd))
        return np.clip(age, 18, 65)
    
    def _generate_experience(self, level: str) -> float:
        """Seviyeye göre deneyim yılı"""
        exp_params = {
            'novice': (0.5, 0.3),
            'advanced_beginner': (1.5, 0.8),
            'competent': (4.0, 1.5),
            'proficient': (8.0, 2.5),
            'expert': (15.0, 5.0)
        }
        mean, sd = exp_params[level]
        exp = np.random.normal(mean, sd)
        return round(max(0, exp), 1)
    
    def _generate_education(self, level: str) -> str:
        """Seviyeye göre eğitim durumu"""
        # Novice: Çoğu lisans
        # Expert: Çoğu doktora
        rand = np.random.rand()
        
        if level in ['novice', 'advanced_beginner']:
            if rand < 0.7:
                return 'Lisans'
            elif rand < 0.95:
                return 'Yüksek Lisans'
            else:
                return 'Doktora'
        
        elif level == 'competent':
            if rand < 0.4:
                return 'Lisans'
            elif rand < 0.8:
                return 'Yüksek Lisans'
            else:
                return 'Doktora'
        
        else:  # proficient, expert
            if rand < 0.2:
                return 'Lisans'
            elif rand < 0.6:
                return 'Yüksek Lisans'
            else:
                return 'Doktora'
    
    def export_to_json(self, filepath='data/synthetic_users.json'):
        """JSON'a export et"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(self.users)} synthetic user kaydedildi: {filepath}")
    
    def get_statistics(self) -> Dict:
        """İstatistiksel özet"""
        if not self.users:
            return {}
        
        tech_scores = [u['technical_score'] for u in self.users]
        edu_scores = [u['educational_score'] for u in self.users]
        
        stats = {
            'total_users': len(self.users),
            'technical': {
                'mean': np.mean(tech_scores),
                'std': np.std(tech_scores),
                'min': np.min(tech_scores),
                'max': np.max(tech_scores)
            },
            'educational': {
                'mean': np.mean(edu_scores),
                'std': np.std(edu_scores),
                'min': np.min(edu_scores),
                'max': np.max(edu_scores)
            },
            'correlation': np.corrcoef(tech_scores, edu_scores)[0, 1],
            'level_distribution': {
                level: sum(1 for u in self.users if u['level'] == level)
                for level in self.LEVELS
            },
            'domain_distribution': {
                domain: sum(1 for u in self.users if u['dominant_domain'] == domain)
                for domain in self.DOMAINS
            }
        }
        
        return stats


# Test için
if __name__ == "__main__":
    print("🧪 Synthetic User Generator Test\n")
    
    generator = SyntheticUserGenerator(seed=42)
    users = generator.generate_users(n_per_stratum=15)
    
    print(f"✅ {len(users)} user oluşturuldu\n")
    
    # İstatistikler
    stats = generator.get_statistics()
    
    print("📊 İstatistikler:")
    print(f"  Technical: M={stats['technical']['mean']:.1f}, SD={stats['technical']['std']:.1f}")
    print(f"  Educational: M={stats['educational']['mean']:.1f}, SD={stats['educational']['std']:.1f}")
    print(f"  Correlation: r={stats['correlation']:.3f}")
    print(f"\n  Seviye dağılımı: {stats['level_distribution']}")
    print(f"  Domain dağılımı: {stats['domain_distribution']}")
    
    # Export
    generator.export_to_json()
    
    # Örnek 5 user göster
    print("\n📋 Örnek 5 User:")
    for u in users[:5]:
        print(f"  {u['id']}: {u['level']}, {u['dominant_domain']}, "
              f"Tech={u['technical_score']:.1f}, Edu={u['educational_score']:.1f}")





