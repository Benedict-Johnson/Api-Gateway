import time
from fastapi import APIRouter
from fastapi.responses import JSONResponse

START_TIME = time.time()

def create_health_router(redis_client, service_registry, circuit_breaker_policy):
    router = APIRouter()

    @router.get("/live")
    async def live():
        return {"status": "UP"}

    @router.get("/ready")
    async def ready():
        # Check Redis connection
        try:
            is_ready = await redis_client.ping()
            if not is_ready:
                return JSONResponse(status_code=503, content={"status": "DOWN", "reason": "Redis ping failed"})
        except Exception:
            return JSONResponse(status_code=503, content={"status": "DOWN", "reason": "Redis connection error"})
            
        # Check Service Registry
        if not service_registry.services:
            return JSONResponse(status_code=503, content={"status": "DOWN", "reason": "Service registry empty"})
            
        return {"status": "UP"}

    @router.get("/health")
    async def health():
        redis_status = "UP"
        try:
            if not await redis_client.ping():
                redis_status = "DOWN"
        except Exception:
            redis_status = "DOWN"

        registered_services = {}
        circuit_breakers = {}

        for service_name, service in service_registry.services.items():
            # If a service has active instances, we consider it UP for this snapshot
            is_up = any(inst for inst in service.instances)
            registered_services[service_name] = "UP" if is_up else "DOWN"
            
            # Fetch Circuit breaker state safely
            breaker = await circuit_breaker_policy.get_breaker(service_name)
            cb_state = await breaker.get_state()
            circuit_breakers[service_name] = cb_state.value

        return {
            "gateway": "UP",
            "redis": redis_status,
            "cache": redis_status,  # Using same Redis cluster for now
            "registered_services": registered_services,
            "circuit_breakers": circuit_breakers,
            "uptime_seconds": int(time.time() - START_TIME)
        }

    return router
