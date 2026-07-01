import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure we connect to PostgreSQL for testing (use localhost if running outside docker)
if not os.path.exists("/.dockerenv"):
    if "DATABASE_URL" in os.environ:
        os.environ["DATABASE_URL"] = os.environ["DATABASE_URL"].replace(
            "@postgres:5432", "@localhost:5432"
        )
    else:
        os.environ["DATABASE_URL"] = (
            "postgresql://postgres:postgres@localhost:5432/gateway"
        )

from auth.api_key_service import api_key_service
from database.database import engine, get_db_session, init_db
from gateway.app import app

# Initialize DB schema in PostgreSQL
init_db()

SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_database_api_key_lifecycle():
    """Test APIKeyService CRUD, bcrypt verification, soft revocation, and usage statistics in PostgreSQL."""
    with get_db_session() as db:
        # 1. Create Key
        db_key, plaintext_key = api_key_service.create_key(
            db=db,
            name="test-lifecycle-key",
            role="service",
            client="test-lifecycle-client",
            actor="test_runner",
        )
        key_id = db_key.id
        assert db_key.active is True
        assert db_key.usage_count == 0
        assert db_key.revoked_at is None
        assert db_key.hashed_key != plaintext_key

        # 2. Verify Key (Authentication simulation)
        verified_key = api_key_service.verify_and_get_key(db, plaintext_key)
        assert verified_key is not None
        assert verified_key.id == key_id
        assert verified_key.usage_count == 1
        assert verified_key.last_used is not None

        # 3. List Keys
        keys = api_key_service.list_keys(db)
        assert any(k.id == key_id for k in keys)

        # 4. Soft Revoke Key
        success = api_key_service.revoke_key(db, key_id=key_id, actor="test_runner")
        assert success is True

        revoked_key = api_key_service.get_key_by_id(db, key_id)
        assert revoked_key.active is False
        assert revoked_key.revoked_at is not None

        # 5. Verify Revoked Key should fail
        failed_verify = api_key_service.verify_and_get_key(db, plaintext_key)
        assert failed_verify is None


def test_admin_router_rbac_and_crud(client):
    """Test RBAC protection and CRUD endpoints on /admin/api-keys."""
    with get_db_session() as db:
        # Create an admin key and a non-admin dev key
        admin_db_key, admin_plaintext = api_key_service.create_key(
            db=db,
            name="admin-test-key",
            role="admin",
            client="admin-test-client",
        )
        dev_db_key, dev_plaintext = api_key_service.create_key(
            db=db, name="dev-test-key", role="dev", client="dev-test-client"
        )
        admin_id = admin_db_key.id
        dev_id = dev_db_key.id

    # 1. Access without key -> 401 Unauthorized
    resp = client.get("/admin/api-keys")
    assert resp.status_code == 401

    # 2. Access with dev key -> 403 Forbidden
    resp = client.get("/admin/api-keys", headers={"X-API-Key": dev_plaintext})
    assert resp.status_code == 403

    # 3. Access with admin key -> 200 OK
    resp = client.get("/admin/api-keys", headers={"X-API-Key": admin_plaintext})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # 4. Create new key via Admin API -> 200 OK
    payload = {
        "name": "api-created-key",
        "role": "service",
        "client": "api-created-client",
    }
    resp = client.post(
        "/admin/api-keys",
        json=payload,
        headers={"X-API-Key": admin_plaintext},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "api_key" in data
    assert data["name"] == "api-created-key"
    created_id = data["id"]

    # 5. Revoke key via Admin API -> 200 OK
    resp = client.delete(
        f"/admin/api-keys/{created_id}",
        headers={"X-API-Key": admin_plaintext},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "API key revoked successfully"

    # Clean up test keys so they do not slow down subsequent bcrypt authentication checks
    with get_db_session() as db:
        api_key_service.revoke_key(db, key_id=admin_id, actor="test_runner")
        api_key_service.revoke_key(db, key_id=dev_id, actor="test_runner")


def test_security_headers(client):
    """Verify that SecurityHeadersMiddleware injects required headers."""
    resp = client.get("/")
    assert resp.status_code == 200
    headers = resp.headers
    assert "strict-transport-security" in headers
    assert "x-frame-options" in headers
    assert "x-content-type-options" in headers
    assert "referrer-policy" in headers
    assert "permissions-policy" in headers
    assert "content-security-policy" in headers


def test_request_validation(client):
    """Verify RequestValidationMiddleware limits and constraints."""
    # 1. Oversized URI (414)
    long_uri = "/" + "a" * 3000
    resp = client.get(long_uri)
    assert resp.status_code == 414
    assert resp.json()["detail"] == "URI Too Long"

    # 2. Oversized Headers (431)
    resp = client.get("/", headers={"X-Large-Header": "a" * 10000})
    assert resp.status_code == 431
    assert resp.json()["detail"] == "Request Header Fields Too Large"

    # 3. Oversized Content-Length (413)
    resp = client.post("/", headers={"Content-Length": "10000000"})
    assert resp.status_code == 413
    assert resp.json()["detail"] == "Payload Too Large"

    # 4. Unsupported Content-Type (415)
    resp = client.post(
        "/", headers={"Content-Type": "application/xml"}, content="<xml></xml>"
    )
    assert resp.status_code == 415
    assert "Unsupported Content-Type" in resp.json()["detail"]

    # 5. Malformed JSON (400)
    resp = client.post(
        "/",
        headers={"Content-Type": "application/json"},
        content='{"bad": "json"',
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Malformed JSON"


def test_audit_logging(caplog):
    """Verify that audit_logger emits standardized structured events."""
    import logging

    from audit.logger import audit_logger

    with caplog.at_level(logging.INFO, logger="audit"):
        audit_logger.log(
            event=audit_logger.AUTH_SUCCESS,
            actor="test_user",
            target="test_target",
            details={"foo": "bar"},
        )

    assert any("AUTH_SUCCESS" in record.message for record in caplog.records)
