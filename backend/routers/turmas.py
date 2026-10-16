import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from backend.database import get_session
from backend.models import (
    AlunoBadge,
    HistoricoInteracao,
    Progresso,
    Roteiro,
    StatusProgresso,
    TipoUsuario,
    Turma,
    TurmaAluno,
    Usuario,
)
from backend.schemas import (
    DashboardTurma,
    LinhaDashboard,
    TurmaCriar,
    TurmaDetalhe,
    TurmaLer,
    UsuarioLer,
)

router = APIRouter(prefix="/turmas", tags=["Turmas"])


def gerar_codigo(session: Session) -> str:
    caracteres = string.ascii_uppercase + string.digits
    while True:
        codigo = "".join(secrets.choice(caracteres) for _ in range(6))
        if not session.exec(select(Turma).where(Turma.codigo == codigo)).first():
            return codigo


def buscar_ou_404(session: Session, turma_id: int) -> Turma:
    turma = session.get(Turma, turma_id)
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return turma


def validar_usuario(session: Session, usuario_id: int, tipo: TipoUsuario, nome: str) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if not usuario or usuario.tipo != tipo:
        raise HTTPException(status_code=404, detail=f"{nome} não encontrado")
    return usuario


def contar(session: Session, modelo, *condicoes) -> int:
    return session.exec(select(func.count()).select_from(modelo).where(*condicoes)).one()


def alunos_da_turma(session: Session, turma_id: int) -> list[Usuario]:
    return session.exec(
        select(Usuario)
        .join(TurmaAluno, TurmaAluno.aluno_id == Usuario.id)
        .where(TurmaAluno.turma_id == turma_id)
        .order_by(Usuario.nome)
    ).all()


def montar(session: Session, turma: Turma) -> TurmaLer:
    professor = session.get(Usuario, turma.professor_id)
    return TurmaLer(
        **turma.model_dump(),
        professor_nome=professor.nome if professor else "",
        total_alunos=contar(session, TurmaAluno, TurmaAluno.turma_id == turma.id),
    )


def montar_detalhe(session: Session, turma: Turma) -> TurmaDetalhe:
    return TurmaDetalhe(
        **montar(session, turma).model_dump(),
        alunos=[UsuarioLer(**a.model_dump()) for a in alunos_da_turma(session, turma.id)],
    )


@router.post("", response_model=TurmaLer, status_code=201)
def criar_turma(dados: TurmaCriar, session: Session = Depends(get_session)):
    validar_usuario(session, dados.professor_id, TipoUsuario.professor, "Professor")
    turma = Turma(nome=dados.nome, professor_id=dados.professor_id, codigo=gerar_codigo(session))
    session.add(turma)
    session.commit()
    session.refresh(turma)
    return montar(session, turma)


@router.get("", response_model=list[TurmaLer])
def listar_turmas(professor_id: int | None = None, session: Session = Depends(get_session)):
    consulta = select(Turma)
    if professor_id:
        consulta = consulta.where(Turma.professor_id == professor_id)
    return [montar(session, t) for t in session.exec(consulta.order_by(Turma.nome)).all()]


@router.get("/{turma_id}", response_model=TurmaDetalhe)
def obter_turma(turma_id: int, session: Session = Depends(get_session)):
    return montar_detalhe(session, buscar_ou_404(session, turma_id))


@router.get("/{turma_id}/dashboard", response_model=DashboardTurma)
def dashboard_turma(turma_id: int, session: Session = Depends(get_session)):
    turma = buscar_ou_404(session, turma_id)
    linhas = []
    for aluno in alunos_da_turma(session, turma_id):
        linhas.append(
            LinhaDashboard(
                aluno_id=aluno.id,
                nome=aluno.nome,
                ano_escolar=aluno.ano_escolar,
                concluidos=contar(
                    session,
                    Progresso,
                    Progresso.aluno_id == aluno.id,
                    Progresso.status == StatusProgresso.concluido,
                ),
                em_andamento=contar(
                    session,
                    Progresso,
                    Progresso.aluno_id == aluno.id,
                    Progresso.status == StatusProgresso.em_andamento,
                ),
                badges=contar(session, AlunoBadge, AlunoBadge.aluno_id == aluno.id),
                perguntas=contar(
                    session, HistoricoInteracao, HistoricoInteracao.aluno_id == aluno.id
                ),
            )
        )
    media = round(sum(l.concluidos for l in linhas) / len(linhas), 1) if linhas else 0
    return DashboardTurma(
        turma_id=turma.id,
        turma_nome=turma.nome,
        total_roteiros=contar(session, Roteiro),
        media_concluidos=media,
        total_perguntas=sum(l.perguntas for l in linhas),
        alunos=linhas,
    )


@router.put("/{turma_id}", response_model=TurmaLer)
def atualizar_turma(turma_id: int, dados: TurmaCriar, session: Session = Depends(get_session)):
    turma = buscar_ou_404(session, turma_id)
    validar_usuario(session, dados.professor_id, TipoUsuario.professor, "Professor")
    turma.nome = dados.nome
    turma.professor_id = dados.professor_id
    session.add(turma)
    session.commit()
    session.refresh(turma)
    return montar(session, turma)


@router.delete("/{turma_id}", status_code=204)
def excluir_turma(turma_id: int, session: Session = Depends(get_session)):
    turma = buscar_ou_404(session, turma_id)
    for vinculo in session.exec(select(TurmaAluno).where(TurmaAluno.turma_id == turma_id)).all():
        session.delete(vinculo)
    session.delete(turma)
    session.commit()


@router.post("/{turma_id}/alunos/{aluno_id}", response_model=TurmaDetalhe)
def adicionar_aluno(turma_id: int, aluno_id: int, session: Session = Depends(get_session)):
    turma = buscar_ou_404(session, turma_id)
    validar_usuario(session, aluno_id, TipoUsuario.aluno, "Aluno")
    if session.get(TurmaAluno, (turma_id, aluno_id)):
        raise HTTPException(status_code=409, detail="Aluno já está na turma")
    session.add(TurmaAluno(turma_id=turma_id, aluno_id=aluno_id))
    session.commit()
    return montar_detalhe(session, turma)


@router.delete("/{turma_id}/alunos/{aluno_id}", response_model=TurmaDetalhe)
def remover_aluno(turma_id: int, aluno_id: int, session: Session = Depends(get_session)):
    turma = buscar_ou_404(session, turma_id)
    vinculo = session.get(TurmaAluno, (turma_id, aluno_id))
    if not vinculo:
        raise HTTPException(status_code=404, detail="Aluno não está na turma")
    session.delete(vinculo)
    session.commit()
    return montar_detalhe(session, turma)