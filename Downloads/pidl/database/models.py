"""
SQLAlchemy Models for PIDL Research System
Tüm araştırma verilerini saklamak için database modelleri
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class CompetencyLevel(enum.Enum):
    """Yetkinlik seviyeleri"""
    NOVICE = "Novice"
    ADVANCED_BEGINNER = "Advanced Beginner"
    COMPETENT = "Competent"
    PROFICIENT = "Proficient"
    EXPERT = "Expert"


class AIType(enum.Enum):
    """AI tipi"""
    SIMILAR = "Similar"
    COMPLEMENTARY = "Complementary"


class TaskStatus(enum.Enum):
    """Görev durumu"""
    STARTED = "started"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


class TestType(enum.Enum):
    """Test tipi"""
    PRE = "pre"
    POST = "post"


class Participant(Base):
    """Katılımcı bilgileri"""
    __tablename__ = 'participants'

    uuid = Column(String(36), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Demografik bilgiler
    age = Column(Integer)
    gender = Column(String(50))
    education = Column(String(100))
    work_field = Column(String(100))

    # Yetkinlik skorları
    technical_score = Column(Integer)  # 0-300
    pedagogical_score = Column(Integer)  # 0-300
    competency_level = Column(SQLEnum(CompetencyLevel))

    # Onam ve tamamlanma durumu
    consent_given = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    total_duration_minutes = Column(Integer)

    # İlişkiler
    task_sessions = relationship("TaskSession", back_populates="participant", cascade="all, delete-orphan")
    final_evaluation = relationship("FinalEvaluation", back_populates="participant", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Participant {self.uuid} - {self.competency_level}>"


class TaskSession(Base):
    """Görev oturumu - Her görev için bir kayıt"""
    __tablename__ = 'task_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    participant_uuid = Column(String(36), ForeignKey('participants.uuid'))

    task_number = Column(Integer)  # 1-6
    assigned_ai_type = Column(SQLEnum(AIType))
    assigned_persona = Column(String(100))

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.STARTED)

    # İlişkiler
    participant = relationship("Participant", back_populates="task_sessions")
    pre_post_tests = relationship("PrePostTest", back_populates="task_session", cascade="all, delete-orphan")
    generated_codes = relationship("GeneratedCode", back_populates="task_session", cascade="all, delete-orphan")
    nasa_tlx = relationship("NASATLXResponse", back_populates="task_session", uselist=False, cascade="all, delete-orphan")
    ai_evaluation = relationship("AICodeEvaluation", back_populates="task_session", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TaskSession {self.id} - Task {self.task_number} - {self.assigned_ai_type}>"


class PrePostTest(Base):
    """Pre-test ve Post-test cevapları"""
    __tablename__ = 'pre_post_tests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_session_id = Column(Integer, ForeignKey('task_sessions.id'))

    test_type = Column(SQLEnum(TestType))
    q1_answer = Column(String(200))
    q2_answer = Column(String(200))
    q3_answer = Column(Text)
    q4_answer = Column(String(200), nullable=True)  # Post only
    q5_answer = Column(Text, nullable=True)  # Post only

    score = Column(Integer)  # 0-100
    completed_at = Column(DateTime, default=datetime.utcnow)

    # İlişki
    task_session = relationship("TaskSession", back_populates="pre_post_tests")

    def __repr__(self):
        return f"<PrePostTest {self.id} - {self.test_type} - Score: {self.score}>"


class GeneratedCode(Base):
    """AI tarafından üretilen kodlar"""
    __tablename__ = 'generated_codes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_session_id = Column(Integer, ForeignKey('task_sessions.id'))

    code_text = Column(Text)
    language = Column(String(50))  # Solidity, Python
    prompt_used = Column(Text)
    ai_persona = Column(String(100))
    generation_time_seconds = Column(Float)

    # Otomatik değerlendirme skorları
    functionality_score = Column(Integer, nullable=True)  # 0-30
    security_score = Column(Integer, nullable=True)  # 0-25
    gas_optimization_score = Column(Integer, nullable=True)  # 0-25
    code_quality_score = Column(Integer, nullable=True)  # 0-20
    total_score = Column(Integer, nullable=True)  # 0-100

    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişki
    task_session = relationship("TaskSession", back_populates="generated_codes")

    def __repr__(self):
        return f"<GeneratedCode {self.id} - {self.language} - Score: {self.total_score}>"


class NASATLXResponse(Base):
    """NASA-TLX Bilişsel Yük Ölçeği"""
    __tablename__ = 'nasa_tlx_responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_session_id = Column(Integer, ForeignKey('task_sessions.id'))

    mental_demand = Column(Integer)  # 1-10
    physical_demand = Column(Integer)  # 1-10
    temporal_demand = Column(Integer)  # 1-10
    performance = Column(Integer)  # 1-10
    effort = Column(Integer)  # 1-10
    frustration = Column(Integer)  # 1-10

    total_cognitive_load = Column(Integer)  # 6-60
    completed_at = Column(DateTime, default=datetime.utcnow)

    # İlişki
    task_session = relationship("TaskSession", back_populates="nasa_tlx")

    def __repr__(self):
        return f"<NASATLXResponse {self.id} - Total Load: {self.total_cognitive_load}>"


class AICodeEvaluation(Base):
    """Katılımcının AI kodunu değerlendirmesi"""
    __tablename__ = 'ai_code_evaluations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_session_id = Column(Integer, ForeignKey('task_sessions.id'))

    code_understandability = Column(Integer)  # 1-10
    explanation_quality = Column(Integer)  # 1-10
    educational_value = Column(Integer)  # 1-10
    perceived_code_quality = Column(Integer)  # 1-10
    perceived_security = Column(Integer)  # 1-10

    best_aspect = Column(Text)
    improvement_needed = Column(Text)

    completed_at = Column(DateTime, default=datetime.utcnow)

    # İlişki
    task_session = relationship("TaskSession", back_populates="ai_evaluation")

    def __repr__(self):
        return f"<AICodeEvaluation {self.id}>"


class FinalEvaluation(Base):
    """Final değerlendirme anketi"""
    __tablename__ = 'final_evaluations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    participant_uuid = Column(String(36), ForeignKey('participants.uuid'))

    # AI Karşılaştırması
    preferred_ai = Column(String(50))  # Similar/Complementary/Both
    preferred_ai_reason = Column(Text)
    learning_better_ai = Column(String(50))  # Similar/Complementary/Equal
    speed_better_ai = Column(String(50))  # Similar/Complementary/Equal

    # Likert ölçekli sorular (1-5)
    comfort_similar = Column(Integer)
    development_complementary = Column(Integer)
    clarity_similar = Column(Integer)
    quality_complementary = Column(Integer)
    hybrid_ideal = Column(Integer)

    # Genel deneyim
    blockchain_view_change = Column(String(50))
    ai_learning_rating = Column(Integer)  # 1-10
    would_recommend = Column(String(50))

    # Açık uçlu sorular
    hardest_task = Column(Text)
    ai_potential = Column(Text)
    suggestions = Column(Text)
    blockchain_education_view = Column(Text)

    completed_at = Column(DateTime, default=datetime.utcnow)

    # İlişki
    participant = relationship("Participant", back_populates="final_evaluation")

    def __repr__(self):
        return f"<FinalEvaluation {self.id} - Preferred: {self.preferred_ai}>"
