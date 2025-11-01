"""
Görev 1: Diploma Doğrulama Sistemi
Zorluk: Düşük
"""

from .base_task import BaseTask
from typing import List, Dict, Any


class Task1Diploma(BaseTask):
    def __init__(self):
        super().__init__()
        self.task_number = 1
        self.difficulty = "Düşük"
        self.title = "Diploma Doğrulama Sistemi"
        self.description = """Üniversite için blockchain tabanlı diploma doğrulama sistemi oluşturun:

**Gereksinimler:**
- Sadece üniversite yönetimi diploma ekleyebilsin
- Diploma hash'i ve öğrenci bilgileri saklanacak
- Mezuniyet tarihi kaydedilecek
- Herkes diploma doğrulayabilsin
- İptal edilebilir diploma özelliği

**Beklenen Fonksiyonlar:**
- `addDiploma(address student, bytes32 diplomaHash, string memory studentName, uint256 graduationDate)`
- `verifyDiploma(address student) returns (bool, bytes32, string, uint256)`
- `revokeDiploma(address student)`
- `isDiplomaValid(address student) returns (bool)`
"""

    def get_pre_test_questions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "q1",
                "question": "Blockchain'de diploma saklamanın avantajı nedir?",
                "type": "multiple_choice",
                "options": [
                    "Değiştirilemez kayıt",
                    "Daha ucuz",
                    "Daha hızlı",
                    "Bilmiyorum"
                ],
                "correct_answer": "Değiştirilemez kayıt"
            },
            {
                "id": "q2",
                "question": "Hash fonksiyonu ne işe yarar?",
                "type": "multiple_choice",
                "options": [
                    "Şifreleme yapar",
                    "Benzersiz parmak izi oluşturur",
                    "Veri sıkıştırır",
                    "Bilmiyorum"
                ],
                "correct_answer": "Benzersiz parmak izi oluşturur"
            },
            {
                "id": "q3",
                "question": "onlyOwner modifier'ı eğitim kurumları için neden önemlidir?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]

    def get_post_test_questions(self) -> List[Dict[str, Any]]:
        pre_questions = self.get_pre_test_questions()
        post_only = [
            {
                "id": "q4",
                "question": "Diploma hash'i yerine tüm diploma verisini saklamak ne gibi sorunlar yaratır?",
                "type": "multiple_choice",
                "options": [
                    "Gas maliyeti artar",
                    "Gizlilik sorunu",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q5",
                "question": "Sahte diploma ile mücadelede blockchain nasıl yardımcı olur?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]
        return pre_questions + post_only

    def get_evaluation_criteria(self) -> Dict[str, Dict[str, int]]:
        return {
            "functionality": {
                "compiles": 10,
                "has_add_diploma": 10,
                "has_verify_diploma": 10,
                "total": 30
            },
            "security": {
                "onlyOwner_modifier": 10,
                "input_validation": 8,
                "revoke_function": 7,
                "total": 25
            },
            "gas_optimization": {
                "efficient_storage": 10,
                "minimal_operations": 8,
                "events_usage": 7,
                "total": 25
            },
            "code_quality": {
                "naming_convention": 7,
                "comments": 6,
                "structure": 7,
                "total": 20
            }
        }
