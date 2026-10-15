import flet as ft

import api
import componentes as c
import navegacao


def mostrar(page: ft.Page):
    cabecalho = ft.Row([c.botao_voltar("roteiros"), c.titulo("Gerenciar roteiros")])
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
        )
        for r in roteiros
    ]
    c.mostrar(
        page,
        cabecalho,
        ft.FilledButton(
            "Novo roteiro", icon=ft.Icons.ADD, on_click=lambda e: navegacao.ir("formulario_roteiro")
        ),
        *(linhas or [ft.Text("Nenhum roteiro cadastrado.")]),
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

    campo_titulo = ft.TextField(label="Título", value=dados.get("titulo", ""))
    campo_descricao = ft.TextField(
        label="Descrição", value=dados.get("descricao", ""), multiline=True, min_lines=2
    )
    campo_materiais = ft.TextField(
        label="Materiais", value=dados.get("materiais", ""), multiline=True, min_lines=2
    )
    campo_codigo = ft.TextField(
        label="Código comentado",
        value=dados.get("codigo_comentado", ""),
        multiline=True,
        min_lines=6,
        text_style=ft.TextStyle(font_family="Consolas"),
    )
    imagem_roteiro = c.seletor_imagem(page, dados.get("imagem"), "roteiros", aviso)

    etapas = []
    coluna_etapas = ft.Column()

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
            "rotulo": ft.Text(weight=ft.FontWeight.BOLD),
            "campo": ft.TextField(label="Conteúdo", value=conteudo, multiline=True, min_lines=2),
            "imagem": c.seletor_imagem(page, caminho, "roteiros", aviso),
        }
        et["cartao"] = ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                et["rotulo"],
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Remover passo",
                                    on_click=lambda e: remover_etapa(et),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        et["campo"],
                        et["imagem"][0],
                    ]
                ),
            )
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
        ft.Row(
            [
                c.botao_voltar("gerenciar_roteiros"),
                c.titulo("Editar roteiro" if roteiro_id else "Novo roteiro"),
            ]
        ),
        campo_titulo,
        campo_descricao,
        campo_materiais,
        ft.Text("Imagem do roteiro", weight=ft.FontWeight.BOLD),
        imagem_roteiro[0],
        campo_codigo,
        ft.Text("Passos", size=20, weight=ft.FontWeight.BOLD),
        coluna_etapas,
        ft.OutlinedButton("Adicionar passo", icon=ft.Icons.ADD, on_click=novo_passo),
        aviso,
        ft.Row(
            [
                ft.OutlinedButton(
                    "Cancelar", on_click=lambda e: navegacao.ir("gerenciar_roteiros")
                ),
                ft.FilledButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
            ]
        ),
    )