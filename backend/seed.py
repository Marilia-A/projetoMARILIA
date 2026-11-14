import os
from pathlib import Path

from sqlmodel import Session, func, select

from backend.database import engine
from backend.models import Badge, Etapa, Roteiro, TermoGlossario, TipoUsuario, Usuario
from backend.seguranca import gerar_hash, verificar_senha

PASTA_IMAGENS = Path(__file__).parent / "imagens"


def imagem_se_existir(caminho: str | None) -> str | None:
    return caminho if caminho and (PASTA_IMAGENS / caminho).exists() else None


ROTEIROS = [
    {
        "titulo": "LED Piscando",
        "descricao": "Primeiro projeto com Arduino: fazer um LED acender e apagar sozinho.",
        "materiais": "1 Arduino Uno; 1 LED; 1 resistor de 220 ohms; 1 protoboard; 2 jumpers; cabo USB",
        "imagem": "roteiros/led_piscando.jpg",
        "codigo_comentado": (
            "void setup() {\n"
            "  pinMode(13, OUTPUT);     // define o pino 13 como saída\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  digitalWrite(13, HIGH);  // liga o LED\n"
            "  delay(1000);             // espera 1 segundo\n"
            "  digitalWrite(13, LOW);   // desliga o LED\n"
            "  delay(1000);             // espera 1 segundo\n"
            "}\n"
        ),
        "sugestoes": (
            "- Troque delay(1000) por delay(200) e veja o LED piscar bem mais rápido.\n"
            "- Deixe o LED aceso por 2 segundos e apagado por meio segundo.\n"
            "- Ligue um segundo LED no pino 12 e faça os dois piscarem alternados.\n"
            "- Desafio: faça o LED piscar 3 vezes rápido e depois esperar 2 segundos."
        ),
        "etapas": [
            {
                "conteudo": "O LED é uma pequena lâmpada que acende quando a energia passa por ele. "
                "Ele tem duas pernas: a maior é o positivo e a menor é o negativo.",
                "imagem": None,
            },
            {
                "conteudo": "O resistor protege o LED, diminuindo a energia que chega até ele. "
                "Sem o resistor, o LED pode queimar.",
                "imagem": None,
            },
            {
                "conteudo": "Montagem: com o Arduino desligado do computador, ligue o pino 13 ao resistor, "
                "o resistor à perna maior do LED e a perna menor do LED ao pino GND.",
                "imagem": None,
            },
            {
                "conteudo": "Conecte o cabo USB, copie o código, clique em Carregar na IDE do Arduino "
                "e observe o LED acender e apagar a cada segundo.",
                "imagem": None,
            },
        ],
    },
    {
        "titulo": "Semáforo",
        "descricao": "Usar três LEDs para imitar um semáforo de trânsito: verde, amarelo e vermelho.",
        "materiais": "1 Arduino Uno; 1 LED verde; 1 LED amarelo; 1 LED vermelho; 3 resistores de 220 ohms; "
        "1 protoboard; 6 jumpers; cabo USB",
        "imagem": "roteiros/semaforo.jpg",
        "codigo_comentado": (
            "int verde = 8;      // LED verde no pino 8\n"
            "int amarelo = 9;    // LED amarelo no pino 9\n"
            "int vermelho = 10;  // LED vermelho no pino 10\n"
            "\n"
            "void setup() {\n"
            "  pinMode(verde, OUTPUT);     // os três pinos são saídas\n"
            "  pinMode(amarelo, OUTPUT);\n"
            "  pinMode(vermelho, OUTPUT);\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  digitalWrite(verde, HIGH);     // verde aceso: pode passar\n"
            "  delay(4000);                   // espera 4 segundos\n"
            "  digitalWrite(verde, LOW);      // apaga o verde\n"
            "\n"
            "  digitalWrite(amarelo, HIGH);   // amarelo aceso: atenção\n"
            "  delay(1000);                   // espera 1 segundo\n"
            "  digitalWrite(amarelo, LOW);    // apaga o amarelo\n"
            "\n"
            "  digitalWrite(vermelho, HIGH);  // vermelho aceso: pare\n"
            "  delay(4000);                   // espera 4 segundos\n"
            "  digitalWrite(vermelho, LOW);   // apaga o vermelho e recomeça\n"
            "}\n"
        ),
        "sugestoes": (
            "- Mude os tempos: deixe o verde aceso por mais tempo que o vermelho.\n"
            "- Faça o amarelo piscar 3 vezes antes de ficar vermelho.\n"
            "- Crie um semáforo de pedestre com mais dois LEDs (verde e vermelho) que funcione ao contrário do semáforo dos carros.\n"
            "- Desafio: faça o modo noturno, com só o amarelo piscando sem parar."
        ),
        "etapas": [
            {
                "conteudo": "No semáforo de verdade, a ordem é verde, depois amarelo, depois vermelho, "
                "e então volta ao verde. Vamos fazer o Arduino controlar essa sequência.",
                "imagem": None,
            },
            {
                "conteudo": "Cada LED precisa do seu próprio resistor e do seu próprio pino. Usaremos o pino 8 "
                "para o verde, o 9 para o amarelo e o 10 para o vermelho.",
                "imagem": None,
            },
            {
                "conteudo": "Montagem: com o Arduino desligado, ligue cada pino a um resistor e cada resistor à perna "
                "maior do LED da cor certa. Ligue a perna menor dos três LEDs à linha GND da protoboard "
                "e essa linha ao pino GND do Arduino.",
                "imagem": None,
            },
            {
                "conteudo": "Carregue o código e confira se as cores acendem na ordem certa. "
                "Se uma cor não acender, verifique se o LED não está invertido.",
                "imagem": None,
            },
        ],
    },
    {
        "titulo": "Botão que Acende o LED",
        "descricao": "Aprender a ler um botão: o LED acende somente enquanto o botão estiver apertado.",
        "materiais": "1 Arduino Uno; 1 botão (push button); 1 LED; 1 resistor de 220 ohms; 1 protoboard; "
        "4 jumpers; cabo USB",
        "imagem": "roteiros/botao_led.jpg",
        "codigo_comentado": (
            "int botao = 2;  // botão no pino 2\n"
            "int led = 13;   // LED no pino 13\n"
            "\n"
            "void setup() {\n"
            "  pinMode(botao, INPUT_PULLUP);  // pino 2 é entrada, com resistor interno ligado\n"
            "  pinMode(led, OUTPUT);          // pino 13 é saída\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  if (digitalRead(botao) == LOW) {  // LOW quer dizer: botão apertado\n"
            "    digitalWrite(led, HIGH);        // acende o LED\n"
            "  } else {\n"
            "    digitalWrite(led, LOW);         // botão solto: apaga o LED\n"
            "  }\n"
            "}\n"
        ),
        "sugestoes": (
            "- Inverta a lógica: faça o LED ficar aceso e apagar quando o botão for apertado.\n"
            "- Faça o LED piscar rápido enquanto o botão estiver apertado.\n"
            "- Use dois botões: um liga e o outro desliga o LED.\n"
            "- Desafio: faça cada aperto do botão trocar o LED entre ligado e desligado, como um interruptor."
        ),
        "etapas": [
            {
                "conteudo": "Até agora o Arduino só mandava ordens (saída). Agora ele vai ouvir o mundo: "
                "o botão é uma entrada, e o Arduino pergunta o tempo todo se ele está apertado.",
                "imagem": None,
            },
            {
                "conteudo": "Usamos INPUT_PULLUP, que liga um resistor dentro do próprio Arduino. Assim, com o botão "
                "solto o pino lê HIGH, e com o botão apertado lê LOW.",
                "imagem": None,
            },
            {
                "conteudo": "Montagem: com o Arduino desligado, encaixe o botão no meio da protoboard. Ligue uma perna "
                "do botão ao pino 2 e a perna do lado oposto ao GND. Monte o LED com o resistor no pino 13, "
                "como no primeiro roteiro.",
                "imagem": None,
            },
            {
                "conteudo": "Carregue o código e aperte o botão. O LED deve acender só enquanto você segura. "
                "Se ficar sempre aceso, gire o botão 90 graus na protoboard.",
                "imagem": None,
            },
        ],
    },
    {
        "titulo": "Luz Noturna Automática",
        "descricao": "Usar um sensor de luz (LDR) para acender um LED sozinho quando o ambiente fica escuro.",
        "materiais": "1 Arduino Uno; 1 sensor de luz LDR; 1 resistor de 10 mil ohms (10k); 1 LED; "
        "1 resistor de 220 ohms; 1 protoboard; 6 jumpers; cabo USB",
        "imagem": "roteiros/luz_noturna.jpg",
        "codigo_comentado": (
            "int sensor = A0;  // LDR no pino analógico A0\n"
            "int led = 9;      // LED no pino 9\n"
            "int limite = 300; // abaixo deste valor consideramos que está escuro\n"
            "\n"
            "void setup() {\n"
            "  pinMode(led, OUTPUT);  // pino 9 é saída\n"
            "  Serial.begin(9600);    // liga o Monitor Serial para ver os valores\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  int luz = analogRead(sensor);  // lê a luz: número de 0 a 1023\n"
            "  Serial.println(luz);           // mostra o valor no Monitor Serial\n"
            "\n"
            "  if (luz < limite) {            // pouca luz?\n"
            "    digitalWrite(led, HIGH);     // acende o LED\n"
            "  } else {\n"
            "    digitalWrite(led, LOW);      // tem luz: apaga o LED\n"
            "  }\n"
            "  delay(200);                    // pequena pausa entre as leituras\n"
            "}\n"
        ),
        "sugestoes": (
            "- Abra o Monitor Serial e anote o valor com a luz acesa e com a mão tapando o sensor. Ajuste o limite.\n"
            "- Faça o LED piscar quando estiver muito escuro (valor bem baixo).\n"
            "- Use três LEDs para mostrar pouca, média e muita luz.\n"
            "- Desafio: use analogWrite no pino 9 para o LED ficar mais forte quanto mais escuro estiver."
        ),
        "etapas": [
            {
                "conteudo": "O botão só tem dois estados: apertado ou solto. O sensor de luz é diferente: ele "
                "informa quanta luz existe, com um número de 0 a 1023. Por isso usamos um pino analógico (A0).",
                "imagem": None,
            },
            {
                "conteudo": "O LDR muda de resistência com a luz: no claro deixa passar mais energia, no escuro "
                "deixa passar menos. Junto com o resistor de 10k, isso vira um número que o Arduino consegue ler.",
                "imagem": None,
            },
            {
                "conteudo": "Montagem: com o Arduino desligado, ligue uma perna do LDR ao 5V e a outra ao pino A0. "
                "Desse mesmo ponto (A0), ligue o resistor de 10k ao GND. Monte o LED com o resistor de 220 ohms no pino 9.",
                "imagem": None,
            },
            {
                "conteudo": "Carregue o código, abra o Monitor Serial (lupa no canto da IDE) e tape o sensor com a mão. "
                "O número deve cair e o LED deve acender. Se não acender, ajuste o valor do limite.",
                "imagem": None,
            },
        ],
    },
    {
        "titulo": "Alarme com Sensor de Presença",
        "descricao": "Montar um alarme que acende um LED e toca um buzzer quando alguém passa na frente do sensor.",
        "materiais": "1 Arduino Uno; 1 sensor de presença PIR (HC-SR501); 1 buzzer ativo; 1 LED vermelho; "
        "1 resistor de 220 ohms; 1 protoboard; 7 jumpers; cabo USB",
        "imagem": "roteiros/alarme_pir.jpg",
        "codigo_comentado": (
            "int sensor = 7;   // saída do sensor PIR no pino 7\n"
            "int buzzer = 8;   // buzzer no pino 8\n"
            "int led = 13;     // LED no pino 13\n"
            "\n"
            "void setup() {\n"
            "  pinMode(sensor, INPUT);   // o sensor envia informação: entrada\n"
            "  pinMode(buzzer, OUTPUT);  // buzzer e LED recebem ordens: saídas\n"
            "  pinMode(led, OUTPUT);\n"
            "  delay(30000);             // espera 30 segundos para o sensor se ajustar\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  if (digitalRead(sensor) == HIGH) {  // HIGH: o sensor viu movimento\n"
            "    digitalWrite(led, HIGH);          // acende o LED\n"
            "    digitalWrite(buzzer, HIGH);       // liga o som\n"
            "    delay(1000);                      // alarme por 1 segundo\n"
            "  } else {\n"
            "    digitalWrite(led, LOW);           // sem movimento: tudo desligado\n"
            "    digitalWrite(buzzer, LOW);\n"
            "  }\n"
            "}\n"
        ),
        "sugestoes": (
            "- Faça o buzzer apitar 3 vezes curtas em vez de um som contínuo.\n"
            "- Troque o LED vermelho pelo semáforo: verde sem movimento, vermelho com movimento.\n"
            "- Junte com o roteiro do botão: o botão liga e desliga o alarme.\n"
            "- Desafio: junte com o sensor de luz para o alarme funcionar só quando estiver escuro."
        ),
        "etapas": [
            {
                "conteudo": "O sensor PIR percebe o calor do corpo das pessoas e dos animais em movimento. "
                "Quando alguém passa na frente, ele avisa o Arduino mandando HIGH no fio de saída.",
                "imagem": None,
            },
            {
                "conteudo": "O buzzer é um pequeno alto-falante. O buzzer ativo apita sozinho quando recebe energia, "
                "então basta ligar e desligar com digitalWrite, como fazemos com o LED.",
                "imagem": None,
            },
            {
                "conteudo": "Montagem: com o Arduino desligado, ligue o pino VCC do sensor ao 5V, o GND ao GND e o "
                "pino OUT ao pino 7. Ligue o positivo do buzzer (perna maior ou marcada com +) ao pino 8 e o "
                "negativo ao GND. Monte o LED com o resistor no pino 13.",
                "imagem": None,
            },
            {
                "conteudo": "Carregue o código e espere 30 segundos sem se mexer na frente do sensor, para ele se ajustar. "
                "Depois passe a mão na frente: o LED acende e o buzzer apita.",
                "imagem": None,
            },
        ],
    },
]

