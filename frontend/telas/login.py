import asyncio

import flet as ft

import api
import componentes as c
import navegacao
import robos
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

    botao_entrar = c.botao_principal("Entrar", ft.Icons.ROCKET_LAUNCH, None, largura=380)
    aguarde = ft.Text(
        "Entrando... Se o servidor estava desligado, o primeiro acesso pode levar até 1 minuto.",
        size=14,
        color=c.TEXTO_SUAVE,
        text_align=ft.TextAlign.CENTER,
        width=380,
        visible=False,
    )
    # O clique é assíncrono e o pedido à API roda em segundo plano (asyncio.to_thread).
    # Assim a janela continua livre para mostrar o "Entrando..." enquanto espera.
    # Um login por vez: cliques repetidos (ou Enter) durante a espera são ignorados,
    # para não contar várias tentativas erradas de uma vez no limite de login.
    estado = {"entrando": False}

    def aguardando(sim: bool):
        estado["entrando"] = sim
        botao_entrar.disabled = sim
        botao_entrar.content = "Entrando..." if sim else "Entrar"
        campo_email.disabled = sim
        campo_senha.disabled = sim
        aguarde.visible = sim
        page.update()

    async def entrar(e):
        if estado["entrando"]:
            return
        email = (campo_email.value or "").strip()
        senha = campo_senha.value or ""
        if not email or not senha:
            aviso.value = "Informe e-mail e senha."
            page.update()
            return
        aviso.value = ""
        aguardando(True)
        try:
            usuario = await asyncio.to_thread(api.login, email, senha)
        except api.ErroAPI as erro:
            aviso.value = "E-mail ou senha inválidos." if erro.status == 401 else erro.mensagem
            aguardando(False)
            return
        except Exception:
            aviso.value = "Não foi possível entrar. Tente de novo."
            aguardando(False)
            return
        sessao.entrar(usuario)
        navegacao.ir("roteiros")

    botao_entrar.on_click = entrar

    campo_senha.on_submit = entrar

    logo, _ = robos.mascote(
        [
            "Oi! Eu sou o robô do MARILIA. Clique em mim!",
            "Entre com o e-mail e a senha que a escola te deu.",
            "Hoje é dia de acender LEDs!",
            "Pronto para virar inventor?",
        ],
        escala=0.75,
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
                aguarde,
                botao_entrar,
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
