from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, or_, select

from backend.database import get_session
from backend.models import TermoGlossario
from backend.schemas import TermoCriar, TermoLer

router = APIRouter(prefix="/glossario", tags=["Glossário"])


def buscar_ou_404(session: Session, termo_id: int) -> TermoGlossario:
    termo = session.get(TermoGlossario, termo_id)
    if not termo:
        raise HTTPException(status_code=404, detail="Termo não encontrado")
    return termo


def salvar(session: Session, termo: TermoGlossario) -> TermoGlossario:
    session.add(termo)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Já existe um termo com esse nome")
    session.refresh(termo)
    return termo


@router.post("", response_model=TermoLer, status_code=201)
def criar_termo(dados: TermoCriar, session: Session = Depends(get_session)):
    return salvar(session, TermoGlossario(**dados.model_dump()))


@router.get("", response_model=list[TermoLer])
def buscar_termos(busca: str | None = None, session: Session = Depends(get_session)):
    consulta = select(TermoGlossario)
    if busca:
        termo = f"%{busca}%"
        consulta = consulta.where(
            or_(
                col(TermoGlossario.nome).ilike(termo),
                col(TermoGlossario.definicao).ilike(termo),
            )
        )
    return session.exec(consulta.order_by(TermoGlossario.nome)).all()


@router.get("/{termo_id}", response_model=TermoLer)
def obter_termo(termo_id: int, session: Session = Depends(get_session)):
    return buscar_ou_404(session, termo_id)


@router.put("/{termo_id}", response_model=TermoLer)
def atualizar_termo(
    termo_id: int, dados: TermoCriar, session: Session = Depends(get_session)
):
    termo = buscar_ou_404(session, termo_id)
    for campo, valor in dados.model_dump().items():
        setattr(termo, campo, valor)
    return salvar(session, termo)


@router.delete("/{termo_id}", status_code=204)
def excluir_termo(termo_id: int, session: Session = Depends(get_session)):
    session.delete(buscar_ou_404(session, termo_id))
    session.commit()