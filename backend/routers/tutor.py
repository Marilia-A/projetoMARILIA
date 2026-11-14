import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Etapa, HistoricoInteracao, Roteiro, Usuario
from backend.schemas import HistoricoLer, NivelProfundidade, PerguntaTutor
from backend.seguranca import exigir_acesso_ao_aluno, usuario_atual

load_dotenv()

router = APIRouter(tags=["Tutor"])

URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"
TENTATIVAS = 3
PERGUNTA_MAXIMA = 500  # caracteres

INSTRUCOES_NIVEL = {
    NivelProfundidade.superficial: (
        "Dê uma explicação superficial: curta, em até 5 frases simples, com uma comparação "
        "do dia a dia, só para esclarecer a dúvida pontual. Não use termos técnicos sem explicar."
    ),
    NivelProfundidade.moderado: (
        "Dê uma explicação moderada: um ou dois parágrafos, mostrando o raciocínio por trás "
        "da resposta e exemplos práticos ligados aos componentes e ao código do roteiro."
    ),
    NivelProfundidade.detalhado: (
        "Dê uma explicação detalhada: completa e aprofundada, relacionando com os conceitos "
        "teóricos de eletrônica e programação envolvidos, e mostre trechos de código quando ajudar."
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
        "Jeito de explicar: fale como um professor paciente conversando com uma criança "
        "de 10 a 12 anos. Use frases curtas, palavras do dia a dia e um tom acolhedor. "
        "Sempre que usar um termo técnico (pino, corrente, HIGH, LOW, função), explique o "
        "que ele significa com uma comparação do cotidiano, como um interruptor de luz, "
        "uma torneira de água ou uma ordem dada a um robô. Prefira mostrar o que acontece "
        "na prática (o LED acende, o LED apaga) antes de explicar a teoria. Termine com uma "
        "pergunta curta ou um desafio simples para o aluno testar se entendeu.",
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


def preparar_requisicao(instrucoes: str, pergunta: str):
    provedor = os.getenv("IA_PROVEDOR", "gemini").lower()
    if provedor == "groq":
        chave = os.getenv("GROQ_API_KEY")
        corpo = {
            "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            "messages": [
                {"role": "system", "content": instrucoes},
                {"role": "user", "content": pergunta},
            ],
            "temperature": 0.4,
        }
        return (
            chave,
            URL_GROQ,
            {"Authorization": f"Bearer {chave}"},
            corpo,
            lambda d: d["choices"][0]["message"]["content"],
        )

    chave = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    corpo = {
        "system_instruction": {"parts": [{"text": instrucoes}]},
        "contents": [{"role": "user", "parts": [{"text": pergunta}]}],
        "generationConfig": {"temperature": 0.4},
    }
    return (
        chave,
        URL_GEMINI.format(modelo=modelo),
        {"x-goog-api-key": chave},
        corpo,
        lambda d: d["candidates"][0]["content"]["parts"][0]["text"],
    )


def gerar_resposta(instrucoes: str, pergunta: str) -> str:
    chave, url, cabecalhos, corpo, extrair = preparar_requisicao(instrucoes, pergunta)
    if not chave:
        return f"[modo simulado, sem chave configurada] Você perguntou: {pergunta}"

    for tentativa in range(TENTATIVAS):
        try:
            r = httpx.post(url, headers=cabecalhos, json=corpo, timeout=60)
        except httpx.HTTPError:
            raise HTTPException(502, "Não foi possível conectar ao serviço de IA.")

        if r.status_code == 200:
            try:
                return extrair(r.json()).strip()
            except (KeyError, IndexError, TypeError, AttributeError):
                raise HTTPException(502, "O serviço de IA não retornou uma resposta.")
        if r.status_code in (429, 503) and tentativa < TENTATIVAS - 1:
            time.sleep(2 * (tentativa + 1))
            continue
        if r.status_code in (429, 503):
            raise HTTPException(503, "O tutor está ocupado agora. Tente de novo em instantes.")
        raise HTTPException(502, f"Erro no serviço de IA ({r.status_code}).")


@router.post("/tutor/perguntar", response_model=HistoricoLer)
def perguntar(
    dados: PerguntaTutor,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(usuario_atual),
):
    if dados.aluno_id != usuario.id:
        raise HTTPException(403, "Você só pode perguntar com o próprio usuário.")
    if not dados.pergunta.strip():
        raise HTTPException(422, "A pergunta não pode ser vazia.")
    if len(dados.pergunta) > PERGUNTA_MAXIMA:
        raise HTTPException(422, f"A pergunta pode ter no máximo {PERGUNTA_MAXIMA} caracteres.")

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


@router.get("/alunos/{aluno_id}/historico", response_model=list[HistoricoLer], tags=["Tutor"])
def listar_historico(
    aluno_id: int,
    roteiro_id: int | None = None,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(usuario_atual),
):
    exigir_acesso_ao_aluno(session, usuario, aluno_id)
    consulta = select(HistoricoInteracao).where(HistoricoInteracao.aluno_id == aluno_id)
    if roteiro_id is not None:
        consulta = consulta.where(HistoricoInteracao.roteiro_id == roteiro_id)
    return session.exec(consulta.order_by(HistoricoInteracao.data_hora)).all()