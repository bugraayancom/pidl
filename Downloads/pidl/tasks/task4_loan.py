"""
Görev 4: Öğrenci Kredisi Havuzu
Zorluk: Orta-Yüksek
"""

from .base_task import BaseTask
from typing import List, Dict, Any


class Task4Loan(BaseTask):
    def __init__(self):
        super().__init__()
        self.task_number = 4
        self.difficulty = "Orta-Yüksek"
        self.title = "Öğrenci Kredisi Havuzu"
        self.description = """Merkezi olmayan öğrenci kredisi havuzu:

**Gereksinimler:**
- Yatırımcılar fon sağlasın
- Öğrenciler kredi başvurusu yapsın
- Öğrenci bilgileri: Bölüm, dönem, not ortalaması
- Otomatik risk skorlaması
- Geri ödeme takibi
- Temerrüt durumu yönetimi
- Yatırımcılara orantılı gelir dağıtımı

**Beklenen Fonksiyonlar:**
- `deposit() payable` - Yatırımcı fon ekler
- `requestLoan(uint256 amount, string memory department, uint8 semester, uint8 gpa)`
- `approveLoan(address student)`
- `repayLoan() payable`
- `calculateRiskScore(address student) returns (uint8)`
"""

    def get_pre_test_questions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "q1",
                "question": "DeFi lending protokollerinin eğitimdeki potansiyeli nedir?",
                "type": "multiple_choice",
                "options": [
                    "Öğrenciye erişim kolaylığı",
                    "Şeffaf kredi sistemi",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q2",
                "question": "Collateral (teminat) olmadan kredi vermenin riskleri?",
                "type": "multiple_choice",
                "options": [
                    "Geri ödememe riski",
                    "Sybil attack riski",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q3",
                "question": "Havuz bazlı kredi sistemi nasıl çalışır?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]

    def get_post_test_questions(self) -> List[Dict[str, Any]]:
        pre_questions = self.get_pre_test_questions()
        post_only = [
            {
                "id": "q4",
                "question": "Öğrenci kredilerinde oracle kullanımı ne sağlar?",
                "type": "multiple_choice",
                "options": [
                    "Not ortalaması verisi",
                    "Mezuniyet durumu",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q5",
                "question": "Eğitimde reputation-based lending nasıl işler?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]
        return pre_questions + post_only

    def get_evaluation_criteria(self) -> Dict[str, Dict[str, int]]:
        return {
            "functionality": {
                "compiles": 10,
                "deposit_withdraw": 10,
                "loan_logic": 10,
                "total": 30
            },
            "security": {
                "reentrancy_guard": 10,
                "access_control": 8,
                "risk_validation": 7,
                "total": 25
            },
            "gas_optimization": {
                "storage": 10,
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
