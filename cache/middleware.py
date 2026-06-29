from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from cache.manager import cache_manager
from observability.logger import logger
from observability.metrics import GATEWAY_CACHE_HITS, GATEWAY_CACHE_MISSES
from observability.context import cache_status_var


class CacheMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(
    self,
    request: Request,
    call_next,
):

    # Handle write requests first
        if request.method in [
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]:

            response = await call_next(request)

            if response.status_code < 400:
                await cache_manager.invalidate(request)

            return response

        config = cache_manager.config

        if (
            not config.enabled
            or request.method not in config.cacheable_methods
            or not config.routes.get(request.url.path, False)
        ):
            return await call_next(request)

        cached = await cache_manager.get(request)

        logger.debug(f"Cache key: {request.method}:{request.url.path}, Hit: {cached is not None}")

        if cached:
            GATEWAY_CACHE_HITS.inc()
            cache_status_var.set("HIT")
            return Response(
                content=cached,
                media_type="application/json",
                headers={
                    "X-Cache": "HIT"
                }
            )

        response = await call_next(request)

        if response.status_code == 200:

            body = b""

            async for chunk in response.body_iterator:
                body += chunk
            
            logger.debug("Writing response to Redis...")
            await cache_manager.set(
                request,
                body,
            )
            key = f"{request.method}:{request.url.path}"

            exists = await cache_manager.get(request)

            logger.debug(f"After write check: {exists is not None}")
            logger.info(f"Cached response for {key}")

            GATEWAY_CACHE_MISSES.inc()
            cache_status_var.set("MISS")
            
            return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
                headers={
                    **dict(response.headers),
                    "X-Cache": "MISS",
                },
            )

        return response