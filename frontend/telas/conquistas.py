from datetime import datetime, timedelta, timezone

import flet as ft

import api
import componentes as c
import sessao

BRASILIA = timezone(timedelta(hours=-3))


def formatar_data(valor: str) -> str:
    data = datetime.fromisoformat(valor).astimezone(BRASILIA)
    return data.strftime("%d/%m/%Y")


def cartao(badge: dict):
    if badge["conquistada"]:
        icone = ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.AMBER, size=40)
        subtitulo = f"{badge['criterio']} — conquistada em {formatar_data(badge['data_conquista'])}"
    else:
        icone = ft.Icon(ft.Icons.LOCK, color=ft.Colors.GREY, size=40)
        subtitulo = badge["criterio"]
    return ft.Card(
        content=ft.ListTile(
            leading=icone,
            title=ft.Text(badge["nome"], weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(subtitulo),
        ),
        opacity=1 if badge["conquistada"] else 0.5,
    )


def mostrar(page: ft.Page):
    cabecalho = ft.Row([c.botao_voltar("roteiros"), c.titulo("Minhas conquistas")])
    try:
        badges = api.listar_badges(sessao.usuario()["id"])
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho, ft.Text(erro.mensagem))
        return

    total = sum(1 for b in badges if b["conquistada"])
    c.mostrar(
        page,
        cabecalho,
        ft.Text(f"{total} de {len(badges)} conquistas", size=16),
        *[cartao(b) for b in badges],
    )