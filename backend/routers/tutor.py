import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Etapa, HistoricoInteracao, Roteiro, TipoUsuario, Usuario
from backend.schemas import HistoricoLer, NivelProfundidade, PerguntaTutor

load_dotenv()

router = APIRouter(tags=["tutor"])

URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
TENTATIVAS = 3

INSTRUCOES_NIVEL = {
    NivelProfundidade.basico: (
        "Responda em até 4 frases curtas, com palavras simples e um exemplo do dia a dia. "
        "Não use termos técnicos sem explicar."
    ),
    NivelProfundidade.intermediario: (
        "Responda em um ou dois parágrafos, explicando o porquê das coisas e "
        "relacionando com os componentes e o código do roteiro."
    ),
    NivelProfundidade.avancado: (
        "Responda de forma detalhada, incluindo conceitos de eletrônica e programação "
        "envolvidos, e mostre trechos de código quando ajudar."
    ),
}


def montar_instrucoes(nivel: NivelProfundidade, roteiro: Roteiro | None, etapas: list[Etapa]) -> str:
    partes = [
        "Você é o tutor do MARILIA, um aplicativo de apoio ao ensino de robótica educacional "
        "com Arduino para alunos do ensino básico.",
        "Regras: responda sempre em português do Brasil, com linguagem adequada para "
        "crianças e adolescentes. Responda somente dúvidas sobre robótica, Arduino, "
        "eletrônica básica, programação e o roteiro em estudo. Se a pergunta fugir desses "
        "assuntos, diga com gentileza que só pode ajudar com robótica e convide o aluno a "
        "voltar ao roteiro. Não invente componentes ou passos que não existem no roteiro. "
        "Sempre lembre dos cuidados de segurança quando a dúvida envolver ligações elétricas. "
        "Guie o aluno a entender, sem apenas entregar a resposta pronta.",
        INSTRUCOES_NIVEL[nivel],
    ]
    if roteiro:
        passos = "\n".join(f"{e.ordem}. {e.conteudo}" for e in etapas)
        partes.append(
            "Roteiro em estudo:\n"
            f"Título: {roteiro.titulo}\n"
            f"Descrição: {roteiro.descricao}\n"
            f"Materiais: {roteiro.materiais}\n"
            f"Etapas:\n{passos}\n"
            f"Código:\n{roteiro.codigo_comentado}"
        )
    return "\n\n".join(partes)


def gerar_resposta(instrucoes: str, pergunta: str) -> str:
    chave = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if not chave:
        return f"[modo simulado, sem chave configurada] Você perguntou: {pergunta}"

    corpo = {
        "system_instruction": {"parts": [{"text": instrucoes}]},
        "contents": [{"role": "user", "parts": [{"text": pergunta}]}],
        "generationConfig": {"temperature": 0.4},
    }
    for tentativa in range(TENTATIVAS):
        try:
            r = httpx.post(
                URL_GEMINI.format(modelo=modelo),
                headers={"x-goog-api-key": chave},
                json=corpo,
                timeout=60,
            )
        except httpx.HTTPError:
            raise HTTPException(502, "Não foi possível conectar ao serviço de IA.")

        if r.status_code == 200:
            try:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError):
                raise HTTPException(502, "O serviço de IA não retornou uma resposta.")
        if r.status_code in (429, 503) and tentativa < TENTATIVAS - 1:
            time.sleep(2 * (tentativa + 1))
            continue
        if r.status_code in (429, 503):
            raise HTTPException(503, "O tutor está ocupado agora. Tente de novo em instantes.")
        raise HTTPException(502, f"Erro no serviço de IA ({r.status_code}).")


@router.post("/tutor/perguntar", response_model=HistoricoLer)
def perguntar(dados: PerguntaTutor, session: Session = Depends(get_session)):
    aluno = session.get(Usuario, dados.aluno_id)
    if not aluno or aluno.tipo != TipoUsuario.aluno:
        raise HTTPException(404, "Aluno não encontrado.")
    if not dados.pergunta.strip():
        raise HTTPException(422, "A pergunta não pode ser vazia.")

    roteiro = None
    etapas = []
    if dados.roteiro_id is not None:
        roteiro = session.get(Roteiro, dados.roteiro_id)
        if not roteiro:
            raise HTTPException(404, "Roteiro não encontrado.")
        etapas = session.exec(
            select(Etapa).where(Etapa.roteiro_id == roteiro.id).order_by(Etapa.ordem)
        ).all()

    instrucoes = montar_instrucoes(dados.nivel_profundidade, roteiro, etapas)
    resposta = gerar_resposta(instrucoes, dados.pergunta)

    registro = HistoricoInteracao(
        aluno_id=dados.aluno_id,
        roteiro_id=dados.roteiro_id,
        nivel_profundidade=dados.nivel_profundidade.value,
        pergunta=dados.pergunta,
        resposta=resposta,
    )
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


@router.get("/alunos/{aluno_id}/historico", response_model=list[HistoricoLer])
def listar_historico(
    aluno_id: int,
    roteiro_id: int | None = None,
    session: Session = Depends(get_session),
):
    consulta = select(HistoricoInteracao).where(HistoricoInteracao.aluno_id == aluno_id)
    if roteiro_id is not None:
        consulta = consulta.where(HistoricoInteracao.roteiro_id == roteiro_id)
    return session.exec(consulta.order_by(HistoricoInteracao.data_hora)).all()