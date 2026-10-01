from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship


class TipoUsuario(str, Enum):
    aluno = "aluno"
    professor = "professor"
    admin = "admin"


class StatusProgresso(str, Enum):
    nao_iniciado = "nao_iniciado"
    em_andamento = "em_andamento"
    concluido = "concluido"


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True, index=True)
    senha_hash: str
    tipo: TipoUsuario
    ano_escolar: str | None = None


class Turma(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    codigo: str = Field(unique=True, index=True)
    professor_id: int = Field(foreign_key="usuario.id")


class TurmaAluno(SQLModel, table=True):
    turma_id: int = Field(foreign_key="turma.id", primary_key=True)
    aluno_id: int = Field(foreign_key="usuario.id", primary_key=True)


class Roteiro(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    descricao: str
    materiais: str
    codigo_comentado: str

    etapas: list["Etapa"] = Relationship(back_populates="roteiro", cascade_delete=True)


class Etapa(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ordem: int
    conteudo: str
    roteiro_id: int = Field(foreign_key="roteiro.id", ondelete="CASCADE")

    roteiro: Roteiro | None = Relationship(back_populates="etapas")


class Progresso(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    aluno_id: int = Field(foreign_key="usuario.id")
    roteiro_id: int = Field(foreign_key="roteiro.id")
    status: StatusProgresso = StatusProgresso.nao_iniciado
    data_conclusao: datetime | None = None


class HistoricoInteracao(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    aluno_id: int = Field(foreign_key="usuario.id")
    roteiro_id: int | None = Field(default=None, foreign_key="roteiro.id")
    nivel_profundidade: int
    pergunta: str
    resposta: str
    data_hora: datetime = Field(default_factory=datetime.now)


class TermoGlossario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(unique=True, index=True)
    definicao: str
    imagem: str | None = None


class Badge(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    criterio: str


class AlunoBadge(SQLModel, table=True):
    aluno_id: int = Field(foreign_key="usuario.id", primary_key=True)
    badge_id: int = Field(foreign_key="badge.id", primary_key=True)
    data_conquista: datetime = Field(default_factory=datetime.now)