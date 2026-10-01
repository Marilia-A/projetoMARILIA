from sqlmodel import SQLModel

from backend.models import TipoUsuario


class EtapaCriar(SQLModel):
    ordem: int
    conteudo: str


class EtapaLer(EtapaCriar):
    id: int


class RoteiroBase(SQLModel):
    titulo: str
    descricao: str
    materiais: str
    codigo_comentado: str


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