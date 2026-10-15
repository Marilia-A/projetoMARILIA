from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/upload", tags=["Upload"])

PASTA_IMAGENS = Path(__file__).resolve().parent.parent / "imagens"
EXTENSOES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
TAMANHO_MAX = 5 * 1024 * 1024


@router.post("/{pasta}", status_code=201)
async def enviar_imagem(
    pasta: Literal["roteiros", "glossario"], arquivo: UploadFile = File(...)
):
    extensao = Path(arquivo.filename or "").suffix.lower()
    if extensao not in EXTENSOES:
        raise HTTPException(status_code=400, detail="Formato de imagem não aceito")

    conteudo = await arquivo.read()
    if len(conteudo) > TAMANHO_MAX:
        raise HTTPException(status_code=400, detail="Imagem maior que 5 MB")

    nome = f"{uuid4().hex}{extensao}"
    (PASTA_IMAGENS / pasta / nome).write_bytes(conteudo)
    return {"caminho": f"{pasta}/{nome}"}