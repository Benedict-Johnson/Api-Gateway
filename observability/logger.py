import logging
import sys

from observability.context import get_log_context


class StructuredFormatter(logging.Formatter):
    def format(self, record):
        ctx = get_log_context()

        # Build the context string
        # e.g., [req_123] [user-service] [cache=HIT] [retries=0] [circuit=CLOSED]
        ctx_parts = []
        if ctx["req_id"] != "-":
            ctx_parts.append(f"[{ctx['req_id']}]")
        if ctx["service"] != "-":
            ctx_parts.append(f"[{ctx['service']}]")
        if ctx["cache"] != "-":
            ctx_parts.append(f"[cache={ctx['cache']}]")
        if ctx["retries"] > 0:
            ctx_parts.append(f"[retries={ctx['retries']}]")
        if ctx["circuit"] not in ("-", "CLOSED"):
            ctx_parts.append(f"[circuit={ctx['circuit']}]")

        ctx_str = " ".join(ctx_parts)
        if ctx_str:
            ctx_str += " "

        timestamp = self.formatTime(record, self.datefmt)

        return f"[{timestamp}] {record.levelname} {ctx_str}{record.getMessage()}"


def get_logger(name="gateway"):
    from config.settings import settings

    logger = logging.getLogger(name)

    if not logger.handlers:
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    return logger


logger = get_logger()
