import flet as ft

import api
import componentes as c
import navegacao
import sessao


def mostrar(page: ft.Page):
    resultados = ft.Column()

    def carregar():
        texto = (campo_busca.value or "").strip()
        try:
            termos = api.listar_termos(texto or None)
        except api.ErroAPI as erro:
            resultados.controls = [ft.Text(erro.mensagem)]
            page.update()
            return

        if not termos:
            resultados.controls = [
                ft.Text("Nenhum termo encontrado." if texto else "Nenhum termo cadastrado.")
            ]
        else:
            cartoes = []
            for t in termos:
                conteudo = [
                    ft.Text(t["nome"], size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(t["definicao"], size=16),
                ]
                if t["imagem"]:
                    conteudo.append(c.imagem(t["imagem"], altura=150))
                cartoes.append(
                    ft.Card(content=ft.Container(padding=15, content=ft.Column(conteudo)))
                )
            resultados.controls = cartoes
        page.update()

    linha_busca, campo_busca = c.barra_busca("Buscar termo", carregar)

    cabecalho = [c.botao_voltar("roteiros"), c.titulo("Glossário")]
    if sessao.pode_gerenciar():
        cabecalho.append(
            ft.OutlinedButton(
                "Gerenciar glossário",
                icon=ft.Icons.SETTINGS,
                on_click=lambda e: navegacao.ir("gerenciar_glossario"),
            )
        )

    c.mostrar(page, ft.Row(cabecalho), linha_busca, resultados)
    carregar()