TERMOS = [
    {
        "nome": "Arduino Uno",
        "definicao": "Pequena placa com um computador simples dentro. Ela recebe o código que escrevemos e "
        "controla LEDs, motores e sensores pelos seus pinos.",
        "imagem": None,
    },
    {
        "nome": "LED",
        "definicao": "Pequena lâmpada que acende quando a energia passa por ela. Tem polaridade: a perna maior "
        "é o positivo e a menor é o negativo.",
        "imagem": None,
    },
    {
        "nome": "Resistor",
        "definicao": "Componente que limita a passagem de corrente elétrica no circuito, protegendo outras peças "
        "como o LED.",
        "imagem": None,
    },
    {
        "nome": "Protoboard",
        "definicao": "Placa cheia de furinhos usada para montar circuitos sem solda. Os furos de uma mesma linha "
        "são ligados por dentro.",
        "imagem": None,
    },
    {
        "nome": "Jumper",
        "definicao": "Fio com pontas próprias para encaixar na protoboard e no Arduino, usado para ligar as peças.",
        "imagem": None,
    },
    {
        "nome": "GND",
        "definicao": "O polo negativo do circuito, também chamado de terra. Todo circuito precisa voltar ao GND "
        "para a energia circular.",
        "imagem": None,
    },
    {
        "nome": "Pino digital",
        "definicao": "Pino do Arduino que trabalha com só dois valores: HIGH (ligado) ou LOW (desligado). "
        "Serve para LEDs, botões e buzzers.",
        "imagem": None,
    },
    {
        "nome": "Pino analógico",
        "definicao": "Pino do Arduino (A0 a A5) que lê valores de 0 a 1023. Serve para sensores que medem "
        "quantidades, como luz e temperatura.",
        "imagem": None,
    },
    {
        "nome": "Botão (push button)",
        "definicao": "Interruptor que só fecha o circuito enquanto está apertado. Ao soltar, o circuito abre de novo.",
        "imagem": None,
    },
    {
        "nome": "Sensor de luz (LDR)",
        "definicao": "Componente que muda de resistência com a luz: no claro deixa passar mais corrente e no "
        "escuro deixa passar menos.",
        "imagem": None,
    },
    {
        "nome": "Sensor de presença (PIR)",
        "definicao": "Sensor que percebe o calor de pessoas e animais em movimento e avisa o Arduino.",
        "imagem": None,
    },
    {
        "nome": "Buzzer",
        "definicao": "Pequeno alto-falante que emite um apito. O buzzer ativo apita sozinho quando recebe energia.",
        "imagem": None,
    },
]

