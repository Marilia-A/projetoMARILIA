import flet as ft

import api
import componentes as c
import navegacao
import sessao


def mostrar(page: ft.Page, aviso: str | None = None):
    sessao.sair()

    campo_email = ft.TextField(
        label="E-mail", width=380, prefix_icon=ft.Icons.EMAIL, border_radius=14, text_size=16
    )
    campo_senha = ft.TextField(
        label="Senha",
        width=380,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        border_radius=14,
        text_size=16,
    )
    mensagem = aviso
    aviso = c.aviso_erro()
    if mensagem:
        aviso.value = mensagem

    def entrar(e):
        email = (campo_email.value or "").strip()
        senha = campo_senha.value or ""
        if not email or not senha:
            aviso.value = "Informe e-mail e senha."
            page.update()
            return
        try:
            usuario = api.login(email, senha)
        except api.ErroAPI as erro:
            aviso.value = "E-mail ou senha inválidos." if erro.status == 401 else erro.mensagem
            page.update()
            return
        sessao.entrar(usuario)
        navegacao.ir("roteiros")

    campo_senha.on_submit = entrar

    logo = ft.Container(
        content=ft.Icon(ft.Icons.SMART_TOY, color=ft.Colors.WHITE, size=64),
        width=110,
        height=110,
        border_radius=55,
        alignment=ft.Alignment.CENTER,
        gradient=ft.LinearGradient(colors=[c.ROXO, c.AZUL], begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT),
        shadow=c.sombra(),
    )
    cartao_login = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Text("MARILIA", size=40, weight=ft.FontWeight.BOLD, color=c.ROXO),
                ft.Text(
                    "Robótica com Arduino para aprender fazendo!",
                    size=16,
                    color=c.TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                campo_email,
                campo_senha,
                aviso,
                c.botao_principal("Entrar", ft.Icons.ROCKET_LAUNCH, entrar, largura=380),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=28,
        padding=ft.Padding.symmetric(horizontal=36, vertical=32),
        width=460,
        shadow=c.sombra(),
    )

    c.mostrar(
        page,
        ft.Container(
            content=cartao_login,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.only(top=40),
        ),
    )
