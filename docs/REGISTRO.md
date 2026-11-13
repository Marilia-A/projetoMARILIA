# Registro de desenvolvimento – MARILIA

Diário do que foi feito no software, blocos de correções, decisões e pendências.
Atualizado a cada etapa. (Itens de texto do TCC ficam no checklist pessoal; aqui só aparecem quando dependem do software.)

Última atualização: **13/11/2026**

---

## Situação geral

| Versão | Commit / estado | Conteúdo |
|---|---|---|
| v1.0 | `8bd3ab4` | Antes das correções da análise de código |
| v1.1 | `970d7c3` | Blocos 1 a 3 + DATABASE_URL + admin do seed (PRs #1 a #4) |
| v1.2 | *a criar* | Bloco 4 – front na nuvem + executável |
| v1.3 | *a criar* | Bloco 5 – acesso do professor, upload, limites (PRs #5, #6 + commit de 13/11) |

- API no ar: `https://marilia-api.onrender.com` (Render, gratuito, região Oregon)
- Banco: Neon (PostgreSQL gratuito, US East). PostgreSQL local para desenvolvimento.
- Front: aplicativo desktop (Flet), um `.exe` por computador, apontando para a API.

---

## Linha do tempo

### 11/11/2026
- Análise completa do código (back e front), falhas classificadas em crítico / importante / melhoria.
- **Bloco 1** – `requirements.txt` em UTF-8; usuários de teste opcionais (`SEED_USUARIOS_TESTE`); `JWT_SECRET` obrigatório; `pool_pre_ping`; e-mail sem diferença de maiúsculas; professor só vê as próprias turmas e dashboards (admin vê todas). Testado no PostgreSQL 16: 33 verificações aprovadas.
- **Bloco 2** – token expirado volta ao login com aviso "Sua sessão expirou".
- **Bloco 3** – imagens guardadas no banco (tabela `Imagem`); app espera até 90 s o servidor acordar; admin inicial por `ADMIN_EMAIL`/`ADMIN_SENHA`; `render.yaml`, `requirements-api.txt` e ping a cada 10 min (GitHub Actions + variável `MARILIA_API_URL`).
- PR #3 – `DATABASE_URL` aceita texto extra ao colar.
- Banco criado no Neon; API publicada no Render e testada (raiz 200, rotas protegidas 401, imagens ok, login ~0,6 s). Senha do Neon trocada depois de exposta.

### 12/11/2026
- Diagnóstico do login no Render: Neon estava sem usuários (não era erro de código). Regra mantida: só o admin cria usuários.
- `ADMIN_EMAIL`/`ADMIN_SENHA` configurados no Render; seed criou usuários de teste, roteiros, glossário e badges no Neon.
- PR #4 – seed mantém o admin do ambiente e atualiza a senha pelo `ADMIN_SENHA`.
- Histórico do Git limpo (commits e tags só com o nome/e-mail da autora). Tags v1.0 e v1.1 conferidas.
- Decisão: front continua desktop (`.exe`) apontando para a nuvem; versão web do Flet vira trabalho futuro.

### 13/11/2026
- PR #5 (`correcoes-revisao-prs`) – tipo da imagem pela extensão do arquivo; professor só lista alunos e só vê alunos das próprias turmas em `/usuarios/{id}`; seed acha o admin sem diferença de maiúsculas; `DATABASE_URL` com qualquer driver postgres; ping avisa quando falta `MARILIA_API_URL`.
- PR #6 (`correcao-lgpd-dados-alunos`) – professor só acessa progresso, conquistas e histórico de alunos das próprias turmas.
- **Bloco 4** (commit `68ec582`):
  - `frontend/config.py`: padrão passa a ser `https://marilia-api.onrender.com`; `MARILIA_API` continua valendo para desenvolvimento local ou servidor da escola (barra final é ignorada).
  - `frontend/gerar_executavel.bat`: gera `frontend/dist/MARILIA.exe` com `flet pack` (PyInstaller). `dist/`, `build/` e `*.spec` no `.gitignore`.
  - Testado: front conversando com a API local via `MARILIA_API`. **Falta:** gerar o `.exe` no Windows e testar contra a nuvem (de preferência em outro PC).
- **Bloco 5 – restante** (commit `a95f555`):
  - Limite de login: 5 senhas erradas para o mesmo e-mail em 15 min → HTTP 429 "Muitas tentativas de login. Aguarde N minuto(s)". Login certo zera a contagem. Controle em memória (suficiente para um único servidor; zera se o Render reiniciar).
  - Pergunta ao tutor limitada a 500 caracteres (API devolve 422; campo do app com contador e `max_length=500`).
  - Tela do tutor passa a mostrar a mensagem real da API para 422 e 503 (antes trocava "O tutor está ocupado agora" por um texto genérico).
  - Professor pode consultar o próprio cadastro em `/usuarios/{id}` (antes recebia 403).
  - Testado com SQLite: 5×401 + 429; outro e-mail não é afetado; professor 200 no próprio cadastro e 403 no do admin; pergunta com 501 caracteres → 422.

---

## Decisões registradas

- **Sem autocadastro**: só o admin cria usuários.
- **Front desktop** (`.exe`) apontando para a API; web fica como trabalho futuro.
- **Listagem de alunos para o professor** (`GET /usuarios`): o professor vê todos os alunos (nome, e-mail, ano) porque é dessa lista que ele escolhe quem adicionar à turma. Progresso, conquistas, histórico e detalhe continuam restritos às turmas dele. Alternativa futura: o professor só adiciona alunos pelo código da turma, e a listagem passa a mostrar só os alunos dele.
- **Limite de login por e-mail** (e não por IP): o Render fica atrás de proxy e o IP real não é confiável sem configuração extra. Efeito colateral aceito: alguém que erre a senha de outra pessoa 5 vezes bloqueia aquele login por 15 min.

---

## Pendências

### Configuração na nuvem (sem código)
- [ ] Testar o login do admin no Swagger (`/docs` → `POST /usuarios/login`).
- [ ] **CRÍTICO**: `SEED_USUARIOS_TESTE=false` no Render; excluir `admin@teste.com` pelo app; trocar a senha do aluno/professor de teste (o repositório é público e mostra a senha padrão).
- [ ] Observação: no código o padrão de `SEED_USUARIOS_TESTE` é `true`. O `render.yaml` já define `false`, mas vale conferir no painel do Render se a variável está mesmo lá. (Melhoria possível: mudar o padrão do código para `false`.)

### Bloco 4 – front na nuvem + executável → tag v1.2
- [x] Front aponta para a nuvem por padrão
- [x] Script do executável
- [ ] Gerar o `.exe` no Windows e testar (login, roteiro, tutor, dashboard)
- [ ] PR + tag v1.2

### Bloco 5 – segurança e limites → tag v1.3
- [x] Professor só acessa dados de alunos das próprias turmas (PRs #5 e #6)
- [x] Tipo da imagem pela extensão (PR #5)
- [x] Limite de tentativas de login
- [x] Limite de tamanho da pergunta ao tutor
- [ ] PR + tag v1.3

### Bloco 6 – Documentação (READMEs para o GitHub)
Três arquivos, cada um com o que é necessário para aquela parte:

- [ ] **`README.md` (raiz)**
  - O que é o MARILIA (origem do nome, público, contexto do START e do TCC)
  - Funcionalidades por perfil (aluno, professor, admin)
  - Arquitetura: front Flet desktop → API FastAPI → PostgreSQL; IA (Groq / Gemini); diagrama simples
  - Estrutura de pastas
  - Início rápido (link para os READMEs do back e do front)
  - Implantação atual (Render + Neon, gratuitos) e ping do GitHub Actions
  - Versões / tags (v1.0 a v1.3) e o que cada uma traz
  - Privacidade / LGPD (minimização de dados, professor só vê os próprios alunos, usuários de teste desligados em produção)
  - Autoria, orientação e licença
- [ ] **`backend/README.md`**
  - Requisitos: Python 3.13, PostgreSQL 16 (ou SQLite para teste rápido)
  - Instalação: `pip install -r requirements-api.txt`
  - Variáveis de ambiente (tabela, com obrigatoriedade e padrão):
    `DATABASE_URL` (padrão SQLite local), `JWT_SECRET` (obrigatória), `IA_PROVEDOR` (`gemini`/`groq`, padrão `gemini`), `GROQ_API_KEY`, `GROQ_MODEL` (padrão `openai/gpt-oss-120b`), `GEMINI_API_KEY`, `GEMINI_MODEL`, `ADMIN_EMAIL`, `ADMIN_SENHA`, `SEED_USUARIOS_TESTE` (padrão `true`)
  - Exemplo de `.env` (sem segredos reais)
  - Como rodar: `uvicorn backend.main:app --reload` a partir da raiz; Swagger em `/docs`
  - O que o seed cria (roteiros, glossário, badges, admin, usuários de teste opcionais)
  - Rotas por grupo e quem pode acessar (aluno / professor / admin)
  - Segurança: JWT, hash de senha, limite de login, limite da pergunta, upload de imagens (tipos e 5 MB)
  - Deploy no Render (`render.yaml`) + Neon; variável `MARILIA_API_URL` do ping
- [ ] **`frontend/README.md`**
  - Requisitos: Python 3.13, Windows (para o `.exe`)
  - Instalação: `pip install -r requirements.txt`
  - Rodar em desenvolvimento: `python main.py` dentro de `frontend/`
  - `MARILIA_API`: padrão nuvem; como apontar para `http://127.0.0.1:8000` ou para o servidor da escola
  - Gerar o executável: `pip install pyinstaller` + `gerar_executavel.bat` → `dist/MARILIA.exe`
  - Primeira abertura: o servidor gratuito pode levar até ~1 min para acordar (o app espera até 90 s)
  - Telas por perfil (com prints quando o visual estiver pronto)
  - Problemas comuns (sem conexão, sessão expirada, muitas tentativas de login, tutor ocupado)
- [ ] Revisar se `requirements.txt` (front + back) e `requirements-api.txt` (só servidor) estão descritos certo.

### Melhorias opcionais
- [ ] Dashboard com menos consultas por aluno
- [ ] Apagar imagens antigas do banco ao trocar/excluir
- [x] Mensagem "tutor ocupado" no app (13/11)
- [ ] Progresso único por aluno/roteiro no banco (restrição de unicidade)
- [ ] Recriar o serviço do Render na região Virginia (banco está na Virginia) se o dashboard ficar lento
- [ ] Visual infantil no Flet + prints das telas para o TCC (6.2)
- [ ] Padrão de `SEED_USUARIOS_TESTE` = `false` no código

### Dependências do texto do TCC ligadas ao software
- 3.4, 5.1, 5.3.7 e 6.1: incluir a implantação na nuvem (Neon + Render) como demonstração, imagens no banco, admin por variável de ambiente, usuários de teste desligados (+ LGPD).
- 6.1/6.2: citar o limite de login (5 tentativas / 15 min) e o limite da pergunta (500 caracteres) entre as medidas de segurança.
- 6.3: tempo de login medido na nuvem (~0,6 s, RNF08 < 2 s).
- Cap. 7: versão web do Flet como trabalho futuro.
