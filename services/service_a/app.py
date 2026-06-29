from fastapi import FastAPI
import asyncio
app = FastAPI()


@app.get("/users")
async def users():
    return {
        "served_by": "service-a",
        "instance": "A"
    }


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {
        "served_by": "service-a",
        "instance": "A",
        "user_id": user_id
    }


@app.get("/hello")
async def hello():
    return {
        "served_by": "service-a"
    }

@app.get("/slow")
async def slow():

    await asyncio.sleep(5)

    return {
        "served_by": "service-a",
        "instance": "A"
    }