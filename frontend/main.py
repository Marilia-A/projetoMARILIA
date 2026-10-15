import flet as ft

import componentes
import navegacao
from telas import gerenciar_glossario, gerenciar_roteiros, glossario, login, roteiro, roteiros


def main(page: ft.Page):
    page.title = "MARILIA"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    componentes.preparar(page)

    navegacao.configurar(
        page,
        {
            "login": login.mostrar,
            "roteiros": roteiros.mostrar,
            "roteiro": roteiro.mostrar,
            "glossario": glossario.mostrar,
            "gerenciar_roteiros": gerenciar_roteiros.mostrar,
            "formulario_roteiro": gerenciar_roteiros.formulario,
            "gerenciar_glossario": gerenciar_glossario.mostrar,
            "formulario_termo": gerenciar_glossario.formulario,
        },
    )
    navegacao.ir("login")


ft.run(main)