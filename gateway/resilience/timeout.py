import httpx
from config.timeout import TimeoutLoader

class TimeoutPolicy:
    def __init__(self, path: str = "config/timeout.yaml"):
        self.config = TimeoutLoader(path).config
        
    def get_httpx_timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.config.connect_timeout,
            read=self.config.read_timeout,
            write=self.config.write_timeout,
            pool=self.config.pool_timeout,
        )
