# Task Manager API

API REST para gestão de tarefas, com usuários, categorias e relatórios de produtividade.
Cada tarefa pode ser atribuída a um usuário e a uma categoria, ter prioridade, prazo e tags.

## Stack

- **Linguagem:** Python 3
- **Framework:** Flask 3 (Flask-SQLAlchemy, Flask-CORS)
- **Banco:** SQLite (`tasks.db`)

## Arquitetura (MVC)

O projeto segue uma separação de camadas com direção única de dependência
(`views → controllers → models → database`):

```
task-manager-api/
├── config/         # Configuração lida do ambiente (settings.py)
├── models/         # Entidades de domínio + acesso a dados (Task, User, Category)
├── controllers/    # Regras de negócio, validações e orquestração do fluxo
├── views/          # Blueprints Flask: declaram endpoints e serializam entrada/saída
├── middlewares/    # Tratamento de erros centralizado (exceções de domínio → HTTP)
├── services/       # Serviços auxiliares (ex.: notificações por e-mail)
├── utils/          # Utilitários compartilhados (datas)
├── constants.py    # Constantes de domínio (status, roles, limites)
├── database.py     # Instância do SQLAlchemy
├── seed.py         # Popula o banco com dados de exemplo
└── app.py          # Entry point / application factory (create_app)
```

- **config** — toda a configuração vem de variáveis de ambiente; nenhum segredo no código.
- **models** — encapsulam as queries e a serialização das entidades; não conhecem HTTP.
- **controllers** — concentram validação e regra de negócio; sinalizam falhas lançando exceções de domínio.
- **views** — handlers curtos que extraem a requisição, chamam o controller e devolvem a resposta.
- **middlewares** — convertem exceções de domínio (`ValidationError`, `NotFoundError`, ...) em respostas HTTP padronizadas.

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # ajuste os valores conforme necessário
python3 seed.py            # popula o banco (rode antes do primeiro boot)
python3 app.py
```

A aplicação sobe em `http://localhost:5000` por padrão. O `seed.py` cria usuários,
categorias e tasks de exemplo — **rode-o antes do primeiro boot**, senão os endpoints
retornam listas vazias.

## Variáveis de ambiente

Definidas em `.env` (veja `.env.example`):

| Variável                                                  | Descrição                                   | Default              |
| --------------------------------------------------------- | ------------------------------------------- | -------------------- |
| `SECRET_KEY`                                              | Chave de assinatura da aplicação            | `dev-only-change-me` |
| `DATABASE_URI`                                            | URI do banco (SQLAlchemy)                   | `sqlite:///tasks.db` |
| `FLASK_DEBUG`                                             | Ativa o modo debug (`1`/`0`)                | `0`                  |
| `HOST`                                                    | Host de bind                                | `0.0.0.0`            |
| `PORT`                                                    | Porta de bind                               | `5000`               |
| `MAIL_HOST` / `MAIL_PORT` / `MAIL_USER` / `MAIL_PASSWORD` | Credenciais SMTP do serviço de notificações | —                    |

## Endpoints

| Método | Path                 | Descrição                                                    |
| ------ | -------------------- | ------------------------------------------------------------ |
| GET    | `/`                  | Metadados da API                                             |
| GET    | `/health`            | Healthcheck                                                  |
| GET    | `/tasks`             | Lista tasks (com nome de usuário/categoria e flag de atraso) |
| POST   | `/tasks`             | Cria uma task                                                |
| GET    | `/tasks/<id>`        | Detalha uma task                                             |
| PUT    | `/tasks/<id>`        | Atualiza uma task                                            |
| DELETE | `/tasks/<id>`        | Remove uma task                                              |
| GET    | `/tasks/search`      | Busca tasks por `q`, `status`, `priority`, `user_id`         |
| GET    | `/tasks/stats`       | Estatísticas agregadas de tasks                              |
| GET    | `/users`             | Lista usuários                                               |
| POST   | `/users`             | Cria um usuário                                              |
| GET    | `/users/<id>`        | Detalha um usuário com suas tasks                            |
| PUT    | `/users/<id>`        | Atualiza um usuário                                          |
| DELETE | `/users/<id>`        | Remove um usuário (e suas tasks)                             |
| GET    | `/users/<id>/tasks`  | Lista as tasks de um usuário                                 |
| POST   | `/login`             | Autentica e retorna um token                                 |
| GET    | `/categories`        | Lista categorias (com contagem de tasks)                     |
| POST   | `/categories`        | Cria uma categoria                                           |
| PUT    | `/categories/<id>`   | Atualiza uma categoria                                       |
| DELETE | `/categories/<id>`   | Remove uma categoria                                         |
| GET    | `/reports/summary`   | Relatório geral de produtividade                             |
| GET    | `/reports/user/<id>` | Relatório de produtividade de um usuário                     |
