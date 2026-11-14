import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import TipoUsuario, Turma, TurmaAluno, Usuario

load_dotenv()

ITERACOES = 600_000
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("Defina JWT_SECRET no .env")
JWT_ALGORITMO = "HS256"
HORAS_VALIDADE = 8

bearer = HTTPBearer(auto_error=False)


def gerar_hash(senha: str) -> str:
    sal = secrets.token_bytes(16)
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, ITERACOES)
    return f"{sal.hex()}${resumo.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    sal_hex, resumo_hex = senha_hash.split("$")
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal_hex), ITERACOES)
    return hmac.compare_digest(resumo.hex(), resumo_hex)


def criar_token(usuario: Usuario) -> str:
    dados = {
        "sub": str(usuario.id),
        "tipo": usuario.tipo.value,
        "exp": datetime.now(timezone.utc) + timedelta(hours=HORAS_VALIDADE),
    }
    return jwt.encode(dados, JWT_SECRET, algorithm=JWT_ALGORITMO)


def usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: Session = Depends(get_session),
) -> Usuario:
    if not credenciais:
        raise HTTPException(status_code=401, detail="Faça login para continuar")
    try:
        dados = jwt.decode(credenciais.credentials, JWT_SECRET, algorithms=[JWT_ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sessão expirada. Entre novamente.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    usuario = session.get(Usuario, int(dados["sub"]))
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario


def gerente_atual(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
    if usuario.tipo not in (TipoUsuario.professor, TipoUsuario.admin):
        raise HTTPException(status_code=403, detail="Acesso permitido só para professor ou admin")
    return usuario


def admin_atual(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
    if usuario.tipo != TipoUsuario.admin:
        raise HTTPException(status_code=403, detail="Acesso permitido só para admin")
    return usuario


def exigir_proprio_ou_gerente(usuario: Usuario, aluno_id: int):
    if usuario.tipo == TipoUsuario.aluno and usuario.id != aluno_id:
        raise HTTPException(status_code=403, detail="Aluno só acessa os próprios dados")


def aluno_do_professor(session: Session, aluno_id: int, professor_id: int) -> bool:
    consulta = (
        select(TurmaAluno)
        .join(Turma, Turma.id == TurmaAluno.turma_id)
        .where(TurmaAluno.aluno_id == aluno_id, Turma.professor_id == professor_id)
    )
    return session.exec(consulta).first() is not None


def exigir_acesso_ao_aluno(session: Session, usuario: Usuario, aluno_id: int):
    exigir_proprio_ou_gerente(usuario, aluno_id)
    if usuario.tipo != TipoUsuario.professor or usuario.id == aluno_id:
        return
    if not aluno_do_professor(session, aluno_id, usuario.id):
        raise HTTPException(status_code=403, detail="Professor só acessa alunos das próprias turmas")