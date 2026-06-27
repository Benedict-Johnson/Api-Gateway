from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def users():
    return {"service": "service-a"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {
        "service": "service-a",
        "user_id": user_id
    }

@app.get("/hello")
async def hello():
    return {
        "message": "Hot Reload Works!"
    }