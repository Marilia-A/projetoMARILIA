from datetime import datetime, timedelta, timezone

import flet as ft

import api
import componentes as c
import navegacao
from telas.roteiros import icone_status

BRASILIA = timezone(timedelta(hours=-3))
STATUS = {"concluido": "Concluído", "em_andamento": "Em andamento", "nao_iniciado": "Não iniciado"}


def formatar_data_hora(valor: str) -> str:
    return datetime.fromisoformat(valor).astimezone(BRASILIA).strftime("%d/%m/%Y %H:%M")


def cartao_resumo(rotulo: str, valor: str, icone, cor: str):
    return ft.Container(
        width=220,
        padding=18,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        border=ft.Border.all(2, ft.Colors.with_opacity(0.3, cor)),
        shadow=c.sombra(),
        content=ft.Column(
            [
                c.circulo_icone(icone, cor, 52),
                ft.Text(valor, size=26, weight=ft.FontWeight.BOLD, color=c.TEXTO),
                ft.Text(rotulo, size=15, color=c.TEXTO_SUAVE, text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        ),
    )


def mostrar(page: ft.Page, turma_id: int):
    cabecalho_erro = c.cabecalho("Progresso", ft.Icons.INSIGHTS, voltar="turma", turma_id=turma_id)
    try:
        d = api.dashboard_turma(turma_id)
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho_erro, ft.Text(erro.mensagem))
        return

    total = d["total_roteiros"]

    def cartao_aluno(a):
        resumo = (
            f'{a["concluidos"]} de {total} concluídos — {a["em_andamento"]} em andamento — '
            f'{a["badges"]} conquista(s) — {a["perguntas"]} pergunta(s) ao tutor'
        )
        return c.cartao(
            a["nome"],
            resumo,
            icone=ft.Icons.PERSON,
            cor=c.CORES_CARTOES[a["aluno_id"] % len(c.CORES_CARTOES)],
            direita=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=c.CINZA, size=32),
            extra=[
                ft.ProgressBar(
                    value=a["concluidos"] / total if total else 0,
                    bar_height=10, border_radius=5, color=c.VERDE, bgcolor="#E3F7EE",
                )
            ],
            ao_clicar=lambda e: navegacao.ir("aluno_progresso", turma_id=turma_id, aluno_id=a["aluno_id"]),
        )

    c.mostrar(
        page,
        c.cabecalho(
            f'Progresso — {d["turma_nome"]}', ft.Icons.INSIGHTS, voltar="turma",
            subtitulo="Clique em um aluno para ver os detalhes", turma_id=turma_id,
        ),
        ft.Row(
            [
                cartao_resumo("Alunos", str(len(d["alunos"])), ft.Icons.GROUPS, c.AZUL),
                cartao_resumo(
                    "Média de roteiros concluídos",
                    f'{d["media_concluidos"]} de {total}',
                    ft.Icons.CHECK_CIRCLE,
                    c.VERDE,
                ),
                cartao_resumo(
                    "Perguntas ao tutor", str(d["total_perguntas"]), ft.Icons.QUESTION_ANSWER, c.ROXO
                ),
            ],
            wrap=True,
            spacing=14,
            run_spacing=14,
        ),
        ft.Text("Alunos", size=22, weight=ft.FontWeight.BOLD, color=c.TEXTO),
        *([cartao_aluno(a) for a in d["alunos"]] or [ft.Text("Nenhum aluno na turma.")]),
    )


def aluno(page: ft.Page, turma_id: int, aluno_id: int):
    def cabecalho(titulo_tela, subtitulo=None):
        return c.cabecalho(titulo_tela, ft.Icons.PERSON, voltar="dashboard", subtitulo=subtitulo, turma_id=turma_id)

    try:
        usuario = api.obter_usuario(aluno_id)
        roteiros = api.listar_roteiros()
        progresso = api.listar_progresso(aluno_id)
        badges = api.listar_badges(aluno_id)
        historico = api.listar_historico(aluno_id)
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho("Aluno"), ft.Text(erro.mensagem))
        return

    titulos = {r["id"]: r["titulo"] for r in roteiros}

    linhas_roteiros = [
        ft.ListTile(
            leading=icone_status(progresso.get(r["id"]))
            if progresso.get(r["id"])
            else ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, color=c.CINZA, size=32),
            title=ft.Text(r["titulo"]),
            subtitle=ft.Text(STATUS[progresso.get(r["id"], "nao_iniciado")]),
        )
        for r in roteiros
    ]

    conquistadas = [b["nome"] for b in badges if b["conquistada"]]

    perguntas = [
        ft.ExpansionTile(
            title=ft.Text(h["pergunta"]),
            subtitle=ft.Text(
                f'{formatar_data_hora(h["data_hora"])} — {h["nivel_profundidade"]} — '
                f'{titulos.get(h["roteiro_id"], "sem roteiro")}'
            ),
            controls=[
                ft.Container(
                    padding=10,
                    content=ft.Markdown(
                        h["resposta"],
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    ),
                )
            ],
        )
        for h in reversed(historico[-10:])
    ]

    subtitulo = usuario["email"]
    if usuario["ano_escolar"]:
        subtitulo += f' — {usuario["ano_escolar"]}'

    def secao(icone, cor, texto):
        return ft.Row([ft.Icon(icone, color=cor), ft.Text(texto, size=20, weight=ft.FontWeight.BOLD, color=c.TEXTO)])

    c.mostrar(
        page,
        cabecalho(usuario["nome"], subtitulo),
        c.painel(
            secao(ft.Icons.MEMORY, c.AZUL, "Roteiros"),
            *(linhas_roteiros or [ft.Text("Nenhum roteiro cadastrado.")]),
        ),
        c.painel(
            secao(ft.Icons.EMOJI_EVENTS, c.LARANJA, "Conquistas"),
            ft.Text(", ".join(conquistadas) if conquistadas else "Nenhuma conquista ainda.", size=16),
        ),
        c.painel(
            secao(ft.Icons.QUESTION_ANSWER, c.ROXO, f"Perguntas ao tutor ({len(historico)}) — últimas 10"),
            *(perguntas or [ft.Text("Nenhuma pergunta feita.")]),
        ),
    )