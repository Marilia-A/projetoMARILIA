import flet as ft

import api
import componentes as c
import navegacao
import sessao


def avisar_badges(page: ft.Page, badges: list):
    def ver_conquistas(e):
        page.pop_dialog()
        navegacao.ir("conquistas")

    page.show_dialog(
        ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.AMBER), ft.Text("Nova conquista!")]),
            content=ft.Column(
                [ft.Text(f"{b['nome']}: {b['criterio']}", size=16) for b in badges],
                tight=True,
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Ver conquistas", on_click=ver_conquistas),
            ],
        )
    )


def mostrar(page: ft.Page, roteiro_id: int):
    try:
        roteiro = api.obter_roteiro(roteiro_id)
    except api.ErroAPI:
        c.mostrar(
            page,
            ft.Text("Não foi possível abrir o roteiro."),
            ft.OutlinedButton("Voltar aos roteiros", on_click=lambda e: navegacao.ir("roteiros")),
        )
        return

    usuario = sessao.usuario()
    eh_aluno = usuario["tipo"] == "aluno"
    progresso = {"status": None}

    if eh_aluno:
        try:
            progresso["status"] = api.listar_progresso(usuario["id"]).get(roteiro_id)
            if progresso["status"] is None:
                api.atualizar_progresso(usuario["id"], roteiro_id, "em_andamento")
                progresso["status"] = "em_andamento"
        except api.ErroAPI:
            pass

    capa = [ft.Text(roteiro["descricao"], size=16)]
    if roteiro["imagem"]:
        capa.append(c.imagem(roteiro["imagem"]))
    capa.append(ft.Text("Materiais", size=18, weight=ft.FontWeight.BOLD))
    capa.append(ft.Text(roteiro["materiais"], size=16))
    paginas = [("O que vamos fazer", capa)]

    for etapa in roteiro["etapas"]:
        conteudo = [ft.Text(etapa["conteudo"], size=16)]
        if etapa["imagem"]:
            conteudo.append(c.imagem(etapa["imagem"]))
        paginas.append((f"Passo {etapa['ordem']}", conteudo))

    paginas.append(
        (
            "Código",
            [
                ft.Container(
                    content=ft.Text(
                        roteiro["codigo_comentado"],
                        font_family="Consolas",
                        color=ft.Colors.WHITE,
                        selectable=True,
                    ),
                    bgcolor=ft.Colors.BLACK,
                    padding=15,
                    border_radius=8,
                )
            ],
        )
    )

    nivel = ft.RadioGroup(
        value="superficial",
        content=ft.Row(
            [
                ft.Radio(value="superficial", label="Superficial"),
                ft.Radio(value="moderado", label="Moderado"),
                ft.Radio(value="detalhado", label="Detalhado"),
            ]
        ),
    )
    campo_pergunta = ft.TextField(
        label="Escreva sua dúvida sobre este roteiro",
        multiline=True,
        min_lines=2,
        max_lines=5,
    )
    carregando = ft.ProgressRing(width=24, height=24, visible=False)
    resposta_tutor = ft.Markdown(
        "",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
    )

    def perguntar(e):
        texto = (campo_pergunta.value or "").strip()
        if not texto:
            return
        botao_perguntar.disabled = True
        carregando.visible = True
        resposta_tutor.value = ""
        page.update()
        try:
            resposta_tutor.value = api.perguntar_tutor(
                usuario["id"], roteiro_id, nivel.value, texto
            )
        except api.ErroAPI:
            resposta_tutor.value = "Não foi possível falar com o tutor. Tente de novo."
        botao_perguntar.disabled = False
        carregando.visible = False
        page.update()

    botao_perguntar = ft.FilledButton("Perguntar", on_click=perguntar)

    pagina_duvidas = [
        ft.Text("Escolha o nível da explicação:", size=16),
        nivel,
        campo_pergunta,
        ft.Row([botao_perguntar, carregando]),
        resposta_tutor,
    ]

    if eh_aluno:
        texto_concluido = ft.Text(
            "Roteiro concluído!", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD, size=16
        )
        aviso_erro = ft.Text("", color=ft.Colors.RED)

        def ajustar_conclusao():
            concluido = progresso["status"] == "concluido"
            botao_concluir.visible = not concluido
            texto_concluido.visible = concluido

        def concluir(e):
            novas = []
            try:
                resultado = api.atualizar_progresso(usuario["id"], roteiro_id, "concluido")
                progresso["status"] = "concluido"
                novas = resultado.get("novas_badges", [])
                aviso_erro.value = ""
            except api.ErroAPI as erro:
                aviso_erro.value = erro.mensagem
            ajustar_conclusao()
            page.update()
            if novas:
                avisar_badges(page, novas)

        botao_concluir = ft.FilledButton(
            "Marcar como concluído", icon=ft.Icons.CHECK, on_click=concluir
        )
        ajustar_conclusao()
        pagina_duvidas += [ft.Divider(), botao_concluir, texto_concluido, aviso_erro]

    paginas.append(("Tire suas dúvidas", pagina_duvidas))

    estado = {"atual": 0}

    def mudar_pagina(passo):
        estado["atual"] += passo
        desenhar()

    def desenhar():
        i = estado["atual"]
        nome, conteudo = paginas[i]
        c.mostrar(
            page,
            ft.Row([c.botao_voltar("roteiros"), c.titulo(roteiro["titulo"])]),
            ft.Text(nome, size=20, weight=ft.FontWeight.BOLD),
            *conteudo,
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Voltar", disabled=i == 0, on_click=lambda e: mudar_pagina(-1)
                    ),
                    ft.Text(f"Página {i + 1} de {len(paginas)}"),
                    ft.FilledButton(
                        "Avançar",
                        disabled=i == len(paginas) - 1,
                        on_click=lambda e: mudar_pagina(1),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    desenhar()