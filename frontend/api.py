import httpx

from config import API_URL


class ErroAPI(Exception):
    def __init__(self, mensagem: str, status: int | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def _requisicao(metodo, caminho, timeout=10, **kwargs):
    try:
        r = httpx.request(metodo, f"{API_URL}{caminho}", timeout=timeout, **kwargs)
    except httpx.HTTPError:
        raise ErroAPI("Não foi possível conectar ao servidor.")
    if r.is_error:
        try:
            detalhe = r.json().get("detail")
        except ValueError:
            detalhe = None
        mensagem = detalhe if isinstance(detalhe, str) else "Erro ao comunicar com o servidor."
        raise ErroAPI(mensagem, r.status_code)
    return r.json() if r.content else None


def url_imagem(caminho: str) -> str:
    return f"{API_URL}/imagens/{caminho}"


# ---------- Usuários ----------

def login(email: str, senha: str) -> dict:
    return _requisicao("POST", "/usuarios/login", json={"email": email, "senha": senha})


def listar_usuarios(tipo: str | None = None) -> list:
    return _requisicao("GET", "/usuarios", params={"tipo": tipo} if tipo else None)


def obter_usuario(usuario_id: int) -> dict:
    return _requisicao("GET", f"/usuarios/{usuario_id}")


def criar_usuario(dados: dict) -> dict:
    return _requisicao("POST", "/usuarios", json=dados)


def atualizar_usuario(usuario_id: int, dados: dict) -> dict:
    return _requisicao("PUT", f"/usuarios/{usuario_id}", json=dados)


def excluir_usuario(usuario_id: int):
    _requisicao("DELETE", f"/usuarios/{usuario_id}")


# ---------- Turmas ----------

def listar_turmas(professor_id: int | None = None) -> list:
    return _requisicao(
        "GET", "/turmas", params={"professor_id": professor_id} if professor_id else None
    )


def obter_turma(turma_id: int) -> dict:
    return _requisicao("GET", f"/turmas/{turma_id}")


def criar_turma(dados: dict) -> dict:
    return _requisicao("POST", "/turmas", json=dados)


def atualizar_turma(turma_id: int, dados: dict) -> dict:
    return _requisicao("PUT", f"/turmas/{turma_id}", json=dados)


def excluir_turma(turma_id: int):
    _requisicao("DELETE", f"/turmas/{turma_id}")


def adicionar_aluno_turma(turma_id: int, aluno_id: int) -> dict:
    return _requisicao("POST", f"/turmas/{turma_id}/alunos/{aluno_id}")


def remover_aluno_turma(turma_id: int, aluno_id: int) -> dict:
    return _requisicao("DELETE", f"/turmas/{turma_id}/alunos/{aluno_id}")


def dashboard_turma(turma_id: int) -> dict:
    return _requisicao("GET", f"/turmas/{turma_id}/dashboard")


# ---------- Roteiros ----------

def listar_roteiros(busca: str | None = None) -> list:
    return _requisicao("GET", "/roteiros", params={"busca": busca} if busca else None)


def obter_roteiro(roteiro_id: int) -> dict:
    return _requisicao("GET", f"/roteiros/{roteiro_id}")


def criar_roteiro(dados: dict) -> dict:
    return _requisicao("POST", "/roteiros", json=dados)


def atualizar_roteiro(roteiro_id: int, dados: dict) -> dict:
    return _requisicao("PUT", f"/roteiros/{roteiro_id}", json=dados)


def excluir_roteiro(roteiro_id: int):
    _requisicao("DELETE", f"/roteiros/{roteiro_id}")


# ---------- Progresso e badges ----------

def listar_progresso(aluno_id: int) -> dict:
    lista = _requisicao("GET", f"/alunos/{aluno_id}/progresso")
    return {p["roteiro_id"]: p["status"] for p in lista}


def atualizar_progresso(aluno_id: int, roteiro_id: int, status: str) -> dict:
    return _requisicao(
        "PUT", f"/alunos/{aluno_id}/progresso/{roteiro_id}", json={"status": status}
    )


def listar_badges(aluno_id: int) -> list:
    return _requisicao("GET", f"/alunos/{aluno_id}/badges")


# ---------- Glossário ----------

def listar_termos(busca: str | None = None) -> list:
    return _requisicao("GET", "/glossario", params={"busca": busca} if busca else None)


def obter_termo(termo_id: int) -> dict:
    return _requisicao("GET", f"/glossario/{termo_id}")


def criar_termo(dados: dict) -> dict:
    return _requisicao("POST", "/glossario", json=dados)


def atualizar_termo(termo_id: int, dados: dict) -> dict:
    return _requisicao("PUT", f"/glossario/{termo_id}", json=dados)


def excluir_termo(termo_id: int):
    _requisicao("DELETE", f"/glossario/{termo_id}")


# ---------- Imagens ----------

def enviar_imagem(pasta: str, caminho_arquivo: str, nome: str) -> str:
    with open(caminho_arquivo, "rb") as f:
        resposta = _requisicao(
            "POST", f"/upload/{pasta}", timeout=30, files={"arquivo": (nome, f)}
        )
    return resposta["caminho"]


# ---------- Tutor IA ----------

def perguntar_tutor(aluno_id: int, roteiro_id: int, nivel: str, pergunta: str) -> str:
    resposta = _requisicao(
        "POST",
        "/tutor/perguntar",
        timeout=90,
        json={
            "aluno_id": aluno_id,
            "roteiro_id": roteiro_id,
            "nivel_profundidade": nivel,
            "pergunta": pergunta,
        },
    )
    return resposta["resposta"]


def listar_historico(aluno_id: int) -> list:
    return _requisicao("GET", f"/alunos/{aluno_id}/historico")