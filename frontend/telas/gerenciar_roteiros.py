import flet as ft

import api
import componentes as c
import navegacao


def mostrar(page: ft.Page):
    cabecalho = c.cabecalho("Gerenciar roteiros", ft.Icons.SETTINGS, voltar="roteiros",
                            subtitulo="Crie, edite ou exclua os roteiros do app")
    try:
        roteiros = api.listar_roteiros()
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho, ft.Text(erro.mensagem))
        return

    def excluir(roteiro_id):
        try:
            api.excluir_roteiro(roteiro_id)
        except api.ErroAPI:
            pass
        navegacao.ir("gerenciar_roteiros")

    linhas = [
        c.cartao_gerenciar(
            r["titulo"],
            r["descricao"],
            lambda e, rid=r["id"]: navegacao.ir("formulario_roteiro", roteiro_id=rid),
            lambda e, r=r: c.confirmar_exclusao(
                page,
                "Excluir roteiro",
                f'Excluir "{r["titulo"]}"? O progresso dos alunos '
                "nesse roteiro também será apagado.",
                lambda: excluir(r["id"]),
            ),
            icone=ft.Icons.MEMORY,
            cor=c.CORES_CARTOES[i % len(c.CORES_CARTOES)],
        )
        for i, r in enumerate(roteiros)
    ]
    c.mostrar(
        page,
        cabecalho,
        ft.Row([c.botao_principal("Novo roteiro", ft.Icons.ADD, lambda e: navegacao.ir("formulario_roteiro"))]),
        *(linhas or [ft.Text("Nenhum roteiro cadastrado.", size=16, color=c.TEXTO_SUAVE)]),
    )


def formulario(page: ft.Page, roteiro_id: int | None = None):
    dados = {}
    if roteiro_id:
        try:
            dados = api.obter_roteiro(roteiro_id)
        except api.ErroAPI:
            c.mostrar(
                page,
                ft.Text("Não foi possível abrir o roteiro."),
                ft.OutlinedButton("Voltar", on_click=lambda e: navegacao.ir("gerenciar_roteiros")),
            )
            return

    aviso = c.aviso_erro()

    campo_titulo = c.campo("Título", value=dados.get("titulo", ""))
    campo_descricao = c.campo(
        "Descrição", value=dados.get("descricao", ""), multiline=True, min_lines=2
    )
    campo_materiais = c.campo(
        "Materiais", value=dados.get("materiais", ""), multiline=True, min_lines=2
    )
    campo_codigo = c.campo(
        "Código comentado",
        value=dados.get("codigo_comentado", ""),
        multiline=True,
        min_lines=6,
        text_style=ft.TextStyle(font_family="Consolas"),
    )
    campo_sugestoes = c.campo(
        "Sugestões de experimentos (opcional, uma por linha começando com -)",
        value=dados.get("sugestoes") or "",
        multiline=True,
        min_lines=3,
    )
    imagem_roteiro = c.seletor_imagem(page, dados.get("imagem"), "roteiros", aviso)

    etapas = []
    coluna_etapas = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def desenhar_etapas():
        for i, et in enumerate(etapas, start=1):
            et["rotulo"].value = f"Passo {i}"
        coluna_etapas.controls = [et["cartao"] for et in etapas]

    def remover_etapa(et):
        etapas.remove(et)
        desenhar_etapas()
        page.update()

    def adicionar_etapa(conteudo="", caminho=None):
        et = {
            "rotulo": ft.Text(weight=ft.FontWeight.BOLD, size=17, color=c.ROXO),
            "campo": c.campo("Conteúdo", value=conteudo, multiline=True, min_lines=2),
            "imagem": c.seletor_imagem(page, caminho, "roteiros", aviso),
        }
        et["cartao"] = ft.Container(
            bgcolor="#EFEAFF",
            border_radius=16,
            padding=14,
            content=ft.Column(
                    [
                        ft.Row(
                            [
                                et["rotulo"],
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Remover passo",
                                    on_click=lambda e: remover_etapa(et),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        et["campo"],
                        et["imagem"][0],
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )
        etapas.append(et)

    for et in dados.get("etapas", []):
        adicionar_etapa(et["conteudo"], et["imagem"])
    desenhar_etapas()

    def novo_passo(e):
        adicionar_etapa()
        desenhar_etapas()
        page.update()

    def salvar(e):
        obrigatorios = [campo_titulo, campo_descricao, campo_materiais, campo_codigo]
        vazios = any(not (cp.value or "").strip() for cp in obrigatorios) or any(
            not (et["campo"].value or "").strip() for et in etapas
        )
        if vazios:
            aviso.value = "Preencha todos os campos e o conteúdo de cada passo."
            page.update()
            return

        corpo = {
            "titulo": campo_titulo.value.strip(),
            "descricao": campo_descricao.value.strip(),
            "materiais": campo_materiais.value.strip(),
            "codigo_comentado": campo_codigo.value,
            "imagem": imagem_roteiro[1](),
            "sugestoes": (campo_sugestoes.value or "").strip() or None,
            "etapas": [
                {
                    "ordem": i,
                    "conteudo": et["campo"].value.strip(),
                    "imagem": et["imagem"][1](),
                }
                for i, et in enumerate(etapas, start=1)
            ],
        }
        try:
            if roteiro_id:
                api.atualizar_roteiro(roteiro_id, corpo)
            else:
                api.criar_roteiro(corpo)
        except api.ErroAPI:
            aviso.value = "Não foi possível salvar o roteiro."
            page.update()
            return
        navegacao.ir("gerenciar_roteiros")

    c.mostrar(
        page,
        c.cabecalho("Editar roteiro" if roteiro_id else "Novo roteiro", ft.Icons.EDIT_NOTE,
                    voltar="gerenciar_roteiros"),
        c.painel(
            campo_titulo,
            campo_descricao,
            campo_materiais,
            ft.Text("Imagem do roteiro", size=16, weight=ft.FontWeight.BOLD, color=c.TEXTO),
            imagem_roteiro[0],
            campo_codigo,
            esticar=True,
        ),
        c.painel(
            ft.Text("Passos", size=20, weight=ft.FontWeight.BOLD, color=c.TEXTO),
            coluna_etapas,
            ft.Row([c.botao_secundario("Adicionar passo", ft.Icons.ADD, novo_passo)]),
            esticar=True,
        ),
        c.painel(campo_sugestoes, esticar=True),
        aviso,
        c.botoes_salvar(lambda e: navegacao.ir("gerenciar_roteiros"), salvar),
    )