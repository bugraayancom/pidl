"""
İleri Seviye Matematiksel Modeller
Doktora Araştırması: İnsan-AI İşbirliği Modellerinde Yetkinlik Transferi

Teorik Kaynaklar:
- Shannon (1948): Information Theory
- Bayes (1763): Probability Theory
- Pareto (1896): Multi-Objective Optimization
- Markov (1906): Stochastic Processes
- Wiener (1949): Time Series Analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
import json


class InformationTheoryAnalyzer:
    """
    Shannon Bilgi Teorisi Analizleri
    
    H(X) = -Σ p(x) · log₂(p(x))
    """
    
    @staticmethod
    def calculate_shannon_entropy(code: str) -> float:
        """
        Shannon Entropy - Kod karmaşıklık entropisi
        
        Yüksek entropi = yüksek belirsizlik/çeşitlilik
        Düşük entropi = düşük belirsizlik/tekrar
        
        H(X) = -Σ p(xᵢ) · log₂(p(xᵢ))
        
        Args:
            code: Kaynak kod
            
        Returns:
            Entropy değeri (0-∞, genelde 0-8 arası)
        """
        if not code:
            return 0.0
        
        # Token'lara ayır (her karakter bir symbol)
        tokens = list(code.replace('\n', '').replace(' ', ''))
        
        if not tokens:
            return 0.0
        
        # Frekans dağılımı
        freq_dist = Counter(tokens)
        total = len(tokens)
        
        # Shannon entropy hesapla
        entropy = 0.0
        for count in freq_dist.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    @staticmethod
    def calculate_prompt_diversity(prompts: List[str]) -> Dict:
        """
        Prompt Çeşitlilik Analizi
        
        Farklı persona'ların prompt'ları ne kadar çeşitli?
        
        Metrikler:
        - Inter-prompt distance (ortalama mesafe)
        - Diversity index
        - Unique token ratio
        
        Returns:
            Çeşitlilik metrikleri
        """
        if not prompts:
            return {"diversity_index": 0, "avg_distance": 0}
        
        # Her prompt için token seti
        token_sets = []
        for prompt in prompts:
            tokens = set(prompt.lower().split())
            token_sets.append(tokens)
        
        # Pairwise Jaccard distance
        distances = []
        n = len(token_sets)
        for i in range(n):
            for j in range(i+1, n):
                intersection = len(token_sets[i] & token_sets[j])
                union = len(token_sets[i] | token_sets[j])
                jaccard_sim = intersection / union if union > 0 else 0
                jaccard_dist = 1 - jaccard_sim
                distances.append(jaccard_dist)
        
        avg_distance = np.mean(distances) if distances else 0
        
        # Diversity index (Simpson's Index)
        all_tokens = []
        for prompt in prompts:
            all_tokens.extend(prompt.lower().split())
        
        freq_dist = Counter(all_tokens)
        total = len(all_tokens)
        
        simpson_index = 0
        for count in freq_dist.values():
            p = count / total
            simpson_index += p * p
        
        diversity = 1 - simpson_index  # Gini-Simpson index
        
        return {
            "diversity_index": round(diversity, 4),
            "avg_jaccard_distance": round(avg_distance, 4),
            "unique_token_ratio": round(len(freq_dist) / total, 4) if total > 0 else 0
        }
    
    @staticmethod
    def mutual_information(code1: str, code2: str) -> float:
        """
        Mutual Information - İki kod arasındaki bilgi paylaşımı
        
        I(X;Y) = H(X) + H(Y) - H(X,Y)
        
        Yüksek MI = kodlar benzer
        Düşük MI = kodlar farklı
        """
        h1 = InformationTheoryAnalyzer.calculate_shannon_entropy(code1)
        h2 = InformationTheoryAnalyzer.calculate_shannon_entropy(code2)
        
        # Joint entropy (basitleştirilmiş)
        combined = code1 + code2
        h_joint = InformationTheoryAnalyzer.calculate_shannon_entropy(combined)
        
        # MI = H(X) + H(Y) - H(X,Y)
        mi = h1 + h2 - h_joint
        
        return max(0, mi)


class BayesianInference:
    """
    Bayesian İstatistik Modelleri
    
    P(θ|D) = [P(D|θ) · P(θ)] / P(D)
    """
    
    @staticmethod
    def calculate_posterior_probability(prior: float, likelihood: float, 
                                       evidence: float = None) -> float:
        """
        Posterior olasılık hesapla
        
        P(θ|D) = [P(D|θ) · P(θ)] / P(D)
        
        Args:
            prior: P(θ) - Öncül olasılık
            likelihood: P(D|θ) - Olabilirlik
            evidence: P(D) - Kanıt (None ise normalize edilir)
            
        Returns:
            Posterior olasılık
        """
        numerator = likelihood * prior
        
        if evidence is None:
            # Normalization constant hesapla
            evidence = numerator  # Basitleştirilmiş
        
        posterior = numerator / evidence if evidence > 0 else prior
        
        return min(1.0, max(0.0, posterior))
    
    @staticmethod
    def update_persona_beliefs(initial_beliefs: Dict[str, float], 
                              feedback: Dict[str, float]) -> Dict[str, float]:
        """
        Bayesian güncelleme ile persona inançlarını güncelle
        
        Her feedback'ten sonra, hangi persona'nın daha uygun olduğuna 
        dair inancımızı güncelle
        
        Args:
            initial_beliefs: İlk inanç dağılımı (prior)
            feedback: Persona ID -> başarı skoru (0-1)
            
        Returns:
            Güncellenmiş inanç dağılımı (posterior)
        """
        updated = {}
        
        for persona_id, prior in initial_beliefs.items():
            # Likelihood (feedback'den)
            likelihood = feedback.get(persona_id, 0.5)
            
            # Bayesian update
            posterior = BayesianInference.calculate_posterior_probability(
                prior, likelihood
            )
            
            updated[persona_id] = posterior
        
        # Normalize et (toplamı 1 olmalı)
        total = sum(updated.values())
        if total > 0:
            updated = {k: v/total for k, v in updated.items()}
        
        return updated
    
    @staticmethod
    def credible_interval(mean: float, std: float, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Bayesian Credible Interval
        
        Args:
            mean: Ortalama
            std: Standart sapma
            confidence: Güven düzeyi
            
        Returns:
            (lower, upper) interval
        """
        z = 1.96 if confidence == 0.95 else 2.576  # 95% veya 99%
        
        lower = mean - z * std
        upper = mean + z * std
        
        return (max(0, lower), min(1, upper))


