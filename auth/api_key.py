import yaml

from auth.models import APIKey
from config.settings import settings


class APIKeyManager:

    def __init__(self, path: str):

        with open(path) as f:
            raw = yaml.safe_load(f)

        self.keys = {}
        for item in raw.get("api_keys", []):
            if "env" in item:
                key_val = getattr(settings, item["env"])
            else:
                key_val = item["key"]
            client_name = item.get("client", item.get("name", "client"))
            self.keys[key_val] = APIKey(key=key_val, client=client_name)

    def validate(self, key: str):

        return self.keys.get(key)
