from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.get("/api/v1/users")
def get_users():
    return {"status": "ok", "users": []}
