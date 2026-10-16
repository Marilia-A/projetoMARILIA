from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import (
    AlunoBadge,
    Badge,
    Progresso,
    Roteiro,
    StatusProgresso,
    TipoUsuario,
    Usuario,
    agora,
)
from backend.schemas import (
    BadgeAluno,
    BadgeLer,
    ProgressoAtualizar,
    ProgressoLer,
    ProgressoResultado,
)

router = APIRouter(prefix="/alunos/{aluno_id}")


def validar_aluno(session: Session, aluno_id: int) -> None:
    aluno = session.get(Usuario, aluno_id)
    if not aluno or aluno.tipo != TipoUsuario.aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")


def conceder_badges(session: Session, aluno_id: int) -> list[BadgeLer]:
    concluidos = len(
        session.exec(
            select(Progresso).where(
                Progresso.aluno_id == aluno_id,
                Progresso.status == StatusProgresso.concluido,
            )
        ).all()
    )
    ja_tem = set(
        session.exec(select(AlunoBadge.badge_id).where(AlunoBadge.aluno_id == aluno_id)).all()
    )
    disponiveis = session.exec(
        select(Badge).where(Badge.roteiros_necessarios <= concluidos)
    ).all()

    novas = []
    for badge in disponiveis:
        if badge.id not in ja_tem:
            novas.append(BadgeLer(**badge.model_dump()))
            session.add(AlunoBadge(aluno_id=aluno_id, badge_id=badge.id))
    session.commit()
    return novas


@router.get("/progresso", response_model=list[ProgressoLer], tags=["Progresso"])
def listar_progresso(aluno_id: int, session: Session = Depends(get_session)):
    validar_aluno(session, aluno_id)
    return session.exec(
        select(Progresso)
        .where(Progresso.aluno_id == aluno_id)
        .order_by(Progresso.roteiro_id)
    ).all()


@router.put("/progresso/{roteiro_id}", response_model=ProgressoResultado, tags=["Progresso"])
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
    resultado = ProgressoLer(**progresso.model_dump())

    novas = conceder_badges(session, aluno_id) if dados.status == StatusProgresso.concluido else []
    return ProgressoResultado(**resultado.model_dump(), novas_badges=novas)


@router.get("/badges", response_model=list[BadgeAluno], tags=["Badges"])
def listar_badges(aluno_id: int, session: Session = Depends(get_session)):
    validar_aluno(session, aluno_id)
    conquistas = {
        ab.badge_id: ab.data_conquista
        for ab in session.exec(select(AlunoBadge).where(AlunoBadge.aluno_id == aluno_id)).all()
    }
    badges = session.exec(select(Badge).order_by(Badge.roteiros_necessarios)).all()
    return [
        BadgeAluno(
            **b.model_dump(),
            conquistada=b.id in conquistas,
            data_conquista=conquistas.get(b.id),
        )
        for b in badges
    ]