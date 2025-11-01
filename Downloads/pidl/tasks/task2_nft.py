"""
Görev 2: Öğrenci Başarı NFT Sistemi
Zorluk: Düşük-Orta
"""

from .base_task import BaseTask
from typing import List, Dict, Any


class Task2NFT(BaseTask):
    def __init__(self):
        super().__init__()
        self.task_number = 2
        self.difficulty = "Düşük-Orta"
        self.title = "Öğrenci Başarı NFT Sistemi"
        self.description = """Öğrenci başarılarını NFT olarak ödüllendiren sistem:

**Gereksinimler:**
- Her başarı unique NFT olacak (Matematik Şampiyonu, Proje Ödülü vs.)
- Öğretmen/yönetici mint edebilsin
- NFT'ler transfer edilemesin (soulbound)
- Metadata: Başarı türü, tarih, açıklama
- Başarı kategorileri olsun

**Beklenen Fonksiyonlar:**
- `mintAchievement(address student, string memory category, string memory description)`
- `getStudentAchievements(address student) returns (uint256[] memory)`
- `getAchievementDetails(uint256 tokenId) returns (string, string, uint256)`
"""

    def get_pre_test_questions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "q1",
                "question": "Eğitimde NFT kullanımının amacı nedir?",
                "type": "multiple_choice",
                "options": [
                    "Para kazanmak",
                    "Dijital başarı rozeti vermek",
                    "Öğrenci takibi",
                    "Bilmiyorum"
                ],
                "correct_answer": "Dijital başarı rozeti vermek"
            },
            {
                "id": "q2",
                "question": "Soulbound token ne demektir?",
                "type": "multiple_choice",
                "options": [
                    "Pahalı token",
                    "Transfer edilemeyen token",
                    "Yakılabilen token",
                    "Bilmiyorum"
                ],
                "correct_answer": "Transfer edilemeyen token"
            },
            {
                "id": "q3",
                "question": "Eğitim NFT'lerinde metadata neden önemlidir?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]

    def get_post_test_questions(self) -> List[Dict[str, Any]]:
        pre_questions = self.get_pre_test_questions()
        post_only = [
            {
                "id": "q4",
                "question": "Başarı NFT'lerinin transfer edilememesi neden önemlidir?",
                "type": "multiple_choice",
                "options": [
                    "Kişiye özel başarı olması için",
                    "Gas tasarrufu için",
                    "Daha hızlı işlem için",
                    "Bilmiyorum"
                ],
                "correct_answer": "Kişiye özel başarı olması için"
            },
            {
                "id": "q5",
                "question": "Eğitim kurumları için on-chain vs off-chain metadata farkı?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]
        return pre_questions + post_only

    def get_evaluation_criteria(self) -> Dict[str, Dict[str, int]]:
        return {
            "functionality": {
                "compiles": 10,
                "mint_function": 10,
                "soulbound_logic": 10,
                "total": 30
            },
            "security": {
                "access_control": 10,
                "no_transfer": 10,
                "validation": 5,
                "total": 25
            },
            "gas_optimization": {
                "efficient_storage": 10,
                "batch_operations": 8,
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
