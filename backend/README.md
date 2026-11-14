# MARILIA – Back-end (API)

API em **Python + FastAPI + SQLModel** que concentra as regras do sistema: usuários e permissões, turmas, roteiros, glossário, progresso, conquistas, imagens e o tutor de IA.

## Requisitos

- Python 3.13
- PostgreSQL 16 (recomendado) — ou SQLite, sem instalar nada, para testes rápidos
- Uma chave de API do provedor de IA escolhido (Groq ou Google Gemini)

## Instalação

A partir da **raiz do repositório**:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate        # Windows (no Linux/macOS: source .venv/bin/activate)
```

```bash
pip install -r requirements-api.txt
```

(`requirements-api.txt` tem só o servidor; `requirements.txt` tem servidor + aplicativo Flet.)

## Variáveis de ambiente

Copie `.env.example` (na raiz) para `.env` e preencha. O arquivo `.env` está no `.gitignore` e **nunca** deve ir para o GitHub.

| Variável | Obrigatória | Padrão | Para que serve |
|---|---|---|---|
| `JWT_SECRET` | **Sim** | — | Chave que assina os tokens de login. A API não sobe sem ela. Use um texto longo e aleatório. |
| `DATABASE_URL` | Não | `sqlite:///./marilia.db` | Endereço do banco. Aceita `postgres://`, `postgresql://` ou `postgresql+psycopg2://` (convertidos para o driver `psycopg`), e tolera aspas ou o prefixo `psql '...'` colados por engano. |
| `IA_PROVEDOR` | Não | `gemini` | `groq` ou `gemini`. |
| `GROQ_API_KEY` | Se `IA_PROVEDOR=groq` | — | Chave da Groq. |
| `GROQ_MODEL` | Não | `openai/gpt-oss-120b` | Modelo usado na Groq. |
| `GEMINI_API_KEY` | Se `IA_PROVEDOR=gemini` | — | Chave do Google Gemini. |
| `GEMINI_MODEL` | Não | `gemini-3.5-flash-lite` | Modelo usado no Gemini. |
| `ADMIN_EMAIL` | Recomendada | — | E-mail do administrador inicial (criado no primeiro início). |
| `ADMIN_SENHA` | Recomendada | — | Senha desse administrador. Se mudar, a senha é atualizada no próximo início. |
| `SEED_USUARIOS_TESTE` | Não | `false` | `true` cria usuários de teste (admin, professor e aluno com senha conhecida). Use só no seu computador, **nunca** em ambiente público. |

## Como rodar

Sempre a partir da raiz do repositório (o pacote se chama `backend`):

```bash
uvicorn backend.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Documentação interativa (Swagger): `http://127.0.0.1:8000/docs` — para testar rotas protegidas, faça `POST /usuarios/login`, copie o `access_token` e clique em **Authorize**.

Para ter os usuários de teste no seu computador, coloque `SEED_USUARIOS_TESTE=true` no `.env`.

Para o app em outro computador da mesma rede: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.

## O que é criado no primeiro início

Ao subir, a API cria as tabelas que ainda não existem (inclusive as novas, como `TentativaLogin`) e o *seed* carrega:

- os 5 roteiros (com etapas, materiais, código e sugestões);
- os 12 termos do glossário;
- as conquistas (badges);
- o administrador de `ADMIN_EMAIL`/`ADMIN_SENHA`;
- os usuários de teste, somente se `SEED_USUARIOS_TESTE=true` (desligado por padrão).

O seed não duplica nada: pode rodar quantas vezes for preciso.

## Rotas e permissões

