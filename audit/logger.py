import json
import logging
from datetime import datetime
from typing import Any

# Create dedicated audit logger distinct from observability logs
logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[AUDIT] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


class AuditLogger:
    """Generic audit logger interface for recording system security and lifecycle events."""

    AUTH_SUCCESS = "AUTH_SUCCESS"
    AUTH_FAILURE = "AUTH_FAILURE"
    API_KEY_CREATED = "API_KEY_CREATED"
    API_KEY_REVOKED = "API_KEY_REVOKED"
    ADMIN_ACCESS = "ADMIN_ACCESS"
    SERVICE_REGISTERED = "SERVICE_REGISTERED"
    SERVICE_DEREGISTERED = "SERVICE_DEREGISTERED"
    CONFIG_VALIDATION_FAILED = "CONFIG_VALIDATION_FAILED"

    def log(
        self,
        event: str,
        actor: str,
        target: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        if details is None:
            details = {}

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "actor": actor,
            "target": target,
            "details": details,
        }
        logger.info(json.dumps(record))


audit_logger = AuditLogger()
