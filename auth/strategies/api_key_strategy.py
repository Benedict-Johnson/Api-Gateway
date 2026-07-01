from fastapi import Request

from audit.logger import audit_logger
from auth.api_key_service import api_key_service
from auth.base import AuthenticationStrategy
from database.database import get_db_session


class APIKeyStrategy(AuthenticationStrategy):

    async def authenticate(self, request: Request):
        key = request.headers.get("X-API-Key")
        if not key:
            return None

        with get_db_session() as db:
            api_key = api_key_service.verify_and_get_key(db, key)

            if api_key is None:
                audit_logger.log(
                    event=audit_logger.AUTH_FAILURE,
                    actor="unknown",
                    target=f"path:{request.url.path}",
                    details={"reason": "Invalid or revoked API Key"},
                )
                return None

            audit_logger.log(
                event=audit_logger.AUTH_SUCCESS,
                actor=f"client:{api_key.client}",
                target=f"path:{request.url.path}",
                details={"api_key_id": api_key.id, "role": api_key.role},
            )

            return {
                "client": api_key.client,
                "role": api_key.role,
            }
