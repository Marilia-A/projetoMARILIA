from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel

from backend.models import StatusProgresso, TipoUsuario


class EtapaCriar(SQLModel):
    ordem: int
    conteudo: str
    imagem: str | None = None


class EtapaLer(EtapaCriar):
    id: int


class RoteiroBase(SQLModel):
    titulo: str
    descricao: str
    materiais: str
    codigo_comentado: str
    imagem: str | None = None


class RoteiroCriar(RoteiroBase):
    etapas: list[EtapaCriar] = []


class RoteiroResumo(RoteiroBase):
    id: int


class RoteiroLer(RoteiroResumo):
    etapas: list[EtapaLer] = []


class TermoCriar(SQLModel):
    nome: str
    definicao: str
    imagem: str | None = None


class TermoLer(TermoCriar):
    id: int


class UsuarioBase(SQLModel):
    nome: str
    email: str
    tipo: TipoUsuario
    ano_escolar: str | None = None


class UsuarioCriar(UsuarioBase):
    senha: str


class UsuarioAtualizar(UsuarioBase):
    senha: str | None = None


class UsuarioLer(UsuarioBase):
    id: int


class LoginDados(SQLModel):
    email: str
    senha: str


class TurmaCriar(SQLModel):
    nome: str
    professor_id: int


class TurmaLer(SQLModel):
    id: int
    nome: str
    codigo: str
    professor_id: int
    professor_nome: str
    total_alunos: int


class TurmaDetalhe(TurmaLer):
    alunos: list[UsuarioLer] = []


class BadgeLer(SQLModel):
    id: int
    nome: str
    criterio: str
    roteiros_necessarios: int


class BadgeAluno(BadgeLer):
    conquistada: bool
    data_conquista: datetime | None = None


class ProgressoAtualizar(SQLModel):
    status: StatusProgresso


class ProgressoLer(SQLModel):
    id: int
    aluno_id: int
    roteiro_id: int
    status: StatusProgresso
    data_conclusao: datetime | None = None


class ProgressoResultado(ProgressoLer):
    novas_badges: list[BadgeLer] = []


class NivelProfundidade(str, Enum):
    superficial = "superficial"
    moderado = "moderado"
    detalhado = "detalhado"


class PerguntaTutor(SQLModel):
    aluno_id: int
    roteiro_id: int | None = None
    nivel_profundidade: NivelProfundidade = NivelProfundidade.superficial
    pergunta: str


class HistoricoLer(SQLModel):
    id: int
    aluno_id: int
    roteiro_id: int | None = None
    nivel_profundidade: str
    pergunta: str
    resposta: str
    data_hora: datetime