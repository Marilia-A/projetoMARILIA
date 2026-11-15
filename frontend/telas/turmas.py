import flet as ft

import api
import componentes as c
import navegacao
import sessao


def mostrar(page: ft.Page):
    usuario = sessao.usuario()
    admin = sessao.eh_admin()
    cabecalho = c.cabecalho("Turmas", ft.Icons.GROUPS, voltar="roteiros",
                            subtitulo="Clique numa turma para ver os alunos e o progresso")
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

    def cartao(t, i):
        subtitulo = f'Código {t["codigo"]} — {t["total_alunos"]} aluno(s)'
        if admin:
            subtitulo += f' — Prof. {t["professor_nome"]}'
        return c.cartao_gerenciar(
            t["nome"],
            subtitulo,
            lambda e: navegacao.ir("formulario_turma", turma_id=t["id"]),
            lambda e: c.confirmar_exclusao(
                page,
                "Excluir turma",
                f'Excluir a turma "{t["nome"]}"? Os alunos não serão apagados.',
                lambda: excluir(t["id"]),
            ),
            icone=ft.Icons.GROUPS,
            cor=c.CORES_CARTOES[i % len(c.CORES_CARTOES)],
            ao_clicar=lambda e: navegacao.ir("turma", turma_id=t["id"]),
        )

    c.mostrar(
        page,
        cabecalho,
        ft.Row([c.botao_principal("Nova turma", ft.Icons.ADD, lambda e: navegacao.ir("formulario_turma"))]),
        aviso,
        *([cartao(t, i) for i, t in enumerate(turmas)]
          or [ft.Text("Nenhuma turma cadastrada.", size=16, color=c.TEXTO_SUAVE)]),
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
    campo_nome = c.campo("Nome da turma (ex.: 8º A)", value=dados.get("nome", ""))
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

    campos = [campo_nome]
    if admin:
        campos.append(ft.Text("Professor responsável", size=16, weight=ft.FontWeight.BOLD, color=c.TEXTO))
        campos.append(
            seletor_professor if professores else ft.Text("Nenhum professor cadastrado.")
        )
    c.mostrar(
        page,
        c.cabecalho("Editar turma" if turma_id else "Nova turma", ft.Icons.GROUP_ADD, voltar="turmas"),
        c.painel(*campos, esticar=True),
        aviso,
        c.botoes_salvar(lambda e: navegacao.ir("turmas"), salvar),
    )


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
        c.cartao(
            a["nome"],
            descricao(a),
            ft.Icons.FACE,
            c.CORES_CARTOES[i % len(c.CORES_CARTOES)],
            direita=ft.IconButton(
                icon=ft.Icons.PERSON_REMOVE,
                icon_color=ft.Colors.RED_400,
                tooltip="Remover da turma",
                on_click=lambda e, aid=a["id"]: alterar(api.remover_aluno_turma, aid),
            ),
        )
        for i, a in enumerate(turma["alunos"])
    ]

    lista_disponiveis = ft.Column()

    def filtrar(e=None):
        texto = (campo_filtro.value or "").strip().lower()
        lista_disponiveis.controls = [
            c.cartao(
                a["nome"],
                descricao(a),
                ft.Icons.PERSON_OUTLINE,
                c.CINZA,
                direita=ft.IconButton(
                    icon=ft.Icons.PERSON_ADD,
                    icon_color=c.VERDE,
                    tooltip="Adicionar à turma",
                    on_click=lambda e, aid=a["id"]: alterar(api.adicionar_aluno_turma, aid),
                ),
            )
            for a in disponiveis
            if texto in a["nome"].lower() or texto in a["email"].lower()
        ] or [ft.Text("Nenhum aluno disponível.", size=16, color=c.TEXTO_SUAVE)]
        if e:
            page.update()

    campo_filtro = c.campo("Filtrar alunos por nome ou e-mail", prefix_icon=ft.Icons.SEARCH, on_change=filtrar,
                           expand=True)
    filtrar()

    c.mostrar(
        page,
        c.cabecalho(turma["nome"], ft.Icons.GROUPS, voltar="turmas",
                    subtitulo=f'Código da turma: {turma["codigo"]} — Professor: {turma["professor_nome"]}'),
        ft.Row([c.botao_principal("Ver progresso", ft.Icons.INSIGHTS,
                                  lambda e: navegacao.ir("dashboard", turma_id=turma_id), cor=c.VERDE)]),
        aviso,
        ft.Text(f'Alunos da turma ({len(turma["alunos"])})', size=20, weight=ft.FontWeight.BOLD, color=c.TEXTO),
        *(membros or [ft.Text("Nenhum aluno na turma.", size=16, color=c.TEXTO_SUAVE)]),
        ft.Divider(),
        ft.Text("Adicionar alunos", size=20, weight=ft.FontWeight.BOLD, color=c.TEXTO),
        ft.Row([campo_filtro]),
        lista_disponiveis,
    )