import yaml

from cache.models import CacheConfig


class CacheConfigLoader:

    def __init__(self, path):

        with open(path) as f:

            raw = yaml.safe_load(f)

        self.config = CacheConfig(**raw)