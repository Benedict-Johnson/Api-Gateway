import yaml

from load_balancer.models import Service
from load_balancer.models import ServiceInstance


class ServiceRegistry:

    def __init__(self, path: str):

        with open(path) as file:
            raw = yaml.safe_load(file)

        self.services = {}

        for service in raw["services"]:

            instances = []

            for instance in service["instances"]:

                instances.append(
                    ServiceInstance(
                        host=instance["host"],
                        port=instance["port"],
                        weight=instance.get("weight", 1)
                    )
                )

            self.services[service["name"]] = Service(
                name=service["name"],
                instances=instances
            )

    def get(self, name: str):

        return self.services.get(name)