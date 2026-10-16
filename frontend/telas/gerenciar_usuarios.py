import flet as ft

import api
import componentes as c
import navegacao
import sessao

TIPOS = {"aluno": "Alunos", "professor": "Professores", "admin": "Administradores"}


def seletor_tipo(valor: str, ao_mudar=None):
    return ft.RadioGroup(
        value=valor,
        on_change=ao_mudar,
        content=ft.Row([ft.Radio(value=k, label=v) for k, v in TIPOS.items()]),
    )


def mostrar(page: ft.Page, tipo: str = "aluno"):
    cabecalho = ft.Row([c.botao_voltar("roteiros"), c.titulo("Gerenciar usuários")])
    filtro = seletor_tipo(
        tipo, lambda e: navegacao.ir("gerenciar_usuarios", tipo=e.control.value)
    )
    aviso = c.aviso_erro()

    try:
        usuarios = api.listar_usuarios(tipo)
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho, filtro, ft.Text(erro.mensagem))
        return

    def excluir(usuario_id):
        try:
            api.excluir_usuario(usuario_id)
        except api.ErroAPI as erro:
            aviso.value = erro.mensagem
            page.update()
            return
        navegacao.ir("gerenciar_usuarios", tipo=tipo)

    def pedir_exclusao(u):
        if u["id"] == sessao.usuario()["id"]:
            aviso.value = "Você não pode excluir o próprio usuário."
            page.update()
            return
        c.confirmar_exclusao(
            page,
            "Excluir usuário",
            f'Excluir "{u["nome"]}"? O progresso e o histórico dele também serão apagados.',
            lambda: excluir(u["id"]),
        )

    def subtitulo(u):
        return f'{u["email"]} — {u["ano_escolar"]}' if u["ano_escolar"] else u["email"]

    linhas = [
        c.cartao_gerenciar(
            u["nome"],
            subtitulo(u),
            lambda e, uid=u["id"]: navegacao.ir(
                "formulario_usuario", usuario_id=uid, tipo=tipo
            ),
            lambda e, u=u: pedir_exclusao(u),
        )
        for u in usuarios
    ]
    c.mostrar(
        page,
        cabecalho,
        filtro,
        ft.FilledButton(
            "Novo usuário",
            icon=ft.Icons.PERSON_ADD,
            on_click=lambda e: navegacao.ir("formulario_usuario", tipo=tipo),
        ),
        aviso,
        *(linhas or [ft.Text("Nenhum usuário cadastrado.")]),
    )


def formulario(page: ft.Page, usuario_id: int | None = None, tipo: str = "aluno"):
    dados = {"tipo": tipo}
    if usuario_id:
        try:
            dados = api.obter_usuario(usuario_id)
        except api.ErroAPI:
            c.mostrar(
                page,
                ft.Text("Não foi possível abrir o usuário."),
                ft.OutlinedButton(
                    "Voltar", on_click=lambda e: navegacao.ir("gerenciar_usuarios", tipo=tipo)
                ),
            )
            return

    aviso = c.aviso_erro()
    campo_nome = ft.TextField(label="Nome", value=dados.get("nome", ""))
    campo_email = ft.TextField(label="E-mail", value=dados.get("email", ""))
    campo_ano = ft.TextField(
        label="Ano escolar (ex.: 8º ano)",
        value=dados.get("ano_escolar") or "",
        visible=dados["tipo"] == "aluno",
    )
    campo_senha = ft.TextField(
        label="Nova senha (deixe em branco para manter)" if usuario_id else "Senha",
        password=True,
        can_reveal_password=True,
    )

    def mudar_tipo(e):
        campo_ano.visible = e.control.value == "aluno"
        page.update()

    campo_tipo = seletor_tipo(dados["tipo"], mudar_tipo)

    def salvar(e):
        nome = (campo_nome.value or "").strip()
        email = (campo_email.value or "").strip()
        senha = (campo_senha.value or "").strip()
        if not nome or not email or (not usuario_id and not senha):
            aviso.value = "Preencha nome, e-mail e senha."
            page.update()
            return

        corpo = {
            "nome": nome,
            "email": email,
            "tipo": campo_tipo.value,
            "ano_escolar": (campo_ano.value or "").strip() or None,
            "senha": senha or None,
        }
        try:
            if usuario_id:
                api.atualizar_usuario(usuario_id, corpo)
            else:
                api.criar_usuario(corpo)
        except api.ErroAPI as erro:
            aviso.value = (
                "Já existe um usuário com esse e-mail."
                if erro.status == 409
                else "Não foi possível salvar o usuário."
            )
            page.update()
            return
        navegacao.ir("gerenciar_usuarios", tipo=campo_tipo.value)

    c.mostrar(
        page,
        ft.Row(
            [
                c.botao_voltar("gerenciar_usuarios", tipo=tipo),
                c.titulo("Editar usuário" if usuario_id else "Novo usuário"),
            ]
        ),
        ft.Text("Tipo de usuário", weight=ft.FontWeight.BOLD),
        campo_tipo,
        campo_nome,
        campo_email,
        campo_ano,
        campo_senha,
        aviso,
        ft.Row(
            [
                ft.OutlinedButton(
                    "Cancelar", on_click=lambda e: navegacao.ir("gerenciar_usuarios", tipo=tipo)
                ),
                ft.FilledButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
            ]
        ),
    )