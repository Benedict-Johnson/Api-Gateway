import yaml

from auth.models import APIKey


class APIKeyManager:

    def __init__(self, path: str):

        with open(path) as f:
            raw = yaml.safe_load(f)

        self.keys = {
            item["key"]: APIKey(**item)
            for item in raw["api_keys"]
        }

    def validate(self, key: str):

        return self.keys.get(key)