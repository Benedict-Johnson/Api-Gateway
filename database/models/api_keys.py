from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from database.database import Base


class APIKey(Base):

    __tablename__ = "api_keys"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    hashed_key = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    role = Column(
        String,
        nullable=False,
    )

    client = Column(
        String,
        nullable=True,
    )

    active = Column(
        Boolean,
        default=True,
    )

    expires_at = Column(
        DateTime,
        nullable=True,
    )

    last_used = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    revoked_at = Column(
        DateTime,
        nullable=True,
    )

    usage_count = Column(
        Integer,
        default=0,
    )
