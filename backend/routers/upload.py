import mimetypes
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Etapa, Imagem, Roteiro, TermoGlossario

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
    tipo = mimetypes.guess_type(caminho)[0] or "application/octet-stream"
    session.add(Imagem(caminho=caminho, conteudo=conteudo, tipo=tipo))
    session.commit()
    return {"caminho": caminho}


def remover_imagens_sem_uso(session: Session, caminhos) -> None:
    """Apaga do banco as imagens enviadas que nenhum roteiro, etapa ou termo usa mais."""
    session.flush()
    for caminho in {c for c in caminhos if c}:
        em_uso = (
            session.exec(select(Roteiro.id).where(Roteiro.imagem == caminho)).first()
            or session.exec(select(Etapa.id).where(Etapa.imagem == caminho)).first()
            or session.exec(select(TermoGlossario.id).where(TermoGlossario.imagem == caminho)).first()
        )
        registro = session.get(Imagem, caminho)
        if registro and not em_uso:
            session.delete(registro)
