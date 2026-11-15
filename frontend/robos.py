"""Robôs desenhados com formas simples do Flet e pequenas brincadeiras interativas.

Cada brincadeira imita, de forma bem simples, o circuito de um roteiro:
clicar no robô acende a lâmpada (LED Piscando), troca a cor do semáforo,
acende o LED enquanto o botão está apertado, e assim por diante.
Nada aqui chama a API: é só animação na tela.
"""

import asyncio
import random

import flet as ft

import componentes as c

ESCURO = "#3A3360"
DESLIGADO = "#D9D4EA"
AMARELO_LUZ = "#FFD84D"


def _atualizar(controle) -> bool:
    """Atualiza a tela; devolve False se o controle já saiu dela (a criança trocou de tela no meio da animação)."""
    try:
        controle.update()
        return True
    except Exception:
        return False


def _rapida(ms: int = 250):
    return ft.Animation(ms, ft.AnimationCurve.EASE_OUT)


def _brilho(cor: str):
    return ft.BoxShadow(blur_radius=28, spread_radius=6, color=ft.Colors.with_opacity(0.7, cor))


class Robo:
    """Robô simpático montado com retângulos arredondados.

    Partes que mudam: olhos, luz do peito, boca, braço direito (acena) e o corpo todo (pula).
    """

    def __init__(self, cor: str = c.ROXO, escala: float = 1.0, ao_clicar=None, dica: str | None = None):
        s = escala
        self.cor = cor
        self.escala = s

        def caixa(x, y, w, h, raio, cor_fundo, **kw):
            return ft.Container(left=x * s, top=y * s, width=w * s, height=h * s,
                                border_radius=raio * s, bgcolor=cor_fundo, **kw)

        self.olho_esq = caixa(40, 40, 12, 12, 6, ESCURO, animate=_rapida())
        self.olho_dir = caixa(68, 40, 12, 12, 6, ESCURO, animate=_rapida())
        self.boca = caixa(48, 58, 24, 5, 3, ESCURO, animate=_rapida())
        self.peito = caixa(52, 98, 16, 16, 8, DESLIGADO, animate=_rapida())
        self.antena = caixa(52, 0, 16, 16, 8, c.AMARELO, animate=_rapida())
        self.braco = caixa(94, 90, 14, 36, 7, cor, rotate=ft.Rotate(0, alignment=ft.Alignment.TOP_CENTER),
                           animate_rotation=_rapida(300))

        self.desenho = ft.Stack(
            [
                caixa(58, 12, 4, 12, 2, ESCURO),           # haste da antena
                self.antena,
                caixa(20, 22, 80, 56, 18, cor),            # cabeça
                caixa(30, 32, 60, 36, 12, ft.Colors.WHITE),  # rosto
                self.olho_esq, self.olho_dir, self.boca,
                caixa(52, 78, 16, 6, 2, ESCURO),           # pescoço
                caixa(12, 90, 14, 36, 7, cor),             # braço esquerdo
                self.braco,
                caixa(28, 84, 64, 50, 14, cor),            # corpo
                self.peito,
                caixa(40, 134, 14, 14, 5, ESCURO),         # pernas
                caixa(66, 134, 14, 14, 5, ESCURO),
            ],
            width=120 * s,
            height=150 * s,
        )
        self.controle = ft.Container(
            content=self.desenho,
            on_click=ao_clicar,
            tooltip=dica,
            scale=ft.Scale(1),
            animate_scale=ft.Animation(220, ft.AnimationCurve.BOUNCE_OUT),
            ink=False,
        )

    # ---------- pequenas expressões ----------
    def olhos(self, cor: str):
        self.olho_esq.bgcolor = cor
        self.olho_dir.bgcolor = cor

    def luz_peito(self, cor: str | None):
        self.peito.bgcolor = cor or DESLIGADO
        self.peito.shadow = _brilho(cor) if cor else None

    def sorriso(self, feliz: bool):
        self.boca.width = (32 if feliz else 24) * self.escala
        self.boca.left = (44 if feliz else 48) * self.escala
        self.boca.bgcolor = c.ROSA if feliz else ESCURO

    async def acenar(self, vezes: int = 2):
        for _ in range(vezes):
            self.braco.rotate.angle = -0.9
            _atualizar(self.braco)
            await asyncio.sleep(0.3)
            self.braco.rotate.angle = 0
            _atualizar(self.braco)
            await asyncio.sleep(0.3)

    async def pular(self):
        self.controle.scale.scale = 1.12
        _atualizar(self.controle)
        await asyncio.sleep(0.22)
        self.controle.scale.scale = 1
        _atualizar(self.controle)


