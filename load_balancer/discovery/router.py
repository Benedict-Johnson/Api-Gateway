from fastapi import APIRouter

from audit.logger import audit_logger
from load_balancer.discovery.heartbeat import (
    heartbeat_manager,
)
from load_balancer.discovery.models import ServiceInstance
from load_balancer.discovery.registry import registry

router = APIRouter(prefix="/discovery", tags=["Service Discovery"])


@router.post(
    "/register",
    summary="Register Service Instance",
    description="Registers a new microservice backend instance into the dynamic service discovery registry. Once registered, the load balancer will immediately begin routing traffic to this host and port.",
    responses={
        200: {
            "description": "Instance successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Registered successfully",
                        "service": "user-service",
                        "host": "service-a",
                        "port": 8001,
                    }
                }
            },
        }
    },
)
async def register(instance: ServiceInstance):

    registry.register(instance)

    audit_logger.log(
        event=audit_logger.SERVICE_REGISTERED,
        actor="service_discovery",
        target=f"service:{instance.service}",
        details={"host": instance.host, "port": instance.port},
    )

    return {
        "message": "Registered successfully",
        "service": instance.service,
        "host": instance.host,
        "port": instance.port,
    }


@router.get(
    "/{service}",
    summary="List Service Instances",
    description="Retrieves all currently registered and active backend instances for the specified service name.",
    responses={
        200: {
            "description": "List of active service instances",
            "content": {
                "application/json": {
                    "example": [
                        {"service": "user-service", "host": "service-a", "port": 8001}
                    ]
                }
            },
        }
    },
)
async def get_instances(service: str):

    return registry.get(service)


@router.post(
    "/heartbeat",
    summary="Send Instance Heartbeat",
    description="Renews the lease of a registered service instance. If heartbeats stop arriving before the configured cleanup threshold, the instance is automatically evicted from load balancer rotation.",
    responses={
        200: {
            "description": "Heartbeat processed",
            "content": {
                "application/json": {"example": {"message": "Heartbeat received"}}
            },
        }
    },
)
async def heartbeat(instance: ServiceInstance):

    success = heartbeat_manager.heartbeat(
        instance.service,
        instance.host,
        instance.port,
    )

    if not success:
        return {"message": "Service not registered"}

    return {"message": "Heartbeat received"}


@router.delete(
    "/deregister",
    summary="Deregister Service Instance",
    description="Gracefully removes a service instance from the discovery registry, immediately stopping new traffic routing to this destination.",
    responses={
        200: {
            "description": "Instance successfully deregistered",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Service deregistered",
                        "service": "user-service",
                        "host": "service-a",
                        "port": 8001,
                    }
                }
            },
        }
    },
)
async def deregister(instance: ServiceInstance):

    registry.deregister(
        instance.service,
        instance.host,
        instance.port,
    )

    audit_logger.log(
        event=audit_logger.SERVICE_DEREGISTERED,
        actor="service_discovery",
        target=f"service:{instance.service}",
        details={"host": instance.host, "port": instance.port},
    )

    return {
        "message": "Service deregistered",
        "service": instance.service,
        "host": instance.host,
        "port": instance.port,
    }
