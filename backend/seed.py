from sqlmodel import Session, select

from backend.database import engine
from backend.models import Etapa, Roteiro, TermoGlossario, TipoUsuario, Usuario
from backend.seguranca import gerar_hash

ROTEIROS = [
    {
        "titulo": "LED Piscando",
        "descricao": "Primeiro projeto com Arduino: fazer um LED acender e apagar sozinho.",
        "materiais": "1 Arduino Uno; 1 LED; 1 resistor de 220 ohms; 1 protoboard; 2 jumpers; cabo USB",
        "imagem": "roteiros/teste.jpg",
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
        "etapas": [
            {
                "conteudo": "O LED é uma pequena lâmpada que acende quando a energia passa por ele. "
                "Ele tem duas pernas: a maior é o positivo e a menor é o negativo.",
                "imagem": "roteiros/teste.jpg",
            },
            {
                "conteudo": "O resistor protege o LED, diminuindo a energia que chega até ele. "
                "Sem o resistor, o LED pode queimar.",
                "imagem": None,
            },
            {
                "conteudo": "Montagem: ligue a perna maior do LED ao pino 13 do Arduino, passando pelo resistor. "
                "Ligue a perna menor ao pino GND.",
                "imagem": None,
            },
        ],
    },
]

TERMOS = [
    {
        "nome": "Resistor",
        "definicao": "Componente que limita a passagem de corrente elétrica no circuito, protegendo outras peças como o LED.",
        "imagem": None,
    },
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
                etapas = [Etapa(ordem=i, **e) for i, e in enumerate(dados["etapas"], start=1)]
                session.add(Roteiro(**campos, etapas=etapas))

        if not session.exec(select(TermoGlossario)).first():
            for dados in TERMOS:
                session.add(TermoGlossario(**dados))

        for dados in USUARIOS:
            existe = session.exec(select(Usuario).where(Usuario.email == dados["email"])).first()
            if not existe:
                session.add(Usuario(**dados, senha_hash=gerar_hash("123456")))

        session.commit()