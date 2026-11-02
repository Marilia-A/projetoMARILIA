import flet as ft

import api
import componentes as c
import navegacao


def mostrar(page: ft.Page):
    cabecalho = ft.Row([c.botao_voltar("roteiros"), c.titulo("Minhas turmas")])
    aviso = c.aviso_erro()
    campo_codigo = ft.TextField(
        label="Código da turma (6 caracteres)",
        width=300,
        max_length=6,
        capitalization=ft.TextCapitalization.CHARACTERS,
        prefix_icon=ft.Icons.KEY,
    )

    def entrar(e):
        codigo = (campo_codigo.value or "").strip()
        if len(codigo) != 6:
            aviso.value = "Digite o código de 6 caracteres que o professor passou."
            page.update()
            return
        try:
            api.entrar_turma(codigo)
        except api.ErroAPI as erro:
            aviso.value = erro.mensagem
            page.update()
            return
        navegacao.ir("minhas_turmas")

    campo_codigo.on_submit = entrar

    try:
        turmas = api.minhas_turmas()
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho, ft.Text(erro.mensagem))
        return

    lista = [
        ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.Icons.GROUPS),
                title=ft.Text(t["nome"], weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f'Professor: {t["professor_nome"]} — Código {t["codigo"]}'),
            )
        )
        for t in turmas
    ]

    c.mostrar(
        page,
        cabecalho,
        ft.Text("Entrar em uma turma", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([campo_codigo, ft.FilledButton("Entrar", icon=ft.Icons.LOGIN, on_click=entrar)]),
        aviso,
        ft.Divider(),
        ft.Text("Turmas em que você está", size=18, weight=ft.FontWeight.BOLD),
        *(lista or [ft.Text("Você ainda não está em nenhuma turma.")]),
    )