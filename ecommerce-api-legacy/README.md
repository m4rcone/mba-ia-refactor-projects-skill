# ecommerce-api-legacy

API de um LMS (plataforma de cursos) com fluxo de checkout: usuários se matriculam em
cursos, pagam e o administrador consulta um relatório financeiro. Construída em
Node.js + Express com banco SQLite.

## Stack

- **Linguagem:** JavaScript (Node.js, CommonJS)
- **Framework web:** Express 4
- **Banco de dados:** SQLite (`sqlite3`), em memória por padrão

## Estrutura do projeto

O código segue o padrão MVC com direção de dependência única
(`routes → controllers → models → database`):

```
src/
├── config/          # Configuração centralizada, lida de variáveis de ambiente
├── database/         # Conexão SQLite (Promises) e criação de schema + seed
├── models/           # Acesso a dados por entidade (queries parametrizadas)
├── controllers/      # Regras de negócio e orquestração do fluxo
├── routes/           # Endpoints: validação de entrada e serialização da saída
├── middlewares/      # Erros de domínio e tratamento centralizado de erros
├── services/         # Serviços de domínio (hash de senha)
├── constants.js      # Constantes de domínio (status de pagamento etc.)
└── app.js            # Entry point: monta dependências, rotas e sobe o servidor
```

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e carrega
seeds automaticamente no boot.

## Variáveis de ambiente

Todas são opcionais e têm default seguro para desenvolvimento. Copie `.env.example`
para orientar a configuração por ambiente:

| Variável              | Descrição                                         | Default     |
| --------------------- | ------------------------------------------------- | ----------- |
| `PORT`                | Porta HTTP da aplicação                           | `3000`      |
| `DB_FILE`             | Caminho do arquivo SQLite (`:memory:` para memória) | `:memory:`  |
| `DB_USER`             | Usuário do banco                                  | —           |
| `DB_PASSWORD`         | Senha do banco                                    | —           |
| `PAYMENT_GATEWAY_KEY` | Chave do gateway de pagamento                     | —           |
| `SMTP_USER`           | Usuário SMTP para envio de e-mails                | —           |

## Endpoints

| Método   | Rota                          | Descrição                                                              |
| -------- | ----------------------------- | ---------------------------------------------------------------------- |
| `POST`   | `/api/checkout`               | Cria/reutiliza o usuário, processa o pagamento e efetua a matrícula.   |
| `GET`    | `/api/admin/financial-report` | Relatório de receita e alunos por curso.                               |
| `DELETE` | `/api/users/:id`              | Remove um usuário e, em cascata, suas matrículas e pagamentos.         |

Exemplos de requisições estão em `api.http`.

### POST /api/checkout

Corpo esperado:

```json
{
  "usr": "Guilherme",
  "eml": "gui@fullcycle.com.br",
  "pwd": "senhaforte",
  "c_id": 2,
  "card": "4111222233334444"
}
```

Cartões que começam com `4` são aprovados; os demais retornam `400` (pagamento recusado).
Resposta de sucesso: `{ "msg": "Sucesso", "enrollment_id": <id> }`.
