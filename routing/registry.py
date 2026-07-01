import os

import yaml

from routing.models import GatewayConfig
from routing.router import Router


class RouteRegistry:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.last_modified = 0

        self.config = None
        self.router = None

        self.reload()

    def reload(self):

        with open(self.config_path) as file:
            raw = yaml.safe_load(file)

        self.config = GatewayConfig(**raw)
        self.router = Router(self.config.routes)

        self.last_modified = os.path.getmtime(self.config_path)

    def reload_if_needed(self):

        current = os.path.getmtime(self.config_path)

        if current != self.last_modified:
            print("Reloading gateway configuration...")
            self.reload()

    def resolve(self, path: str, method: str):

        self.reload_if_needed()

        return self.router.resolve(path, method)
