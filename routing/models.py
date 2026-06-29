from pydantic import BaseModel


class Service(BaseModel):
    url: str


class Route(BaseModel):
    path: str
    service: str
    methods: list[str] = ["GET"]
    roles: list[str] = []


class GatewayConfig(BaseModel):
    services: dict[str, Service]
    routes: list[Route]