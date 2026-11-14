import flet as ft

import api
import componentes as c
import navegacao
import sessao


def mostrar(page: ft.Page):
    resultados = ft.Column(spacing=12)

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
            for i, t in enumerate(termos):
                extra = [c.imagem(t["imagem"], altura=150)] if t["imagem"] else []
                cartoes.append(
                    c.cartao(
                        t["nome"],
                        t["definicao"],
                        icone=ft.Icons.MENU_BOOK,
                        cor=c.CORES_CARTOES[i % len(c.CORES_CARTOES)],
                        extra=extra,
                    )
                )
            resultados.controls = cartoes
        page.update()

    linha_busca, campo_busca = c.barra_busca("Buscar termo", carregar)

    extras = []
    if sessao.pode_gerenciar():
        extras.append(
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                icon_color=ft.Colors.WHITE,
                tooltip="Gerenciar glossário",
                on_click=lambda e: navegacao.ir("gerenciar_glossario"),
            )
        )
    cabecalho = c.cabecalho("Glossário", ft.Icons.MENU_BOOK, voltar="roteiros",
                            subtitulo="As palavras da robótica explicadas em português", extras=extras)

    c.mostrar(page, cabecalho, linha_busca, resultados)
    carregar()