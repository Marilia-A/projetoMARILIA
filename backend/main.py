from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend import models  # noqa: F401
from backend.database import criar_tabelas
from backend.routers import glossario, progresso, roteiros, tutor, usuarios

PASTA_IMAGENS = Path(__file__).parent / "imagens"
for sub in ("roteiros", "glossario"):
    (PASTA_IMAGENS / sub).mkdir(parents=True, exist_ok=True)


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
app.mount("/imagens", StaticFiles(directory=PASTA_IMAGENS), name="imagens")


@app.get("/")
def raiz():
    return {"status": "ok", "app": "MARILIA"}