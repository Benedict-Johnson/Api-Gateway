from load_balancer.algorithms.least_connections import LeastConnectionsBalancer
from load_balancer.algorithms.round_robin import RoundRobinBalancer
from load_balancer.algorithms.weighted_round_robin import WeightedRoundRobinBalancer
from load_balancer.config import LoadBalancerConfigLoader


class LoadBalancerManager:

    def __init__(self):

        config = LoadBalancerConfigLoader("load_balancer/config.yaml")

        algorithms = {
            "round_robin": RoundRobinBalancer(),
            "weighted_round_robin": WeightedRoundRobinBalancer(),
            "least_connections": LeastConnectionsBalancer(),
        }

        self.algorithm = algorithms[config.config.algorithm]

    def next(self, service):

        return self.algorithm.next(service)
