from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import TipoUsuario, Usuario
from backend.schemas import UsuarioCriar, UsuarioLer
from backend.seguranca import gerar_hash

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def buscar_ou_404(session: Session, usuario_id: int) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.post("", response_model=UsuarioLer, status_code=201)
def criar_usuario(dados: UsuarioCriar, session: Session = Depends(get_session)):
    usuario = Usuario(
        **dados.model_dump(exclude={"senha"}),
        senha_hash=gerar_hash(dados.senha),
    )
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(usuario)
    return usuario


@router.get("", response_model=list[UsuarioLer])
def listar_usuarios(tipo: TipoUsuario | None = None, session: Session = Depends(get_session)):
    consulta = select(Usuario)
    if tipo:
        consulta = consulta.where(Usuario.tipo == tipo)
    return session.exec(consulta.order_by(Usuario.nome)).all()


@router.get("/{usuario_id}", response_model=UsuarioLer)
def obter_usuario(usuario_id: int, session: Session = Depends(get_session)):
    return buscar_ou_404(session, usuario_id)


@router.delete("/{usuario_id}", status_code=204)
def excluir_usuario(usuario_id: int, session: Session = Depends(get_session)):
    session.delete(buscar_ou_404(session, usuario_id))
    session.commit()