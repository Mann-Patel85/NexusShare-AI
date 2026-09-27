import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import FRONTEND_DIST, get_local_ip
from app.api.routes import router

app = FastAPI(
    title="NexusShare AI API",
    description="Intelligent Local Network File Sharing, ML Document Auto-Tagging, Biometric Security & Real-Time Engine",
    version="2.2.0"
)

# Enable CORS for React dev server & local intranet access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount compiled React assets if frontend/dist exists
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")


# Mount API Router
app.include_router(router)


# HTML Root Route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    dist_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(dist_index):
        with open(dist_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>NexusShare AI API Server Running</h1><p>Frontend app starting...</p>")


if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    print("=" * 65)
    print("NEXUSSHARE AI PRODUCTION BACKEND SERVER STARTING...")
    print(f"  - Local App URL:     http://localhost:8000")
    print(f"  - Intranet Wi-Fi:   http://{local_ip}:8000")
    print(f"  - WebSocket Stream:  ws://{local_ip}:8000/ws/network")
    print("=" * 65)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)