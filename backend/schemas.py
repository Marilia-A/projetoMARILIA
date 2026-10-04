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


class UsuarioLer(UsuarioBase):
    id: int


class ProgressoAtualizar(SQLModel):
    status: StatusProgresso


class ProgressoLer(SQLModel):
    id: int
    aluno_id: int
    roteiro_id: int
    status: StatusProgresso
    data_conclusao: datetime | None = None


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