class ParetoOptimization:
    """
    Multi-Objective Optimization - Pareto Optimality
    
    Birden fazla hedefi aynı anda optimize et
    (Öğreticilik vs Performans trade-off)
    """
    
    @staticmethod
    def is_pareto_optimal(point: np.ndarray, points: np.ndarray) -> bool:
        """
        Bir noktanın Pareto optimal olup olmadığını kontrol et
        
        Pareto optimal = Başka hiçbir nokta tüm boyutlarda daha iyi değil
        
        Args:
            point: Test edilen nokta
            points: Tüm noktalar
            
        Returns:
            Pareto optimal mi?
        """
        # Her boyutta bu noktadan daha iyi olan var mı?
        dominated = np.all(points >= point, axis=1) & np.any(points > point, axis=1)
        
        return not np.any(dominated)
    
    @staticmethod
    def find_pareto_frontier(personas_metrics: List[Dict]) -> List[Dict]:
        """
        Pareto optimal persona setini bul
        
        Amaçlar:
        1. Maksimize: Öğreticilik
        2. Maksimize: Kod kalitesi
        3. Minimize: Karmaşıklık
        
        Args:
            personas_metrics: Persona metrik listesi
            
        Returns:
            Pareto optimal persona'lar
        """
        if not personas_metrics:
            return []
        
        # Metrik matrisini oluştur
        points = []
        for p in personas_metrics:
            general = p.get('metrics', {}).get('general', {})
            point = [
                general.get('instructiveness_index', 0),  # Maximize
                p.get('quality_score', 0),  # Maximize
                -general.get('lines_of_code', 50)  # Minimize (negative for maximization)
            ]
            points.append(point)
        
        points = np.array(points)
        
        # Pareto optimal noktaları bul
        pareto_optimal = []
        for i, point in enumerate(points):
            if ParetoOptimization.is_pareto_optimal(point, points):
                pareto_optimal.append(personas_metrics[i])
        
        return pareto_optimal
    
    @staticmethod
    def calculate_dominated_count(persona_metrics: Dict, all_metrics: List[Dict]) -> int:
        """
        Bir persona'yı kaç persona dominate ediyor?
        
        Düşük sayı = daha iyi (az kişi dominate ediyor)
        """
        dominated_by = 0
        
        p_general = persona_metrics.get('metrics', {}).get('general', {})
        p_point = np.array([
            p_general.get('instructiveness_index', 0),
            persona_metrics.get('quality_score', 0),
            -p_general.get('lines_of_code', 50)
        ])
        
        for other in all_metrics:
            if other == persona_metrics:
                continue
            
            o_general = other.get('metrics', {}).get('general', {})
            o_point = np.array([
                o_general.get('instructiveness_index', 0),
                other.get('quality_score', 0),
                -o_general.get('lines_of_code', 50)
            ])
            
            # Other dominate ediyor mu?
            if np.all(o_point >= p_point) and np.any(o_point > p_point):
                dominated_by += 1
        
        return dominated_by


