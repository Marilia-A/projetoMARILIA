from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend import models  # noqa: F401
from backend.database import criar_tabelas
from backend.routers import glossario, progresso, roteiros, tutor, usuarios


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="MARILIA API", lifespan=lifespan)
app.include_router(roteiros.router)
app.include_router(glossario.router)
app.include_router(usuarios.router)
app.include_router(progresso.router)
app.include_router(tutor.router)


@app.get("/")
def raiz():
    return {"status": "ok", "app": "MARILIA"}