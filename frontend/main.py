import flet as ft
import httpx

API = "http://127.0.0.1:8000"
ALUNO_ID = 1  # provisório, até existir login


def main(page: ft.Page):
    page.title = "MARILIA"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    seletor_arquivos = ft.FilePicker()
    page.services.append(seletor_arquivos)

    def buscar(caminho, params=None):
        resposta = httpx.get(f"{API}{caminho}", params=params, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    def mostrar(*controles):
        page.controls.clear()
        page.add(*controles)

    def titulo(texto):
        return ft.Text(texto, size=28, weight=ft.FontWeight.BOLD)

    def imagem(caminho, altura=250):
        return ft.Image(src=f"{API}/imagens/{caminho}", height=altura)

    def barra_busca(rotulo, ao_buscar):
        campo = ft.TextField(
            label=rotulo,
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            on_submit=lambda e: ao_buscar(),
        )

        def limpar(e):
            campo.value = ""
            ao_buscar()

        linha = ft.Row(
            [
                campo,
                ft.FilledButton("Buscar", on_click=lambda e: ao_buscar()),
                ft.IconButton(icon=ft.Icons.CLEAR, tooltip="Limpar busca", on_click=limpar),
            ]
        )
        return linha, campo

    def seletor_imagem(caminho, pasta, aviso):
        estado = {"caminho": caminho}
        area = ft.Row()

        async def escolher(e):
            arquivos = await seletor_arquivos.pick_files(
                allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE
            )
            if not arquivos:
                return
            arq = arquivos[0]
            try:
                with open(arq.path, "rb") as f:
                    r = httpx.post(
                        f"{API}/upload/{pasta}",
                        files={"arquivo": (arq.name, f)},
                        timeout=30,
                    )
                r.raise_for_status()
                estado["caminho"] = r.json()["caminho"]
                aviso.value = ""
            except httpx.HTTPStatusError as erro:
                aviso.value = erro.response.json().get("detail", "Erro ao enviar a imagem.")
            except (httpx.HTTPError, OSError):
                aviso.value = "Não foi possível enviar a imagem."
            atualizar()
            page.update()

        def remover(e):
            estado["caminho"] = None
            atualizar()
            page.update()

        def atualizar():
            if estado["caminho"]:
                area.controls = [
                    imagem(estado["caminho"], altura=120),
                    ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Remover imagem", on_click=remover),
                ]
            else:
                area.controls = [
                    ft.OutlinedButton("Escolher imagem", icon=ft.Icons.IMAGE, on_click=escolher)
                ]

        atualizar()
        return area, lambda: estado["caminho"]

    def confirmar_exclusao(titulo_dialogo, mensagem, caminho_api, depois):
        def excluir(e):
            page.pop_dialog()
            try:
                httpx.delete(f"{API}{caminho_api}", timeout=10).raise_for_status()
            except httpx.HTTPError:
                pass
            depois()

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(titulo_dialogo),
                content=ft.Text(mensagem),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton("Excluir", on_click=excluir),
                ],
            )
        )

    def cartao_gerenciar(titulo_item, subtitulo, ao_editar, ao_excluir):
        return ft.Card(
            content=ft.ListTile(
                title=ft.Text(titulo_item, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(subtitulo, max_lines=2),
                trailing=ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=ao_editar),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            tooltip="Excluir",
                            on_click=ao_excluir,
                        ),
                    ],
                    tight=True,
                ),
            )
        )

    # ---------- Telas do aluno ----------

    def tela_lista(e=None):
        resultados = ft.Column()

        def carregar():
            texto = (campo_busca.value or "").strip()
            try:
                roteiros = buscar("/roteiros", {"busca": texto} if texto else None)
            except httpx.HTTPError:
                resultados.controls = [ft.Text("Não foi possível conectar ao servidor.")]
                page.update()
                return

            if not roteiros:
                resultados.controls = [
                    ft.Text("Nenhum roteiro encontrado." if texto else "Nenhum roteiro cadastrado.")
                ]
            else:
                resultados.controls = [
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
            page.update()

        linha_busca, campo_busca = barra_busca("Buscar roteiro por palavra-chave", carregar)

        mostrar(
            ft.Row(
                [
                    titulo("Roteiros"),
                    ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda e: carregar()),
                    ft.OutlinedButton("Glossário", icon=ft.Icons.MENU_BOOK, on_click=tela_glossario),
                    ft.OutlinedButton(
                        "Gerenciar roteiros", icon=ft.Icons.SETTINGS, on_click=tela_gerenciar
                    ),
                ]
            ),
            linha_busca,
            resultados,
        )
        carregar()

    def tela_glossario(e=None):
        resultados = ft.Column()

        def carregar():
            texto = (campo_busca.value or "").strip()
            try:
                termos = buscar("/glossario", {"busca": texto} if texto else None)
            except httpx.HTTPError:
                resultados.controls = [ft.Text("Não foi possível conectar ao servidor.")]
                page.update()
                return

            if not termos:
                resultados.controls = [
                    ft.Text("Nenhum termo encontrado." if texto else "Nenhum termo cadastrado.")
                ]
            else:
                cartoes = []
                for t in termos:
                    conteudo = [
                        ft.Text(t["nome"], size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(t["definicao"], size=16),
                    ]
                    if t["imagem"]:
                        conteudo.append(imagem(t["imagem"], altura=150))
                    cartoes.append(
                        ft.Card(content=ft.Container(padding=15, content=ft.Column(conteudo)))
                    )
                resultados.controls = cartoes
            page.update()

        linha_busca, campo_busca = barra_busca("Buscar termo", carregar)

        mostrar(
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=tela_lista),
                    titulo("Glossário"),
                    ft.OutlinedButton(
                        "Gerenciar glossário",
                        icon=ft.Icons.SETTINGS,
                        on_click=tela_gerenciar_glossario,
                    ),
                ]
            ),
            linha_busca,
            resultados,
        )
        carregar()

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

    # ---------- Gerenciar roteiros (professor/admin) ----------

    def tela_gerenciar(e=None):
        cabecalho = ft.Row(
            [
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=tela_lista),
                titulo("Gerenciar roteiros"),
            ]
        )
        try:
            roteiros = buscar("/roteiros")
        except httpx.HTTPError:
            mostrar(cabecalho, ft.Text("Não foi possível conectar ao servidor."))
            return

        linhas = [
            cartao_gerenciar(
                r["titulo"],
                r["descricao"],
                lambda e, rid=r["id"]: tela_formulario(rid),
                lambda e, r=r: confirmar_exclusao(
                    "Excluir roteiro",
                    f'Excluir "{r["titulo"]}"? O progresso dos alunos '
                    "nesse roteiro também será apagado.",
                    f"/roteiros/{r['id']}",
                    tela_gerenciar,
                ),
            )
            for r in roteiros
        ]
        mostrar(
            cabecalho,
            ft.FilledButton("Novo roteiro", icon=ft.Icons.ADD, on_click=lambda e: tela_formulario()),
            *(linhas or [ft.Text("Nenhum roteiro cadastrado.")]),
        )

    def tela_formulario(roteiro_id=None):
        dados = {}
        if roteiro_id:
            try:
                dados = buscar(f"/roteiros/{roteiro_id}")
            except httpx.HTTPError:
                mostrar(
                    ft.Text("Não foi possível abrir o roteiro."),
                    ft.OutlinedButton("Voltar", on_click=tela_gerenciar),
                )
                return

        aviso = ft.Text(color=ft.Colors.RED)

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
        imagem_roteiro = seletor_imagem(dados.get("imagem"), "roteiros", aviso)

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
                "imagem": seletor_imagem(caminho, "roteiros", aviso),
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
            vazios = any(not (c.value or "").strip() for c in obrigatorios) or any(
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
                    r = httpx.put(f"{API}/roteiros/{roteiro_id}", json=corpo, timeout=10)
                else:
                    r = httpx.post(f"{API}/roteiros", json=corpo, timeout=10)
                r.raise_for_status()
            except httpx.HTTPError:
                aviso.value = "Não foi possível salvar o roteiro."
                page.update()
                return
            tela_gerenciar()

        mostrar(
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=tela_gerenciar),
                    titulo("Editar roteiro" if roteiro_id else "Novo roteiro"),
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
                    ft.OutlinedButton("Cancelar", on_click=tela_gerenciar),
                    ft.FilledButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
                ]
            ),
        )

    # ---------- Gerenciar glossário (professor/admin) ----------

    def tela_gerenciar_glossario(e=None):
        cabecalho = ft.Row(
            [
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=tela_glossario),
                titulo("Gerenciar glossário"),
            ]
        )
        try:
            termos = buscar("/glossario")
        except httpx.HTTPError:
            mostrar(cabecalho, ft.Text("Não foi possível conectar ao servidor."))
            return

        linhas = [
            cartao_gerenciar(
                t["nome"],
                t["definicao"],
                lambda e, tid=t["id"]: tela_formulario_termo(tid),
                lambda e, t=t: confirmar_exclusao(
                    "Excluir termo",
                    f'Excluir o termo "{t["nome"]}"?',
                    f"/glossario/{t['id']}",
                    tela_gerenciar_glossario,
                ),
            )
            for t in termos
        ]
        mostrar(
            cabecalho,
            ft.FilledButton(
                "Novo termo", icon=ft.Icons.ADD, on_click=lambda e: tela_formulario_termo()
            ),
            *(linhas or [ft.Text("Nenhum termo cadastrado.")]),
        )

    def tela_formulario_termo(termo_id=None):
        dados = {}
        if termo_id:
            try:
                dados = buscar(f"/glossario/{termo_id}")
            except httpx.HTTPError:
                mostrar(
                    ft.Text("Não foi possível abrir o termo."),
                    ft.OutlinedButton("Voltar", on_click=tela_gerenciar_glossario),
                )
                return

        aviso = ft.Text(color=ft.Colors.RED)
        campo_nome = ft.TextField(label="Nome do termo", value=dados.get("nome", ""))
        campo_definicao = ft.TextField(
            label="Definição", value=dados.get("definicao", ""), multiline=True, min_lines=3
        )
        imagem_termo = seletor_imagem(dados.get("imagem"), "glossario", aviso)

        def salvar(e):
            if not (campo_nome.value or "").strip() or not (campo_definicao.value or "").strip():
                aviso.value = "Preencha o nome e a definição."
                page.update()
                return

            corpo = {
                "nome": campo_nome.value.strip(),
                "definicao": campo_definicao.value.strip(),
                "imagem": imagem_termo[1](),
            }
            try:
                if termo_id:
                    r = httpx.put(f"{API}/glossario/{termo_id}", json=corpo, timeout=10)
                else:
                    r = httpx.post(f"{API}/glossario", json=corpo, timeout=10)
                r.raise_for_status()
            except httpx.HTTPStatusError as erro:
                if erro.response.status_code == 409:
                    aviso.value = "Já existe um termo com esse nome."
                else:
                    aviso.value = "Não foi possível salvar o termo."
                page.update()
                return
            except httpx.HTTPError:
                aviso.value = "Não foi possível salvar o termo."
                page.update()
                return
            tela_gerenciar_glossario()

        mostrar(
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=tela_gerenciar_glossario),
                    titulo("Editar termo" if termo_id else "Novo termo"),
                ]
            ),
            campo_nome,
            campo_definicao,
            ft.Text("Imagem do termo", weight=ft.FontWeight.BOLD),
            imagem_termo[0],
            aviso,
            ft.Row(
                [
                    ft.OutlinedButton("Cancelar", on_click=tela_gerenciar_glossario),
                    ft.FilledButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
                ]
            ),
        )

    tela_lista()


ft.run(main)