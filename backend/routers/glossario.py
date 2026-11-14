from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, or_, select

from backend.database import get_session
from backend.models import TermoGlossario
from backend.routers.upload import remover_imagens_sem_uso
from backend.schemas import TermoCriar, TermoLer
from backend.seguranca import gerente_atual, usuario_atual

router = APIRouter(
    prefix="/glossario", tags=["Glossário"], dependencies=[Depends(usuario_atual)]
)


def buscar_ou_404(session: Session, termo_id: int) -> TermoGlossario:
    termo = session.get(TermoGlossario, termo_id)
    if not termo:
        raise HTTPException(status_code=404, detail="Termo não encontrado")
    return termo


def salvar(session: Session, termo: TermoGlossario, imagem_antiga: str | None = None) -> TermoGlossario:
    session.add(termo)
    try:
        remover_imagens_sem_uso(session, [imagem_antiga])
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Já existe um termo com esse nome")
    session.refresh(termo)
    return termo


@router.post("", response_model=TermoLer, status_code=201, dependencies=[Depends(gerente_atual)])
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


@router.put("/{termo_id}", response_model=TermoLer, dependencies=[Depends(gerente_atual)])
def atualizar_termo(
    termo_id: int, dados: TermoCriar, session: Session = Depends(get_session)
):
    termo = buscar_ou_404(session, termo_id)
    imagem_antiga = termo.imagem
    for campo, valor in dados.model_dump().items():
        setattr(termo, campo, valor)
    return salvar(session, termo, imagem_antiga)


@router.delete("/{termo_id}", status_code=204, dependencies=[Depends(gerente_atual)])
def excluir_termo(termo_id: int, session: Session = Depends(get_session)):
    termo = buscar_ou_404(session, termo_id)
    imagem = termo.imagem
    session.delete(termo)
    remover_imagens_sem_uso(session, [imagem])
    session.commit()