| Grupo | Rotas | Quem acessa |
|---|---|---|
| Login | `POST /usuarios/login` | Público |
| Usuários | `POST/PUT/DELETE /usuarios` | Admin |
| | `GET /usuarios`, `GET /usuarios/{id}` | Admin (todos); professor (lista de alunos; detalhe só dos alunos das suas turmas e do próprio cadastro) |
| Roteiros | `GET /roteiros`, `GET /roteiros/{id}` | Qualquer usuário logado |
| | `POST/PUT/DELETE /roteiros` | Professor e admin |
| Glossário | `GET /glossario`, `GET /glossario/{id}` | Qualquer usuário logado |
| | `POST/PUT/DELETE /glossario` | Professor e admin |
| Turmas | `GET/POST/PUT/DELETE /turmas`, alunos da turma, `GET /turmas/{id}/dashboard` | Professor (só as próprias) e admin |
| | `POST /turmas/entrar`, `GET /turmas/minhas` | Aluno |
| Progresso e badges | `GET /alunos/{id}/progresso`, `PUT /alunos/{id}/progresso/{roteiro}`, `GET /alunos/{id}/badges` | O próprio aluno; professor (alunos das suas turmas); admin |
| Tutor | `POST /tutor/perguntar` | O próprio aluno |
| | `GET /alunos/{id}/historico` | O próprio aluno; professor (alunos das suas turmas); admin |
| Imagens | `POST /upload/{roteiros\|glossario}` | Professor e admin |
| | `GET /imagens/{pasta}/{nome}` | Público (imagens didáticas) |
| Saúde | `GET /` | Público |

## Segurança

- **Autenticação**: JWT (`Authorization: Bearer <token>`); token expirado devolve 401 e o app volta ao login.
- **Senhas**: guardadas só como hash; mínimo de 6 caracteres.
- **Limite de login** (guardado no banco, tabela `TentativaLogin`, não se perde quando o servidor reinicia):
  - 5 senhas erradas para o mesmo e-mail **a partir do mesmo endereço** em 15 minutos → HTTP 429 para aquele endereço; a dona da conta continua entrando de outro computador;
  - 20 senhas erradas para o mesmo e-mail, de qualquer endereço, em 15 minutos → HTTP 429 (proteção contra tentativas distribuídas);
  - um login certo apaga as falhas daquele e-mail e endereço; tentativas com mais de 15 minutos são apagadas automaticamente;
  - atrás de proxy (Render), o endereço é o último item do cabeçalho `X-Forwarded-For`.
- **Tutor**: pergunta de até 500 caracteres; instruções com regras de segurança e restrição ao tema (robótica, eletrônica, programação e o roteiro em estudo); nenhum dado pessoal vai para a IA. Se o provedor estiver sobrecarregado, a API tenta de novo e, se não conseguir, devolve 503 "O tutor está ocupado agora".
- **Upload**: só `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, até 5 MB; o tipo é definido pela extensão; as imagens ficam no banco (tabela `Imagem`) e são apagadas quando nenhum roteiro, etapa ou termo do glossário as usa mais.
- **LGPD**: professor restrito aos alunos das próprias turmas; e-mails comparados sem diferença de maiúsculas.

## Implantação (Render + Neon)

1. Crie um banco PostgreSQL no Neon e copie a *connection string*.
2. No Render, crie o serviço a partir do `render.yaml` (Blueprint) ou manualmente:
   - Build: `pip install -r requirements-api.txt`
   - Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. Preencha as variáveis: `DATABASE_URL`, `GROQ_API_KEY` (ou Gemini), `ADMIN_EMAIL`, `ADMIN_SENHA`. O `render.yaml` já define `SEED_USUARIOS_TESTE=false`, `IA_PROVEDOR=groq` e gera o `JWT_SECRET`.
4. Confira `https://<servico>.onrender.com/` (`{"status": "ok"}`) e `/docs`.
5. Para evitar que o serviço gratuito durma, defina no GitHub a variável de repositório `MARILIA_API_URL` (Settings → Secrets and variables → Actions → Variables) com o endereço da API; o workflow `manter-api-acordada.yml` faz o ping a cada 10 minutos.

## Scripts auxiliares (raiz)

- `teste_groq.py`, `teste_gemini.py`: testam a chave e o modelo do provedor de IA.
- `listar_modelos.py`: lista os modelos disponíveis no Gemini.
