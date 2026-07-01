from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


from contextlib import contextmanager


def init_db():
    Base.metadata.create_all(bind=engine)

    with get_db_session() as db:
        from datetime import datetime

        import bcrypt

        from database.models.api_keys import APIKey

        if not db.query(APIKey).filter_by(name="default-service-key").first():
            hashed_bytes = bcrypt.hashpw(
                settings.API_KEY_SECRET.encode("utf-8"), bcrypt.gensalt()
            )
            hashed_key = hashed_bytes.decode("utf-8")
            default_key = APIKey(
                name="default-service-key",
                hashed_key=hashed_key,
                role="service",
                client="internal-service",
                active=True,
                created_at=datetime.utcnow(),
                usage_count=0,
            )
            db.add(default_key)
            db.commit()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()