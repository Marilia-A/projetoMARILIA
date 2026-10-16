import flet as ft

import componentes
import navegacao
from telas import (
    conquistas,
    gerenciar_glossario,
    gerenciar_roteiros,
    gerenciar_usuarios,
    glossario,
    login,
    roteiro,
    roteiros,
    turmas,
)


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
            "conquistas": conquistas.mostrar,
            "gerenciar_roteiros": gerenciar_roteiros.mostrar,
            "formulario_roteiro": gerenciar_roteiros.formulario,
            "gerenciar_glossario": gerenciar_glossario.mostrar,
            "formulario_termo": gerenciar_glossario.formulario,
            "gerenciar_usuarios": gerenciar_usuarios.mostrar,
            "formulario_usuario": gerenciar_usuarios.formulario,
            "turmas": turmas.mostrar,
            "formulario_turma": turmas.formulario,
            "turma": turmas.detalhe,
        },
    )
    navegacao.ir("login")


ft.run(main)