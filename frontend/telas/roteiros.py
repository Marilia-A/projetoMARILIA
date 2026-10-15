import flet as ft

import api
import componentes as c
import navegacao
import sessao


def icone_status(status):
    if status == "concluido":
        return ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, tooltip="Concluído")
    if status == "em_andamento":
        return ft.Icon(ft.Icons.TIMELAPSE, color=ft.Colors.AMBER, tooltip="Em andamento")
    return None


def mostrar(page: ft.Page):
    resultados = ft.Column()
    eh_aluno = sessao.usuario()["tipo"] == "aluno"

    def carregar():
        texto = (campo_busca.value or "").strip()
        try:
            roteiros = api.listar_roteiros(texto or None)
        except api.ErroAPI as erro:
            resultados.controls = [ft.Text(erro.mensagem)]
            page.update()
            return

        progresso = {}
        if eh_aluno:
            try:
                progresso = api.listar_progresso(sessao.usuario()["id"])
            except api.ErroAPI:
                pass

        if not roteiros:
            resultados.controls = [
                ft.Text("Nenhum roteiro encontrado." if texto else "Nenhum roteiro cadastrado.")
            ]
        else:
            resultados.controls = [
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.MEMORY),
                        title=ft.Text(r["titulo"], weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(r["descricao"]),
                        trailing=icone_status(progresso.get(r["id"])),
                        on_click=lambda e, rid=r["id"]: navegacao.ir("roteiro", roteiro_id=rid),
                    )
                )
                for r in roteiros
            ]
        page.update()

    linha_busca, campo_busca = c.barra_busca("Buscar roteiro por palavra-chave", carregar)

    botoes = [
        c.titulo("Roteiros"),
        ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda e: carregar()),
        ft.OutlinedButton(
            "Glossário", icon=ft.Icons.MENU_BOOK, on_click=lambda e: navegacao.ir("glossario")
        ),
    ]
    if sessao.pode_gerenciar():
        botoes.append(
            ft.OutlinedButton(
                "Gerenciar roteiros",
                icon=ft.Icons.SETTINGS,
                on_click=lambda e: navegacao.ir("gerenciar_roteiros"),
            )
        )

    c.mostrar(
        page,
        ft.Row(
            [
                ft.Row(botoes, wrap=True, expand=True),
                ft.Text(sessao.usuario()["nome"]),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT, tooltip="Sair", on_click=lambda e: navegacao.ir("login")
                ),
            ]
        ),
        linha_busca,
        resultados,
    )
    carregar()