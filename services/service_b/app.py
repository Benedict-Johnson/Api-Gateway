from fastapi import FastAPI
import asyncio
app = FastAPI()


@app.get("/users")
async def users():
    return {
        "served_by": "service-b",
        "instance": "B"
    }


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {
        "served_by": "service-b",
        "instance": "B",
        "user_id": user_id
    }


@app.get("/orders")
async def orders():
    return {
        "served_by": "service-b"
    }


@app.get("/orders/{order_id}")
async def order(order_id: int):
    return {
        "served_by": "service-b",
        "order_id": order_id
    }

@app.get("/slow")
async def slow():

    await asyncio.sleep(5)

    return {
        "served_by": "service-b",
        "instance": "B"
    }