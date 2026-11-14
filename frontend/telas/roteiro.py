import flet as ft

import api
import componentes as c
import navegacao
import sessao

ESTILO_CODIGO = ft.MarkdownStyleSheet(
    code_text_style=ft.TextStyle(font_family="Consolas", size=15)
)


def markdown(texto: str) -> ft.Markdown:
    return ft.Markdown(
        texto,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
        code_style_sheet=ESTILO_CODIGO,
    )


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

    capa = [ft.Text(roteiro["descricao"], size=17, color=c.TEXTO)]
    if roteiro["imagem"]:
        capa.append(c.imagem(roteiro["imagem"]))
    capa.append(
        ft.Row(
            [ft.Icon(ft.Icons.INVENTORY_2, color=c.LARANJA), ft.Text("Materiais", size=19, weight=ft.FontWeight.BOLD, color=c.TEXTO)]
        )
    )
    capa.append(ft.Text(roteiro["materiais"], size=17, color=c.TEXTO))
    paginas = [("O que vamos fazer", capa)]

    for etapa in roteiro["etapas"]:
        conteudo = [ft.Text(etapa["conteudo"], size=17, color=c.TEXTO)]
        if etapa["imagem"]:
            conteudo.append(c.imagem(etapa["imagem"]))
        paginas.append((f"Passo {etapa['ordem']}", conteudo))

    paginas.append(
        (
            "Código",
            [markdown(f"```cpp\n{roteiro['codigo_comentado'].strip()}\n```")],
        )
    )

    if roteiro.get("sugestoes"):
        paginas.append(
            (
                "Sugestões de experimentos",
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.AUTO_AWESOME, color=c.AMARELO),
                            ft.Text("Agora que o roteiro funcionou, que tal experimentar?", size=17, color=c.TEXTO),
                        ]
                    ),
                    markdown(roteiro["sugestoes"]),
                ],
            )
        )

    nivel = ft.RadioGroup(
        value="superficial",
        content=ft.Row(
            [
                ft.Radio(value="superficial", label="Superficial (curtinha)"),
                ft.Radio(value="moderado", label="Moderado"),
                ft.Radio(value="detalhado", label="Detalhado (completa)"),
            ]
        ),
    )
    campo_pergunta = ft.TextField(
        label="Escreva sua dúvida sobre este roteiro",
        multiline=True,
        min_lines=2,
        max_lines=5,
        max_length=500,
        border_radius=14,
        filled=True,
        bgcolor=ft.Colors.WHITE,
        text_size=16,
    )
    carregando = ft.ProgressRing(width=24, height=24, visible=False, color=c.ROXO)
    resposta_tutor = markdown("")
    bolha_resposta = ft.Container(
        content=ft.Row(
            [
                c.circulo_icone(ft.Icons.SMART_TOY, c.ROXO, 44),
                ft.Container(content=resposta_tutor, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=12,
        ),
        bgcolor="#EFEAFF",
        border_radius=18,
        padding=16,
        visible=False,
    )

    def perguntar(e):
        texto = (campo_pergunta.value or "").strip()
        if not texto:
            return
        botao_perguntar.disabled = True
        carregando.visible = True
        resposta_tutor.value = ""
        bolha_resposta.visible = False
        page.update()
        try:
            resposta_tutor.value = api.perguntar_tutor(
                usuario["id"], roteiro_id, nivel.value, texto
            )
        except api.ErroAPI as erro:
            resposta_tutor.value = (
                erro.mensagem
                if erro.status in (422, 503)
                else "Não foi possível falar com o tutor. Tente de novo."
            )
        botao_perguntar.disabled = False
        carregando.visible = False
        bolha_resposta.visible = bool(resposta_tutor.value)
        page.update()

    botao_perguntar = c.botao_principal("Perguntar", ft.Icons.SEND, perguntar)

    apresentacao = ft.Container(
        content=ft.Row(
            [
                c.circulo_icone(ft.Icons.SMART_TOY, c.ROXO, 56),
                ft.Text(
                    "Oi! Eu sou a tutora do MARILIA. Escolha o nível da explicação e me pergunte "
                    "o que quiser sobre este roteiro.",
                    size=16,
                    color=c.TEXTO,
                    expand=True,
                ),
            ],
            spacing=14,
        ),
        bgcolor="#EFEAFF",
        border_radius=18,
        padding=16,
    )

    pagina_duvidas = [
        apresentacao,
        ft.Text("Escolha o nível da explicação:", size=17, weight=ft.FontWeight.BOLD, color=c.TEXTO),
        nivel,
        campo_pergunta,
        ft.Row([botao_perguntar, carregando]),
        bolha_resposta,
    ]

    if eh_aluno:
        texto_concluido = ft.Text(
            "Roteiro concluído! Mandou bem!", color=c.VERDE, weight=ft.FontWeight.BOLD, size=18
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

        botao_concluir = c.botao_principal("Marcar como concluído", ft.Icons.CHECK, concluir, cor=c.VERDE)
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
        ultima = i == len(paginas) - 1
        c.mostrar(
            page,
            c.cabecalho(roteiro["titulo"], ft.Icons.MEMORY, voltar="roteiros", subtitulo=nome),
            ft.Row(
                [
                    ft.Text(f"Página {i + 1} de {len(paginas)}", size=15, color=c.TEXTO_SUAVE),
                    ft.ProgressBar(
                        value=(i + 1) / len(paginas), bar_height=10, border_radius=5,
                        color=c.ROXO, bgcolor="#E4DCFF", expand=True,
                    ),
                ],
                spacing=12,
            ),
            c.painel(
                ft.Text(nome, size=22, weight=ft.FontWeight.BOLD, color=c.ROXO),
                *conteudo,
            ),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Voltar",
                        icon=ft.Icons.ARROW_BACK,
                        disabled=i == 0,
                        on_click=lambda e: mudar_pagina(-1),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=14),
                            padding=ft.Padding.symmetric(horizontal=22, vertical=16),
                        ),
                    ),
                    c.botao_principal(
                        "Avançar", ft.Icons.ARROW_FORWARD, lambda e: mudar_pagina(1), desativado=ultima
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    desenhar()
