import flet as ft

import api
import componentes as c
import navegacao


def mostrar(page: ft.Page):
    cabecalho = ft.Row([c.botao_voltar("glossario"), c.titulo("Gerenciar glossário")])
    try:
        termos = api.listar_termos()
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho, ft.Text(erro.mensagem))
        return

    def excluir(termo_id):
        try:
            api.excluir_termo(termo_id)
        except api.ErroAPI:
            pass
        navegacao.ir("gerenciar_glossario")

    linhas = [
        c.cartao_gerenciar(
            t["nome"],
            t["definicao"],
            lambda e, tid=t["id"]: navegacao.ir("formulario_termo", termo_id=tid),
            lambda e, t=t: c.confirmar_exclusao(
                page,
                "Excluir termo",
                f'Excluir o termo "{t["nome"]}"?',
                lambda: excluir(t["id"]),
            ),
        )
        for t in termos
    ]
    c.mostrar(
        page,
        cabecalho,
        ft.FilledButton(
            "Novo termo", icon=ft.Icons.ADD, on_click=lambda e: navegacao.ir("formulario_termo")
        ),
        *(linhas or [ft.Text("Nenhum termo cadastrado.")]),
    )


def formulario(page: ft.Page, termo_id: int | None = None):
    dados = {}
    if termo_id:
        try:
            dados = api.obter_termo(termo_id)
        except api.ErroAPI:
            c.mostrar(
                page,
                ft.Text("Não foi possível abrir o termo."),
                ft.OutlinedButton("Voltar", on_click=lambda e: navegacao.ir("gerenciar_glossario")),
            )
            return

    aviso = c.aviso_erro()
    campo_nome = ft.TextField(label="Nome do termo", value=dados.get("nome", ""))
    campo_definicao = ft.TextField(
        label="Definição", value=dados.get("definicao", ""), multiline=True, min_lines=3
    )
    imagem_termo = c.seletor_imagem(page, dados.get("imagem"), "glossario", aviso)

    def salvar(e):
        if not (campo_nome.value or "").strip() or not (campo_definicao.value or "").strip():
            aviso.value = "Preencha o nome e a definição."
            page.update()
            return

        corpo = {
            "nome": campo_nome.value.strip(),
            "definicao": campo_definicao.value.strip(),
            "imagem": imagem_termo[1](),
        }
        try:
            if termo_id:
                api.atualizar_termo(termo_id, corpo)
            else:
                api.criar_termo(corpo)
        except api.ErroAPI as erro:
            aviso.value = (
                "Já existe um termo com esse nome."
                if erro.status == 409
                else "Não foi possível salvar o termo."
            )
            page.update()
            return
        navegacao.ir("gerenciar_glossario")

    c.mostrar(
        page,
        ft.Row(
            [
                c.botao_voltar("gerenciar_glossario"),
                c.titulo("Editar termo" if termo_id else "Novo termo"),
            ]
        ),
        campo_nome,
        campo_definicao,
        ft.Text("Imagem do termo", weight=ft.FontWeight.BOLD),
        imagem_termo[0],
        aviso,
        ft.Row(
            [
                ft.OutlinedButton(
                    "Cancelar", on_click=lambda e: navegacao.ir("gerenciar_glossario")
                ),
                ft.FilledButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
            ]
        ),
    )