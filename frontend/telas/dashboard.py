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


def cartao_resumo(rotulo: str, valor: str, icone):
    return ft.Card(
        content=ft.Container(
            width=200,
            padding=15,
            content=ft.Column(
                [
                    ft.Icon(icone, size=30),
                    ft.Text(valor, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(rotulo),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
    )


def mostrar(page: ft.Page, turma_id: int):
    cabecalho_erro = ft.Row([c.botao_voltar("turma", turma_id=turma_id), c.titulo("Progresso")])
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
        return ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text(a["nome"], weight=ft.FontWeight.BOLD),
                subtitle=ft.Column(
                    [
                        ft.Text(resumo),
                        ft.ProgressBar(value=a["concluidos"] / total if total else 0),
                    ],
                    tight=True,
                ),
                on_click=lambda e: navegacao.ir(
                    "aluno_progresso", turma_id=turma_id, aluno_id=a["aluno_id"]
                ),
            )
        )

    c.mostrar(
        page,
        ft.Row(
            [
                c.botao_voltar("turma", turma_id=turma_id),
                c.titulo(f'Progresso — {d["turma_nome"]}'),
            ]
        ),
        ft.Row(
            [
                cartao_resumo("Alunos", str(len(d["alunos"])), ft.Icons.GROUPS),
                cartao_resumo(
                    "Média de roteiros concluídos",
                    f'{d["media_concluidos"]} de {total}',
                    ft.Icons.CHECK_CIRCLE,
                ),
                cartao_resumo(
                    "Perguntas ao tutor", str(d["total_perguntas"]), ft.Icons.QUESTION_ANSWER
                ),
            ],
            wrap=True,
        ),
        ft.Text("Alunos", size=20, weight=ft.FontWeight.BOLD),
        *([cartao_aluno(a) for a in d["alunos"]] or [ft.Text("Nenhum aluno na turma.")]),
    )


def aluno(page: ft.Page, turma_id: int, aluno_id: int):
    voltar = c.botao_voltar("dashboard", turma_id=turma_id)
    try:
        usuario = api.obter_usuario(aluno_id)
        roteiros = api.listar_roteiros()
        progresso = api.listar_progresso(aluno_id)
        badges = api.listar_badges(aluno_id)
        historico = api.listar_historico(aluno_id)
    except api.ErroAPI as erro:
        c.mostrar(page, ft.Row([voltar, c.titulo("Aluno")]), ft.Text(erro.mensagem))
        return

    titulos = {r["id"]: r["titulo"] for r in roteiros}

    linhas_roteiros = [
        ft.ListTile(
            leading=icone_status(progresso.get(r["id"]))
            or ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, color=ft.Colors.GREY),
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

    c.mostrar(
        page,
        ft.Row([voltar, c.titulo(usuario["nome"])]),
        ft.Text(subtitulo, size=16),
        ft.Text("Roteiros", size=20, weight=ft.FontWeight.BOLD),
        *(linhas_roteiros or [ft.Text("Nenhum roteiro cadastrado.")]),
        ft.Divider(),
        ft.Text("Conquistas", size=20, weight=ft.FontWeight.BOLD),
        ft.Text(", ".join(conquistadas) if conquistadas else "Nenhuma conquista ainda."),
        ft.Divider(),
        ft.Text(
            f"Perguntas ao tutor ({len(historico)}) — últimas 10",
            size=20,
            weight=ft.FontWeight.BOLD,
        ),
        *(perguntas or [ft.Text("Nenhuma pergunta feita.")]),
    )