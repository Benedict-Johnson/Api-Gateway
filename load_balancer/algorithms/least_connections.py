from load_balancer.models import Service


class LeastConnectionsBalancer:

    def next(self, service: Service):

        healthy = [
            instance
            for instance in service.instances
            if instance.healthy
        ]

        if not healthy:
            raise RuntimeError(
                "No healthy service instances available."
            )

        return min(
            healthy,
            key=lambda instance: instance.active_connections
        )