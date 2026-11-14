import flet as ft

import api
import componentes as c
import navegacao


def mostrar(page: ft.Page):
    cabecalho = c.cabecalho("Minhas turmas", ft.Icons.GROUPS, voltar="roteiros",
                            subtitulo="Entre na turma com o código que o professor passou")
    aviso = c.aviso_erro()
    campo_codigo = ft.TextField(
        label="Código da turma (6 caracteres)",
        width=300,
        max_length=6,
        capitalization=ft.TextCapitalization.CHARACTERS,
        prefix_icon=ft.Icons.KEY,
        border_radius=14,
        text_size=18,
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
        c.cartao(
            t["nome"],
            f'Professor: {t["professor_nome"]} — Código {t["codigo"]}',
            icone=ft.Icons.GROUPS,
            cor=c.CORES_CARTOES[i % len(c.CORES_CARTOES)],
        )
        for i, t in enumerate(turmas)
    ]

    c.mostrar(
        page,
        cabecalho,
        c.painel(
            ft.Text("Entrar em uma turma", size=19, weight=ft.FontWeight.BOLD, color=c.TEXTO),
            ft.Row([campo_codigo, c.botao_principal("Entrar", ft.Icons.LOGIN, entrar, cor=c.VERDE)], wrap=True),
            aviso,
        ),
        ft.Text("Turmas em que você está", size=20, weight=ft.FontWeight.BOLD, color=c.TEXTO),
        *(lista or [ft.Text("Você ainda não está em nenhuma turma.", size=16, color=c.TEXTO_SUAVE)]),
    )