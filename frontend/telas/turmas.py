import flet as ft

import api
import componentes as c
import navegacao
import sessao


def mostrar(page: ft.Page):
    usuario = sessao.usuario()
    admin = sessao.eh_admin()
    cabecalho = ft.Row([c.botao_voltar("roteiros"), c.titulo("Turmas")])
    aviso = c.aviso_erro()

    try:
        turmas = api.listar_turmas(None if admin else usuario["id"])
    except api.ErroAPI as erro:
        c.mostrar(page, cabecalho, ft.Text(erro.mensagem))
        return

    def excluir(turma_id):
        try:
            api.excluir_turma(turma_id)
        except api.ErroAPI as erro:
            aviso.value = erro.mensagem
            page.update()
            return
        navegacao.ir("turmas")

    def cartao(t):
        subtitulo = f'Código {t["codigo"]} — {t["total_alunos"]} aluno(s)'
        if admin:
            subtitulo += f' — Prof. {t["professor_nome"]}'
        return ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.Icons.GROUPS),
                title=ft.Text(t["nome"], weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(subtitulo),
                on_click=lambda e: navegacao.ir("turma", turma_id=t["id"]),
                trailing=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Editar",
                            on_click=lambda e: navegacao.ir("formulario_turma", turma_id=t["id"]),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            tooltip="Excluir",
                            on_click=lambda e: c.confirmar_exclusao(
                                page,
                                "Excluir turma",
                                f'Excluir a turma "{t["nome"]}"? Os alunos não serão apagados.',
                                lambda: excluir(t["id"]),
                            ),
                        ),
                    ],
                    tight=True,
                ),
            )
        )

    c.mostrar(
        page,
        cabecalho,
        ft.FilledButton(
            "Nova turma", icon=ft.Icons.ADD, on_click=lambda e: navegacao.ir("formulario_turma")
        ),
        aviso,
        *([cartao(t) for t in turmas] or [ft.Text("Nenhuma turma cadastrada.")]),
    )


def formulario(page: ft.Page, turma_id: int | None = None):
    usuario = sessao.usuario()
    admin = sessao.eh_admin()
    dados = {}
    try:
        if turma_id:
            dados = api.obter_turma(turma_id)
        professores = api.listar_usuarios("professor") if admin else []
    except api.ErroAPI:
        c.mostrar(
            page,
            ft.Text("Não foi possível abrir a turma."),
            ft.OutlinedButton("Voltar", on_click=lambda e: navegacao.ir("turmas")),
        )
        return

    aviso = c.aviso_erro()
    campo_nome = ft.TextField(label="Nome da turma (ex.: 8º A)", value=dados.get("nome", ""))
    seletor_professor = None
    if admin:
        valor = str(dados["professor_id"]) if dados else None
        seletor_professor = ft.RadioGroup(
            value=valor,
            content=ft.Column(
                [ft.Radio(value=str(p["id"]), label=p["nome"]) for p in professores]
            ),
        )

    def salvar(e):
        nome = (campo_nome.value or "").strip()
        if admin:
            professor_id = seletor_professor.value
        else:
            professor_id = dados.get("professor_id", usuario["id"])
        if not nome or not professor_id:
            aviso.value = "Preencha o nome e escolha o professor."
            page.update()
            return
        corpo = {"nome": nome, "professor_id": int(professor_id)}
        try:
            if turma_id:
                api.atualizar_turma(turma_id, corpo)
            else:
                api.criar_turma(corpo)
        except api.ErroAPI as erro:
            aviso.value = erro.mensagem
            page.update()
            return
        navegacao.ir("turmas")

    controles = [
        ft.Row(
            [c.botao_voltar("turmas"), c.titulo("Editar turma" if turma_id else "Nova turma")]
        ),
        campo_nome,
    ]
    if admin:
        controles.append(ft.Text("Professor responsável", weight=ft.FontWeight.BOLD))
        controles.append(
            seletor_professor if professores else ft.Text("Nenhum professor cadastrado.")
        )
    controles += [
        aviso,
        ft.Row(
            [
                ft.OutlinedButton("Cancelar", on_click=lambda e: navegacao.ir("turmas")),
                ft.FilledButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
            ]
        ),
    ]
    c.mostrar(page, *controles)


def detalhe(page: ft.Page, turma_id: int):
    try:
        turma = api.obter_turma(turma_id)
        todos_alunos = api.listar_usuarios("aluno")
    except api.ErroAPI:
        c.mostrar(
            page,
            ft.Text("Não foi possível abrir a turma."),
            ft.OutlinedButton("Voltar", on_click=lambda e: navegacao.ir("turmas")),
        )
        return

    aviso = c.aviso_erro()
    na_turma = {a["id"] for a in turma["alunos"]}
    disponiveis = [a for a in todos_alunos if a["id"] not in na_turma]

    def alterar(acao, aluno_id):
        try:
            acao(turma_id, aluno_id)
        except api.ErroAPI as erro:
            aviso.value = erro.mensagem
            page.update()
            return
        navegacao.ir("turma", turma_id=turma_id)

    def descricao(a):
        return f'{a["email"]} — {a["ano_escolar"]}' if a["ano_escolar"] else a["email"]

    membros = [
        ft.ListTile(
            leading=ft.Icon(ft.Icons.PERSON),
            title=ft.Text(a["nome"]),
            subtitle=ft.Text(descricao(a)),
            trailing=ft.IconButton(
                icon=ft.Icons.PERSON_REMOVE,
                icon_color=ft.Colors.RED,
                tooltip="Remover da turma",
                on_click=lambda e, aid=a["id"]: alterar(api.remover_aluno_turma, aid),
            ),
        )
        for a in turma["alunos"]
    ]

    lista_disponiveis = ft.Column()

    def filtrar(e=None):
        texto = (campo_filtro.value or "").strip().lower()
        lista_disponiveis.controls = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON_OUTLINE),
                title=ft.Text(a["nome"]),
                subtitle=ft.Text(descricao(a)),
                trailing=ft.IconButton(
                    icon=ft.Icons.PERSON_ADD,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Adicionar à turma",
                    on_click=lambda e, aid=a["id"]: alterar(api.adicionar_aluno_turma, aid),
                ),
            )
            for a in disponiveis
            if texto in a["nome"].lower() or texto in a["email"].lower()
        ] or [ft.Text("Nenhum aluno disponível.")]
        if e:
            page.update()

    campo_filtro = ft.TextField(
        label="Filtrar alunos por nome ou e-mail", prefix_icon=ft.Icons.SEARCH, on_change=filtrar
    )
    filtrar()

    c.mostrar(
        page,
        ft.Row([c.botao_voltar("turmas"), c.titulo(turma["nome"])]),
        ft.Text(f'Código: {turma["codigo"]} — Professor: {turma["professor_nome"]}', size=16),
        ft.FilledButton(
            "Ver progresso",
            icon=ft.Icons.INSIGHTS,
            on_click=lambda e: navegacao.ir("dashboard", turma_id=turma_id),
        ),
        aviso,
        ft.Text(
            f'Alunos da turma ({len(turma["alunos"])})', size=20, weight=ft.FontWeight.BOLD
        ),
        *(membros or [ft.Text("Nenhum aluno na turma.")]),
        ft.Divider(),
        ft.Text("Adicionar alunos", size=20, weight=ft.FontWeight.BOLD),
        campo_filtro,
        lista_disponiveis,
    )