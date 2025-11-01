"""
User-Persona Matching Tester
150 synthetic users × 10 personas = 1,500 matching scenarios test eder
"""

import numpy as np
import pandas as pd
from typing import List, Dict
import json

from synthetic_user_generator import SyntheticUserGenerator
from recommendation_engine import RecommendationEngine
from personas import get_all_personas


class MatchingTester:
    """User-Persona matching test sistemi"""
    
    def __init__(self):
        """Matching tester başlat"""
        self.rec_engine = RecommendationEngine()
        self.personas = get_all_personas()
        self.matching_results = []
    
    def test_all_matchings(self, users: List[Dict]) -> List[Dict]:
        """
        Tüm user-persona matchings'i test et
        
        Args:
            users: Synthetic user list
            
        Returns:
            Matching results
        """
        total = len(users) * len(self.personas) * 2  # 2 modes
        print(f"🔬 Testing: {len(users)} users × {len(self.personas)} personas × 2 modes = {total} matchings")
        
        count = 0
        
        for user in users:
            # User vector oluştur
            user_vec = self.rec_engine.create_user_vector(user)
            
            for persona in self.personas:
                persona_vec = self.rec_engine.persona_vectors[persona.id]
                
                # Her iki mod için de test
                for mode in ['similarity', 'complementary']:
                    
                    count += 1
                    if count % 100 == 0:
                        print(f"  Progress: {count}/{total} ({count/total*100:.1f}%)")
                    
                    # Recommendation score hesapla
                    score_dict = self.rec_engine.calculate_recommendation_score(
                        user_vec,
                        persona_vec,
                        mode=mode
                    )
                    
                    # Kaydet
                    matching = {
                        'user_id': user['id'],
                        'user_level': user['level'],
                        'user_domain': user['dominant_domain'],
                        'user_tech_score': user['technical_score'],
                        'user_edu_score': user['educational_score'],
                        'persona_id': persona.id,
                        'persona_name': persona.name,
                        'persona_category': persona.category,
                        'mode': mode,
                        'recommendation_score': score_dict['total_score'],
                        'similarity': score_dict['components']['similarity'],
                        'complementarity': score_dict['components'].get('complementarity', 0),
                        'competency_match': score_dict['components']['competency_match'],
                        'performance_pred': score_dict['components']['performance_prediction'],
                        'learning_traj': score_dict['components']['learning_trajectory'],
                        'strategy': score_dict.get('strategy', mode)
                    }
                    
                    self.matching_results.append(matching)
        
        print(f"\n✅ {len(self.matching_results)} matching tamamlandı!")
        
        return self.matching_results
    
    def analyze_results(self) -> Dict:
        """Matching sonuçlarını analiz et"""
        df = pd.DataFrame(self.matching_results)
        
        analysis = {
            'total_matchings': len(df),
            
            # Mode comparison
            'similarity_mode': {
                'mean_score': df[df['mode']=='similarity']['recommendation_score'].mean(),
                'std': df[df['mode']=='similarity']['recommendation_score'].std()
            },
            'complementary_mode': {
                'mean_score': df[df['mode']=='complementary']['recommendation_score'].mean(),
                'std': df[df['mode']=='complementary']['recommendation_score'].std()
            },
            
            # Best matches per user
            'best_similarity_matches': self._find_best_matches(df, 'similarity'),
            'best_complementary_matches': self._find_best_matches(df, 'complementary'),
            
            # Persona popularity
            'persona_selection_frequency': df.groupby('persona_id').size().to_dict(),
            
            # Category preference by user domain
            'tech_users_prefer': self._category_preference(df, 'technical'),
            'edu_users_prefer': self._category_preference(df, 'educational')
        }
        
        return analysis
    
    def _find_best_matches(self, df: pd.DataFrame, mode: str, top_k: int = 3) -> Dict:
        """Her user için en iyi top-k persona'ları bul"""
        mode_df = df[df['mode'] == mode]
        
        best_matches = {}
        for user_id in mode_df['user_id'].unique():
            user_matches = mode_df[mode_df['user_id'] == user_id].nlargest(top_k, 'recommendation_score')
            best_matches[user_id] = user_matches['persona_id'].tolist()
        
        return best_matches
    
    def _category_preference(self, df: pd.DataFrame, user_domain: str) -> Dict:
        """Bir domain'deki kullanıcılar hangi category'yi tercih eder?"""
        user_df = df[df['user_domain'] == user_domain]
        
        # Her mode için
        sim_df = user_df[user_df['mode'] == 'similarity']
        comp_df = user_df[user_df['mode'] == 'complementary']
        
        return {
            'similarity_mode': {
                'education_personas': (sim_df['persona_category']=='education').sum(),
                'technology_personas': (sim_df['persona_category']=='technology').sum()
            },
            'complementary_mode': {
                'education_personas': (comp_df['persona_category']=='education').sum(),
                'technology_personas': (comp_df['persona_category']=='technology').sum()
            }
        }
    
    def export_results(self, filepath='data/matching_results.csv'):
        """CSV olarak export"""
        df = pd.DataFrame(self.matching_results)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')  # UTF-8 with BOM (Excel için)
        print(f"💾 Matching results kaydedildi: {filepath}")
    
    def generate_summary_report(self) -> str:
        """Özet rapor üret"""
        analysis = self.analyze_results()
        
        report = f"""
        📊 MATCHING TEST SUMMARY REPORT
        ================================
        
        Total Matchings: {analysis['total_matchings']}
        
        MODE COMPARISON:
        - Similarity Mode: M={analysis['similarity_mode']['mean_score']:.3f}, SD={analysis['similarity_mode']['std']:.3f}
        - Complementary Mode: M={analysis['complementary_mode']['mean_score']:.3f}, SD={analysis['complementary_mode']['std']:.3f}
        
        PERSONA POPULARITY (Top 5):
        """
        
        # Persona popularity
        pop = analysis['persona_selection_frequency']
        sorted_pop = sorted(pop.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (pid, count) in enumerate(sorted_pop, 1):
            persona_name = next(p.name for p in self.personas if p.id == pid)
            report += f"\n        {i}. {persona_name}: {count} times"
        
        return report


# Test için
if __name__ == "__main__":
    print("🧪 Matching Tester - Quick Test\n")
    
    # 10 synthetic user (küçük test)
    generator = SyntheticUserGenerator(seed=42)
    users = generator.generate_users(n_per_stratum=1)  # Her gruptan 1 = 10 user
    
    print(f"✅ {len(users)} user oluşturuldu")
    
    # Matching test
    tester = MatchingTester()
    results = tester.test_all_matchings(users)
    
    # Analiz
    print("\n" + tester.generate_summary_report())
    
    # Export
    tester.export_results('data/matching_test_small.csv')
    
    print("\n✅ Test tamamlandı!")





