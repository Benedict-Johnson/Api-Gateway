import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from gateway.lifecycle import lifecycle_manager
from observability.context import (
    cache_status_var,
    circuit_state_var,
    request_id_var,
    retry_count_var,
    service_name_var,
)
from observability.logger import logger
from observability.metrics import (
    GATEWAY_4XX_TOTAL,
    GATEWAY_5XX_TOTAL,
    GATEWAY_ACTIVE_REQUESTS,
    GATEWAY_REQUEST_DURATION,
    GATEWAY_REQUEST_SIZE,
    GATEWAY_REQUESTS_TOTAL,
    GATEWAY_RESPONSE_SIZE,
)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if lifecycle_manager.shutting_down:
            return JSONResponse(
                status_code=503, content={"detail": "Gateway is shutting down"}
            )

        start_time = time.time()
        GATEWAY_ACTIVE_REQUESTS.inc()
        await lifecycle_manager.increment_requests()

        # 1. Handle X-Request-ID
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(req_id)

        # Initialize context vars
        service_name_var.set("-")
        cache_status_var.set("-")
        retry_count_var.set(0)
        circuit_state_var.set("-")

        # Mutate headers for downstream
        headers = dict(request.scope["headers"])
        headers[b"x-request-id"] = req_id.encode("latin-1")
        request.scope["headers"] = [(k, v) for k, v in headers.items()]

        # Estimate request size (headers + body length if available)
        req_size = sum(len(k) + len(v) for k, v in request.scope["headers"])
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit():
            req_size += int(content_length)
        GATEWAY_REQUEST_SIZE.observe(req_size)

        try:
            response = await call_next(request)
            status_code = response.status_code

            # Estimate response size
            res_size = sum(len(k) + len(v) for k, v in response.headers.raw)
            cl = response.headers.get("content-length")
            if cl and cl.isdigit():
                res_size += int(cl)
            GATEWAY_RESPONSE_SIZE.observe(res_size)

            return response

        except Exception as e:
            status_code = 500
            logger.error(f"Unhandled exception: {str(e)}")
            raise

        finally:
            GATEWAY_ACTIVE_REQUESTS.dec()
            await lifecycle_manager.decrement_requests()
            duration = time.time() - start_time

            # The service_name might be populated by the app router during execution
            service = service_name_var.get()

            GATEWAY_REQUEST_DURATION.labels(
                method=request.method, service=service
            ).observe(duration)

            GATEWAY_REQUESTS_TOTAL.labels(
                method=request.method, service=service, status=str(status_code)
            ).inc()

            if 400 <= status_code < 500:
                GATEWAY_4XX_TOTAL.labels(service=service).inc()
            elif status_code >= 500:
                GATEWAY_5XX_TOTAL.labels(service=service).inc()

            logger.info(
                f"{request.method} {request.url.path} - {status_code} ({duration*1000:.2f}ms)"
            )
