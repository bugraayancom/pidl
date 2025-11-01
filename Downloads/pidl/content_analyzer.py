"""
İçerik Analiz Modülü
Üretilen promptlar ve kodlar için 6 aşamalı matematiksel analiz
"""

import re
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import ast


class ContentAnalyzer:
    """Üretilen prompt ve kodlar için detaylı analiz"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    # =========================================================================
    # AŞAMA 1: PROMPT ANALİZİ - Metin Özellik Çıkarımı
    # =========================================================================

    def analyze_prompt(self, prompt: str) -> Dict:
        """
        AŞAMA 1: Prompt özelliklerini analiz et

        Returns:
            - length: Karakter sayısı
            - word_count: Kelime sayısı
            - sentence_count: Cümle sayısı
            - technical_term_count: Teknik terim sayısı
            - clarity_score: Netlik skoru (0-100)
            - specificity_score: Özgüllük skoru (0-100)
        """
        # Temel metrikler
        length = len(prompt)
        words = prompt.split()
        word_count = len(words)
        sentences = re.split(r'[.!?]+', prompt)
        sentence_count = len([s for s in sentences if s.strip()])

        # Teknik terimler
        technical_terms = [
            'contract', 'function', 'struct', 'mapping', 'address', 'uint',
            'modifier', 'event', 'require', 'assert', 'revert', 'payable',
            'blockchain', 'solidity', 'ethereum', 'gas', 'storage', 'memory'
        ]

        technical_term_count = sum(1 for term in technical_terms
                                   if term.lower() in prompt.lower())

        # Netlik skoru: ortalama cümle uzunluğuna göre (kısa = daha net)
        avg_sentence_length = word_count / max(sentence_count, 1)
        clarity_score = max(0, 100 - (avg_sentence_length - 10) * 2)
        clarity_score = min(100, clarity_score)

        # Özgüllük skoru: teknik terim yoğunluğu
        specificity_score = min(100, (technical_term_count / max(word_count, 1)) * 1000)

        return {
            "length": length,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "technical_term_count": technical_term_count,
            "clarity_score": round(clarity_score, 2),
            "specificity_score": round(specificity_score, 2),
            "avg_word_length": round(length / max(word_count, 1), 2)
        }

    # =========================================================================
    # AŞAMA 2: PROMPT BENZERLİK ANALİZİ - Cosine Similarity
    # =========================================================================

    def calculate_prompt_similarity(self, prompt1: str, prompt2: str) -> Dict:
        """
        AŞAMA 2: İki prompt arasındaki cosine similarity

        Returns:
            - cosine_similarity: TF-IDF bazlı benzerlik (0-1)
            - jaccard_similarity: Kelime kümesi benzerliği (0-1)
            - overlap_ratio: Ortak kelime oranı (0-1)
        """
        # TF-IDF Cosine Similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform([prompt1, prompt2])
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            cosine_sim = 0.0

        # Jaccard Similarity (kelime kümesi)
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        jaccard_sim = intersection / max(union, 1)

        # Overlap Ratio (daha kısa prompt'a göre)
        shorter_length = min(len(words1), len(words2))
        overlap_ratio = intersection / max(shorter_length, 1)

        return {
            "cosine_similarity": round(float(cosine_sim), 4),
            "jaccard_similarity": round(jaccard_sim, 4),
            "overlap_ratio": round(overlap_ratio, 4),
            "interpretation": self._interpret_similarity(cosine_sim)
        }

    def _interpret_similarity(self, similarity: float) -> str:
        """Benzerlik skorunu yorumla"""
        if similarity >= 0.8:
            return "Çok Yüksek - Neredeyse İdentik"
        elif similarity >= 0.6:
            return "Yüksek - Önemli Benzerlik"
        elif similarity >= 0.4:
            return "Orta - Kısmi Benzerlik"
        elif similarity >= 0.2:
            return "Düşük - Az Benzerlik"
        else:
            return "Çok Düşük - Minimal Benzerlik"

    # =========================================================================
    # AŞAMA 3: KOD YAPISI ANALİZİ - Syntactic Analysis
    # =========================================================================

    def analyze_code_structure(self, code: str) -> Dict:
        """
        AŞAMA 3: Kod yapısını analiz et

        Returns:
            - total_lines: Toplam satır sayısı
            - code_lines: Kod satırı sayısı (boş ve yorum hariç)
            - comment_lines: Yorum satırı sayısı
            - blank_lines: Boş satır sayısı
            - comment_ratio: Yorum oranı (%)
            - function_count: Fonksiyon sayısı
            - avg_line_length: Ortalama satır uzunluğu
        """
        lines = code.split('\n')
        total_lines = len(lines)

        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                comment_lines += 1
            else:
                code_lines += 1

        comment_ratio = (comment_lines / max(total_lines, 1)) * 100

        # Fonksiyon sayısı (Solidity)
        function_count = len(re.findall(r'function\s+\w+', code))

        # Ortalama satır uzunluğu
        non_blank_lines = [line for line in lines if line.strip()]
        avg_line_length = sum(len(line) for line in non_blank_lines) / max(len(non_blank_lines), 1)

        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "comment_ratio": round(comment_ratio, 2),
            "function_count": function_count,
            "avg_line_length": round(avg_line_length, 2)
        }

    # =========================================================================
    # AŞAMA 4: KOD KOMPLEKSİTE ANALİZİ - Complexity Metrics
    # =========================================================================

    def analyze_code_complexity(self, code: str) -> Dict:
        """
        AŞAMA 4: Kod karmaşıklığını analiz et

        Returns:
            - cyclomatic_complexity: Döngüsel karmaşıklık (yaklaşık)
            - nesting_depth: Maksimum iç içe geçme derinliği
            - variable_count: Değişken sayısı
            - conditional_count: Koşul sayısı (if, require, etc.)
            - loop_count: Döngü sayısı
            - complexity_score: Genel karmaşıklık skoru (0-100)
        """
        # Koşullar
        if_count = len(re.findall(r'\bif\s*\(', code))
        require_count = len(re.findall(r'\brequire\s*\(', code))
        assert_count = len(re.findall(r'\bassert\s*\(', code))
        conditional_count = if_count + require_count + assert_count

        # Döngüler
        for_count = len(re.findall(r'\bfor\s*\(', code))
        while_count = len(re.findall(r'\bwhile\s*\(', code))
        loop_count = for_count + while_count

        # Cyclomatic Complexity (yaklaşık)
        # CC = decision points + 1
        cyclomatic = conditional_count + loop_count + 1

        # İç içe geçme derinliği
        nesting_depth = self._calculate_nesting_depth(code)

        # Değişken sayısı (yaklaşık - uint, address, bool, string vb.)
        variable_patterns = [
            r'\buint\d*\s+\w+',
            r'\baddress\s+\w+',
            r'\bbool\s+\w+',
            r'\bstring\s+\w+',
            r'\bbytes\d*\s+\w+'
        ]
        variable_count = sum(len(re.findall(pattern, code)) for pattern in variable_patterns)

        # Karmaşıklık skoru (0-100)
        # Yüksek = daha karmaşık
        complexity_score = min(100, cyclomatic * 5 + nesting_depth * 10 + loop_count * 3)

        return {
            "cyclomatic_complexity": cyclomatic,
            "nesting_depth": nesting_depth,
            "variable_count": variable_count,
            "conditional_count": conditional_count,
            "loop_count": loop_count,
            "complexity_score": round(complexity_score, 2),
            "complexity_level": self._interpret_complexity(complexity_score)
        }

    def _calculate_nesting_depth(self, code: str) -> int:
        """İç içe geçme derinliğini hesapla"""
        max_depth = 0
        current_depth = 0

        for char in code:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)

        return max_depth

    def _interpret_complexity(self, score: float) -> str:
        """Karmaşıklık skorunu yorumla"""
        if score >= 80:
            return "Çok Yüksek - Refactoring Önerilir"
        elif score >= 60:
            return "Yüksek - Karmaşık"
        elif score >= 40:
            return "Orta - Kabul Edilebilir"
        elif score >= 20:
            return "Düşük - İyi"
        else:
            return "Çok Düşük - Basit"

    # =========================================================================
    # AŞAMA 5: KOD KALİTE ANALİZİ - Quality Metrics
    # =========================================================================

    def analyze_code_quality(self, code: str) -> Dict:
        """
        AŞAMA 5: Kod kalitesini değerlendir

        Returns:
            - readability_score: Okunabilirlik skoru (0-100)
            - maintainability_score: Sürdürülebilirlik skoru (0-100)
            - documentation_score: Dokümantasyon skoru (0-100)
            - best_practices_score: En iyi pratikler skoru (0-100)
            - overall_quality: Genel kalite skoru (0-100)
        """
        structure = self.analyze_code_structure(code)
        complexity = self.analyze_code_complexity(code)

        # Okunabilirlik: yorum oranı + ortalama satır uzunluğu
        readability = 50
        if structure['comment_ratio'] >= 20:
            readability += 20
        elif structure['comment_ratio'] >= 10:
            readability += 10

        if structure['avg_line_length'] <= 80:
            readability += 30
        elif structure['avg_line_length'] <= 120:
            readability += 15

        # Sürdürülebilirlik: karmaşıklık + modülerlik
        maintainability = 100 - (complexity['complexity_score'] * 0.5)
        if structure['function_count'] >= 3:
            maintainability += 10
        maintainability = min(100, maintainability)

        # Dokümantasyon: yorum oranı
        documentation = min(100, structure['comment_ratio'] * 3)

        # En iyi pratikler: require/assert kullanımı + modifiers
        best_practices = 50
        if 'require(' in code:
            best_practices += 15
        if 'modifier' in code:
            best_practices += 15
        if 'event' in code:
            best_practices += 10
        if 'revert' in code or 'assert' in code:
            best_practices += 10

        # Genel kalite
        overall_quality = (
            readability * 0.25 +
            maintainability * 0.35 +
            documentation * 0.20 +
            best_practices * 0.20
        )

        return {
            "readability_score": round(readability, 2),
            "maintainability_score": round(maintainability, 2),
            "documentation_score": round(documentation, 2),
            "best_practices_score": round(best_practices, 2),
            "overall_quality": round(overall_quality, 2),
            "quality_grade": self._get_quality_grade(overall_quality)
        }

    def _get_quality_grade(self, score: float) -> str:
        """Kalite notunu al"""
        if score >= 90:
            return "A+ (Mükemmel)"
        elif score >= 80:
            return "A (Çok İyi)"
        elif score >= 70:
            return "B (İyi)"
        elif score >= 60:
            return "C (Orta)"
        elif score >= 50:
            return "D (Zayıf)"
        else:
            return "F (Yetersiz)"

    # =========================================================================
    # AŞAMA 6: KOMPARATİF ANALİZ - Persona Karşılaştırması
    # =========================================================================

    def compare_persona_outputs(self,
                                persona1_name: str, code1: str, prompt1: str,
                                persona2_name: str, code2: str, prompt2: str) -> Dict:
        """
        AŞAMA 6: İki persona çıktısını karşılaştır

        Returns:
            Detaylı karşılaştırma metrikleri
        """
        # Her iki kod için analiz
        quality1 = self.analyze_code_quality(code1)
        quality2 = self.analyze_code_quality(code2)

        complexity1 = self.analyze_code_complexity(code1)
        complexity2 = self.analyze_code_complexity(code2)

        structure1 = self.analyze_code_structure(code1)
        structure2 = self.analyze_code_structure(code2)

        # Prompt benzerliği
        prompt_sim = self.calculate_prompt_similarity(prompt1, prompt2)

        # Kod benzerliği (yapısal)
        code_sim = self._compare_code_structures(structure1, structure2)

        return {
            "prompt_similarity": prompt_sim,
            "code_structural_similarity": code_sim,
            "quality_comparison": {
                persona1_name: quality1['overall_quality'],
                persona2_name: quality2['overall_quality'],
                "winner": persona1_name if quality1['overall_quality'] > quality2['overall_quality'] else persona2_name,
                "difference": abs(quality1['overall_quality'] - quality2['overall_quality'])
            },
            "complexity_comparison": {
                persona1_name: complexity1['complexity_score'],
                persona2_name: complexity2['complexity_score'],
                "simpler": persona1_name if complexity1['complexity_score'] < complexity2['complexity_score'] else persona2_name
            },
            "size_comparison": {
                persona1_name: structure1['total_lines'],
                persona2_name: structure2['total_lines'],
                "more_verbose": persona1_name if structure1['total_lines'] > structure2['total_lines'] else persona2_name
            },
            "documentation_comparison": {
                persona1_name: structure1['comment_ratio'],
                persona2_name: structure2['comment_ratio'],
                "better_documented": persona1_name if structure1['comment_ratio'] > structure2['comment_ratio'] else persona2_name
            }
        }

    def _compare_code_structures(self, struct1: Dict, struct2: Dict) -> float:
        """İki kod yapısını karşılaştır (0-1 benzerlik)"""
        # Normalize edilmiş farklar
        metrics = ['code_lines', 'comment_lines', 'function_count']

        similarities = []
        for metric in metrics:
            val1 = struct1.get(metric, 0)
            val2 = struct2.get(metric, 0)
            max_val = max(val1, val2, 1)
            similarity = 1 - (abs(val1 - val2) / max_val)
            similarities.append(similarity)

        return round(sum(similarities) / len(similarities), 4)

    # =========================================================================
    # FULL ANALİZ - Tüm Aşamaları Birleştir
    # =========================================================================

    def full_analysis(self, prompt: str, code: str) -> Dict:
        """
        Tüm 6 aşamalı analizi tek seferde yap

        Returns:
            Tüm analiz sonuçlarını içeren dict
        """
        return {
            "stage_1_prompt_analysis": self.analyze_prompt(prompt),
            "stage_3_code_structure": self.analyze_code_structure(code),
            "stage_4_code_complexity": self.analyze_code_complexity(code),
            "stage_5_code_quality": self.analyze_code_quality(code),
        }


# =========================================================================
# Yardımcı Fonksiyonlar
# =========================================================================

def format_analysis_for_display(analysis: Dict) -> str:
    """Analiz sonuçlarını güzel formatta göster"""
    output = []

    output.append("=" * 80)
    output.append("📊 6 AŞAMALI İÇERİK ANALİZİ RAPORU")
    output.append("=" * 80)

    if "stage_1_prompt_analysis" in analysis:
        output.append("\n🔍 AŞAMA 1: PROMPT ANALİZİ")
        output.append("-" * 80)
        prompt_data = analysis["stage_1_prompt_analysis"]
        output.append(f"  Uzunluk: {prompt_data['length']} karakter")
        output.append(f"  Kelime Sayısı: {prompt_data['word_count']}")
        output.append(f"  Teknik Terim: {prompt_data['technical_term_count']}")
        output.append(f"  Netlik Skoru: {prompt_data['clarity_score']}/100")
        output.append(f"  Özgüllük Skoru: {prompt_data['specificity_score']}/100")

    if "stage_3_code_structure" in analysis:
        output.append("\n🏗️ AŞAMA 3: KOD YAPISI")
        output.append("-" * 80)
        struct_data = analysis["stage_3_code_structure"]
        output.append(f"  Toplam Satır: {struct_data['total_lines']}")
        output.append(f"  Kod Satırı: {struct_data['code_lines']}")
        output.append(f"  Yorum Satırı: {struct_data['comment_lines']}")
        output.append(f"  Yorum Oranı: {struct_data['comment_ratio']}%")
        output.append(f"  Fonksiyon Sayısı: {struct_data['function_count']}")

    if "stage_4_code_complexity" in analysis:
        output.append("\n🔬 AŞAMA 4: KOD KOMPLEKSİTE")
        output.append("-" * 80)
        complex_data = analysis["stage_4_code_complexity"]
        output.append(f"  Cyclomatic Complexity: {complex_data['cyclomatic_complexity']}")
        output.append(f"  İç İçe Geçme Derinliği: {complex_data['nesting_depth']}")
        output.append(f"  Karmaşıklık Skoru: {complex_data['complexity_score']}/100")
        output.append(f"  Seviye: {complex_data['complexity_level']}")

    if "stage_5_code_quality" in analysis:
        output.append("\n⭐ AŞAMA 5: KOD KALİTESİ")
        output.append("-" * 80)
        quality_data = analysis["stage_5_code_quality"]
        output.append(f"  Okunabilirlik: {quality_data['readability_score']}/100")
        output.append(f"  Sürdürülebilirlik: {quality_data['maintainability_score']}/100")
        output.append(f"  Dokümantasyon: {quality_data['documentation_score']}/100")
        output.append(f"  En İyi Pratikler: {quality_data['best_practices_score']}/100")
        output.append(f"  ⭐ GENEL KALİTE: {quality_data['overall_quality']}/100 - {quality_data['quality_grade']}")

    output.append("\n" + "=" * 80)

    return "\n".join(output)
