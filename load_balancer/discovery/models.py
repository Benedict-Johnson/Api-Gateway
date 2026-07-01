import time
from dataclasses import dataclass, field


@dataclass
class ServiceInstance:

    service: str

    host: str

    port: int

    weight: int = 1

    healthy: bool = True

    active_connections: int = 0

    last_seen: float = field(default_factory=time.time)

    @property
    def url(self):

        return f"http://{self.host}:{self.port}"