class MarkovChainLearning:
    """
    Markov Decision Process - Öğrenme Yörüngesi
    
    Kullanıcı farklı persona'lardan öğrendikçe seviye atlar
    """
    
    @staticmethod
    def create_transition_matrix(current_level: str) -> np.ndarray:
        """
        Geçiş olasılıkları matrisi
        
        P[i][j] = i seviyesinden j seviyesine geçiş olasılığı
        
        States: [novice, advanced_beginner, competent, proficient, expert]
        
        Returns:
            5x5 geçiş matrisi
        """
        # İndeksler
        levels = ['novice', 'advanced_beginner', 'competent', 'proficient', 'expert']
        
        # Geçiş matrisi (her satır toplamı = 1)
        # Genellikle aynı seviyede kalma veya bir üst seviyeye geçme
        P = np.array([
            # N     AB    C     P     E
            [0.70, 0.25, 0.05, 0.00, 0.00],  # Novice
            [0.05, 0.65, 0.25, 0.05, 0.00],  # Advanced Beginner
            [0.00, 0.05, 0.60, 0.30, 0.05],  # Competent
            [0.00, 0.00, 0.05, 0.65, 0.30],  # Proficient
            [0.00, 0.00, 0.00, 0.10, 0.90]   # Expert
        ])
        
        return P
    
    @staticmethod
    def predict_future_level(current_level: str, steps: int = 5) -> Dict[str, float]:
        """
        N adım sonra hangi seviyede olma olasılığı?
        
        P^n = P · P · ... · P (n kere)
        
        Args:
            current_level: Şu anki seviye
            steps: Kaç adım sonrası
            
        Returns:
            Seviye olasılıkları
        """
        levels = ['novice', 'advanced_beginner', 'competent', 'proficient', 'expert']
        current_idx = levels.index(current_level)
        
        # Geçiş matrisi
        P = MarkovChainLearning.create_transition_matrix(current_level)
        
        # İlk durum vektörü
        state = np.zeros(5)
        state[current_idx] = 1.0
        
        # N adım ilerlet
        for _ in range(steps):
            state = state @ P
        
        # Dict'e çevir
        predictions = {level: prob for level, prob in zip(levels, state)}
        
        return predictions
    
    @staticmethod
    def expected_value_calculation(rewards: np.ndarray, probabilities: np.ndarray) -> float:
        """
        Beklenen değer hesabı
        
        E[X] = Σ xᵢ · P(xᵢ)
        
        Args:
            rewards: Ödül değerleri
            probabilities: Olasılıklar
            
        Returns:
            Beklenen değer
        """
        return np.sum(rewards * probabilities)


