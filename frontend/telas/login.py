import flet as ft

import api
import componentes as c
import navegacao
import sessao


def mostrar(page: ft.Page):
    sessao.sair()

    campo_email = ft.TextField(label="E-mail", width=400, prefix_icon=ft.Icons.EMAIL)
    campo_senha = ft.TextField(
        label="Senha",
        width=400,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
    )
    aviso = c.aviso_erro()

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

    c.mostrar(
        page,
        ft.Column(
            [
                c.titulo("MARILIA"),
                ft.Text("Entre com seu e-mail e senha", size=16),
                campo_email,
                campo_senha,
                aviso,
                ft.FilledButton("Entrar", icon=ft.Icons.LOGIN, width=400, on_click=entrar),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )