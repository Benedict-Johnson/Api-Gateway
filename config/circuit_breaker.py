import yaml
from pydantic import BaseModel


class CircuitBreakerConfig(BaseModel):

    enabled: bool

    failure_threshold: int

    recovery_timeout: int

    success_threshold: int


class CircuitBreakerLoader:

    def __init__(self, path: str):

        with open(path) as file:

            raw = yaml.safe_load(file)

        self.config = CircuitBreakerConfig(**raw)
