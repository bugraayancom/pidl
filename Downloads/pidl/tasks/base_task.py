"""
Base Task Class
Tüm görevler için ortak yapı ve metodlar
"""

from typing import List, Dict, Any
from abc import ABC, abstractmethod


class BaseTask(ABC):
    """
    Tüm görevlerin kalıtım alacağı base class
    """

    def __init__(self):
        self.task_number: int = 0
        self.difficulty: str = ""
        self.title: str = ""
        self.description: str = ""
        self.max_time_minutes: int = 45

    @abstractmethod
    def get_pre_test_questions(self) -> List[Dict[str, Any]]:
        """Pre-test soruları"""
        pass

    @abstractmethod
    def get_post_test_questions(self) -> List[Dict[str, Any]]:
        """Post-test soruları (pre-test + 2 ek soru)"""
        pass

    @abstractmethod
    def get_evaluation_criteria(self) -> Dict[str, Dict[str, int]]:
        """Otomatik değerlendirme kriterleri"""
        pass

    def get_full_prompt(self, user_context: str = "") -> str:
        """
        AI için tam prompt oluştur

        Args:
            user_context: Kullanıcıdan gelen ek bilgi/istek

        Returns:
            Formatlanmış prompt
        """
        prompt = f"""# GÖREV {self.task_number}: {self.title}

## Görev Açıklaması
{self.description}

## Gereksinimler
Solidity dilinde smart contract yazın. Kod:
- Temiz ve okunabilir olmalı
- Yorumlar içermeli
- Güvenlik best practices uygulamalı
- Gas optimizasyonu düşünülmeli

"""
        if user_context:
            prompt += f"\n## Ek İstekler\n{user_context}\n"

        return prompt

    def calculate_test_score(self, answers: Dict[str, str], test_type: str = "pre") -> int:
        """
        Test cevaplarını puanla (0-100 arası)

        Args:
            answers: {question_id: answer}
            test_type: "pre" veya "post"

        Returns:
            Puan (0-100)
        """
        questions = self.get_pre_test_questions() if test_type == "pre" else self.get_post_test_questions()

        correct_count = 0
        total_questions = len(questions)

        for i, question in enumerate(questions):
            question_id = f"q{i+1}"
            user_answer = answers.get(question_id, "")

            if question.get("type") == "multiple_choice":
                if user_answer == question.get("correct_answer"):
                    correct_count += 1
            elif question.get("type") == "open_ended":
                # Açık uçlu sorular için kısmi puan
                if len(user_answer.strip()) > 20:  # Minimum 20 karakter
                    correct_count += 0.5  # Kısmi puan

        score = int((correct_count / total_questions) * 100)
        return score

    def get_task_info(self) -> Dict[str, Any]:
        """Görev bilgilerini döndür"""
        return {
            "task_number": self.task_number,
            "title": self.title,
            "difficulty": self.difficulty,
            "description": self.description,
            "max_time_minutes": self.max_time_minutes,
            "pre_test_count": len(self.get_pre_test_questions()),
            "post_test_count": len(self.get_post_test_questions())
        }
