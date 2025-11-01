"""
Görev 3: Eğitim Materyali Erişim Kontrolü
Zorluk: Orta
"""

from .base_task import BaseTask
from typing import List, Dict, Any


class Task3Access(BaseTask):
    def __init__(self):
        super().__init__()
        self.task_number = 3
        self.difficulty = "Orta"
        self.title = "Eğitim Materyali Erişim Kontrolü"
        self.description = """Ücretli eğitim içerikleri için akıllı kontrat:

**Gereksinimler:**
- Öğretmen içerik ekleyebilsin (IPFS hash)
- Her içeriğin farklı ücreti olsun
- Öğrenci ödeme yapınca erişim kazansın
- Erişim süresi belirlenebilsin (30 gün, 90 gün, süresiz)
- Öğretmene otomatik ödeme yapılsın
- Komisyon sistemi (%5 platform ücreti)

**Beklenen Fonksiyonlar:**
- `addContent(string memory ipfsHash, uint256 price, uint256 accessDuration)`
- `purchaseAccess(uint256 contentId) payable`
- `hasAccess(address student, uint256 contentId) returns (bool)`
- `withdrawEarnings()`
"""

    def get_pre_test_questions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "q1",
                "question": "IPFS ile blockchain ilişkisi nedir?",
                "type": "multiple_choice",
                "options": [
                    "Aynı teknoloji",
                    "IPFS içerik saklar, blockchain referans tutar",
                    "Blockchain içerik saklar",
                    "Bilmiyorum"
                ],
                "correct_answer": "IPFS içerik saklar, blockchain referans tutar"
            },
            {
                "id": "q2",
                "question": "Eğitim içeriği erişiminde zaman kontrolü neden önemlidir?",
                "type": "multiple_choice",
                "options": [
                    "Abonelik modeli için",
                    "Gas tasarrufu için",
                    "Hız için",
                    "Bilmiyorum"
                ],
                "correct_answer": "Abonelik modeli için"
            },
            {
                "id": "q3",
                "question": "Payable fonksiyonlar nasıl çalışır?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]

    def get_post_test_questions(self) -> List[Dict[str, Any]]:
        pre_questions = self.get_pre_test_questions()
        post_only = [
            {
                "id": "q4",
                "question": "block.timestamp kullanarak süre kontrolü güvenli mi?",
                "type": "multiple_choice",
                "options": [
                    "Tamamen güvenli",
                    "Manipüle edilebilir (±15 saniye)",
                    "Hiç güvenli değil",
                    "Bilmiyorum"
                ],
                "correct_answer": "Manipüle edilebilir (±15 saniye)"
            },
            {
                "id": "q5",
                "question": "Eğitimde mikro ödemeler için blockchain avantajları?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]
        return pre_questions + post_only

    def get_evaluation_criteria(self) -> Dict[str, Dict[str, int]]:
        return {
            "functionality": {
                "compiles": 10,
                "payment_logic": 10,
                "access_control": 10,
                "total": 30
            },
            "security": {
                "reentrancy_guard": 10,
                "overflow_protection": 8,
                "access_validation": 7,
                "total": 25
            },
            "gas_optimization": {
                "storage_efficiency": 10,
                "commission_calc": 8,
                "event_usage": 7,
                "total": 25
            },
            "code_quality": {
                "naming": 7,
                "comments": 6,
                "structure": 7,
                "total": 20
            }
        }
