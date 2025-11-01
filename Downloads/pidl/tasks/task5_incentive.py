"""
Görev 5: Öğretmen Teşvik ve Ödül Sistemi
Zorluk: Yüksek
"""

from .base_task import BaseTask
from typing import List, Dict, Any


class Task5Incentive(BaseTask):
    def __init__(self):
        super().__init__()
        self.task_number = 5
        self.difficulty = "Yüksek"
        self.title = "Öğretmen Teşvik ve Ödül Sistemi"
        self.description = """Kaliteli eğitim içeriği üreten öğretmenler için teşvik sistemi:

**Gereksinimler:**
- Öğretmen içerik yüklesin (kurs, video, materyal)
- Öğrenci oylaması (5 üzerinden puan)
- Öğrenci performansına göre bonus
- Stake edilmiş EDU token ile ağırlıklı oylama
- Aylık ödül havuzu dağıtımı
- En iyi öğretmenlere NFT badge
- Compound rewards sistemi

**Beklenen Fonksiyonlar:**
- `submitContent(string memory contentHash, string memory title)`
- `voteForTeacher(address teacher, uint8 rating, uint256 stakedAmount)`
- `calculateTeacherScore(address teacher) returns (uint256)`
- `distributeMonthlyRewards()`
- `claimRewards()`
"""

    def get_pre_test_questions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "q1",
                "question": "Eğitimde tokenomics nasıl motive edici olabilir?",
                "type": "multiple_choice",
                "options": [
                    "Finansal teşvik",
                    "Şeffaf değerlendirme",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q2",
                "question": "Quadratic voting eğitimde nasıl kullanılır?",
                "type": "multiple_choice",
                "options": [
                    "Adil oylama için",
                    "Whale dominansını önlemek için",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q3",
                "question": "Öğretmen performansının on-chain ölçümü nasıl yapılır?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]

    def get_post_test_questions(self) -> List[Dict[str, Any]]:
        pre_questions = self.get_pre_test_questions()
        post_only = [
            {
                "id": "q4",
                "question": "Sybil-resistant oylama neden önemli?",
                "type": "multiple_choice",
                "options": [
                    "Sahte hesapları önlemek",
                    "Adil değerlendirme",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q5",
                "question": "Eğitimde outcome-based rewards vs activity-based rewards?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]
        return pre_questions + post_only

    def get_evaluation_criteria(self) -> Dict[str, Dict[str, int]]:
        return {
            "functionality": {
                "compiles": 10,
                "voting_system": 10,
                "reward_distribution": 10,
                "total": 30
            },
            "security": {
                "sybil_resistance": 10,
                "overflow_protection": 8,
                "access_control": 7,
                "total": 25
            },
            "gas_optimization": {
                "storage": 10,
                "calculation_efficiency": 8,
                "events": 7,
                "total": 25
            },
            "code_quality": {
                "naming": 7,
                "comments": 6,
                "structure": 7,
                "total": 20
            }
        }
