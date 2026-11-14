import math
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete, func, select

from backend.database import get_session
from backend.models import (
    AlunoBadge,
    HistoricoInteracao,
    Progresso,
    TentativaLogin,
    TipoUsuario,
    Turma,
    TurmaAluno,
    Usuario,
)
from backend.schemas import LoginDados, LoginResposta, UsuarioAtualizar, UsuarioCriar, UsuarioLer
from backend.seguranca import (
    admin_atual,
    aluno_do_professor,
    criar_token,
    gerar_hash,
    gerente_atual,
    verificar_senha,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# Limite de tentativas de login, guardado no banco (não se perde quando o servidor reinicia).
# Conta por e-mail + endereço de quem tenta, para que errar a senha de outra pessoa
# a partir de outro computador não bloqueie o login dela; o limite só por e-mail é mais alto
# e serve de proteção extra contra tentativas vindas de vários endereços.
TENTATIVAS_POR_ENDERECO = 5
TENTATIVAS_POR_EMAIL = 20
JANELA_LOGIN = timedelta(minutes=15)


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _utc(momento: datetime) -> datetime:
    # o SQLite devolve a data sem fuso; o horário gravado é sempre UTC
    return momento if momento.tzinfo else momento.replace(tzinfo=timezone.utc)


def ip_do_cliente(request: Request) -> str:
    # Atrás do proxy do Render, o último endereço do X-Forwarded-For é o que o proxy viu.
    encaminhado = request.headers.get("x-forwarded-for")
    if encaminhado:
        return encaminhado.split(",")[-1].strip()
    return request.client.host if request.client else "desconhecido"


def _bloqueio(session: Session, email: str, ip: str) -> int | None:
    """Apaga tentativas antigas e devolve os minutos de espera, ou None se não houver bloqueio."""
    limite = _agora() - JANELA_LOGIN
    session.exec(delete(TentativaLogin).where(TentativaLogin.data_hora < limite))
    session.commit()
    regras = (
        (TENTATIVAS_POR_ENDERECO, (TentativaLogin.email == email, TentativaLogin.ip == ip)),
        (TENTATIVAS_POR_EMAIL, (TentativaLogin.email == email,)),
    )
    for maximo, filtros in regras:
        total, mais_antiga = session.exec(
            select(func.count(), func.min(TentativaLogin.data_hora)).where(*filtros)
        ).one()
        if total >= maximo:
            restante = (_utc(mais_antiga) + JANELA_LOGIN - _agora()).total_seconds()
            return max(1, math.ceil(restante / 60))
    return None


def buscar_ou_404(session: Session, usuario_id: int) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


def tem_turmas(session: Session, usuario_id: int) -> bool:
    return session.exec(select(Turma).where(Turma.professor_id == usuario_id)).first() is not None


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
def login(dados: LoginDados, request: Request, session: Session = Depends(get_session)):
    email = dados.email.strip().lower()
    ip = ip_do_cliente(request)
    minutos = _bloqueio(session, email, ip)
    if minutos is not None:
        raise HTTPException(
            status_code=429,
            detail=f"Muitas tentativas de login. Aguarde {minutos} minuto(s) e tente de novo.",
        )
    usuario = session.exec(select(Usuario).where(func.lower(Usuario.email) == email)).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        session.add(TentativaLogin(email=email, ip=ip, data_hora=_agora()))
        session.commit()
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    resposta = LoginResposta(**usuario.model_dump(exclude={"senha_hash"}), access_token=criar_token(usuario))
    session.exec(delete(TentativaLogin).where(TentativaLogin.email == email, TentativaLogin.ip == ip))
    session.commit()
    return resposta


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
    if (
        usuario.tipo != TipoUsuario.admin
        and usuario.id != usuario_id
        and not aluno_do_professor(session, usuario_id, usuario.id)
    ):
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