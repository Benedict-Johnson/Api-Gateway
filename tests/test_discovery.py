from load_balancer.discovery.models import (
    ServiceInstance,
)

from load_balancer.discovery.registry import (
    DiscoveryRegistry,
)

registry = DiscoveryRegistry()

registry.register(

    ServiceInstance(
        service="user-service",
        host="service-a",
        port=8001,
    )
)

registry.register(

    ServiceInstance(
        service="user-service",
        host="service-b",
        port=8002,
    )
)

for instance in registry.get("user-service"):

    print(
        instance.host,
        instance.port,
    )