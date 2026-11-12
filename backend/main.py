from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from sqlmodel import Session

from backend import models  # noqa: F401
from backend.database import criar_tabelas, get_session
from backend.models import Imagem
from backend.routers import glossario, progresso, roteiros, turmas, tutor, upload, usuarios
from backend.seed import carregar_dados_iniciais

PASTA_IMAGENS = Path(__file__).parent / "imagens"
for sub in ("roteiros", "glossario"):
    (PASTA_IMAGENS / sub).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    carregar_dados_iniciais()
    yield

app = FastAPI(title="MARILIA API", lifespan=lifespan)
app.include_router(roteiros.router)
app.include_router(glossario.router)
app.include_router(usuarios.router)
app.include_router(turmas.router_aluno)
app.include_router(turmas.router)
app.include_router(progresso.router)
app.include_router(tutor.router)
app.include_router(upload.router)


@app.get("/imagens/{pasta}/{nome}", include_in_schema=False)
def obter_imagem(pasta: str, nome: str, session: Session = Depends(get_session)):
    registro = session.get(Imagem, f"{pasta}/{nome}")
    if registro:
        return Response(registro.conteudo, media_type=registro.tipo)
    arquivo = (PASTA_IMAGENS / pasta / nome).resolve()
    if arquivo.is_relative_to(PASTA_IMAGENS.resolve()) and arquivo.is_file():
        return FileResponse(arquivo)
    raise HTTPException(status_code=404, detail="Imagem não encontrada")


@app.get("/")
def raiz():
    return {"status": "ok", "app": "MARILIA"}