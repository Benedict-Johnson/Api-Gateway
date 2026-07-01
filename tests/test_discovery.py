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


def test_discovery_registry():
    reg = DiscoveryRegistry()
    reg.register(ServiceInstance(service="test-service", host="host-a", port=8001))
    reg.register(ServiceInstance(service="test-service", host="host-b", port=8002))
    instances = reg.get("test-service")
    assert len(instances) == 2
    assert instances[0].host == "host-a"
    assert instances[1].host == "host-b"


if __name__ == "__main__":
    for instance in registry.get("user-service"):

        print(
            instance.host,
            instance.port,
        )
