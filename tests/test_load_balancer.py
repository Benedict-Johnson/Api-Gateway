from load_balancer.manager import LoadBalancerManager
from load_balancer.registry import ServiceRegistry

registry = ServiceRegistry("load_balancer/services.yaml")

manager = LoadBalancerManager()

service = registry.get("user-service")

service.instances[0].active_connections = 1
service.instances[1].active_connections = 9


def test_load_balancer():
    reg = ServiceRegistry("load_balancer/services.yaml")
    mgr = LoadBalancerManager()
    srv = reg.get("user-service")
    srv.instances[0].active_connections = 1
    srv.instances[1].active_connections = 9
    inst = mgr.next(srv)
    assert inst.host == srv.instances[0].host


if __name__ == "__main__":
    instance = manager.next(service)

    print(instance.host)
    print(instance.active_connections)
