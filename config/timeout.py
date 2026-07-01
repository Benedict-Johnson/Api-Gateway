import yaml
from pydantic import BaseModel


class TimeoutConfig(BaseModel):
    enabled: bool

    connect_timeout: float
    read_timeout: float
    write_timeout: float
    pool_timeout: float


class TimeoutLoader:

    def __init__(self, path: str):

        with open(path) as f:
            raw = yaml.safe_load(f)

        self.config = TimeoutConfig(**raw)
