import flet as ft
import httpx

API = "http://127.0.0.1:8000"
ALUNO_ID = 1  # provisório, até existir login


def main(page: ft.Page):
    page.title = "MARILIA"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    def buscar(caminho):
        resposta = httpx.get(f"{API}{caminho}", timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    def mostrar(*controles):
        page.controls.clear()
        page.add(*controles)

    def titulo(texto):
        return ft.Text(texto, size=28, weight=ft.FontWeight.BOLD)

    def imagem(caminho):
        return ft.Image(src=f"{API}/imagens/{caminho}", height=250)

    def tela_lista(e=None):
        cabecalho = ft.Row(
            [titulo("Roteiros"), ft.IconButton(icon=ft.Icons.REFRESH, on_click=tela_lista)]
        )
        try:
            roteiros = buscar("/roteiros")
        except httpx.HTTPError:
            mostrar(cabecalho, ft.Text("Não foi possível conectar ao servidor."))
            return

        if not roteiros:
            mostrar(cabecalho, ft.Text("Nenhum roteiro cadastrado."))
            return

        cartoes = [
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.MEMORY),
                    title=ft.Text(r["titulo"], weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(r["descricao"]),
                    on_click=lambda e, rid=r["id"]: tela_roteiro(rid),
                )
            )
            for r in roteiros
        ]
        mostrar(cabecalho, *cartoes)

    def tela_roteiro(roteiro_id):
        try:
            roteiro = buscar(f"/roteiros/{roteiro_id}")
        except httpx.HTTPError:
            mostrar(
                ft.Text("Não foi possível abrir o roteiro."),
                ft.OutlinedButton("Voltar aos roteiros", on_click=tela_lista),
            )
            return

        capa = [ft.Text(roteiro["descricao"], size=16)]
        if roteiro["imagem"]:
            capa.append(imagem(roteiro["imagem"]))
        capa.append(ft.Text("Materiais", size=18, weight=ft.FontWeight.BOLD))
        capa.append(ft.Text(roteiro["materiais"], size=16))
        paginas = [("O que vamos fazer", capa)]

        for etapa in roteiro["etapas"]:
            conteudo = [ft.Text(etapa["conteudo"], size=16)]
            if etapa["imagem"]:
                conteudo.append(imagem(etapa["imagem"]))
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
                r = httpx.post(
                    f"{API}/tutor/perguntar",
                    json={
                        "aluno_id": ALUNO_ID,
                        "roteiro_id": roteiro_id,
                        "nivel_profundidade": nivel.value,
                        "pergunta": texto,
                    },
                    timeout=90,
                )
                r.raise_for_status()
                resposta_tutor.value = r.json()["resposta"]
            except httpx.HTTPError:
                resposta_tutor.value = "Não foi possível falar com o tutor. Tente de novo."
            botao_perguntar.disabled = False
            carregando.visible = False
            page.update()

        botao_perguntar = ft.FilledButton("Perguntar", on_click=perguntar)

        paginas.append(
            (
                "Tire suas dúvidas",
                [
                    ft.Text("Escolha o nível da explicação:", size=16),
                    nivel,
                    campo_pergunta,
                    ft.Row([botao_perguntar, carregando]),
                    resposta_tutor,
                ],
            )
        )

        estado = {"atual": 0}

        def ir(passo):
            estado["atual"] += passo
            desenhar()

        def desenhar():
            i = estado["atual"]
            nome, conteudo = paginas[i]
            mostrar(
                ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=tela_lista),
                        titulo(roteiro["titulo"]),
                    ]
                ),
                ft.Text(nome, size=20, weight=ft.FontWeight.BOLD),
                *conteudo,
                ft.Row(
                    [
                        ft.OutlinedButton("Voltar", disabled=i == 0, on_click=lambda e: ir(-1)),
                        ft.Text(f"Página {i + 1} de {len(paginas)}"),
                        ft.FilledButton(
                            "Avançar",
                            disabled=i == len(paginas) - 1,
                            on_click=lambda e: ir(1),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )

        desenhar()

    tela_lista()


ft.run(main)