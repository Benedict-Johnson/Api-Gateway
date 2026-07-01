import json

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.request_limits import RequestLimitsLoader


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing URI size, header size, body size, Content-Type, and JSON syntax validation."""

    def __init__(self, app):
        super().__init__(app)
        self.loader = RequestLimitsLoader("config/request_limits.yaml")
        self.config = self.loader.config

    async def dispatch(self, request: Request, call_next):
        # 1. Check URI size
        if len(str(request.url)) > self.config.max_uri_size:
            return JSONResponse(status_code=414, content={"detail": "URI Too Long"})

        # 2. Check Header size
        header_size = sum(len(k) + len(v) for k, v in request.headers.raw)
        if header_size > self.config.max_header_size:
            return JSONResponse(
                status_code=431, content={"detail": "Request Header Fields Too Large"}
            )

        # 3. Check Content-Length header for oversized payload without reading body yet
        content_length_header = request.headers.get("content-length")
        if content_length_header:
            try:
                if int(content_length_header) > self.config.max_body_size:
                    return JSONResponse(
                        status_code=413, content={"detail": "Payload Too Large"}
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400, content={"detail": "Invalid Content-Length header"}
                )

        # 4. For methods with payloads, check Content-Type and validate body
        if request.method in ["POST", "PUT", "PATCH"]:
            raw_ct = request.headers.get("content-type", "")
            content_type = raw_ct.split(";")[0].strip().lower() if raw_ct else ""

            if content_type and content_type not in self.config.allowed_content_types:
                return JSONResponse(
                    status_code=415,
                    content={"detail": f"Unsupported Content-Type: {content_type}"},
                )

            # Read body to check actual size and JSON syntax
            try:
                body = await request.body()
            except Exception:
                return JSONResponse(
                    status_code=400, content={"detail": "Could not read request body"}
                )

            if len(body) > self.config.max_body_size:
                return JSONResponse(
                    status_code=413, content={"detail": "Payload Too Large"}
                )

            if content_type == "application/json" and body:
                try:
                    json.loads(body.decode("utf-8"))
                except Exception:
                    return JSONResponse(
                        status_code=400, content={"detail": "Malformed JSON"}
                    )

        return await call_next(request)
