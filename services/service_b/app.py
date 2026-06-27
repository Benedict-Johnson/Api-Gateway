from fastapi import FastAPI

app = FastAPI()


@app.get("/orders")
async def orders():
    return {"service": "service-b"}


@app.get("/orders/{order_id}")
async def order(order_id: int):
    return {
        "service": "service-b",
        "order_id": order_id
    }