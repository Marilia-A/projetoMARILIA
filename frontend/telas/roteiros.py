import flet as ft

import api
import componentes as c
import navegacao
import sessao


ICONES_ROTEIROS = [
    ft.Icons.LIGHTBULB,
    ft.Icons.TRAFFIC,
    ft.Icons.TOUCH_APP,
    ft.Icons.NIGHTLIGHT,
    ft.Icons.SENSORS,
    ft.Icons.MEMORY,
]


def icone_status(status):
    if status == "concluido":
        return ft.Icon(ft.Icons.CHECK_CIRCLE, color=c.VERDE, size=32, tooltip="Concluído")
    if status == "em_andamento":
        return ft.Icon(ft.Icons.TIMELAPSE, color=c.LARANJA, size=32, tooltip="Em andamento")
    return ft.Icon(ft.Icons.CHEVRON_RIGHT, color=c.CINZA, size=32)


def mostrar(page: ft.Page):
    resultados = ft.Column(spacing=12)
    eh_aluno = sessao.usuario()["tipo"] == "aluno"
    barra = ft.ProgressBar(value=0, bar_height=14, border_radius=7, color=c.VERDE, bgcolor="#E3F7EE")
    texto_barra = ft.Text(size=17, weight=ft.FontWeight.BOLD, color=c.TEXTO)
    painel_progresso = ft.Container(
        content=ft.Row(
            [
                c.circulo_icone(ft.Icons.STAR, c.AMARELO, 48),
                ft.Column([texto_barra, barra], spacing=8, expand=True),
            ],
            spacing=16,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=18,
        padding=16,
        shadow=c.sombra(),
        visible=eh_aluno,
    )

    def atualizar_barra(progresso: dict):
        try:
            total = len(api.listar_roteiros())
        except api.ErroAPI:
            return
        concluidos = sum(1 for s in progresso.values() if s == "concluido")
        barra.value = concluidos / total if total else 0
        texto_barra.value = f"Seu progresso: {concluidos} de {total} roteiros concluídos"
        if total and concluidos == total:
            texto_barra.value += " – parabéns, você concluiu todos!"

    def carregar():
        texto = (campo_busca.value or "").strip()
        try:
            roteiros = api.listar_roteiros(texto or None)
        except api.ErroAPI as erro:
            resultados.controls = [ft.Text(erro.mensagem)]
            page.update()
            return

        progresso = {}
        if eh_aluno:
            try:
                progresso = api.listar_progresso(sessao.usuario()["id"])
            except api.ErroAPI:
                pass
            atualizar_barra(progresso)

        if not roteiros:
            resultados.controls = [
                ft.Text("Nenhum roteiro encontrado." if texto else "Nenhum roteiro cadastrado.")
            ]
        else:
            resultados.controls = [
                c.cartao(
                    r["titulo"],
                    r["descricao"],
                    icone=ICONES_ROTEIROS[i % len(ICONES_ROTEIROS)],
                    cor=c.CORES_CARTOES[i % len(c.CORES_CARTOES)],
                    direita=icone_status(progresso.get(r["id"])),
                    ao_clicar=lambda e, rid=r["id"]: navegacao.ir("roteiro", roteiro_id=rid),
                )
                for i, r in enumerate(roteiros)
            ]
        page.update()

    linha_busca, campo_busca = c.barra_busca("Buscar roteiro por palavra-chave", carregar)

    ir = navegacao.ir
    botoes = [
        c.botao_menu("Glossário", ft.Icons.MENU_BOOK, c.AZUL, lambda e: ir("glossario")),
    ]
    if eh_aluno:
        botoes.append(c.botao_menu("Conquistas", ft.Icons.EMOJI_EVENTS, c.LARANJA, lambda e: ir("conquistas")))
        botoes.append(c.botao_menu("Minhas turmas", ft.Icons.GROUPS, c.VERDE, lambda e: ir("minhas_turmas")))
    if sessao.pode_gerenciar():
        botoes.append(c.botao_menu("Turmas", ft.Icons.GROUPS, c.VERDE, lambda e: ir("turmas")))
        botoes.append(c.botao_menu("Gerenciar roteiros", ft.Icons.SETTINGS, c.ROSA, lambda e: ir("gerenciar_roteiros")))
    if sessao.eh_admin():
        botoes.append(c.botao_menu("Gerenciar usuários", ft.Icons.PEOPLE, c.ROXO, lambda e: ir("gerenciar_usuarios")))

    nome = (sessao.usuario()["nome"] or "").split(" ")[0]
    subtitulo = "Escolha um roteiro e mão na massa!" if eh_aluno else "Acompanhe suas turmas e os conteúdos"
    sair = ft.IconButton(
        icon=ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, tooltip="Sair", on_click=lambda e: ir("login")
    )
    atualizar = ft.IconButton(
        icon=ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, tooltip="Atualizar", on_click=lambda e: carregar()
    )

    c.mostrar(
        page,
        c.cabecalho(f"Olá, {nome}!", ft.Icons.ROCKET_LAUNCH, subtitulo=subtitulo, extras=[atualizar, sair]),
        ft.Row(botoes, wrap=True, spacing=10, run_spacing=10),
        painel_progresso,
        linha_busca,
        ft.Text("Roteiros", size=22, weight=ft.FontWeight.BOLD, color=c.TEXTO),
        resultados,
    )
    carregar()
