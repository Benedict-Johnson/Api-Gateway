from fastapi import FastAPI
import asyncio

from services.common.discovery_client import DiscoveryClient

app = FastAPI()

discovery = DiscoveryClient(
    service="user-service",
    host="service-a",
    port=8001,
    api_key="secret123",
)


@app.on_event("startup")
async def startup():

    asyncio.create_task(
        discovery.run()
    )


@app.on_event("shutdown")
async def shutdown():

    await discovery.deregister()


@app.get("/users")
async def users():

    print("SERVICE A EXECUTED")

    return {
        "served_by": "service-a",
        "instance": "A"
    }


@app.post("/users")
async def create_user():

    print("USER CREATED")

    return {
        "created": True
    }

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {
        "served_by": "service-a",
        "instance": "A",
        "user_id": user_id
    }

@app.put("/users")
async def update_user():

    print("USER UPDATED")

    return {
        "updated": True
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