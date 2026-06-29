class RouteMatcher:

    def __init__(self, routes: dict[str, str]):
        self.routes = routes

    def match(self, path: str):

        matched_prefix = None

        for prefix in self.routes:

            if path.startswith(prefix):

                if matched_prefix is None or len(prefix) > len(matched_prefix):
                    matched_prefix = prefix

        if matched_prefix is None:
            return None

        return self.routes[matched_prefix]