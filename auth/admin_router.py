from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from audit.logger import audit_logger
from auth.api_key_service import api_key_service
from database.database import get_db

router = APIRouter(prefix="/admin/api-keys", tags=["Administration"])


class CreateAPIKeyRequest(BaseModel):
    name: str
    role: str
    client: str | None = None
    expires_at: datetime | None = None


class APIKeyResponse(BaseModel):
    id: int
    name: str
    role: str
    client: str | None
    active: bool
    created_at: datetime
    last_used: datetime | None
    revoked_at: datetime | None
    usage_count: int

    model_config = ConfigDict(from_attributes=True)


class CreateAPIKeyResponse(APIKeyResponse):
    api_key: str


def get_current_admin(request: Request):
    user = getattr(request.state, "user", None)
    if not user or user.get("role") != "admin":
        actor = f"client:{user.get('client')}" if user else "unauthenticated"
        audit_logger.log(
            event=audit_logger.AUTH_FAILURE,
            actor=actor,
            target=f"admin_path:{request.url.path}",
            details={"reason": "Admin role required"},
        )
        raise HTTPException(status_code=403, detail="Forbidden: Admin role required")

    audit_logger.log(
        event=audit_logger.ADMIN_ACCESS,
        actor=f"admin:{user.get('client')}",
        target=f"admin_path:{request.url.path}",
        details={"method": request.method},
    )
    return user


@router.get(
    "",
    response_model=list[APIKeyResponse],
    summary="List API Keys",
    description="Retrieves a list of all API keys (active and soft-revoked) from the database, including usage statistics and revocation timestamps. Plaintext keys are never returned.",
    responses={
        200: {"description": "List of API keys"},
        401: {"description": "Unauthorized - Missing or invalid admin credentials"},
        403: {
            "description": "Forbidden - Admin role required",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden: Admin role required"}
                }
            },
        },
    },
)
async def list_api_keys(
    db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)
):
    return api_key_service.list_keys(db)


@router.post(
    "",
    response_model=CreateAPIKeyResponse,
    summary="Create API Key",
    description="Generates and stores a new database-backed API key hashed with bcrypt. Returns the plaintext secret string only once upon creation.",
    responses={
        200: {"description": "Created API Key with plaintext secret"},
        401: {"description": "Unauthorized - Missing or invalid admin credentials"},
        403: {
            "description": "Forbidden - Admin role required",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden: Admin role required"}
                }
            },
        },
    },
)
async def create_api_key(
    payload: CreateAPIKeyRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    actor = f"admin:{admin.get('client')}"
    db_key, plaintext_key = api_key_service.create_key(
        db=db,
        name=payload.name,
        role=payload.role,
        client=payload.client,
        expires_at=payload.expires_at,
        actor=actor,
    )

    response_dict = {
        "id": db_key.id,
        "name": db_key.name,
        "role": db_key.role,
        "client": db_key.client,
        "active": db_key.active,
        "created_at": db_key.created_at,
        "last_used": db_key.last_used,
        "revoked_at": db_key.revoked_at,
        "usage_count": db_key.usage_count or 0,
        "api_key": plaintext_key,
    }
    return response_dict


@router.delete(
    "/{key_id}",
    summary="Revoke API Key",
    description="Soft-deletes an API key by setting its status to inactive and recording the revocation timestamp. Preserves the record for audit history.",
    responses={
        200: {
            "description": "API key revoked",
            "content": {
                "application/json": {
                    "example": {"message": "API key revoked successfully"}
                }
            },
        },
        401: {"description": "Unauthorized - Missing or invalid admin credentials"},
        403: {
            "description": "Forbidden - Admin role required",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden: Admin role required"}
                }
            },
        },
        404: {
            "description": "API key not found or already revoked",
            "content": {
                "application/json": {
                    "example": {"detail": "API key not found or already revoked"}
                }
            },
        },
    },
)
async def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    actor = f"admin:{admin.get('client')}"
    success = api_key_service.revoke_key(db=db, key_id=key_id, actor=actor)
    if not success:
        raise HTTPException(
            status_code=404, detail="API key not found or already revoked"
        )
    return {"message": "API key revoked successfully"}
