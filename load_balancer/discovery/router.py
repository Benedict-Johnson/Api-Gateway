from fastapi import APIRouter

from load_balancer.discovery.models import ServiceInstance
from load_balancer.discovery.registry import registry
from load_balancer.discovery.heartbeat import (
    heartbeat_manager,
)
router = APIRouter(
    prefix="/discovery",
    tags=["Discovery"]
)




@router.post("/register")
async def register(instance: ServiceInstance):

    registry.register(instance)

    return {
        "message": "Registered successfully",
        "service": instance.service,
        "host": instance.host,
        "port": instance.port
    }


@router.get("/{service}")
async def get_instances(service: str):

    return registry.get(service)


@router.post("/heartbeat")
async def heartbeat(instance: ServiceInstance):

    success = heartbeat_manager.heartbeat(
        instance.service,
        instance.host,
        instance.port,
    )

    if not success:
        return {
            "message": "Service not registered"
        }

    return {
        "message": "Heartbeat received"
    }

@router.delete("/deregister")
async def deregister(instance: ServiceInstance):

    registry.deregister(
        instance.service,
        instance.host,
        instance.port,
    )

    return {
        "message": "Service deregistered",
        "service": instance.service,
        "host": instance.host,
        "port": instance.port,
    }