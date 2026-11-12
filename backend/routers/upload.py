import mimetypes
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session

from backend.database import get_session
from backend.models import Imagem

from backend.seguranca import gerente_atual

router = APIRouter(prefix="/upload", tags=["Upload"], dependencies=[Depends(gerente_atual)])

PASTA_IMAGENS = Path(__file__).resolve().parent.parent / "imagens"
EXTENSOES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
TAMANHO_MAX = 5 * 1024 * 1024


@router.post("/{pasta}", status_code=201)
async def enviar_imagem(
    pasta: Literal["roteiros", "glossario"],
    arquivo: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    extensao = Path(arquivo.filename or "").suffix.lower()
    if extensao not in EXTENSOES:
        raise HTTPException(status_code=400, detail="Formato de imagem não aceito")

    conteudo = await arquivo.read()
    if len(conteudo) > TAMANHO_MAX:
        raise HTTPException(status_code=400, detail="Imagem maior que 5 MB")

    caminho = f"{pasta}/{uuid4().hex}{extensao}"
    tipo = arquivo.content_type or mimetypes.guess_type(caminho)[0] or "application/octet-stream"
    session.add(Imagem(caminho=caminho, conteudo=conteudo, tipo=tipo))
    session.commit()
    return {"caminho": caminho}