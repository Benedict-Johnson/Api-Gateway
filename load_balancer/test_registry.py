from load_balancer.registry import ServiceRegistry

registry = ServiceRegistry(
    "load_balancer/services.yaml"
)

print(registry.get("users"))