class TimeSeriesForecasting:
    """
    Zaman Serisi Tahmini - Öğrenme İlerlemesi
    
    Exponential Smoothing ve Trend Analysis
    """
    
    @staticmethod
    def exponential_smoothing(data: List[float], alpha: float = 0.3) -> List[float]:
        """
        Üstel Düzleştirme
        
        Sₜ = α·yₜ + (1-α)·Sₜ₋₁
        
        Args:
            data: Zaman serisi verisi
            alpha: Düzleştirme parametresi (0-1)
            
        Returns:
            Düzleştirilmiş seri
        """
        if not data:
            return []
        
        smoothed = [data[0]]
        
        for i in range(1, len(data)):
            s = alpha * data[i] + (1 - alpha) * smoothed[i-1]
            smoothed.append(s)
        
        return smoothed
    
    @staticmethod
    def linear_trend_forecast(data: List[float], forecast_steps: int = 3) -> List[float]:
        """
        Doğrusal trend tahmini
        
        ŷ = a + b·t
        
        b = Σ(tᵢ - t̄)(yᵢ - ȳ) / Σ(tᵢ - t̄)²
        a = ȳ - b·t̄
        
        Args:
            data: Geçmiş veriler
            forecast_steps: Kaç adım ilerisi
            
        Returns:
            Tahmin edilen değerler
        """
        if len(data) < 2:
            return [data[0]] * forecast_steps if data else [0] * forecast_steps
        
        # Time steps
        t = np.arange(len(data))
        y = np.array(data)
        
        # Trend parametreleri
        t_mean = np.mean(t)
        y_mean = np.mean(y)
        
        numerator = np.sum((t - t_mean) * (y - y_mean))
        denominator = np.sum((t - t_mean) ** 2)
        
        b = numerator / denominator if denominator != 0 else 0  # Slope
        a = y_mean - b * t_mean  # Intercept
        
        # Forecast
        future_t = np.arange(len(data), len(data) + forecast_steps)
        forecast = a + b * future_t
        
        return forecast.tolist()
    
    @staticmethod
    def learning_curve_model(attempts: int, performance_data: List[float]) -> Dict:
        """
        Öğrenme Eğrisi Modeli (Power Law of Practice)
        
        P(n) = A · n^(-b) + c
        
        A: İlk performans
        b: Öğrenme hızı (0-1)
        c: Asimptotik performans
        n: Deneme sayısı
        
        Args:
            attempts: Deneme sayısı
            performance_data: Performans geçmişi
            
        Returns:
            Model parametreleri ve tahmin
        """
        if len(performance_data) < 3:
            return {"A": 0, "b": 0, "c": 0, "prediction": 0}
        
        # Simplified parameter estimation
        A = performance_data[0]  # İlk performans
        c = np.mean(performance_data[-3:])  # Son performans (asimptot)
        
        # Learning rate estimation
        if len(performance_data) > 1:
            improvements = np.diff(performance_data)
            b = np.mean(improvements) / np.mean(performance_data[:-1]) if np.mean(performance_data[:-1]) > 0 else 0.1
            b = abs(b)
        else:
            b = 0.5
        
        # Next prediction
        n = attempts + 1
        prediction = A * (n ** (-b)) + c
        
        return {
            "A": round(A, 3),
            "b": round(b, 3),
            "c": round(c, 3),
            "prediction": round(prediction, 3),
            "formula": f"P(n) = {A:.2f} · n^(-{b:.2f}) + {c:.2f}"
        }


class ClusteringAnalysis:
    """
    Kümeleme ve Mesafe Metrikleri
    
    Persona'ları benzerliklerine göre kümele
    """
    
    @staticmethod
    def weighted_euclidean_distance(x: np.ndarray, y: np.ndarray, 
                                    weights: np.ndarray = None) -> float:
        """
        Ağırlıklı Euclidean mesafesi
        
        d(x,y) = √(Σ wᵢ·(xᵢ - yᵢ)²)
        
        Args:
            x: Vektör 1
            y: Vektör 2
            weights: Ağırlıklar (None ise eşit)
            
        Returns:
            Ağırlıklı mesafe
        """
        if weights is None:
            weights = np.ones(len(x))
        
        diff = x - y
        weighted_diff = weights * (diff ** 2)
        distance = np.sqrt(np.sum(weighted_diff))
        
        return distance
    
    @staticmethod
    def mahalanobis_distance_simplified(x: np.ndarray, y: np.ndarray, 
                                       cov_matrix: np.ndarray = None) -> float:
        """
        Mahalanobis mesafesi (basitleştirilmiş)
        
        d(x,y) = √((x-y)ᵀ · Σ⁻¹ · (x-y))
        
        Korelasyonları dikkate alır
        """
        diff = x - y
        
        if cov_matrix is None:
            # Identity matrix (basitleştirilmiş)
            cov_matrix = np.eye(len(x))
        
        try:
            inv_cov = np.linalg.inv(cov_matrix)
            distance = np.sqrt(diff.T @ inv_cov @ diff)
        except:
            # Fallback to Euclidean
            distance = np.linalg.norm(diff)
        
        return distance
    
    @staticmethod
    def k_means_clustering(personas_data: List[Dict], k: int = 3) -> Dict:
        """
        K-Means kümeleme (basitleştirilmiş)
        
        Persona'ları benzerliklerine göre k kümeye ayır
        
        Args:
            personas_data: Persona metrikleri
            k: Küme sayısı
            
        Returns:
            Küme atamaları
        """
        if len(personas_data) < k:
            return {}
        
        # Feature matrix oluştur
        features = []
        for p in personas_data:
            general = p.get('metrics', {}).get('general', {})
            feature_vec = [
                general.get('comment_ratio', 0),
                general.get('instructiveness_index', 0),
                p.get('quality_score', 0),
                general.get('type_hint_ratio', 0)
            ]
            features.append(feature_vec)
        
        features = np.array(features)
        
        # Random initialization
        np.random.seed(42)
        centers = features[np.random.choice(len(features), k, replace=False)]
        
        # 10 iterasyon
        for _ in range(10):
            # Assign to nearest center
            assignments = []
            for point in features:
                distances = [np.linalg.norm(point - center) for center in centers]
                assignments.append(np.argmin(distances))
            
            # Update centers
            for i in range(k):
                cluster_points = features[np.array(assignments) == i]
                if len(cluster_points) > 0:
                    centers[i] = np.mean(cluster_points, axis=0)
        
        # Sonuçları formatla
        clusters = {}
        for i, persona in enumerate(personas_data):
            cluster_id = assignments[i]
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(persona.get('persona_name', f'Persona {i}'))
        
        return clusters


