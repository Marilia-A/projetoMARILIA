# Registro de desenvolvimento – MARILIA

Diário do que foi feito no software, blocos de correções, decisões e pendências.
Atualizado a cada etapa. (Itens de texto do TCC ficam no checklist pessoal; aqui só aparecem quando dependem do software.)

Última atualização: **16/11/2026**

---

## ⚠️ Regra primordial – autoria

**Todo o conteúdo do repositório é de autoria exclusiva da autora.**
- Commits, merges e tags: somente `Marilia-A <mariliaalmeidarosa01@gmail.com>`.
- Sem coautores, sem rodapés ou assinaturas automáticas em commits, PRs ou comentários.
- Branches sempre com o nome do bloco (ex.: `bloco-10-visual`).
- Merge feito pelo computador da autora (`git merge --no-ff` + push), não pelo botão do site, para o committer também ser a autora.
- Antes de cada push: conferir `git log --format='%an <%ae>%n%b'`. Depois de criar/editar PR: conferir a descrição.

---

## Situação geral

| Versão | Commit / estado | Conteúdo |
|---|---|---|
| v1.0 | `8bd3ab4` | Antes das correções da análise de código |
| v1.1 | `970d7c3` | Blocos 1 a 3 + DATABASE_URL + admin do seed (PRs #1 a #4) |
| v1.2 | `5d6b100` | Blocos 4 e 5 – front na nuvem + executável; acesso do professor, upload, limites (PRs #5, #6 e os PRs de 13/11) |
| v1.3 | `1d547b2` | Correções da verificação (limite de login no banco, limpeza de imagens, usuários de teste desligados por padrão) + READMEs completos |
| v1.3.1 | `caf7b48` | Limite de login na nuvem pelo endereço real (PR #15) |
| v1.4 | `65cb8cf` | Blocos 10 e 11 – visual infantil + usuários de demonstração. **Guarda o visual de antes do Bloco 12.** |
| v1.5 | `bf08d62` | Bloco 12 – telas de gerenciamento no tema, rodapé fixo no roteiro e robôs interativos (PR #18) |

Regra das tags: **v1.0 nunca muda** (main original). As demais acompanham os blocos já mesclados no `main`.

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

- Revisão do GitHub: descrições dos PRs #1 a #10 sem rodapés automáticos; os dois branches de nome indevido foram apagados (os branches dos blocos continuam no GitHub); tags v1.0, v1.1 e v1.2 publicadas pela autora.
- PR #10 – regra de autoria reescrita em texto neutro; v1.2 registrada.
- Verificação de PRs passada para o chat "Verificar PR e Correções": revisar #1 a #10 e reportar qualquer falha de código (de qualquer nível) para correção posterior.

### 14/11/2026
- PR #12 – `.gitignore` corrigido (`.env` e `dist/` voltam a ser ignorados). Merge local, committer da autora.
- PR #11 – registro com verificação por evento, pendências e falhas. Merge local.
- Texto do TCC revisado capítulo a capítulo (fora do repositório); PDF `TCC_Marilia_3` conferido.
- **Bloco 8 – correções da verificação** (PR #13, branch `bloco-8-correcoes-verificacao`):
  - limite de login guardado no banco (tabela `TentativaLogin`), por **e-mail + endereço** (5 erros/15 min) e geral por e-mail (20 erros/15 min); tentativas antigas apagadas a cada login; endereço lido do último item do `X-Forwarded-For` atrás do proxy do Render;
  - imagens apagadas do banco quando nenhum roteiro, etapa ou termo as usa mais (troca ou exclusão);
  - regra "aluno de turma do professor" em uma só função (`backend/seguranca.py`);
  - `SEED_USUARIOS_TESTE` com padrão `false` no código; `.env.example` com `DATABASE_URL` comentada (SQLite por padrão);
  - testado: 17 verificações em SQLite e PostgreSQL 16 + testes do Bloco 5.
- **Verificação na nuvem** (`verificar_nuvem.py`, rodado pela autora): 56/62 → PR #15 (endereço real pelo `CF-Connecting-IP`/1º item do `X-Forwarded-For`; login certo com 2 consultas em vez de 5) → 59/62 → usuários de teste excluídos e `SEED_USUARIOS_TESTE=false` no Render → **61/62** (login 1,9–2,1 s, ver decisão sobre o hash).
- Tags: v1.3 em `1d547b2` (Blocos 8 e 9); v1.3.1 sugerida em `caf7b48` (correção do PR #15).
- **Bloco 11 – usuários de demonstração** (branch `bloco-11-usuarios-demonstracao`): professor e aluno criados por `DEMO_PROFESSOR_*`/`DEMO_ALUNO_*` (senhas só no servidor), já ligados à "Turma de Demonstração"; admin continua sendo só o do `ADMIN_*`. Testado: 14 verificações, incluindo cadastro bloqueado para quem não é admin (401/403).
- **Bloco 10 – visual infantil** (branch `bloco-10-visual`): tema em Flet com paleta colorida (roxo, azul, laranja, verde, rosa, amarelo), cabeçalho em faixa colorida, cartões arredondados com ícone, botões grandes, login com logo, tutor com balão de conversa, conquistas em troféus, dashboard com cartões de resumo. Telas do professor/admin herdam o tema. Testado: 21 telas montadas com dados reais da API + navegação por todas as páginas do roteiro + balão do tutor. Falta: teste visual no Windows e prints.
- **Bloco 9 – documentação** (branch `bloco-9-documentacao`): READMEs com a sigla, a autoria e o comportamento do Bloco 8; registro atualizado; renumeração (Bloco 10 = visual).
- PRs #16 e #17 mesclados pelo botão do site (committer "GitHub"); daqui para frente, voltar ao merge local.

### 15/11/2026
- **Verificação geral**: `main` testado localmente (13/13); API no Render e banco no Neon respondendo (raiz 200, rotas protegidas 401, login consultando o banco em 0,7–0,9 s, imagem servida do banco). Primeiro acesso com o servidor dormindo: ~33 s. O ping do GitHub Actions roda só a cada 4–6 h (o GitHub atrasa agendamentos de 10 min), então não mantém a API acordada.
- **Contas de teste criadas pela autora** (aluno e professor): 51 verificações em todas as rotas, todas funcionando (permissões 401/403 corretas, tutor respondendo, turma/roteiro/termo/imagem temporários criados e apagados). As variáveis `DEMO_*` não estão no Render.
- **Bloco 12 – ajustes visuais e robôs interativos** (branch `bloco-12-ajustes-visuais`):
  - Turmas, detalhe da turma, formulários e gerenciamento de roteiros, glossário e usuários passam a usar o tema (cabeçalho colorido, cartões, botões e campos arredondados, campos na largura do painel);
  - roteiro: **Voltar/Avançar fixos no rodapé** (antes mudavam de altura a cada página); a página volta ao topo ao trocar; texto da tutora e das sugestões em 17 px; campo de pergunta mais largo;
  - dashboard com vírgula decimal ("1,0 de 5");
  - `frontend/robos.py`: robô desenhado com formas do Flet; mascote que acena/fala no login, na tela inicial e nas conquistas; uma brincadeira por roteiro na primeira página (lâmpada, semáforo, botão, dia/noite com LDR, alarme com PIR); cabeça do robô na tutora; robô que comemora ao concluir;
  - animações seguras: trocar de tela no meio de uma animação não trava o app;
  - testado com a API local (SQLite): telas de aluno, professor e admin; as 5 brincadeiras clicadas; aviso de nova conquista depois da comemoração. Falta: teste no Windows (`.exe`).
- PR #18 (Bloco 12) mesclado pelo botão do site (`bf08d62`, committer "GitHub"); o commit do bloco está no nome da autora. Comandos das tags v1.4 e v1.5 passados à autora.
- O VS Code da autora estava no branch antigo `bloco-10-visual` (por isso parecia que o Bloco 10 não tinha entrado); os Blocos 10 e 12 estão no `main`. Orientação: `git checkout main` + `git pull origin main`.
- **Bloco 13 – prints e registro** (branch `bloco-13-prints-registro`): 22 prints em `docs/prints/` (2560 × 1600) com índice e sugestão de uso no 6.2; prints principais no README do front; registro atualizado. O tutor e o painel do professor foram fotografados na nuvem (1 pergunta a mais no histórico da conta de teste do aluno).
- Verificação dos PRs devolvida ao chat "Verificar PR e Correções" (por evento, como antes), começando pelo PR #18 e pelo PR do Bloco 13.
- PR #19 (Bloco 13) mesclado pelo botão do site (`f394ac4`, committer "GitHub").
- **Revisão do Bloco 12 e do Bloco 13** (chat "Verificar PR e Correções"): nenhum erro de código; as 31 telas abriram como aluno, professor e admin; os robôs e as brincadeiras funcionaram nos cliques. Pontos visuais e de conteúdo anotados em "Falhas encontradas na verificação".
- **Nuvem confirmada pela autora**: o Render respondeu (~32 s no primeiro acesso com o servidor dormindo) e o Neon recebeu as tentativas de login (tabela `tentativalogin`), tanto as de um teste direto na API quanto as feitas pelo Flet rodando no VS Code. O app usa a API do Render e o banco do Neon, nada local.
- **Testes das telas pela autora** com admin, aluno (AnaTester) e professor (BrunoTester) contra a nuvem: todas as telas, robôs, brincadeiras e tutor funcionando. O `uvicorn` local ficou sem nenhuma requisição, confirmando que tudo passou pela API no ar.
- **Bloco 15 – login e versão do executável** (branch `bloco-15-login-versao`):
  - login: enquanto espera a API, o botão vira "Entrando...", fica desativado junto com os campos e aparece o aviso de que o primeiro acesso pode levar até 1 minuto (servidor dormindo). Cliques repetidos e Enter são ignorados até a resposta, então não contam várias tentativas erradas de uma vez no limite de login (antes, 5 cliques com a senha errada bloqueavam o e-mail por 15 min);
  - `gerar_executavel.bat`: versão do arquivo de 1.2.0 para 1.6.0;
  - testado (simulado, sem janela): 5 cliques + Enter durante a espera geraram 1 pedido à API; botão e campos voltam ao normal depois do erro; login certo vai para os roteiros. Falta: conferir na janela do app.
- PRs #20 e #21 mesclados pelo botão do site (`18fe84b` e `e1c8a8c`, committer "GitHub").
- **Bloco 15 não funcionou na janela** (a autora não viu o "Entrando..."): no Flet 0.86, um clique com função comum (sem `async`) trava a janela até terminar, então nada aparece antes da resposta da API, e os cliques extras ficam na fila e viram logins seguidos. O teste do Bloco 15 era simulado, sem a janela, e não pegou isso.
- **Bloco 16 – login assíncrono** (branch `bloco-16-login-assincrono`): o clique do login virou `async` e o pedido à API roda em segundo plano (`asyncio.to_thread`); a janela fica livre para mostrar o aviso, e os cliques durante a espera são ignorados. Testado **na janela** (Flet no navegador, API falsa com 3–5 s de espera): aparecem o "Entrando..." e o aviso; 5 cliques geraram 1 login (o código do Bloco 15 gerou 5, igual ao print do Neon da autora); a senha errada volta com a mensagem de erro; o login certo abre a tela de roteiros.
- PR #22 (Bloco 16) mesclado pelo botão do site (`f64768d`, committer "GitHub"). Revisão dos PRs #20 a #22 pelo chat "Verificar PR e Correções": nenhum erro de código; apontou que o tutor tinha o mesmo problema do login.
- Primeira tentativa de gerar o `.exe`: no PowerShell, `gerar_executavel.bat` não roda sem o `.\` antes (o PowerShell não executa arquivos da pasta atual pelo nome).
- **Bloco 17 – tutor assíncrono e `.bat` mais fácil** (branch `bloco-17-tutor-executavel`):
  - tutor: o clique em "Perguntar" virou `async` e a pergunta roda em segundo plano (`asyncio.to_thread`), como o login; a rodinha de carregando aparece e cliques repetidos são ignorados (antes viravam várias perguntas ao Groq, todas gravadas no histórico do aluno). Campo de pergunta desativado durante a espera;
  - `gerar_executavel.bat`: ativa sozinho a `.venv` da raiz (funciona com dois cliques), avisa se faltar o Flet ou o PyInstaller e para com mensagem se der erro; README do front explica o `.\` do PowerShell;
  - testado **na janela** (Flet no navegador, API local com SQLite e IA falsa de 4 s): rodinha aparece durante a espera; 5 cliques geraram 1 pergunta; a resposta aparece na bolha da tutora.
- Pendente (🟡, apontado na revisão): os outros cliques que chamam a API (salvar, buscar, concluir roteiro, montar a tela de roteiros depois do login) ainda travam a janela durante a resposta. São rápidos com o servidor acordado; corrigir só se incomodar.
- PR #23 (Bloco 17) mesclado pelo botão do site (`9a8f1b4`, committer "GitHub"). O merge local da autora travou no editor `vi` do Git; resolvido com `git reset --hard origin/main` (conteúdo idêntico). Para os próximos merges: `git merge --no-ff --no-edit` ou `git config --global core.editor "code --wait"`.
- **Executável gerado e testado pela autora** (Windows 11, no próprio computador): `.\gerar_executavel.bat` no PowerShell terminou com "Build complete!" (Python 3.13.7 da `.venv`, PyInstaller 6.22.3, arquivo único sem console). `MARILIA.exe` com **53,9 MB**, versão do arquivo 1.6.0.0 e do produto 1.6.0. Os três perfis (admin, AnaTester e BrunoTester) funcionaram com seus níveis de acesso; o "Entrando..." aparece e o login com o servidor acordado levou cerca de 2 s.
  - ⚪ Duas mensagens "O sistema não pode encontrar o caminho especificado" no início do `.bat`, sem efeito na geração (provavelmente da reativação da `.venv` já ativa).
  - ⚪ Nas propriedades do `.exe`: "Nome do arquivo original" aparece como `flet.exe`, idioma Inglês e "Direitos autorais" vazio (padrão do `flet pack`). Dá para preencher com `--copyright` no `.bat`, se quiser.
- **Código encerrado** por decisão da autora (16/11). Daqui para frente: tag v1.6, teste do `.exe` em outro PC e texto do TCC.
- **SUS (System Usability Scale), avaliação preliminar pela autora** (16/11), 10 itens padrão em escala de 1 a 5:
  - respostas: 5, 1, 5, 1, 4, 1, 5, 1, 4, 1;
  - cálculo: ímpares (resposta − 1) = 4+4+3+4+3 = 18; pares (5 − resposta) = 4+4+4+4+4 = 20; (18 + 20) × 2,5 = **95**;
  - classificação: acima de 85, faixa "excelente" (Bangor, Kortum e Miller, 2009); nota A+ na escala de Sauro e Lewis (a partir de 84,1);
  - limitação: uma só respondente, que é a autora do sistema. Deve aparecer no texto como avaliação preliminar, não como teste de usabilidade com usuários. Pontos conhecidos que pesam contra: contraste das cores e primeiro acesso de ~33 s com o servidor dormindo.

---

## Como trabalhamos (vale para todas as sessões)

- **Regra primordial de autoria** (topo deste arquivo) antes de qualquer envio.
- Um branch e um PR por bloco; tag só depois do merge, criada pela autora (o ambiente automatizado não consegue enviar tags nem apagar branches).
- **Verificação por evento, não periódica**: sempre que um PR for aberto ou algo for enviado ao GitHub, o chat "Verificar PR e Correções" é avisado, revisa e testa. Sem check-ins a cada poucas horas.
- Falhas encontradas na verificação (qualquer nível) são anotadas na seção "Falhas encontradas na verificação" abaixo e corrigidas depois, quando a autora pedir.
- Este arquivo é a memória do projeto: cada sessão deve lê-lo antes de começar e atualizá-lo ao terminar.

---

## Decisões registradas

- **Sem autocadastro**: só o admin cria usuários.
- **Front desktop** (`.exe`) apontando para a API; web fica como trabalho futuro.
- **Listagem de alunos para o professor** (`GET /usuarios`): o professor vê todos os alunos (nome, e-mail, ano) porque é dessa lista que ele escolhe quem adicionar à turma. Progresso, conquistas, histórico e detalhe continuam restritos às turmas dele. Alternativa futura: o professor só adiciona alunos pelo código da turma, e a listagem passa a mostrar só os alunos dele.
- **Limite de login por e-mail + endereço** (Bloco 8, substitui a decisão de 13/11 de contar só por e-mail): errar a senha de outra pessoa a partir de outro computador não bloqueia mais a conta dela. O limite geral de 20 erros por e-mail continua existindo como proteção contra tentativas de vários endereços; nesse caso extremo, a conta pode ficar bloqueada por até 15 min.
- **Contas de demonstração do TCC** (15/11): **AnaTester** (aluna, `ana@ifg.com`) e **BrunoTester** (professor), criadas pela autora pelo admin em 14/11. Os e-mails são fictícios e ficam assim por decisão da autora. Os usuários de demonstração pelas variáveis `DEMO_*` (Bloco 11) **não** serão configurados no Render; o código continua lá, mas sem uso. Novos prints devem usar sempre essas duas contas.

---

## Pendências

### Configuração na nuvem (sem código)
- [ ] Testar o login do admin no Swagger (`/docs` → `POST /usuarios/login`).
- [x] **CRÍTICO**: `SEED_USUARIOS_TESTE=false` no Render; usuários de teste excluídos (14/11, verificação 61/62).
- [ ] Trocar a senha (123456) das contas de teste criadas pelo app em 15/11 antes da banca.
- [ ] Criar as variáveis `DEMO_*` no Render (ou usar as contas de teste no lugar delas).
- [ ] No dia da apresentação, acordar a API ~2 min antes (abrir o endereço ou Actions → Run workflow).
- [x] Padrão de `SEED_USUARIOS_TESTE` mudado para `false` no código (Bloco 8). Mesmo assim, conferir no painel do Render.

### Bloco 4 – front na nuvem + executável → tag v1.2
- [x] Front aponta para a nuvem por padrão
- [x] Script do executável
- [ ] Gerar o `.exe` no Windows e testar (login, roteiro, tutor, dashboard)
- [x] PR #7 mesclado + tag v1.2

### Bloco 5 – segurança e limites → tag v1.2
- [x] Professor só acessa dados de alunos das próprias turmas (PRs #5 e #6)
- [x] Tipo da imagem pela extensão (PR #5)
- [x] Limite de tentativas de login
- [x] Limite de tamanho da pergunta ao tutor
- [x] PR #8 mesclado → incluído na tag v1.2

### Bloco 6 – Documentação (READMEs para o GitHub)
Três arquivos, cada um com o que é necessário para aquela parte. **Escritos e mesclados em 13/11** (PR #9), junto com `.env.example`. Sigla e autoria preenchidas no Bloco 9 (14/11). Falta só: prints das telas no README do front (Bloco 10).

- [x] **`README.md` (raiz)**
  - O que é o MARILIA (origem do nome, público, contexto do START e do TCC)
  - Funcionalidades por perfil (aluno, professor, admin)
  - Arquitetura: front Flet desktop → API FastAPI → PostgreSQL; IA (Groq / Gemini); diagrama simples
  - Estrutura de pastas
  - Início rápido (link para os READMEs do back e do front)
  - Implantação atual (Render + Neon, gratuitos) e ping do GitHub Actions
  - Versões / tags (v1.0 a v1.3) e o que cada uma traz
  - Privacidade / LGPD (minimização de dados, professor só vê os próprios alunos, usuários de teste desligados em produção)
  - Autoria, orientação e licença
- [x] **`backend/README.md`**
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
- [x] **`frontend/README.md`**
  - Requisitos: Python 3.13, Windows (para o `.exe`)
  - Instalação: `pip install -r requirements.txt`
  - Rodar em desenvolvimento: `python main.py` dentro de `frontend/`
  - `MARILIA_API`: padrão nuvem; como apontar para `http://127.0.0.1:8000` ou para o servidor da escola
  - Gerar o executável: `pip install pyinstaller` + `gerar_executavel.bat` → `dist/MARILIA.exe`
  - Primeira abertura: o servidor gratuito pode levar até ~1 min para acordar (o app espera até 90 s)
  - Telas por perfil (com prints quando o visual estiver pronto)
  - Problemas comuns (sem conexão, sessão expirada, muitas tentativas de login, tutor ocupado)
- [x] Revisar se `requirements.txt` (front + back) e `requirements-api.txt` (só servidor) estão descritos certo.

### Fluxo de trabalho
- Seguir a **regra primordial de autoria** (topo deste arquivo).
- Um branch e um PR **separado por bloco**; tag criada só depois do merge no `main`.
- PRs acompanhados automaticamente (comentários, revisões e CI).

### Para fazer mais tarde (agendado)
- [x] **Bloco 10 – visual infantil** no Flet (PR #17) + Bloco 12 (gerenciamento no tema e robôs interativos).
- [x] Prints das telas para o 6.2 e para o README do front (Bloco 13, `docs/prints/`). Refazer no Windows só se o visual mudar.
- [x] Testar o `MARILIA.exe` no Windows contra a nuvem: funcionou no computador da autora (16/11).
- [ ] Testar o `MARILIA.exe` em outro PC, sem Python (laboratório da escola).
- [x] Item CRÍTICO no Render (14/11).
- [ ] Tags: `v1.4` (`65cb8cf`) e `v1.5` (`bf08d62`) conferidas no GitHub (15/11). Criar `v1.6` depois do merge do Bloco 17 (executável 1.6.0).
- [x] Preencher nos READMEs: sigla do MARILIA, orientação/instituição (Bloco 9).
- [x] Padronizar os nomes dos roteiros entre texto e `backend/seed.py` (o texto do TCC passou a usar os nomes do app, 14/11) ("Luz Noturna Automática" × "Luz Noturna com LDR"; "Alarme com Sensor de Presença" × "Alarme com Sensor PIR").
- [x] Corrigir as falhas que a verificação dos PRs apontou (Bloco 8, PR #13).

### Falhas encontradas na verificação
*(preenchido pelo chat "Verificar PR e Correções"; nada corrigido sem pedido da autora)*
Revisão de 13/11 dos PRs #1 a #11 (53 verificações automáticas passaram na `main` 4d14675):

- 🔴 **`.gitignore` sem proteger `.env` e `dist/`** (linhas grudadas desde o PR #7) → corrigido no PR #12.
- ✅ (regra) 🟠 **Committer dos merges pelo site**: merges dos PRs #5 a #10 (e o commit da v1.2) ficam com committer "GitHub" (padrão do botão de merge). Não reescrever o histórico; daqui para frente, merge local (`git merge --no-ff` + push) evita.
- ✅ (Bloco 8) 🟠 **Limite de login usado contra outra pessoa**: 5 senhas erradas bloqueiam aquele e-mail por 15 min, mesmo com a senha certa depois; contagem em memória se perde quando o Render reinicia.
- ✅ (Bloco 8) 🟡 Lista de falhas de login só cresce (e-mails inventados ficam guardados até o servidor reiniciar).
- ✅ (Bloco 8) 🟡 `.env.example` com `DATABASE_URL` de Postgres ativa: quem copiar sem editar e não tiver Postgres não sobe a API.
- ✅ (Bloco 8) 🟡 Imagens de itens excluídos/trocados continuam no banco.
- ✅ (Bloco 8) 🟡 Regra "aluno de turma do professor" repetida em dois lugares (`seguranca.py` e `routers/usuarios.py`) → juntar numa função.
- ✅ (16/11) 🟡 `gerar_executavel.bat` testado no Windows: gerou o `MARILIA.exe` 1.6.0.
- Decisão mantida: professor vê a lista de todos os alunos. Padrão `SEED_USUARIOS_TESTE` já é `false` (Bloco 8).

Revisão de 15/11 do PR #18 (Bloco 12) e do Bloco 13 (PR #19); nenhum erro de código:

- 🟠 **Committer dos merges pelo site** continua: PRs #13 a #19 ficaram com committer "GitHub". Não reescrever o histórico; voltar ao merge local.
- 🟡 **Contraste das cores** (desde o Bloco 10): texto branco sobre verde, laranja e amarelo fica difícil de ler (ex.: botão "Ver progresso", estrela amarela).
- ⚪ **Brincadeira do LED**: o balão fala em `delay(1000)` (1 segundo), mas a animação pisca a cada 0,5 s.
- ⚪ **Prints com contas misturadas**: 17 e 20 usam "Aluno Demonstração" (API local); 21 e 22 usam AnaTester (nuvem). Resolvido pela decisão de usar só AnaTester e BrunoTester; refazer os prints 17 e 20 se forem para o TCC.
- ⚪ **"8 ano" sem o º** no nome da turma da conta de teste (as outras telas mostram "8º ano").
- ⚪ **Print 22 cortado**: a seção "Perguntas ao tutor" só mostra o título.

### Melhorias opcionais
- [ ] Dashboard com menos consultas por aluno
- [x] Apagar imagens antigas do banco ao trocar/excluir (Bloco 8)
- [x] Mensagem "tutor ocupado" no app (13/11)
- [ ] Progresso único por aluno/roteiro no banco (restrição de unicidade)
- [ ] Recriar o serviço do Render na região Virginia (banco está na Virginia) se o dashboard ficar lento
- [x] Visual infantil no Flet → Blocos 10 e 12
- [x] Padrão de `SEED_USUARIOS_TESTE` = `false` no código (Bloco 8)

### Dependências do texto do TCC ligadas ao software
- ✅ 3.4, 5.1, 5.6 e 6.1: implantação na nuvem, imagens no banco, admin por variável de ambiente, usuários de teste desligados (texto revisado em 14/11).
- ✅ (16/11) 6.1: **atualizar a frase** do limite de login (Bloco 8 já entrou): 5 erros por e-mail + endereço em 15 min, limite geral de 20 por e-mail.
- ✅ (16/11) 5.6: não cita usuários de demonstração por variáveis de ambiente, nada a mudar; pela decisão de 15/11 (AnaTester e BrunoTester criadas pelo admin), o 6.1 já diz que as contas foram criadas no aplicativo.
- ✅ (16/11) 6.2: prints novos (`docs/prints/`) e robôs interativos/brincadeiras (Bloco 12).
- ✅ (16/11) 6.3 e Tabela 7: trocar o "~0,6 s" (medido com o banco vazio em 11/11). Medições de 15/11: 0,7–0,9 s (login errado, servidor acordado), 1,5–2,4 s (login certo, por causa do hash PBKDF2) e ~33 s no primeiro acesso com o servidor dormindo. Falta medir na rede local.
- ✅ (16/11) Cap. 7: tirar "melhoria do visual para o público infantil" dos trabalhos futuros (Blocos 10 e 12 entraram).
- ✅ Cap. 7: versão web como trabalho futuro.
- ✅ (16/11) Texto revisado (arquivos `05_Implementao.tex` = cap. 6 e `06_Consideraes.tex` = cap. 7): SUS como avaliação preliminar pela autora (95, Tabela de respostas, `Bangor2009` no `.bib`), RNF01 preenchido, RNF08 "atendido com adaptação" (login certo 1,5–2,4 s por causa do hash), 4 figuras (`01_login`, `03_roteiro_led`, `11_tutor`, `21_dashboard`), robôs e visual infantil, limitação do servidor gratuito (~33 s), contraste como trabalho futuro.
- ✅ (16/11) Referência à ZDP no cap. 6 ("Capítulo 1") está certa: a ZDP é apresentada na Introdução.
- ✅ (16/11) Resumo e Abstract (SUS preliminar, 95 pontos), cap. 5 (Front-End distribuído como executável), cap. 3 (visual infantil a partir do START; testes finais na nuvem e com o `.exe`; SUS como avaliação preliminar) e cap. 1 (4º objetivo sem "conformidade com a SUS"; tutor delimitado ao conteúdo de cada roteiro) atualizados.
