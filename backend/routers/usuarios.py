from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import (
    AlunoBadge,
    HistoricoInteracao,
    Progresso,
    TipoUsuario,
    Turma,
    TurmaAluno,
    Usuario,
)
from backend.schemas import LoginDados, UsuarioAtualizar, UsuarioCriar, UsuarioLer
from backend.seguranca import gerar_hash, verificar_senha

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def buscar_ou_404(session: Session, usuario_id: int) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


def tem_turmas(session: Session, usuario_id: int) -> bool:
    return session.exec(select(Turma).where(Turma.professor_id == usuario_id)).first() is not None


def salvar(session: Session, usuario: Usuario) -> Usuario:
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(usuario)
    return usuario


@router.post("", response_model=UsuarioLer, status_code=201)
def criar_usuario(dados: UsuarioCriar, session: Session = Depends(get_session)):
    usuario = Usuario(
        **dados.model_dump(exclude={"senha"}),
        senha_hash=gerar_hash(dados.senha),
    )
    if usuario.tipo != TipoUsuario.aluno:
        usuario.ano_escolar = None
    return salvar(session, usuario)


@router.post("/login", response_model=UsuarioLer)
def login(dados: LoginDados, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email.strip())).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
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


@router.put("/{usuario_id}", response_model=UsuarioLer)
def atualizar_usuario(
    usuario_id: int, dados: UsuarioAtualizar, session: Session = Depends(get_session)
):
    usuario = buscar_ou_404(session, usuario_id)
    tipo_antigo = usuario.tipo

    if tipo_antigo == TipoUsuario.professor and dados.tipo != TipoUsuario.professor:
        if tem_turmas(session, usuario_id):
            raise HTTPException(
                status_code=409,
                detail="Professor possui turmas cadastradas. Transfira ou exclua as turmas antes de mudar o tipo.",
            )

    if tipo_antigo == TipoUsuario.aluno and dados.tipo != TipoUsuario.aluno:
        for vinculo in session.exec(select(TurmaAluno).where(TurmaAluno.aluno_id == usuario_id)).all():
            session.delete(vinculo)

    for campo, valor in dados.model_dump(exclude={"senha"}).items():
        setattr(usuario, campo, valor)
    if dados.senha:
        usuario.senha_hash = gerar_hash(dados.senha)
    if usuario.tipo != TipoUsuario.aluno:
        usuario.ano_escolar = None
    return salvar(session, usuario)


@router.delete("/{usuario_id}", status_code=204)
def excluir_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = buscar_ou_404(session, usuario_id)
    if tem_turmas(session, usuario_id):
        raise HTTPException(status_code=409, detail="Professor possui turmas cadastradas")

    for modelo in (Progresso, HistoricoInteracao, AlunoBadge, TurmaAluno):
        for item in session.exec(select(modelo).where(modelo.aluno_id == usuario_id)).all():
            session.delete(item)

    session.delete(usuario)
    session.commit()