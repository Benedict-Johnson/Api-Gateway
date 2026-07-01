from load_balancer.models import Service


class RoundRobinBalancer:

    def __init__(self):
        self.indices = {}

    def next(self, service: Service):

        if service.name not in self.indices:
            self.indices[service.name] = 0

        instances = service.instances

        index = self.indices[service.name]

        instance = instances[index]

        self.indices[service.name] = (index + 1) % len(instances)

        return instance
