import yaml
from pydantic import BaseModel


class LoadBalancerConfig(BaseModel):
    algorithm: str


class LoadBalancerConfigLoader:

    def __init__(self, path: str):

        with open(path) as file:
            raw = yaml.safe_load(file)

        self.config = LoadBalancerConfig(**raw)
