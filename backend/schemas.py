from sqlmodel import SQLModel


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