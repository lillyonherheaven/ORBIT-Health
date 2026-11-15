from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router

app = FastAPI(title="ORBIT Health v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/src", StaticFiles(directory=str(frontend_dir / "src")), name="src")

@app.get("/")
def serve_ui():
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": "offline-first", "thresholds": "ILLUSTRATIVE"}
