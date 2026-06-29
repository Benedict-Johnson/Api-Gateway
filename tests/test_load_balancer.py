from load_balancer.manager import LoadBalancerManager
from load_balancer.registry import ServiceRegistry


registry = ServiceRegistry(
    "load_balancer/services.yaml"
)

manager = LoadBalancerManager()

service = registry.get("user-service")

service.instances[0].active_connections = 1
service.instances[1].active_connections = 9

instance = manager.next(service)

print(instance.host)
print(instance.active_connections)