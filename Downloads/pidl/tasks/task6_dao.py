"""
Görev 6: Merkezi Olmayan Üniversite DAO'su
Zorluk: Yüksek
"""

from .base_task import BaseTask
from typing import List, Dict, Any


class Task6DAO(BaseTask):
    def __init__(self):
        super().__init__()
        self.task_number = 6
        self.difficulty = "Yüksek"
        self.title = "Merkezi Olmayan Üniversite DAO'su"
        self.description = """Blockchain tabanlı üniversite yönetim DAO'su:

**Gereksinimler:**
- Öğrenci, öğretmen ve yönetici rolleri
- Müfredat değişikliği önerileri
- Bütçe tahsisi oylamaları
- Öğretmen işe alım oylaması
- Token bazlı oy ağırlığı (öğrenci %40, öğretmen %40, yönetim %20)
- 72 saat oylama süresi
- %30 quorum gerekliliği
- Timelock execution (48 saat)

**Beklenen Fonksiyonlar:**
- `createProposal(string memory description, ProposalType propType)`
- `vote(uint256 proposalId, bool support)`
- `executeProposal(uint256 proposalId)`
- `delegateVote(address delegate)`
- `getProposalState(uint256 proposalId) returns (ProposalState)`
"""

    def get_pre_test_questions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "q1",
                "question": "Eğitim kurumlarında DAO modelinin faydaları?",
                "type": "multiple_choice",
                "options": [
                    "Şeffaf yönetim",
                    "Demokratik karar alma",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q2",
                "question": "Role-based voting eğitimde neden önemli?",
                "type": "multiple_choice",
                "options": [
                    "Farklı perspektifleri dengelemek",
                    "Gas tasarrufu",
                    "Hız için",
                    "Bilmiyorum"
                ],
                "correct_answer": "Farklı perspektifleri dengelemek"
            },
            {
                "id": "q3",
                "question": "Eğitim DAO'sunda timelock neden kritik?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]

    def get_post_test_questions(self) -> List[Dict[str, Any]]:
        pre_questions = self.get_pre_test_questions()
        post_only = [
            {
                "id": "q4",
                "question": "Delegation (temsili oy) eğitim DAO'sunda nasıl işler?",
                "type": "multiple_choice",
                "options": [
                    "Öğrenci temsilcileri sistemi",
                    "Uzman delegeler",
                    "Her ikisi de",
                    "Bilmiyorum"
                ],
                "correct_answer": "Her ikisi de"
            },
            {
                "id": "q5",
                "question": "Eğitim kurumlarında on-chain vs off-chain governance dengesi?",
                "type": "open_ended",
                "placeholder": "Cevabınızı buraya yazın..."
            }
        ]
        return pre_questions + post_only

    def get_evaluation_criteria(self) -> Dict[str, Dict[str, int]]:
        return {
            "functionality": {
                "compiles": 10,
                "proposal_creation": 10,
                "voting_logic": 10,
                "total": 30
            },
            "security": {
                "access_control": 10,
                "timelock": 8,
                "quorum_check": 7,
                "total": 25
            },
            "gas_optimization": {
                "storage": 10,
                "vote_counting": 8,
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
