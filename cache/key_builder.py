from fastapi import Request


class CacheKeyBuilder:

    def build(self, request: Request):

        method = request.method

        path = request.url.path

        query = request.url.query

        if query:

            return f"{method}:{path}?{query}"

        return f"{method}:{path}"


key_builder = CacheKeyBuilder()
