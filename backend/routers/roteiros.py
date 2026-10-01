from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, or_, select

from backend.database import get_session
from backend.models import Etapa, Roteiro
from backend.schemas import EtapaLer, RoteiroCriar, RoteiroLer, RoteiroResumo

router = APIRouter(prefix="/roteiros", tags=["Roteiros"])


def buscar_ou_404(session: Session, roteiro_id: int) -> Roteiro:
    roteiro = session.get(Roteiro, roteiro_id)
    if not roteiro:
        raise HTTPException(status_code=404, detail="Roteiro não encontrado")
    return roteiro


def montar_resposta(session: Session, roteiro: Roteiro) -> RoteiroLer:
    etapas = session.exec(
        select(Etapa).where(Etapa.roteiro_id == roteiro.id).order_by(Etapa.ordem)
    ).all()
    return RoteiroLer(
        **roteiro.model_dump(),
        etapas=[EtapaLer.model_validate(e) for e in etapas],
    )


@router.post("", response_model=RoteiroLer, status_code=201)
def criar_roteiro(dados: RoteiroCriar, session: Session = Depends(get_session)):
    roteiro = Roteiro(**dados.model_dump(exclude={"etapas"}))
    session.add(roteiro)
    session.flush()
    for etapa in dados.etapas:
        session.add(Etapa(**etapa.model_dump(), roteiro_id=roteiro.id))
    session.commit()
    session.refresh(roteiro)
    return montar_resposta(session, roteiro)


@router.get("", response_model=list[RoteiroResumo])
def listar_roteiros(busca: str | None = None, session: Session = Depends(get_session)):
    consulta = select(Roteiro)
    if busca:
        termo = f"%{busca}%"
        consulta = consulta.where(
            or_(
                col(Roteiro.titulo).ilike(termo),
                col(Roteiro.descricao).ilike(termo),
                col(Roteiro.materiais).ilike(termo),
            )
        )
    return session.exec(consulta.order_by(Roteiro.id)).all()


@router.get("/{roteiro_id}", response_model=RoteiroLer)
def obter_roteiro(roteiro_id: int, session: Session = Depends(get_session)):
    return montar_resposta(session, buscar_ou_404(session, roteiro_id))


@router.put("/{roteiro_id}", response_model=RoteiroLer)
def atualizar_roteiro(
    roteiro_id: int, dados: RoteiroCriar, session: Session = Depends(get_session)
):
    roteiro = buscar_ou_404(session, roteiro_id)
    for campo, valor in dados.model_dump(exclude={"etapas"}).items():
        setattr(roteiro, campo, valor)

    antigas = session.exec(select(Etapa).where(Etapa.roteiro_id == roteiro.id)).all()
    for etapa in antigas:
        session.delete(etapa)
    session.flush()

    for etapa in dados.etapas:
        session.add(Etapa(**etapa.model_dump(), roteiro_id=roteiro.id))
    session.commit()
    session.refresh(roteiro)
    return montar_resposta(session, roteiro)


@router.delete("/{roteiro_id}", status_code=204)
def excluir_roteiro(roteiro_id: int, session: Session = Depends(get_session)):
    session.delete(buscar_ou_404(session, roteiro_id))
    session.commit()