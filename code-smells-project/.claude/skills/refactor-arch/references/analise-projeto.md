# Análise de Projeto — Heurísticas de Detecção

Guia para a **Fase 1**. O objetivo é descobrir a stack e mapear a arquitetura atual
**apenas lendo arquivos** — nunca assuma nada com base no nome do diretório do projeto.

## 1. Detecção de linguagem

Verifique, nesta ordem, os arquivos-manifesto na raiz do projeto:

| Evidência | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, arquivos `.py` | Python |
| `package.json`, arquivos `.js` / `.ts` | JavaScript / TypeScript (Node.js) |
| `composer.json`, arquivos `.php` | PHP |
| `Gemfile`, arquivos `.rb` | Ruby |
| `pom.xml`, `build.gradle`, arquivos `.java` | Java |
| `go.mod`, arquivos `.go` | Go |
| `*.csproj`, arquivos `.cs` | C# / .NET |

A tabela não é exaustiva: se a linguagem não estiver nela, identifique-a pela extensão
predominante dos arquivos-fonte e pelo manifesto de dependências correspondente do ecossistema.

Se houver mais de uma linguagem, considere principal a que contém os arquivos de aplicação (não scripts auxiliares).

## 2. Detecção de framework e versão

Leia o manifesto de dependências e procure o framework web. Confirme com imports/requires no código:

| Linguagem | Dependência no manifesto | Confirmação no código |
|---|---|---|
| Python | `flask` | `from flask import Flask` |
| Python | `django` | `django.urls`, `manage.py` |
| Python | `fastapi` | `from fastapi import FastAPI` |
| Node.js | `express` | `require('express')` / `import express` |
| Node.js | `fastify`, `koa`, `nestjs` | require/import correspondente |
| PHP | `laravel/framework` | `artisan`, namespace `App\` |
| Ruby | `rails` | `config/routes.rb` |

Para qualquer outra linguagem, aplique o mesmo raciocínio: procure o framework web no
manifesto de dependências do ecossistema e confirme pelos imports no código.

**Versão:** extraia do manifesto (`flask==3.1.1`, `"express": "^4.18.0"`) ou de lockfiles
(`package-lock.json`, `poetry.lock`). Reporte a versão declarada.

## 3. Detecção de banco de dados

Procure por:

- **Drivers/ORMs no manifesto:** `sqlite3` (stdlib Python — procure no código), `psycopg2`, `mysqlclient`, `sqlalchemy`, `pg`, `mysql2`, `mongoose`, `sequelize`, `prisma`, `knex`
- **Strings de conexão:** `sqlite:///`, `postgres://`, `mysql://`, `mongodb://` — em código ou arquivos `.env`
- **Arquivos de banco:** `*.db`, `*.sqlite`, `*.sqlite3` na raiz
- **DDL no código:** comandos `CREATE TABLE` (comum em `database.py`, `db.js`, `schema.sql`, scripts `seed`)

**Tabelas/entidades:** liste a partir dos `CREATE TABLE`, das classes de model/ORM,
ou dos nomes usados em queries (`SELECT ... FROM <tabela>`). Se os dados vivem em
estruturas em memória (listas/dicts/arrays globais), reporte "em memória" e liste as entidades.

## 4. Identificação do domínio

Deduza o domínio da aplicação a partir de:

- Nomes de entidades e tabelas (ex.: `produtos`, `pedidos`, `usuarios` → E-commerce; `tasks`, `projects` → Task Manager; `courses`, `enrollments` → LMS)
- Rotas expostas (`/products`, `/checkout`, `/tasks`)
- README do projeto, se existir

Descreva em uma linha: tipo de sistema + principais entidades.

## 5. Mapeamento da arquitetura atual

Responda às perguntas abaixo lendo os arquivos-fonte:

1. **Onde estão as rotas?** Todas em um arquivo? Espalhadas? Em um diretório `routes/`?
2. **Onde está a lógica de negócio?** Dentro dos handlers de rota? Em services? Misturada com SQL?
3. **Onde está o acesso a dados?** SQL cru inline? ORM? Camada dedicada? Estado global em memória?
4. **Onde está a configuração?** Hardcoded no código? Variáveis de ambiente? Arquivo de config?
5. **Existe tratamento de erros centralizado?** Ou cada rota trata (ou ignora) por conta própria?
6. **Quantos arquivos-fonte existem** (excluindo dependências, testes e assets)?

Classifique a arquitetura em uma linha, por exemplo:

- "Monolítica — tudo em N arquivos, sem separação de camadas"
- "Parcialmente organizada — possui models/routes/services, mas com vazamento de responsabilidades entre camadas"
- "MVC parcial — camadas existem mas controllers contêm lógica de negócio e SQL"

## 6. Inventário de endpoints

Liste todos os endpoints (método HTTP + path) encontrados nas rotas. Esse inventário
é o **contrato que a Fase 3 deve preservar** — guarde-o para a validação final.

Fontes: o mecanismo de declaração de rotas do framework detectado — ex.: decorators
`@app.route(...)` (Flask), `app.get/post/...` (Express), `urls.py` (Django), anotações
`@GetMapping` (Spring), `routes.rb` (Rails) — além de arquivos `.http` ou coleções de API
no repositório (ótima fonte de verdade para validação).

## 7. Arquivos a ignorar

Nunca conte nem analise: `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `.git/`,
`dist/`, `build/`, lockfiles (use-os apenas para versão), `.claude/`.
