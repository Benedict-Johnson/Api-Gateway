import secrets
from datetime import datetime

import bcrypt
from sqlalchemy.orm import Session

from audit.logger import audit_logger
from database.models.api_keys import APIKey


class APIKeyService:
    """Service layer handling database CRUD, soft revocation, and verification for API Keys."""

    @staticmethod
    def create_key(
        db: Session,
        name: str,
        role: str,
        client: str | None = None,
        expires_at: datetime | None = None,
        actor: str = "admin",
    ) -> tuple[APIKey, str]:
        plaintext_key = secrets.token_urlsafe(32)
        hashed_bytes = bcrypt.hashpw(plaintext_key.encode("utf-8"), bcrypt.gensalt())
        hashed_key = hashed_bytes.decode("utf-8")

        db_key = APIKey(
            name=name,
            hashed_key=hashed_key,
            role=role,
            client=client or name,
            active=True,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
            usage_count=0,
        )
        db.add(db_key)
        db.commit()
        db.refresh(db_key)

        audit_logger.log(
            event=audit_logger.API_KEY_CREATED,
            actor=actor,
            target=f"api_key:{db_key.id}",
            details={"name": name, "role": role, "client": db_key.client},
        )

        return db_key, plaintext_key

    @staticmethod
    def revoke_key(db: Session, key_id: int, actor: str = "admin") -> bool:
        db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not db_key or not db_key.active:
            return False

        db_key.active = False
        db_key.revoked_at = datetime.utcnow()
        db.commit()

        audit_logger.log(
            event=audit_logger.API_KEY_REVOKED,
            actor=actor,
            target=f"api_key:{db_key.id}",
            details={"name": db_key.name, "client": db_key.client},
        )
        return True

    @staticmethod
    def list_keys(db: Session) -> list[APIKey]:
        return db.query(APIKey).all()

    @staticmethod
    def get_key_by_id(db: Session, key_id: int) -> APIKey | None:
        return db.query(APIKey).filter(APIKey.id == key_id).first()

    @staticmethod
    def update_last_used(db: Session, key_id: int) -> APIKey | None:
        db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if db_key:
            db_key.last_used = datetime.utcnow()
            db_key.usage_count = (db_key.usage_count or 0) + 1
            db.commit()
            db.refresh(db_key)
        return db_key

    @staticmethod
    def verify_and_get_key(db: Session, plaintext_key: str) -> APIKey | None:
        if not plaintext_key:
            return None

        active_keys = db.query(APIKey).filter(APIKey.active.is_(True)).all()
        now = datetime.utcnow()

        for key in active_keys:
            if key.expires_at and key.expires_at <= now:
                continue

            try:
                if bcrypt.checkpw(
                    plaintext_key.encode("utf-8"), key.hashed_key.encode("utf-8")
                ):
                    key.last_used = now
                    key.usage_count = (key.usage_count or 0) + 1
                    db.commit()
                    db.refresh(key)
                    return key
            except Exception:
                continue

        return None


api_key_service = APIKeyService()
