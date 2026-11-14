# MARILIA

**M**etodologias **A**tivas de **R**obótica para **I**ntegração, **L**ógica e **I**novação na **A**prendizagem.

Aplicativo de tutoria para alunos da educação básica que estão aprendendo robótica com Arduino.

O aluno segue roteiros práticos passo a passo, consulta um glossário ilustrado e tira dúvidas com um tutor de IA que responde no nível de profundidade escolhido (superficial, moderado ou detalhado), sempre dentro do tema do roteiro. O professor acompanha o progresso das suas turmas em um painel, e o administrador gerencia usuários, roteiros e glossário.

Projeto desenvolvido como Trabalho de Conclusão de Curso (TCC), motivado pela experiência no programa START (jul/2025 a jan/2026), de robótica educacional em escolas públicas.

---

## Funcionalidades por perfil

| Perfil | O que pode fazer |
|---|---|
| **Aluno** | Entrar em turmas pelo código; seguir os roteiros e marcar etapas concluídas; perguntar ao tutor de IA; consultar o glossário; ver as conquistas (badges) |
| **Professor** | Criar e gerenciar as próprias turmas; adicionar ou remover alunos; ver o painel da turma (progresso, conquistas, perguntas ao tutor) e o detalhe de cada aluno das suas turmas; cadastrar roteiros, termos do glossário e imagens |
| **Administrador** | Tudo o que o professor faz, para todas as turmas, mais o cadastro de usuários (não há autocadastro) |

## Arquitetura

```
┌─────────────────────┐      HTTPS + JWT       ┌──────────────────────┐      ┌──────────────┐
│ Front-end (Flet)    │ ─────────────────────▶ │ API (FastAPI)        │ ───▶ │ PostgreSQL   │
│ app desktop (.exe)  │ ◀───────────────────── │ regras, segurança,   │      │ dados e      │
│ um por computador   │        JSON            │ seed, prompt da IA   │      │ imagens      │
└─────────────────────┘                        └──────────┬───────────┘      └──────────────┘
                                                          │
                                                          ▼
                                               ┌──────────────────────┐
                                               │ IA: Groq ou Gemini   │
                                               │ (provedor por        │
                                               │  variável de ambiente)│
                                               └──────────────────────┘
```

- **Front-end**: Python + [Flet](https://flet.dev), empacotado como executável para Windows. Não guarda dados: tudo passa pela API.
- **Back-end**: Python + FastAPI + SQLModel, autenticação por JWT, senhas com hash.
- **Banco**: PostgreSQL (SQLite também funciona para testes rápidos). As imagens dos roteiros e do glossário ficam no próprio banco.
- **Tutor de IA**: o back-end monta as instruções (nível de profundidade, conteúdo do roteiro, regras de segurança) e envia só a pergunta, sem dados pessoais do aluno.

## Estrutura de pastas

```
backend/         API FastAPI (rotas, modelos, segurança, seed)   → ver backend/README.md
frontend/        Aplicativo Flet (telas, cliente da API)        → ver frontend/README.md
docs/            Registro de desenvolvimento (REGISTRO.md)
.github/         Ping automático para manter a API acordada
render.yaml      Configuração do serviço no Render
requirements.txt       Dependências completas (front + back, desenvolvimento)
requirements-api.txt   Dependências só do servidor (usado no Render)
.env.example     Modelo das variáveis de ambiente do back-end
```

## Início rápido (desenvolvimento local)

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate        # Windows (no Linux/macOS: source .venv/bin/activate)
```

```bash
pip install -r requirements.txt
```

```bash
uvicorn backend.main:app --reload
```

Em outro terminal, com o ambiente ativado:

```bash
cd frontend && set MARILIA_API=http://127.0.0.1:8000 && python main.py
```

Detalhes (variáveis de ambiente, banco, executável) nos READMEs de [backend](backend/README.md) e [frontend](frontend/README.md).

## Implantação atual (demonstração)

| Parte | Serviço | Plano |
|---|---|---|
| API | [Render](https://render.com) – `https://marilia-api.onrender.com` | Gratuito |
| Banco | [Neon](https://neon.tech) (PostgreSQL) | Gratuito |
| Front | Executável `MARILIA.exe` instalado em cada computador | — |

No plano gratuito o Render "dorme" depois de alguns minutos sem uso; a primeira abertura pode levar até cerca de 1 minuto (o app espera até 90 s). Um workflow do GitHub Actions (`.github/workflows/manter-api-acordada.yml`) acessa a API a cada 10 minutos usando a variável de repositório `MARILIA_API_URL`.

Para uso em uma escola, a mesma API pode rodar em um servidor da rede local; basta apontar o app para ele com `MARILIA_API`.

## Privacidade e LGPD

- Sem autocadastro: só o administrador cria contas.
- Dados mínimos do aluno (nome, e-mail, ano escolar). O tutor de IA recebe apenas a pergunta e o conteúdo do roteiro.
- O professor só acessa progresso, conquistas e histórico de alunos das próprias turmas.
- Usuários de teste (`SEED_USUARIOS_TESTE`) ficam desligados em produção; o administrador inicial é definido por variável de ambiente.
- Limite de tentativas de login (por e-mail e endereço de quem tenta, guardado no banco) e de tamanho das perguntas ao tutor.
- Imagens que deixam de ser usadas são apagadas do banco.

## Versões

| Tag | Conteúdo |
|---|---|
| `v1.0` | Primeira versão completa (antes das correções da análise de código) |
| `v1.1` | Blocos 1 a 3: segurança (JWT obrigatório, e-mail sem maiúsculas, permissões do professor), sessão expirada no app, imagens no banco, implantação na nuvem |
| `v1.2` | Blocos 4 e 5: app aponta para a nuvem e gera `.exe`; professor restrito aos próprios alunos; tipo de imagem pela extensão; limites de login e de pergunta |
| `v1.3` | Blocos 8 e 9: limite de login guardado no banco por e-mail e endereço; limpeza de imagens sem uso; usuários de teste desligados por padrão; READMEs completos |

O histórico detalhado está em [docs/REGISTRO.md](docs/REGISTRO.md).

## Autoria

- **Autora:** Marília Almeida Rosa Pereira
- **Orientador:** Prof. Dr. Aladir Ferreira da Silva Júnior
- **Instituição:** Instituto Federal de Educação, Ciência e Tecnologia de Goiás (IFG), Câmpus Jataí
- **Curso:** Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas

Trabalho de Conclusão de Curso, 2026: *MARILIA: aplicativo para suporte ao aluno no aprendizado e aplicação de robótica no ensino básico*.
