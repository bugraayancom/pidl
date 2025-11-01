"""
Performans Değerlendirme Sistemi
Kodları güvenlik, kalite, performans ve karmaşıklık açısından değerlendirir
"""

import ast
import tempfile
import os
import subprocess
import json
from typing import Dict, List, Optional
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
import re


class CodeEvaluator:
    """Kod değerlendirme sınıfı"""
    
    def __init__(self):
        """Evaluator başlat"""
        self.metrics = {}
    
    def evaluate_code(self, code: str, persona_id: str, persona_name: str) -> Dict:
        """
        Tek bir kodu değerlendir
        
        Args:
            code: Değerlendirilecek kod
            persona_id: Persona ID
            persona_name: Persona adı
            
        Returns:
            Değerlendirme sonuçları
        """
        results = {
            "persona_id": persona_id,
            "persona_name": persona_name,
            "code": code,
            "security_score": 0,
            "quality_score": 0,
            "complexity_score": 0,
            "maintainability_index": 0,
            "total_score": 0,
            "metrics": {},
            "issues": []
        }
        
        try:
            # 1. Güvenlik Analizi (Bandit)
            security_results = self._run_security_analysis(code)
            results["security_score"] = security_results["score"]
            results["metrics"]["security"] = security_results
            results["issues"].extend(security_results.get("issues", []))
            
            # 2. Kod Kalitesi Analizi (Pylint)
            quality_results = self._run_quality_analysis(code)
            results["quality_score"] = quality_results["score"]
            results["metrics"]["quality"] = quality_results
            results["issues"].extend(quality_results.get("issues", []))
            
            # 3. Karmaşıklık Analizi (Radon)
            complexity_results = self._analyze_complexity(code)
            results["complexity_score"] = complexity_results["score"]
            results["metrics"]["complexity"] = complexity_results
            
            # 4. Maintainability Index (Radon)
            mi_results = self._analyze_maintainability(code)
            results["maintainability_index"] = mi_results["index"]
            results["metrics"]["maintainability"] = mi_results
            
            # 5. Genel Metrikler
            general_metrics = self._analyze_general_metrics(code)
            results["metrics"]["general"] = general_metrics
            
            # Toplam skor hesapla (ağırlıklı ortalama)
            results["total_score"] = (
                results["security_score"] * 0.30 +
                results["quality_score"] * 0.30 +
                results["complexity_score"] * 0.20 +
                (results["maintainability_index"] / 100) * 100 * 0.20
            )
            
        except Exception as e:
            results["issues"].append({
                "type": "error",
                "message": f"Değerlendirme hatası: {str(e)}"
            })
        
        return results
    
    def _run_security_analysis(self, code: str) -> Dict:
        """Bandit ile güvenlik analizi"""
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Bandit çalıştır
            result = subprocess.run(
                ['bandit', '-f', 'json', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Geçici dosyayı sil
            os.unlink(temp_file)
            
            if result.stdout:
                bandit_output = json.loads(result.stdout)
                issues = bandit_output.get('results', [])
                
                # Skor hesapla (100 - (her issue için -10))
                severity_weights = {'HIGH': 20, 'MEDIUM': 10, 'LOW': 5}
                penalty = sum(severity_weights.get(issue['issue_severity'], 5) for issue in issues)
                score = max(0, 100 - penalty)
                
                return {
                    "score": score,
                    "issues_count": len(issues),
                    "issues": [
                        {
                            "type": "security",
                            "severity": issue.get('issue_severity', 'UNKNOWN'),
                            "message": issue.get('issue_text', ''),
                            "line": issue.get('line_number', 0)
                        }
                        for issue in issues
                    ]
                }
            else:
                return {"score": 100, "issues_count": 0, "issues": []}
                
        except subprocess.TimeoutExpired:
            return {"score": 50, "issues_count": 0, "issues": [{"type": "security", "message": "Timeout"}]}
        except Exception as e:
            return {"score": 50, "issues_count": 0, "issues": [{"type": "security", "message": str(e)}]}
    
    def _run_quality_analysis(self, code: str) -> Dict:
        """Pylint ile kod kalitesi analizi"""
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Pylint çalıştır
            result = subprocess.run(
                ['pylint', '--output-format=json', temp_file],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Geçici dosyayı sil
            os.unlink(temp_file)
            
            if result.stdout:
                try:
                    pylint_output = json.loads(result.stdout)
                    issues = pylint_output if isinstance(pylint_output, list) else []
                    
                    # Skor hesapla
                    type_weights = {'error': 10, 'warning': 5, 'convention': 2, 'refactor': 3}
                    penalty = sum(type_weights.get(issue.get('type', ''), 2) for issue in issues)
                    score = max(0, 100 - penalty)
                    
                    return {
                        "score": score,
                        "issues_count": len(issues),
                        "issues": [
                            {
                                "type": "quality",
                                "severity": issue.get('type', 'unknown').upper(),
                                "message": issue.get('message', ''),
                                "line": issue.get('line', 0)
                            }
                            for issue in issues[:10]  # İlk 10'u al
                        ]
                    }
                except json.JSONDecodeError:
                    # JSON parse hatası, regex ile skor çıkar
                    score_match = re.search(r'Your code has been rated at ([\d.]+)/10', result.stdout)
                    if score_match:
                        pylint_score = float(score_match.group(1))
                        return {"score": pylint_score * 10, "issues_count": 0, "issues": []}
            
            return {"score": 70, "issues_count": 0, "issues": []}
                
        except subprocess.TimeoutExpired:
            return {"score": 50, "issues_count": 0, "issues": [{"type": "quality", "message": "Timeout"}]}
        except Exception as e:
            return {"score": 50, "issues_count": 0, "issues": [{"type": "quality", "message": str(e)}]}
    
    def _analyze_complexity(self, code: str) -> Dict:
        """Radon ile karmaşıklık analizi"""
        try:
            # Cyclomatic Complexity
            complexity_results = cc_visit(code)
            
            if complexity_results:
                # Ortalama complexity hesapla
                complexities = [item.complexity for item in complexity_results]
                avg_complexity = sum(complexities) / len(complexities)
                max_complexity = max(complexities)
                
                # Skor hesapla (düşük complexity = yüksek skor)
                # 1-5: A (mükemmel), 6-10: B (iyi), 11-20: C (orta), 21+: D-F (zayıf)
                if avg_complexity <= 5:
                    score = 100
                elif avg_complexity <= 10:
                    score = 80
                elif avg_complexity <= 20:
                    score = 60
                else:
                    score = max(0, 100 - (avg_complexity - 20) * 2)
                
                return {
                    "score": score,
                    "average_complexity": round(avg_complexity, 2),
                    "max_complexity": max_complexity,
                    "functions_count": len(complexity_results),
                    "grade": self._complexity_grade(avg_complexity)
                }
            else:
                return {
                    "score": 100,
                    "average_complexity": 0,
                    "max_complexity": 0,
                    "functions_count": 0,
                    "grade": "A"
                }
                
        except Exception as e:
            return {
                "score": 50,
                "average_complexity": 0,
                "error": str(e)
            }
    
    def _analyze_maintainability(self, code: str) -> Dict:
        """Radon ile maintainability index analizi"""
        try:
            # Önce multi=True dene
            mi_results = mi_visit(code, multi=True)
            
            if mi_results:
                # Ortalama MI hesapla
                mi_values = [item.mi for item in mi_results]
                avg_mi = sum(mi_values) / len(mi_values)
                
                return {
                    "index": round(avg_mi, 2),
                    "grade": self._mi_grade(avg_mi),
                    "modules_count": len(mi_results)
                }
            
            # multi=True çalışmazsa multi=False dene
            mi_results = mi_visit(code, multi=False)
            if mi_results:
                mi_values = [item.mi for item in mi_results]
                avg_mi = sum(mi_values) / len(mi_values)
                
                return {
                    "index": round(avg_mi, 2),
                    "grade": self._mi_grade(avg_mi),
                    "modules_count": len(mi_results)
                }
            
            # Hiçbiri çalışmazsa, manuel hesaplama
            # Basit bir kod için yüksek maintainability ver
            raw_metrics = analyze(code)
            
            # Basit heuristic: 
            # - Az satır = iyi (max 100 satır optimal)
            # - İyi yorum oranı = iyi (10-30% optimal)
            # - Düşük karmaşıklık = iyi
            
            loc = raw_metrics.loc if raw_metrics.loc > 0 else 1
            comment_ratio = (raw_metrics.comments / loc * 100) if loc > 0 else 0
            
            # LOC skoru (az satır = iyi)
            loc_score = max(0, 100 - (loc - 50) * 0.5) if loc > 50 else 100
            
            # Yorum skoru (10-30% optimal)
            if 10 <= comment_ratio <= 30:
                comment_score = 100
            elif comment_ratio < 10:
                comment_score = 60 + comment_ratio * 4
            else:
                comment_score = max(60, 130 - comment_ratio)
            
            # Karmaşıklık etkisi
            complexity_results = cc_visit(code)
            if complexity_results:
                avg_complexity = sum(item.complexity for item in complexity_results) / len(complexity_results)
                complexity_score = max(0, 100 - avg_complexity * 5)
            else:
                complexity_score = 100
            
            # Ağırlıklı ortalama
            estimated_mi = (loc_score * 0.4 + comment_score * 0.3 + complexity_score * 0.3)
            
            return {
                "index": round(min(100, max(0, estimated_mi)), 2),
                "grade": self._mi_grade(estimated_mi),
                "modules_count": 0,
                "estimated": True
            }
                
        except Exception as e:
            # Gerçekten hata varsa, genel metriklerden tahmin et
            try:
                raw_metrics = analyze(code)
                loc = raw_metrics.loc if raw_metrics.loc > 0 else 1
                
                # Çok basit tahmin: orta seviye kod
                if loc < 30:
                    estimated_mi = 80  # Küçük kod = iyi maintainability
                elif loc < 100:
                    estimated_mi = 70  # Orta kod
                else:
                    estimated_mi = 60  # Büyük kod
                
                return {
                    "index": estimated_mi,
                    "grade": self._mi_grade(estimated_mi),
                    "error": str(e),
                    "estimated": True
                }
            except:
                return {
                    "index": 65,  # 50 yerine daha gerçekçi default
                    "grade": "B",
                    "error": str(e),
                    "estimated": True
                }
    
    def _analyze_general_metrics(self, code: str) -> Dict:
        """Genel kod metrikleri"""
        try:
            analysis = analyze(code)
            
            # Yorum oranı hesapla
            if analysis.loc > 0:
                comment_ratio = (analysis.comments / analysis.loc) * 100
            else:
                comment_ratio = 0
            
            # Fonksiyon sayısı
            function_count = self._count_functions(code)
            
            # Type hint kullanımı
            type_hint_ratio = self._calculate_type_hint_usage(code)
            
            # Docstring detay skoru
            docstring_score = self._calculate_docstring_quality(code)
            
            # PEDAGOGICAL METRIKLER
            learning_ease = self._calculate_learning_ease(code, comment_ratio, docstring_score, function_count)
            cognitive_load = self._calculate_cognitive_load(code, function_count)
            instructiveness = self._calculate_instructiveness(code, comment_ratio, docstring_score)
            example_quality = self._calculate_example_quality(code)
            
            return {
                "lines_of_code": analysis.loc,
                "logical_lines": analysis.lloc,
                "source_lines": analysis.sloc,
                "comments": analysis.comments,
                "comment_ratio": round(comment_ratio, 2),
                "blank_lines": analysis.blank,
                "multi_line_strings": analysis.multi,
                "function_count": function_count,
                "type_hint_ratio": round(type_hint_ratio, 2),
                "docstring_score": round(docstring_score, 2),
                # Pedagojik metrikler
                "learning_ease": round(learning_ease, 2),
                "cognitive_load_score": round(cognitive_load, 2),
                "instructiveness_index": round(instructiveness, 2),
                "example_quality": round(example_quality, 2)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _count_functions(self, code: str) -> int:
        """Fonksiyon sayısını say"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            return len(functions)
        except:
            return 0
    
    def _calculate_type_hint_usage(self, code: str) -> float:
        """Type hint kullanım oranını hesapla"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            if not functions:
                return 0
            
            type_hinted = 0
            for func in functions:
                # Return type hint var mı?
                has_return_hint = func.returns is not None
                
                # Parametre type hints var mı?
                param_hints = sum(1 for arg in func.args.args if arg.annotation is not None)
                total_params = len(func.args.args)
                
                # Fonksiyonun type hint skoru
                if total_params > 0:
                    func_score = (param_hints / total_params) * 0.7 + (0.3 if has_return_hint else 0)
                else:
                    func_score = 1.0 if has_return_hint else 0
                
                type_hinted += func_score
            
            return (type_hinted / len(functions)) * 100
            
        except:
            return 0
    
    def _calculate_docstring_quality(self, code: str) -> float:
        """Docstring kalite skoru (0-100)"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            if not functions:
                return 0
            
            total_score = 0
            for func in functions:
                docstring = ast.get_docstring(func)
                
                if not docstring:
                    score = 0
                else:
                    # Docstring uzunluğu
                    length_score = min(len(docstring) / 100, 1.0) * 40  # Max 40 puan
                    
                    # Args/Returns açıklaması var mı?
                    has_args = "Args:" in docstring or "Parameters:" in docstring
                    has_returns = "Returns:" in docstring or "Return:" in docstring
                    has_example = "Example:" in docstring or ">>>" in docstring
                    
                    detail_score = (
                        (20 if has_args else 0) +
                        (20 if has_returns else 0) +
                        (20 if has_example else 0)
                    )
                    
                    score = length_score + detail_score
                
                total_score += score
            
            return (total_score / len(functions))
            
        except:
            return 0
    
    def _calculate_learning_ease(self, code: str, comment_ratio: float, 
                                 docstring_score: float, function_count: int) -> float:
        """
        Öğrenme Kolaylığı Skoru (0-100)
        Kod ne kadar kolay öğrenilebilir?
        
        Faktörler:
        - Yüksek yorum oranı = daha kolay öğrenme
        - İyi docstring = kavramları açıklıyor
        - Az fonksiyon = daha basit (başlangıç için)
        - Anlamlı değişken isimleri
        """
        try:
            # Yorum skoru (25-50% optimal öğretici)
            if 25 <= comment_ratio <= 50:
                comment_score = 100
            elif comment_ratio > 50:
                comment_score = max(70, 100 - (comment_ratio - 50))
            else:
                comment_score = comment_ratio * 2  # %25'te 50 puan
            
            # Docstring skoru (zaten 0-100)
            doc_score = docstring_score
            
            # Fonksiyon sayısı (2-5 arası optimal öğretici)
            if function_count == 0:
                func_score = 50
            elif 2 <= function_count <= 5:
                func_score = 100
            elif function_count == 1:
                func_score = 80
            else:
                func_score = max(50, 100 - (function_count - 5) * 5)
            
            # Değişken isim açıklayıcılığı
            name_score = self._check_variable_naming_quality(code)
            
            # Ağırlıklı ortalama
            ease_score = (
                comment_score * 0.35 +
                doc_score * 0.30 +
                func_score * 0.20 +
                name_score * 0.15
            )
            
            return min(100, ease_score)
            
        except:
            return 50
    
    def _calculate_cognitive_load(self, code: str, function_count: int) -> float:
        """
        Bilişsel Yük Skoru (0-100, DÜŞÜK yük = YÜKSEK skor)
        Sweller's Cognitive Load Theory bazlı
        
        Düşük bilişsel yük = öğrenmesi kolay
        Yüksek bilişsel yük = öğrenmesi zor
        """
        try:
            tree = ast.parse(code)
            
            # 1. Nesting depth (iç içe yapılar)
            max_depth = self._calculate_max_nesting_depth(tree)
            # Skor: 0-2 depth = 100, 3-4 = 70, 5+ = 40
            if max_depth <= 2:
                depth_score = 100
            elif max_depth <= 4:
                depth_score = 70
            else:
                depth_score = max(20, 100 - max_depth * 15)
            
            # 2. Ortalama fonksiyon karmaşıklığı
            complexity_results = cc_visit(code)
            if complexity_results:
                avg_complexity = sum(item.complexity for item in complexity_results) / len(complexity_results)
                # Düşük complexity = düşük bilişsel yük
                if avg_complexity <= 3:
                    complexity_score = 100
                elif avg_complexity <= 6:
                    complexity_score = 80
                else:
                    complexity_score = max(30, 100 - avg_complexity * 8)
            else:
                complexity_score = 100
            
            # 3. Satır başına kavram sayısı (her satır kaç şey yapıyor?)
            lines = code.split('\n')
            non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            if non_empty_lines:
                # Operatör sayısı / satır sayısı
                operators = code.count('(') + code.count('[') + code.count('{')
                density = operators / len(non_empty_lines) if non_empty_lines else 0
                # Düşük density = her satır basit
                density_score = max(40, 100 - density * 20)
            else:
                density_score = 100
            
            # Ağırlıklı ortalama
            load_score = (
                depth_score * 0.40 +
                complexity_score * 0.40 +
                density_score * 0.20
            )
            
            return min(100, load_score)
            
        except:
            return 60
    
    def _calculate_instructiveness(self, code: str, comment_ratio: float, 
                                   docstring_score: float) -> float:
        """
        Öğreticilik İndeksi (0-100)
        Kod ne kadar öğretici ve açıklayıcı?
        """
        try:
            # 1. Yorum kalitesi (sadece oran değil, içerik)
            explanatory_comments = self._count_explanatory_comments(code)
            
            # 2. Docstring skoru (zaten var)
            
            # 3. Adım adım açıklama var mı?
            has_step_markers = self._check_step_by_step_markers(code)
            step_score = 100 if has_step_markers else 40
            
            # 4. Örnek kullanım var mı?
            has_examples = self._has_usage_examples(code)
            example_score = 100 if has_examples else 30
            
            # Ağırlıklı ortalama
            instructiveness = (
                explanatory_comments * 0.30 +
                docstring_score * 0.30 +
                step_score * 0.20 +
                example_score * 0.20
            )
            
            return min(100, instructiveness)
            
        except:
            return 50
    
    def _calculate_example_quality(self, code: str) -> float:
        """
        Örnek Kalitesi Skoru (0-100)
        Main bloğu, usage examples, test cases kalitesi
        """
        try:
            score = 0
            
            # 1. if __name__ == "__main__": bloğu var mı?
            has_main = 'if __name__' in code
            if has_main:
                score += 40
            
            # 2. Örnek kullanım gösteriliyor mu?
            has_usage = any(keyword in code.lower() for keyword in ['örnek', 'example', 'usage', 'test'])
            if has_usage:
                score += 30
            
            # 3. Print statements ile output gösterimi
            has_prints = 'print(' in code
            if has_prints:
                score += 20
            
            # 4. Farklı senaryolar gösteriliyor mu?
            print_count = code.count('print(')
            if print_count >= 3:
                score += 10
            
            return min(100, score)
            
        except:
            return 30
    
    def _check_variable_naming_quality(self, code: str) -> float:
        """
        Değişken isim kalitesi (0-100)
        Açıklayıcı ve öğretici isimler mi?
        """
        try:
            tree = ast.parse(code)
            
            # Tüm değişkenleri topla
            variables = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    variables.append(node.id)
            
            if not variables:
                return 50
            
            # Kısa isimler (i, j, k, x, y) - matematiksel kabul edilebilir
            math_vars = {'i', 'j', 'k', 'n', 'm', 'x', 'y', 'z'}
            short_vars = [v for v in variables if len(v) <= 2 and v not in math_vars]
            
            # Uzun açıklayıcı isimler (total_sum, student_count)
            long_vars = [v for v in variables if len(v) > 8]
            
            # Underscore kullanımı (snake_case)
            snake_case_vars = [v for v in variables if '_' in v]
            
            # Skor hesaplama
            total_vars = len(set(variables))
            short_ratio = len(short_vars) / total_vars if total_vars > 0 else 0
            long_ratio = len(long_vars) / total_vars if total_vars > 0 else 0
            snake_ratio = len(snake_case_vars) / total_vars if total_vars > 0 else 0
            
            # Açıklayıcı isimler yüksek puan
            score = (
                (1 - short_ratio) * 40 +  # Az kısa isim = iyi
                long_ratio * 30 +  # Çok uzun isim = iyi
                snake_ratio * 30  # Snake case = iyi
            )
            
            return min(100, score * 100)
            
        except:
            return 50
    
    def _calculate_max_nesting_depth(self, tree) -> int:
        """Maksimum iç içe geçme derinliği"""
        try:
            max_depth = 0
            
            def get_depth(node, current_depth=0):
                nonlocal max_depth
                max_depth = max(max_depth, current_depth)
                
                if isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
                    current_depth += 1
                
                for child in ast.iter_child_nodes(node):
                    get_depth(child, current_depth)
            
            get_depth(tree)
            return max_depth
            
        except:
            return 0
    
    def _count_explanatory_comments(self, code: str) -> float:
        """
        Açıklayıcı yorum sayısı ve kalitesi (0-100)
        """
        try:
            lines = code.split('\n')
            comments = [l for l in lines if l.strip().startswith('#')]
            
            if not comments:
                return 0
            
            # Yorum uzunlukları
            explanatory = 0
            for comment in comments:
                # Uzun yorumlar (>30 karakter) açıklayıcıdır
                if len(comment.strip()) > 30:
                    explanatory += 1
                # Orta yorumlar
                elif len(comment.strip()) > 15:
                    explanatory += 0.5
            
            # Toplam satıra göre normalize et
            total_lines = len([l for l in lines if l.strip()])
            if total_lines > 0:
                ratio = (explanatory / total_lines) * 100
                # %15-30 arası optimal
                if 15 <= ratio <= 30:
                    return 100
                elif ratio > 30:
                    return max(70, 100 - (ratio - 30))
                else:
                    return ratio * 3.33  # %30'da 100 puan
            
            return 50
            
        except:
            return 0
    
    def _check_step_by_step_markers(self, code: str) -> bool:
        """
        Adım adım açıklama marker'ları var mı?
        # ADIM 1:, # Step 1:, etc.
        """
        markers = ['adim', 'step', 'aşama', 'stage', 'phase', '1.', '2.', '3.']
        code_lower = code.lower()
        return any(marker in code_lower for marker in markers)
    
    def _has_usage_examples(self, code: str) -> bool:
        """
        Kullanım örneği var mı?
        """
        example_markers = [
            'if __name__',
            'örnek',
            'example',
            'kullanım',
            'usage',
            'test',
            '# demo'
        ]
        code_lower = code.lower()
        return any(marker in code_lower for marker in example_markers)
    
    def _complexity_grade(self, complexity: float) -> str:
        """Karmaşıklık notu"""
        if complexity <= 5:
            return "A"
        elif complexity <= 10:
            return "B"
        elif complexity <= 20:
            return "C"
        elif complexity <= 30:
            return "D"
        else:
            return "F"
    
    def _mi_grade(self, mi: float) -> str:
        """Maintainability Index notu"""
        if mi >= 80:
            return "A"
        elif mi >= 60:
            return "B"
        elif mi >= 40:
            return "C"
        elif mi >= 20:
            return "D"
        else:
            return "F"
    
    def evaluate_all(self, results: List[Dict]) -> List[Dict]:
        """
        Tüm persona sonuçlarını değerlendir
        
        Args:
            results: Code generator sonuçları
            
        Returns:
            Değerlendirilmiş sonuçlar
        """
        evaluated = []
        
        for result in results:
            if result.get("success") and result.get("code"):
                evaluation = self.evaluate_code(
                    result["code"],
                    result["persona_id"],
                    result["persona_name"]
                )
                # Orijinal bilgileri ekle
                evaluation.update({
                    "persona_role": result.get("persona_role"),
                    "category": result.get("category"),
                    "avatar": result.get("avatar"),
                    "tokens_used": result.get("tokens_used", 0),
                    "persona_prompt": result.get("persona_prompt", "Prompt bulunamadı")
                })
                evaluated.append(evaluation)
            else:
                # Başarısız sonuçları da ekle
                evaluated.append({
                    "persona_id": result["persona_id"],
                    "persona_name": result["persona_name"],
                    "persona_role": result.get("persona_role"),
                    "category": result.get("category"),
                    "avatar": result.get("avatar"),
                    "code": result.get("code", ""),
                    "persona_prompt": result.get("persona_prompt", "Prompt oluşturulamadı"),
                    "total_score": 0,
                    "error": result.get("error")
                })
        
        return evaluated
    
    def get_rankings(self, evaluated_results: List[Dict]) -> Dict:
        """
        Değerlendirme sonuçlarına göre sıralama
        
        Args:
            evaluated_results: Değerlendirilmiş sonuçlar
            
        Returns:
            Sıralamalar ve istatistikler
        """
        # Skor'a göre sırala
        sorted_results = sorted(
            evaluated_results,
            key=lambda x: x.get("total_score", 0),
            reverse=True
        )
        
        # Kategori bazlı en iyiler
        education_best = max(
            [r for r in evaluated_results if r.get("category") == "education"],
            key=lambda x: x.get("total_score", 0),
            default=None
        )
        
        technology_best = max(
            [r for r in evaluated_results if r.get("category") == "technology"],
            key=lambda x: x.get("total_score", 0),
            default=None
        )
        
        # Metrik bazlı en iyiler
        best_security = max(evaluated_results, key=lambda x: x.get("security_score", 0), default=None)
        best_quality = max(evaluated_results, key=lambda x: x.get("quality_score", 0), default=None)
        best_complexity = max(evaluated_results, key=lambda x: x.get("complexity_score", 0), default=None)
        best_maintainability = max(evaluated_results, key=lambda x: x.get("maintainability_index", 0), default=None)
        
        return {
            "overall_ranking": sorted_results,
            "best_overall": sorted_results[0] if sorted_results else None,
            "best_education": education_best,
            "best_technology": technology_best,
            "best_security": best_security,
            "best_quality": best_quality,
            "best_complexity": best_complexity,
            "best_maintainability": best_maintainability,
            "statistics": self._calculate_statistics(evaluated_results)
        }
    
    def _calculate_statistics(self, results: List[Dict]) -> Dict:
        """İstatistik hesapla"""
        if not results:
            return {}
        
        scores = [r.get("total_score", 0) for r in results]
        
        return {
            "average_score": round(sum(scores) / len(scores), 2),
            "max_score": max(scores),
            "min_score": min(scores),
            "total_codes": len(results)
        }


# Test için
if __name__ == "__main__":
    # Test kodu
    test_code = """
def fibonacci(n):
    \"\"\"Fibonacci sayısını hesapla\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test
print(fibonacci(10))
"""
    
    evaluator = CodeEvaluator()
    result = evaluator.evaluate_code(test_code, "test_1", "Test Persona")
    
    print("📊 Değerlendirme Sonuçları:")
    print(f"  • Toplam Skor: {result['total_score']:.2f}/100")
    print(f"  • Güvenlik: {result['security_score']:.2f}/100")
    print(f"  • Kalite: {result['quality_score']:.2f}/100")
    print(f"  • Karmaşıklık: {result['complexity_score']:.2f}/100")
    print(f"  • Maintainability: {result['maintainability_index']:.2f}/100")

