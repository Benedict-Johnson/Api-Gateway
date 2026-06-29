from collections import defaultdict

from load_balancer.discovery.models import ServiceInstance


class DiscoveryRegistry:

    def __init__(self):
        self.services = defaultdict(list)

    def register(self, instance: ServiceInstance):

        existing = self.get_instance(
            instance.service,
            instance.host,
            instance.port
        )

        if existing is None:
            self.services[
                instance.service
            ].append(instance)
            return

        existing.last_seen = instance.last_seen

    def get(self, service):
        return self.services.get(service, [])

    def get_instance(
        self,
        service,
        host,
        port
    ):

        for instance in self.services[service]:

            if (
                instance.host == host
                and
                instance.port == port
            ):
                return instance

        return None

    def deregister(
        self,
        service,
        host,
        port
    ):

        self.services[service] = [

            i

            for i in self.services[service]

            if not (
                i.host == host
                and
                i.port == port
            )
        ]


# Global singleton
registry = DiscoveryRegistry()