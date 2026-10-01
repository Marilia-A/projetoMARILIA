from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import (
    Progresso,
    Roteiro,
    StatusProgresso,
    TipoUsuario,
    Usuario,
    agora,
)
from backend.schemas import ProgressoAtualizar, ProgressoLer

router = APIRouter(prefix="/alunos/{aluno_id}/progresso", tags=["Progresso"])


def validar_aluno(session: Session, aluno_id: int) -> None:
    aluno = session.get(Usuario, aluno_id)
    if not aluno or aluno.tipo != TipoUsuario.aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")


@router.get("", response_model=list[ProgressoLer])
def listar_progresso(aluno_id: int, session: Session = Depends(get_session)):
    validar_aluno(session, aluno_id)
    return session.exec(
        select(Progresso)
        .where(Progresso.aluno_id == aluno_id)
        .order_by(Progresso.roteiro_id)
    ).all()


@router.put("/{roteiro_id}", response_model=ProgressoLer)
def atualizar_progresso(
    aluno_id: int,
    roteiro_id: int,
    dados: ProgressoAtualizar,
    session: Session = Depends(get_session),
):
    validar_aluno(session, aluno_id)
    if not session.get(Roteiro, roteiro_id):
        raise HTTPException(status_code=404, detail="Roteiro não encontrado")

    progresso = session.exec(
        select(Progresso).where(
            Progresso.aluno_id == aluno_id, Progresso.roteiro_id == roteiro_id
        )
    ).first()
    if not progresso:
        progresso = Progresso(aluno_id=aluno_id, roteiro_id=roteiro_id)

    progresso.status = dados.status
    progresso.data_conclusao = agora() if dados.status == StatusProgresso.concluido else None
    session.add(progresso)
    session.commit()
    session.refresh(progresso)
    return progresso