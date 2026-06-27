import httpx
from fastapi import Request, Response


class ReverseProxy:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def forward(
        self,
        request: Request,
        target_url: str,
    ) -> Response:

        response = await self.client.request(
            method=request.method,
            url=target_url,
            headers=request.headers,
            params=request.query_params,
            content=await request.body(),
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )


proxy = ReverseProxy()