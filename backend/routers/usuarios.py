from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

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
from backend.schemas import LoginDados, LoginResposta, UsuarioAtualizar, UsuarioCriar, UsuarioLer
from backend.seguranca import admin_atual, criar_token, gerar_hash, gerente_atual, verificar_senha

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def buscar_ou_404(session: Session, usuario_id: int) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


def tem_turmas(session: Session, usuario_id: int) -> bool:
    return session.exec(select(Turma).where(Turma.professor_id == usuario_id)).first() is not None


def aluno_do_professor(session: Session, aluno_id: int, professor_id: int) -> bool:
    consulta = (
        select(TurmaAluno)
        .join(Turma, Turma.id == TurmaAluno.turma_id)
        .where(TurmaAluno.aluno_id == aluno_id, Turma.professor_id == professor_id)
    )
    return session.exec(consulta).first() is not None


def salvar(session: Session, usuario: Usuario) -> Usuario:
    usuario.email = usuario.email.strip().lower()
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(usuario)
    return usuario


@router.post("", response_model=UsuarioLer, status_code=201)
def criar_usuario(
    dados: UsuarioCriar,
    session: Session = Depends(get_session),
    _: Usuario = Depends(admin_atual),
):
    usuario = Usuario(
        **dados.model_dump(exclude={"senha"}),
        senha_hash=gerar_hash(dados.senha),
    )
    if usuario.tipo != TipoUsuario.aluno:
        usuario.ano_escolar = None
    return salvar(session, usuario)


@router.post("/login", response_model=LoginResposta)
def login(dados: LoginDados, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(func.lower(Usuario.email) == dados.email.strip().lower())).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    return LoginResposta(**usuario.model_dump(exclude={"senha_hash"}), access_token=criar_token(usuario))


@router.get("", response_model=list[UsuarioLer])
def listar_usuarios(
    tipo: TipoUsuario | None = None,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(gerente_atual),
):
    if usuario.tipo != TipoUsuario.admin:
        tipo = TipoUsuario.aluno
    consulta = select(Usuario)
    if tipo:
        consulta = consulta.where(Usuario.tipo == tipo)
    return session.exec(consulta.order_by(Usuario.nome)).all()


@router.get("/{usuario_id}", response_model=UsuarioLer)
def obter_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(gerente_atual),
):
    encontrado = buscar_ou_404(session, usuario_id)
    if usuario.tipo != TipoUsuario.admin and not aluno_do_professor(session, usuario_id, usuario.id):
        raise HTTPException(status_code=403, detail="Professor só acessa alunos das próprias turmas")
    return encontrado


@router.put("/{usuario_id}", response_model=UsuarioLer)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioAtualizar,
    session: Session = Depends(get_session),
    _: Usuario = Depends(admin_atual),
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
def excluir_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    admin: Usuario = Depends(admin_atual),
):
    if usuario_id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir o próprio usuário")
    usuario = buscar_ou_404(session, usuario_id)
    if tem_turmas(session, usuario_id):
        raise HTTPException(status_code=409, detail="Professor possui turmas cadastradas")

    for modelo in (Progresso, HistoricoInteracao, AlunoBadge, TurmaAluno):
        for item in session.exec(select(modelo).where(modelo.aluno_id == usuario_id)).all():
            session.delete(item)
    session.flush()

    session.delete(usuario)
    session.commit()