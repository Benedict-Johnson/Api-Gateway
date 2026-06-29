import time

from load_balancer.discovery.registry import registry


class HeartbeatManager:

    def heartbeat(
        self,
        service: str,
        host: str,
        port: int,
    ):

        instance = registry.get_instance(
            service,
            host,
            port,
        )

        if instance is None:
            return False

        instance.last_seen = time.time()

        return True


heartbeat_manager = HeartbeatManager()