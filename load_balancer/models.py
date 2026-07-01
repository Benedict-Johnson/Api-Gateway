from dataclasses import dataclass


@dataclass
class ServiceInstance:
    host: str
    port: int
    weight: int = 1
    healthy: bool = True
    active_connections: int = 0

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


@dataclass
class Service:
    name: str
    instances: list[ServiceInstance]
