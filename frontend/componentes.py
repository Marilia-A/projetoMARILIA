import flet as ft

import api
import navegacao

_seletor = {"arquivos": None}

# ---------- Paleta e tema (visual infantil) ----------
ROXO = "#6C4BD8"
AZUL = "#2F9BEA"
LARANJA = "#FF8A3D"
VERDE = "#2DBE7E"
ROSA = "#F25C9A"
AMARELO = "#FFC530"
CINZA = "#9E9AB0"
FUNDO = "#F6F3FF"
TEXTO = "#2B2350"
TEXTO_SUAVE = "#5A5277"
CORES_CARTOES = [AZUL, LARANJA, VERDE, ROSA, ROXO, AMARELO]


def preparar(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ROXO, use_material3=True)
    page.bgcolor = FUNDO
    seletor = ft.FilePicker()
    page.services.append(seletor)
    _seletor["arquivos"] = seletor


def mostrar(page: ft.Page, *controles):
    page.controls.clear()
    page.add(*controles)


def titulo(texto: str):
    return ft.Text(texto, size=28, weight=ft.FontWeight.BOLD, color=TEXTO)


def sombra():
    return ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.12, "#000000"), offset=ft.Offset(0, 3))


def circulo_icone(icone, cor: str, tamanho: int = 56, cor_icone: str = ft.Colors.WHITE):
    return ft.Container(
        content=ft.Icon(icone, color=cor_icone, size=int(tamanho * 0.55)),
        width=tamanho,
        height=tamanho,
        bgcolor=cor,
        border_radius=tamanho // 2,
        alignment=ft.Alignment.CENTER,
    )


def cabecalho(texto: str, icone=ft.Icons.SMART_TOY, voltar: str | None = None, subtitulo: str | None = None,
              extras: list | None = None, **params_voltar):
    """Faixa colorida no topo de cada tela."""
    esquerda = []
    if voltar:
        esquerda.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                tooltip="Voltar",
                on_click=lambda e: navegacao.ir(voltar, **params_voltar),
            )
        )
    textos = [ft.Text(texto, size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)]
    if subtitulo:
        textos.append(ft.Text(subtitulo, size=15, color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE)))
    esquerda += [
        circulo_icone(icone, ft.Colors.WHITE, 52, cor_icone=ROXO),
        ft.Column(textos, spacing=2, expand=True),
    ]
    return ft.Container(
        content=ft.Row([ft.Row(esquerda, expand=True), *(extras or [])]),
        gradient=ft.LinearGradient(colors=[ROXO, AZUL], begin=ft.Alignment.CENTER_LEFT, end=ft.Alignment.CENTER_RIGHT),
        padding=ft.Padding.symmetric(horizontal=20, vertical=14),
        border_radius=20,
        margin=ft.Margin.only(bottom=8),
    )


def cartao(titulo_cartao: str, subtitulo: str | None = None, icone=ft.Icons.STAR, cor: str = AZUL,
           ao_clicar=None, direita=None, extra: list | None = None, opacidade: float = 1):
    """Cartão branco arredondado com ícone colorido à esquerda."""
    textos = [ft.Text(titulo_cartao, size=18, weight=ft.FontWeight.BOLD, color=TEXTO)]
    if subtitulo:
        textos.append(ft.Text(subtitulo, size=15, color=TEXTO_SUAVE))
    textos += extra or []
    linha = [circulo_icone(icone, cor), ft.Column(textos, spacing=4, expand=True)]
    if direita is not None:
        linha.append(direita)
    return ft.Container(
        content=ft.Row(linha, spacing=16),
        bgcolor=ft.Colors.WHITE,
        border_radius=18,
        padding=16,
        border=ft.Border.all(2, ft.Colors.with_opacity(0.25, cor)),
        shadow=sombra(),
        on_click=ao_clicar,
        ink=ao_clicar is not None,
        opacity=opacidade,
    )


def painel(*controles, padding: int = 20):
    """Área branca arredondada para agrupar conteúdo."""
    return ft.Container(
        content=ft.Column(list(controles), spacing=12),
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=padding,
        shadow=sombra(),
    )


def botao_menu(texto: str, icone, cor: str, ao_clicar):
    return ft.FilledButton(
        texto,
        icon=icone,
        on_click=ao_clicar,
        style=ft.ButtonStyle(
            bgcolor=cor,
            color=ft.Colors.WHITE,
            icon_color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=14),
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
        ),
    )


def botao_principal(texto: str, icone=None, ao_clicar=None, cor: str = ROXO, largura=None, desativado=False):
    return ft.FilledButton(
        texto,
        icon=icone,
        on_click=ao_clicar,
        width=largura,
        disabled=desativado,
        style=ft.ButtonStyle(
            bgcolor=cor,
            color=ft.Colors.WHITE,
            icon_color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=14),
            padding=ft.Padding.symmetric(horizontal=22, vertical=16),
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
        ),
    )


def imagem(caminho: str, altura: int = 250):
    return ft.Image(src=api.url_imagem(caminho), height=altura)


def aviso_erro():
    return ft.Text(color=ft.Colors.RED_700, size=15, weight=ft.FontWeight.W_500)


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
        filled=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=14,
    )

    def limpar(e):
        campo.value = ""
        ao_buscar()

    linha = ft.Row(
        [
            campo,
            botao_principal("Buscar", ft.Icons.SEARCH, lambda e: ao_buscar()),
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