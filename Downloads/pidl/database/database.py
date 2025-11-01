"""
Database connection and session management
SQLite veritabanı bağlantısı ve session yönetimi
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'research_data.db')
DATABASE_URL = f'sqlite:///{DB_PATH}'

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # SQL loglarını görmek için True yapın
    connect_args={"check_same_thread": False}  # SQLite için gerekli
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Thread-safe session
SessionScoped = scoped_session(SessionLocal)


def init_db():
    """
    Veritabanını başlat - tüm tabloları oluştur
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at: {DB_PATH}")


def get_session():
    """
    Yeni bir database session döndür

    Kullanım:
        session = get_session()
        try:
            # Database işlemleri
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    """
    return SessionLocal()


def drop_all_tables():
    """
    UYARI: Tüm tabloları sil (sadece development için)
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All tables dropped!")


def reset_database():
    """
    Veritabanını sıfırla (drop + create)
    """
    drop_all_tables()
    init_db()
    print("🔄 Database reset complete!")


# Context manager for sessions
class DatabaseSession:
    """
    Context manager for database sessions

    Kullanım:
        with DatabaseSession() as session:
            participant = Participant(uuid="...")
            session.add(participant)
            session.commit()
    """

    def __enter__(self):
        self.session = get_session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        self.session.close()


if __name__ == "__main__":
    # Test: Veritabanını başlat
    init_db()

    # Test: Tablo sayısını göster
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n📊 Created {len(tables)} tables:")
    for table in tables:
        print(f"   - {table}")
