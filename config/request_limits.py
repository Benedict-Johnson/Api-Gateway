import yaml
from pydantic import BaseModel


class RequestLimitsConfig(BaseModel):
    max_body_size: int
    max_header_size: int
    max_uri_size: int
    allowed_content_types: list[str]


class RequestLimitsLoader:

    def __init__(self, path: str):
        with open(path) as f:
            raw = yaml.safe_load(f)

        self.config = RequestLimitsConfig(**raw["request_limits"])
