from pydantic import BaseModel
from config.yaml_loader import YAMLLoader

class ShutdownConfig(BaseModel):
    enabled: bool = True
    graceful_timeout: int = 30

class ShutdownLoader:
    def __init__(self, path: str = "config/shutdown.yaml"):
        self.loader = YAMLLoader(path)
        self.config = self._load()

    def _load(self) -> ShutdownConfig:
        if not self.loader.raw:
            return ShutdownConfig()
        return ShutdownConfig(**self.loader.raw)