BADGES = [
    {"nome": "Primeiro Circuito", "criterio": "Concluir o primeiro roteiro", "roteiros_necessarios": 1},
    {"nome": "Explorador", "criterio": "Concluir 3 roteiros", "roteiros_necessarios": 3},
    {"nome": "Inventor", "criterio": "Concluir 5 roteiros", "roteiros_necessarios": 5},
]

# usuários de teste (senha 123456)
USUARIOS = [
    {"nome": "Aluno Teste", "email": "aluno@teste.com", "tipo": TipoUsuario.aluno, "ano_escolar": "8º ano"},
    {"nome": "Professor Teste", "email": "professor@teste.com", "tipo": TipoUsuario.professor},
    {"nome": "Admin Teste", "email": "admin@teste.com", "tipo": TipoUsuario.admin},
]


def carregar_dados_iniciais():
    with Session(engine) as session:
        if not session.exec(select(Roteiro)).first():
            for dados in ROTEIROS:
                campos = {k: v for k, v in dados.items() if k != "etapas"}
                campos["imagem"] = imagem_se_existir(campos["imagem"])
                etapas = [
                    Etapa(ordem=i, conteudo=e["conteudo"], imagem=imagem_se_existir(e["imagem"]))
                    for i, e in enumerate(dados["etapas"], start=1)
                ]
                session.add(Roteiro(**campos, etapas=etapas))

        if not session.exec(select(TermoGlossario)).first():
            for dados in TERMOS:
                session.add(TermoGlossario(**dados))

        if not session.exec(select(Badge)).first():
            for dados in BADGES:
                session.add(Badge(**dados))

        if os.getenv("SEED_USUARIOS_TESTE", "true").lower() == "true":
            for dados in USUARIOS:
                existe = session.exec(select(Usuario).where(Usuario.email == dados["email"])).first()
                if not existe:
                    session.add(Usuario(**dados, senha_hash=gerar_hash("123456")))

        email_admin = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
        senha_admin = os.getenv("ADMIN_SENHA") or ""
        if email_admin and senha_admin:
            existe = session.exec(select(Usuario).where(func.lower(Usuario.email) == email_admin)).first()
            if not existe:
                session.add(
                    Usuario(
                        nome="Administrador",
                        email=email_admin,
                        tipo=TipoUsuario.admin,
                        senha_hash=gerar_hash(senha_admin),
                    )
                )
            else:
                existe.tipo = TipoUsuario.admin
                if not verificar_senha(senha_admin, existe.senha_hash):
                    existe.senha_hash = gerar_hash(senha_admin)
                session.add(existe)

        session.commit()