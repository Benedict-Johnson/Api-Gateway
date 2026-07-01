from load_balancer.models import Service


class WeightedRoundRobinBalancer:

    def __init__(self):
        self.indices = {}
        self.sequence = {}

    def next(self, service: Service):

        if service.name not in self.sequence:

            expanded = []

            for instance in service.instances:
                expanded.extend([instance] * instance.weight)

            self.sequence[service.name] = expanded
            self.indices[service.name] = 0

        seq = self.sequence[service.name]

        index = self.indices[service.name]

        instance = seq[index]

        self.indices[service.name] = (index + 1) % len(seq)

        return instance
