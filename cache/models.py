from pydantic import BaseModel


class CacheConfig(BaseModel):

    enabled: bool

    default_ttl: int

    cacheable_methods: list[str]

    routes: dict[str, bool]

    invalidate: dict[str, list[str]]