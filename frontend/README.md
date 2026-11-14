# MARILIA – Front-end (aplicativo)

Aplicativo desktop em **Python + [Flet](https://flet.dev)**. Não guarda dados localmente: todas as informações vêm da API (ver [backend/README.md](../backend/README.md)). Cada computador do laboratório só precisa do executável.

## Requisitos

- Para **usar**: Windows e o arquivo `MARILIA.exe`, com acesso à internet (ou à rede da escola, se a API estiver lá).
- Para **desenvolver ou gerar o executável**: Python 3.13 e as dependências de `requirements.txt` (na raiz).

## Instalação (desenvolvimento)

A partir da raiz do repositório:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

## Para qual API o app aponta

Definido em `config.py`:

- **Padrão**: `https://marilia-api.onrender.com` (API na nuvem).
- **Outro endereço**: defina a variável de ambiente `MARILIA_API` antes de abrir o app, por exemplo:
  - API rodando no próprio computador: `http://127.0.0.1:8000`
  - Servidor da escola: `http://<ip-do-servidor>:8000`

## Como rodar

Dentro da pasta `frontend`:

```bash
python main.py
```

Usando a API local (Windows, Prompt de Comando):

```bash
set MARILIA_API=http://127.0.0.1:8000 && python main.py
```

## Gerar o executável (.exe)

No Windows, dentro da pasta `frontend`, com o ambiente virtual ativado:

```bash
pip install pyinstaller
```

```bash
gerar_executavel.bat
```

O arquivo sai em `frontend\dist\MARILIA.exe`. Basta copiá-lo para os outros computadores — não é preciso instalar Python neles. As pastas `dist/` e `build/` e o arquivo `.spec` não vão para o GitHub.

Para um executável que aponte para outro servidor, defina `MARILIA_API` no computador onde ele vai rodar (Painel de Controle → Variáveis de ambiente) ou altere `API_PADRAO` em `config.py` antes de gerar.

## Telas

| Perfil | Telas |
|---|---|
| Todos | Login |
| Aluno | Roteiros (lista e passo a passo, com tutor de IA e níveis de explicação); Glossário; Conquistas; Minhas turmas (entrar pelo código) |
| Professor | Turmas (criar, editar, adicionar alunos); Painel da turma e detalhe do aluno; Gerenciar roteiros; Gerenciar glossário |
| Administrador | Tudo do professor + Gerenciar usuários |

## Organização do código

```
main.py          Ponto de entrada; registra as telas
config.py        Endereço da API (MARILIA_API)
api.py           Cliente HTTP da API (token, erros, sessão expirada)
sessao.py        Usuário logado
navegacao.py     Troca de telas
componentes.py   Elementos visuais reaproveitados
telas/           Uma tela por arquivo
gerar_executavel.bat   Gera o MARILIA.exe
```

## Problemas comuns

| Mensagem | O que fazer |
|---|---|
| "Não foi possível conectar ao servidor." | Verifique a internet. Na primeira abertura do dia o servidor gratuito pode levar até ~1 minuto para acordar (o app espera até 90 s); tente de novo. |
| "Sua sessão expirou. Entre novamente." | O token de login venceu; basta entrar de novo. |
| "Muitas tentativas de login. Aguarde N minuto(s)…" | Foram 5 senhas erradas seguidas para aquele e-mail; espere o tempo indicado. |
| "O tutor está ocupado agora. Tente de novo em instantes." | O serviço de IA está sobrecarregado; espere alguns segundos. |
| "A pergunta pode ter no máximo 500 caracteres." | Resuma a dúvida (o campo mostra o contador). |
