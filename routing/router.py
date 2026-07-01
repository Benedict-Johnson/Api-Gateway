from routing.models import Route


class Router:

    def __init__(self, routes: list[Route]):
        self.routes = routes

    def resolve(self, path: str, method: str):

        matched = None

        for route in self.routes:

            if method not in route.methods:
                continue

            if path.startswith(route.path):

                if matched is None or len(route.path) > len(matched.path):
                    matched = route

        return matched
