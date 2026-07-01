import yaml
from pydantic import BaseModel


class RetryConfig(BaseModel):
    enabled: bool
    attempts: int
    backoff: float
    retry_on: list[int]


class RetryLoader:

    def __init__(self, path: str):

        with open(path) as file:
            raw = yaml.safe_load(file)

        self.config = RetryConfig(**raw)