def _balao(texto: str, cor: str = c.ROXO):
    return ft.Container(
        content=ft.Text(texto, size=16, color=c.TEXTO, weight=ft.FontWeight.W_500),
        bgcolor="#EFEAFF",
        border=ft.Border.all(2, ft.Colors.with_opacity(0.3, cor)),
        border_radius=18,
        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        animate=_rapida(),
    )


def _quadro(titulo: str, *conteudo, cor: str = c.AZUL):
    """Moldura colorida das brincadeiras."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [ft.Icon(ft.Icons.TOUCH_APP, color=cor), ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=c.TEXTO)],
                    spacing=8,
                ),
                *conteudo,
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.with_opacity(0.08, cor),
        border=ft.Border.all(2, ft.Colors.with_opacity(0.3, cor)),
        border_radius=20,
        padding=18,
    )


def _lampada(tamanho: int = 70):
    icone = ft.Icon(ft.Icons.LIGHTBULB, size=tamanho, color=DESLIGADO)
    caixa = ft.Container(content=icone, border_radius=tamanho, padding=6, animate=_rapida())

    def ligar(acesa: bool):
        icone.color = AMARELO_LUZ if acesa else DESLIGADO
        caixa.shadow = _brilho(AMARELO_LUZ) if acesa else None
        _atualizar(caixa)

    return caixa, ligar


def _luz(tamanho: int = 46):
    return ft.Container(width=tamanho, height=tamanho, border_radius=tamanho // 2, bgcolor=DESLIGADO, animate=_rapida())


def _acender(luz: ft.Container, cor: str | None):
    luz.bgcolor = cor or DESLIGADO
    luz.shadow = _brilho(cor) if cor else None


# ---------- uma brincadeira para cada roteiro ----------

def brincadeira_led():
    estado = {"piscando": False}
    balao = _balao("Clique em mim para acender a lâmpada!")
    lampada, ligar = _lampada()

    async def clicar(e):
        if estado["piscando"]:
            return
        estado["piscando"] = True
        balao.content.value = "Olha o LED piscando: acende... apaga..."
        _atualizar(balao)
        robo.luz_peito(AMARELO_LUZ)
        _atualizar(robo.controle)
        for _ in range(3):
            ligar(True)
            await asyncio.sleep(0.5)
            ligar(False)
            await asyncio.sleep(0.5)
        ligar(True)
        robo.luz_peito(None)
        _atualizar(robo.controle)
        balao.content.value = "É isso que o código faz com o delay(1000)! Clique de novo."
        _atualizar(balao)
        estado["piscando"] = False

    robo = Robo(c.AZUL, 0.9, clicar, "Clique no robô")
    return _quadro("Experimente: o robô acende a lâmpada", balao,
                   ft.Row([robo.controle, lampada], alignment=ft.MainAxisAlignment.CENTER, spacing=40), cor=c.AZUL)


def brincadeira_semaforo():
    cores = [c.VERDE, AMARELO_LUZ, "#F2484B"]
    nomes = ["Verde: pode passar!", "Amarelo: atenção!", "Vermelho: pare!"]
    luzes = [_luz() for _ in cores]
    estado = {"i": -1}
    balao = _balao("Clique no robô para mudar o semáforo.")

    def clicar(e):
        estado["i"] = (estado["i"] + 1) % 3
        for k, luz in enumerate(luzes):
            _acender(luz, cores[k] if k == estado["i"] else None)
        robo.olhos(cores[estado["i"]])
        balao.content.value = nomes[estado["i"]]
        _atualizar(quadro)

    robo = Robo(c.LARANJA, 0.9, clicar, "Clique no robô")
    poste = ft.Container(
        content=ft.Column(luzes, spacing=10),
        bgcolor=ESCURO, border_radius=18, padding=12,
    )
    quadro = _quadro("Experimente: controle o semáforo", balao,
                     ft.Row([robo.controle, poste], alignment=ft.MainAxisAlignment.CENTER, spacing=40), cor=c.LARANJA)
    return quadro


def brincadeira_botao():
    led = _luz(54)
    balao = _balao("Segure o botão vermelho apertado.")
    tampa = ft.Container(width=70, height=70, border_radius=35, bgcolor="#F2484B",
                         border=ft.Border.all(8, "#B83236"), animate=_rapida(120))

    def apertar(e):
        tampa.bgcolor = "#B83236"
        _acender(led, c.VERDE)
        robo.olhos(c.VERDE)
        robo.sorriso(True)
        balao.content.value = "Apertado: o LED acende!"
        _atualizar(quadro)

    def soltar(e):
        tampa.bgcolor = "#F2484B"
        _acender(led, None)
        robo.olhos(ESCURO)
        robo.sorriso(False)
        balao.content.value = "Solto: o LED apaga. Aperte de novo!"
        _atualizar(quadro)

    # Toque rápido: tap_down/tap_up. Segurar: o Flutter troca para "long press" (start/end).
    botao = ft.GestureDetector(
        content=tampa,
        on_tap_down=apertar, on_tap_up=soltar,
        on_long_press_start=apertar, on_long_press_end=soltar, on_long_press_cancel=soltar,
        mouse_cursor=ft.MouseCursor.CLICK,
    )
    robo = Robo(c.VERDE, 0.9, dica="O robô fica feliz quando o LED acende")
    quadro = _quadro("Experimente: aperte o botão", balao,
                     ft.Row([robo.controle, botao, led], alignment=ft.MainAxisAlignment.CENTER, spacing=36,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                     cor=c.VERDE)
    return quadro


def brincadeira_luz_noturna():
    estado = {"noite": False}
    balao = _balao("Clique no sol para fazer anoitecer.")
    ceu_icone = ft.Icon(ft.Icons.WB_SUNNY, size=64, color=c.AMARELO)
    lampada, ligar = _lampada(60)

    def clicar(e):
        estado["noite"] = not estado["noite"]
        noite = estado["noite"]
        ceu.bgcolor = "#2B2350" if noite else "#BFE6FF"
        ceu_icone.icon = ft.Icons.NIGHTLIGHT_ROUND if noite else ft.Icons.WB_SUNNY
        ceu_icone.color = "#E9E4FF" if noite else c.AMARELO
        robo.olhos(AMARELO_LUZ if noite else ESCURO)
        balao.content.value = ("Ficou escuro! O sensor LDR percebeu e o LED acendeu sozinho."
                               if noite else "Está claro: o LED fica apagado. Clique na lua para anoitecer.")
        _atualizar(quadro)
        ligar(noite)

    robo = Robo(c.ROSA, 0.7)
    ceu = ft.Container(
        content=ft.Row([ceu_icone, robo.controle, lampada],
                       alignment=ft.MainAxisAlignment.SPACE_AROUND,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#BFE6FF", border_radius=18, padding=16, width=440,
        on_click=clicar, animate=_rapida(400), tooltip="Clique para trocar dia e noite",
    )
    quadro = _quadro("Experimente: dia e noite", balao, ceu, cor=c.ROSA)
    return quadro


def brincadeira_alarme():
    estado = {"tocando": False}
    balao = _balao("Clique no robô para alguém passar na frente do sensor.")
    led = _luz(40)
    buzina = ft.Container(content=ft.Icon(ft.Icons.VOLUME_UP, size=46, color=DESLIGADO),
                          rotate=ft.Rotate(0), animate_rotation=_rapida(90))
    # A pessoa anda dentro de um "corredor" na frente do sensor (não sai dele nem cobre o robô).
    pessoa = ft.Container(content=ft.Icon(ft.Icons.DIRECTIONS_WALK, size=56, color=c.AZUL),
                          left=0, top=4, animate_position=ft.Animation(700, ft.AnimationCurve.EASE_IN_OUT))
    corredor = ft.Container(
        content=ft.Stack([pessoa], width=150, height=64),
        width=150, height=64, bgcolor=ft.Colors.with_opacity(0.08, c.AZUL), border_radius=14,
        clip_behavior=ft.ClipBehavior.HARD_EDGE, tooltip="Clique para alguém passar",
    )

    async def passar(e):
        if estado["tocando"]:
            return
        estado["tocando"] = True
        pessoa.left = 92
        balao.content.value = "Alguém passou! Bip! Bip! Bip!"
        _atualizar(quadro)
        for k in range(6):
            _acender(led, "#F2484B" if k % 2 == 0 else None)
            buzina.content.color = c.LARANJA if k % 2 == 0 else DESLIGADO
            buzina.rotate.angle = 0.25 if k % 2 == 0 else -0.25
            robo.olhos("#F2484B" if k % 2 == 0 else ESCURO)
            _atualizar(quadro)
            await asyncio.sleep(0.3)
        _acender(led, None)
        buzina.rotate.angle = 0
        robo.olhos(ESCURO)
        pessoa.left = 0
        balao.content.value = "Tudo calmo de novo. Clique outra vez!"
        _atualizar(quadro)
        estado["tocando"] = False

    corredor.on_click = passar
    robo = Robo(c.ROXO, 0.9, passar, "Clique para alguém passar")
    sensor = ft.Column([ft.Icon(ft.Icons.SENSORS, size=40, color=c.ROXO), ft.Text("PIR", size=14, color=c.TEXTO_SUAVE)],
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
    quadro = _quadro(
        "Experimente: o alarme com sensor",
        balao,
        ft.Row([robo.controle, sensor, corredor, ft.Column([led, buzina], spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
               alignment=ft.MainAxisAlignment.CENTER, spacing=24, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        cor=c.ROXO,
    )
    return quadro


def brincadeira_para(titulo: str):
    """Escolhe a brincadeira pelo título do roteiro (roteiros novos ganham a da lâmpada)."""
    t = titulo.lower()
    if "semáforo" in t or "semaforo" in t:
        return brincadeira_semaforo()
    if "botão" in t or "botao" in t:
        return brincadeira_botao()
    if "noturna" in t or "ldr" in t:
        return brincadeira_luz_noturna()
    if "alarme" in t or "pir" in t or "presença" in t:
        return brincadeira_alarme()
    return brincadeira_led()


# ---------- robô mascote (login, início, conquistas) ----------

FRASES_INICIO = [
    "Oi! Vamos montar um circuito hoje?",
    "Dica: leia os materiais antes de começar.",
    "Errar faz parte! Confira os fios e tente de novo.",
    "Sabia que o LED tem perna maior e perna menor?",
    "Cada roteiro concluído vale um passo rumo aos troféus!",
    "Ficou com dúvida? A tutora está na última página do roteiro.",
]


def mascote(frases: list[str], cor: str = c.ROXO, escala: float = 0.8, comemorar: bool = False):
    """Robô que acena (ou pula) e fala uma frase nova a cada clique."""
    estado = {"i": 0}
    balao = _balao(frases[0], cor)

    async def clicar(e):
        estado["i"] = (estado["i"] + 1) % len(frases)
        balao.content.value = frases[estado["i"]]
        _atualizar(balao)
        robo.luz_peito(random.choice([c.AMARELO, c.VERDE, c.ROSA, c.AZUL]))
        robo.sorriso(True)
        _atualizar(robo.controle)
        if comemorar:
            for _ in range(2):
                await robo.pular()
        else:
            await robo.acenar()
        robo.luz_peito(None)
        robo.sorriso(False)
        _atualizar(robo.controle)

    robo = Robo(cor, escala, clicar, "Clique no robô")
    return ft.Row([robo.controle, ft.Container(balao, expand=True)], spacing=12,
                  vertical_alignment=ft.CrossAxisAlignment.CENTER), robo


def cabeca_tutora(tamanho: int = 56):
    """Só a cabeça do robô, para o balão da tutora."""
    s = tamanho / 80
    olho = lambda x: ft.Container(left=x * s, top=26 * s, width=12 * s, height=12 * s, border_radius=6 * s, bgcolor=ESCURO)
    return ft.Stack(
        [
            ft.Container(left=34 * s, top=0, width=12 * s, height=12 * s, border_radius=6 * s, bgcolor=c.AMARELO),
            ft.Container(left=4 * s, top=10 * s, width=72 * s, height=56 * s, border_radius=18 * s, bgcolor=c.ROXO),
            ft.Container(left=12 * s, top=18 * s, width=56 * s, height=38 * s, border_radius=12 * s, bgcolor=ft.Colors.WHITE),
            olho(22), olho(46),
            ft.Container(left=30 * s, top=44 * s, width=20 * s, height=5 * s, border_radius=3 * s, bgcolor=c.ROSA),
        ],
        width=80 * s,
        height=66 * s,
    )
