import flet as ft

import api
import navegacao

_seletor = {"arquivos": None}


def preparar(page: ft.Page):
    seletor = ft.FilePicker()
    page.services.append(seletor)
    _seletor["arquivos"] = seletor


def mostrar(page: ft.Page, *controles):
    page.controls.clear()
    page.add(*controles)


def titulo(texto: str):
    return ft.Text(texto, size=28, weight=ft.FontWeight.BOLD)


def imagem(caminho: str, altura: int = 250):
    return ft.Image(src=api.url_imagem(caminho), height=altura)


def aviso_erro():
    return ft.Text(color=ft.Colors.RED)


def botao_voltar(destino: str, **params):
    return ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        tooltip="Voltar",
        on_click=lambda e: navegacao.ir(destino, **params),
    )


def barra_busca(rotulo: str, ao_buscar):
    campo = ft.TextField(
        label=rotulo,
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        on_submit=lambda e: ao_buscar(),
    )

    def limpar(e):
        campo.value = ""
        ao_buscar()

    linha = ft.Row(
        [
            campo,
            ft.FilledButton("Buscar", on_click=lambda e: ao_buscar()),
            ft.IconButton(icon=ft.Icons.CLEAR, tooltip="Limpar busca", on_click=limpar),
        ]
    )
    return linha, campo


def seletor_imagem(page: ft.Page, caminho: str | None, pasta: str, aviso: ft.Text):
    estado = {"caminho": caminho}
    area = ft.Row()

    async def escolher(e):
        arquivos = await _seletor["arquivos"].pick_files(
            allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE
        )
        if not arquivos:
            return
        arq = arquivos[0]
        try:
            estado["caminho"] = api.enviar_imagem(pasta, arq.path, arq.name)
            aviso.value = ""
        except api.ErroAPI as erro:
            aviso.value = erro.mensagem
        except OSError:
            aviso.value = "Não foi possível ler a imagem."
        atualizar()
        page.update()

    def remover(e):
        estado["caminho"] = None
        atualizar()
        page.update()

    def atualizar():
        if estado["caminho"]:
            area.controls = [
                imagem(estado["caminho"], altura=120),
                ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Remover imagem", on_click=remover),
            ]
        else:
            area.controls = [
                ft.OutlinedButton("Escolher imagem", icon=ft.Icons.IMAGE, on_click=escolher)
            ]

    atualizar()
    return area, lambda: estado["caminho"]


def confirmar_exclusao(page: ft.Page, titulo_dialogo: str, mensagem: str, ao_confirmar):
    def excluir(e):
        page.pop_dialog()
        ao_confirmar()

    page.show_dialog(
        ft.AlertDialog(
            title=ft.Text(titulo_dialogo),
            content=ft.Text(mensagem),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Excluir", on_click=excluir),
            ],
        )
    )


def cartao_gerenciar(titulo_item: str, subtitulo: str, ao_editar, ao_excluir):
    return ft.Card(
        content=ft.ListTile(
            title=ft.Text(titulo_item, weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(subtitulo, max_lines=2),
            trailing=ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=ao_editar),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Excluir",
                        on_click=ao_excluir,
                    ),
                ],
                tight=True,
            ),
        )
    )