from datetime import datetime, timedelta, timezone

import flet as ft

import api
import componentes as c
import sessao

BRASILIA = timezone(timedelta(hours=-3))


def formatar_data(valor: str) -> str:
    data = datetime.fromisoformat(valor).astimezone(BRASILIA)
    return data.strftime("%d/%m/%Y")


CORES_BADGES = [c.LARANJA, c.AZUL, c.ROSA, c.VERDE, c.ROXO]


def cartao(badge: dict, indice: int):
    conquistada = badge["conquistada"]
    cor = CORES_BADGES[indice % len(CORES_BADGES)] if conquistada else c.CINZA
    if conquistada:
        rodape = ft.Text(f"Conquistada em {formatar_data(badge['data_conquista'])}", size=14, color=c.VERDE,
                         weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    else:
        rodape = ft.Row([ft.Icon(ft.Icons.LOCK, size=16, color=c.CINZA), ft.Text("Ainda bloqueada", size=14, color=c.CINZA)],
                        alignment=ft.MainAxisAlignment.CENTER, tight=True)
    return ft.Container(
        content=ft.Column(
            [
                c.circulo_icone(ft.Icons.EMOJI_EVENTS, cor, 88),
                ft.Text(badge["nome"], size=20, weight=ft.FontWeight.BOLD, color=c.TEXTO, text_align=ft.TextAlign.CENTER),
                ft.Text(badge["criterio"], size=15, color=c.TEXTO_SUAVE, text_align=ft.TextAlign.CENTER),
                rodape,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=20,
        border=ft.Border.all(2, ft.Colors.with_opacity(0.35, cor)),
        shadow=c.sombra(),
        opacity=1 if conquistada else 0.6,
        col={"xs": 12, "sm": 6, "md": 4},
    )


def mostrar(page: ft.Page):
    cabecalho = c.cabecalho("Minhas conquistas", ft.Icons.EMOJI_EVENTS, voltar="roteiros",
                            subtitulo="Conclua roteiros para ganhar troféus")
    try:
        badges = api.listar_badges(sessao.usuario()["id"])
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho, ft.Text(erro.mensagem))
        return

    total = sum(1 for b in badges if b["conquistada"])
    c.mostrar(
        page,
        cabecalho,
        ft.Text(f"Você tem {total} de {len(badges)} conquistas", size=20, weight=ft.FontWeight.BOLD, color=c.TEXTO),
        ft.ResponsiveRow([cartao(b, i) for i, b in enumerate(badges)], spacing=16, run_spacing=16),
    )
