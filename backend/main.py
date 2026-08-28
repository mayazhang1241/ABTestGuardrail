from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.ws import router
from contextlib import asynccontextmanager
from backend import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_pool()
    yield
    await db.close_pool()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/experiments")
async def list_experiments():
    return await db.list_experiments()

@app.get("/experiments/{experiment_id}/history")
async def get_history(experiment_id: int):
    return await db.get_experiment_history(experiment_id)