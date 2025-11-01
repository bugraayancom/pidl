"""
Data Logger - Veritabanına veri kaydetme modülü
Tüm araştırma verilerini SQLite veritabanına kaydeder
"""

import sys
sys.path.insert(0, '.')

from database.database import DatabaseSession
from database.models import (
    Participant, TaskSession, PrePostTest, GeneratedCode,
    NASATLXResponse, AICodeEvaluation, FinalEvaluation,
    CompetencyLevel, AIType, TaskStatus, TestType
)
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class DataLogger:
    """Veritabanına veri kaydetme sınıfı"""

    @staticmethod
    def create_participant(
        age: int,
        gender: str,
        education: str,
        work_field: str,
        technical_score: int,
        pedagogical_score: int,
        competency_level: str
    ) -> str:
        """
        Yeni katılımcı oluştur

        Returns:
            UUID string
        """
        participant_uuid = str(uuid.uuid4())

        # Competency level enum'a çevir
        level_map = {
            "Novice": CompetencyLevel.NOVICE,
            "Advanced Beginner": CompetencyLevel.ADVANCED_BEGINNER,
            "Competent": CompetencyLevel.COMPETENT,
            "Proficient": CompetencyLevel.PROFICIENT,
            "Expert": CompetencyLevel.EXPERT
        }

        with DatabaseSession() as session:
            participant = Participant(
                uuid=participant_uuid,
                age=age,
                gender=gender,
                education=education,
                work_field=work_field,
                technical_score=technical_score,
                pedagogical_score=pedagogical_score,
                competency_level=level_map.get(competency_level, CompetencyLevel.NOVICE),
                consent_given=True,
                completed=False
            )
            session.add(participant)
            session.commit()

        return participant_uuid

    @staticmethod
    def start_task_session(
        participant_uuid: str,
        task_number: int,
        assigned_ai_type: str,
        assigned_persona: str
    ) -> int:
        """
        Görev oturumu başlat

        Returns:
            Task session ID
        """
        ai_type_map = {
            "Similar": AIType.SIMILAR,
            "Complementary": AIType.COMPLEMENTARY
        }

        with DatabaseSession() as session:
            task_session = TaskSession(
                participant_uuid=participant_uuid,
                task_number=task_number,
                assigned_ai_type=ai_type_map.get(assigned_ai_type, AIType.SIMILAR),
                assigned_persona=assigned_persona,
                status=TaskStatus.STARTED
            )
            session.add(task_session)
            session.commit()
            task_session_id = task_session.id

        return task_session_id

    @staticmethod
    def complete_task_session(task_session_id: int, duration_minutes: int):
        """Görev oturumunu tamamla"""
        with DatabaseSession() as session:
            task_session = session.query(TaskSession).filter_by(id=task_session_id).first()
            if task_session:
                task_session.completed_at = datetime.utcnow()
                task_session.duration_minutes = duration_minutes
                task_session.status = TaskStatus.COMPLETED
                session.commit()

    @staticmethod
    def save_pre_post_test(
        task_session_id: int,
        test_type: str,
        answers: Dict[str, str],
        score: int
    ):
        """Pre-test veya Post-test kaydet"""
        test_type_map = {
            "pre": TestType.PRE,
            "post": TestType.POST
        }

        with DatabaseSession() as session:
            test = PrePostTest(
                task_session_id=task_session_id,
                test_type=test_type_map.get(test_type, TestType.PRE),
                q1_answer=answers.get("q1", ""),
                q2_answer=answers.get("q2", ""),
                q3_answer=answers.get("q3", ""),
                q4_answer=answers.get("q4", ""),
                q5_answer=answers.get("q5", ""),
                score=score
            )
            session.add(test)
            session.commit()

    @staticmethod
    def save_generated_code(
        task_session_id: int,
        code_text: str,
        language: str,
        prompt_used: str,
        ai_persona: str,
        generation_time_seconds: float,
        scores: Optional[Dict[str, int]] = None
    ) -> int:
        """Üretilen kodu kaydet"""
        with DatabaseSession() as session:
            generated_code = GeneratedCode(
                task_session_id=task_session_id,
                code_text=code_text,
                language=language,
                prompt_used=prompt_used,
                ai_persona=ai_persona,
                generation_time_seconds=generation_time_seconds
            )

            if scores:
                generated_code.functionality_score = scores.get("functionality", 0)
                generated_code.security_score = scores.get("security", 0)
                generated_code.gas_optimization_score = scores.get("gas_optimization", 0)
                generated_code.code_quality_score = scores.get("code_quality", 0)
                generated_code.total_score = scores.get("total", 0)

            session.add(generated_code)
            session.commit()
            code_id = generated_code.id

        return code_id

    @staticmethod
    def save_nasa_tlx(task_session_id: int, responses: Dict[str, int]):
        """NASA-TLX bilişsel yük verisi kaydet"""
        with DatabaseSession() as session:
            nasa_tlx = NASATLXResponse(
                task_session_id=task_session_id,
                mental_demand=responses.get("mental_demand", 5),
                physical_demand=responses.get("physical_demand", 5),
                temporal_demand=responses.get("temporal_demand", 5),
                performance=responses.get("performance", 5),
                effort=responses.get("effort", 5),
                frustration=responses.get("frustration", 5),
                total_cognitive_load=responses.get("total_cognitive_load", 30)
            )
            session.add(nasa_tlx)
            session.commit()

    @staticmethod
    def save_ai_evaluation(task_session_id: int, responses: Dict[str, Any]):
        """AI kod değerlendirmesi kaydet"""
        with DatabaseSession() as session:
            ai_eval = AICodeEvaluation(
                task_session_id=task_session_id,
                code_understandability=responses.get("code_understandability", 5),
                explanation_quality=responses.get("explanation_quality", 5),
                educational_value=responses.get("educational_value", 5),
                perceived_code_quality=responses.get("perceived_code_quality", 5),
                perceived_security=responses.get("perceived_security", 5),
                best_aspect=responses.get("best_aspect", ""),
                improvement_needed=responses.get("improvement_needed", "")
            )
            session.add(ai_eval)
            session.commit()

    @staticmethod
    def save_final_evaluation(participant_uuid: str, responses: Dict[str, Any]):
        """Final değerlendirme anketi kaydet"""
        with DatabaseSession() as session:
            final_eval = FinalEvaluation(
                participant_uuid=participant_uuid,
                preferred_ai=responses.get("preferred_ai", ""),
                preferred_ai_reason=responses.get("preferred_ai_reason", ""),
                learning_better_ai=responses.get("learning_better_ai", ""),
                speed_better_ai=responses.get("speed_better_ai", ""),
                comfort_similar=responses.get("comfort_similar", 3),
                development_complementary=responses.get("development_complementary", 3),
                clarity_similar=responses.get("clarity_similar", 3),
                quality_complementary=responses.get("quality_complementary", 3),
                hybrid_ideal=responses.get("hybrid_ideal", 3),
                blockchain_view_change=responses.get("blockchain_view_change", ""),
                ai_learning_rating=responses.get("ai_learning_rating", 5),
                would_recommend=responses.get("would_recommend", ""),
                hardest_task=responses.get("hardest_task", ""),
                ai_potential=responses.get("ai_potential", ""),
                suggestions=responses.get("suggestions", ""),
                blockchain_education_view=responses.get("blockchain_education_view", "")
            )
            session.add(final_eval)
            session.commit()

    @staticmethod
    def mark_participant_completed(participant_uuid: str, total_duration_minutes: int):
        """Katılımcıyı tamamlanmış olarak işaretle"""
        with DatabaseSession() as session:
            participant = session.query(Participant).filter_by(uuid=participant_uuid).first()
            if participant:
                participant.completed = True
                participant.total_duration_minutes = total_duration_minutes
                session.commit()

    @staticmethod
    def get_participant_progress(participant_uuid: str) -> Dict[str, Any]:
        """Katılımcının ilerleme durumunu getir"""
        with DatabaseSession() as session:
            participant = session.query(Participant).filter_by(uuid=participant_uuid).first()

            if not participant:
                return {"exists": False}

            completed_tasks = session.query(TaskSession).filter_by(
                participant_uuid=participant_uuid,
                status=TaskStatus.COMPLETED
            ).count()

            return {
                "exists": True,
                "completed": participant.completed,
                "competency_level": participant.competency_level.value,
                "completed_tasks": completed_tasks,
                "total_tasks": 6
            }