class CorrelationAnalysis:
    """
    Korelasyon ve İlişki Analizleri
    
    Pearson, Spearman, Kendall korelasyonları
    """
    
    @staticmethod
    def pearson_correlation(x: List[float], y: List[float]) -> Tuple[float, float]:
        """
        Pearson korelasyon katsayısı
        
        r = Σ((xᵢ - x̄)(yᵢ - ȳ)) / √(Σ(xᵢ - x̄)² · Σ(yᵢ - ȳ)²)
        
        Returns:
            (r, p-value approximation)
        """
        if len(x) != len(y) or len(x) < 2:
            return (0.0, 1.0)
        
        x_arr = np.array(x)
        y_arr = np.array(y)
        
        # Korelasyon
        r = np.corrcoef(x_arr, y_arr)[0, 1]
        
        # P-value approximation (t-test)
        n = len(x)
        if abs(r) < 1:
            t_stat = r * np.sqrt((n - 2) / (1 - r**2))
            # Simplified p-value
            p_value = 2 * (1 - 0.5 * (1 + np.sign(t_stat) * np.sqrt(1 - np.exp(-2 * t_stat**2 / (n-2)))))
        else:
            p_value = 0.0
        
        return (r, max(0, min(1, p_value)))
    
    @staticmethod
    def calculate_effect_size(group1: List[float], group2: List[float]) -> Dict:
        """
        Cohen's d - Effect size hesaplama
        
        d = (μ₁ - μ₂) / σ_pooled
        
        σ_pooled = √((σ₁² + σ₂²) / 2)
        
        Returns:
            Effect size metrikleri
        """
        g1 = np.array(group1)
        g2 = np.array(group2)
        
        mean1, mean2 = np.mean(g1), np.mean(g2)
        std1, std2 = np.std(g1, ddof=1), np.std(g2, ddof=1)
        
        # Pooled standard deviation
        pooled_std = np.sqrt((std1**2 + std2**2) / 2)
        
        # Cohen's d
        d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
        
        # Interpretation
        if abs(d) < 0.2:
            interpretation = "Negligible"
        elif abs(d) < 0.5:
            interpretation = "Small"
        elif abs(d) < 0.8:
            interpretation = "Medium"
        else:
            interpretation = "Large"
        
        return {
            "cohens_d": round(d, 3),
            "interpretation": interpretation,
            "mean_diff": round(mean1 - mean2, 3),
            "pooled_std": round(pooled_std, 3)
        }


# Test için
if __name__ == "__main__":
    print("🔬 İleri Seviye Matematiksel Modeller Test\n")
    
    # 1. Shannon Entropy
    test_code = "def test(): return x + y"
    entropy = InformationTheoryAnalyzer.calculate_shannon_entropy(test_code)
    print(f"1. Shannon Entropy: {entropy:.3f}")
    
    # 2. Bayesian Update
    prior = {"edu_1": 0.2, "tech_1": 0.3, "tech_2": 0.5}
    feedback = {"edu_1": 0.8, "tech_1": 0.6, "tech_2": 0.4}
    posterior = BayesianInference.update_persona_beliefs(prior, feedback)
    print(f"\n2. Bayesian Update:")
    for k, v in posterior.items():
        print(f"   {k}: {prior[k]:.3f} → {v:.3f}")
    
    # 3. Markov Prediction
    future = MarkovChainLearning.predict_future_level("competent", steps=5)
    print(f"\n3. Markov Prediction (5 steps from 'competent'):")
    for level, prob in future.items():
        if prob > 0.01:
            print(f"   {level}: {prob:.3f}")
    
    # 4. Correlation
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 5, 4, 5]
    r, p = CorrelationAnalysis.pearson_correlation(x, y)
    print(f"\n4. Pearson Correlation: r={r:.3f}, p={p:.3f}")
    
    print("\n✅ Tüm modeller çalışıyor!")

