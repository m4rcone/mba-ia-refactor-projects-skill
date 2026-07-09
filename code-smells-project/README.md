# Loja API

API REST de e-commerce em Python/Flask para gestão de produtos, usuários, pedidos e relatório de vendas. Persistência em SQLite.

## Stack

- **Linguagem:** Python 3
- **Framework:** Flask 3.1.1 (+ flask-cors 5.0.1)
- **Banco:** SQLite (`loja.db`, criado e populado automaticamente no primeiro boot)

## Estrutura do projeto (MVC)

```
config/          Configuração central lida de variáveis de ambiente
models/          Acesso a dados por entidade (queries parametrizadas)
controllers/     Regras de negócio e orquestração do fluxo
views/           Blueprints de rotas por domínio (entrada/saída HTTP)
middlewares/     Exceções de domínio + tratamento de erros centralizado
database.py      Conexão e inicialização/seed do banco (infraestrutura)
app.py           Entry point / application factory (composition root)
```

- **config** — `Config` expõe as configurações via `os.environ`, sem segredos no código.
- **models** — um módulo por entidade (`produto_model`, `usuario_model`, `pedido_model`, `system_model`); só aqui existe SQL, sempre com placeholders.
- **controllers** — validações e regras de negócio (cálculo de total, desconto, notificações); lançam exceções de domínio, nunca montam resposta HTTP.
- **views** — Blueprints que extraem a requisição, chamam o controller e serializam a resposta.
- **middlewares** — `AppError`/`ValidationError`/`NotFoundError`/`UnauthorizedError` e o handler central que as converte em resposta JSON consistente.

Direção de dependência: `views → controllers → models → database`; `config` é importado por qualquer camada.

## Instalação e execução

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # ajuste os valores conforme necessário
python app.py
```

A aplicação sobe em `http://localhost:5000` (porta configurável). No primeiro boot o banco é criado e populado com produtos e usuários de exemplo. As senhas do seed são armazenadas com hash; para login use as credenciais originais, ex.: `admin@loja.com` / `admin123`.

## Variáveis de ambiente

Definidas em `.env` (veja `.env.example`):

| Variável      | Padrão            | Descrição                                  |
| ------------- | ----------------- | ------------------------------------------ |
| `SECRET_KEY`  | `dev-only-change-me` | Chave de assinatura do Flask            |
| `DB_PATH`     | `loja.db`         | Caminho do arquivo SQLite                  |
| `FLASK_DEBUG` | `0`               | Modo debug (`1` liga, `0` desliga)         |
| `HOST`        | `0.0.0.0`         | Host de bind do servidor                   |
| `PORT`        | `5000`            | Porta do servidor                          |
| `APP_ENV`     | `development`     | Identificador de ambiente                  |

## Endpoints

| Método | Rota                              | Descrição                          |
| ------ | --------------------------------- | ---------------------------------- |
| GET    | `/`                               | Índice da API                      |
| GET    | `/health`                         | Health check + contagens           |
| GET    | `/produtos`                       | Lista produtos                     |
| GET    | `/produtos/busca`                 | Busca produtos (`q`, `categoria`, `preco_min`, `preco_max`) |
| GET    | `/produtos/<id>`                  | Detalha um produto                 |
| POST   | `/produtos`                       | Cria produto                       |
| PUT    | `/produtos/<id>`                  | Atualiza produto                   |
| DELETE | `/produtos/<id>`                  | Remove produto                     |
| GET    | `/usuarios`                       | Lista usuários                     |
| GET    | `/usuarios/<id>`                  | Detalha um usuário                 |
| POST   | `/usuarios`                       | Cria usuário                       |
| POST   | `/login`                          | Autentica usuário                  |
| POST   | `/pedidos`                        | Cria pedido                        |
| GET    | `/pedidos`                        | Lista todos os pedidos             |
| GET    | `/pedidos/usuario/<usuario_id>`   | Lista pedidos de um usuário        |
| PUT    | `/pedidos/<pedido_id>/status`     | Atualiza status do pedido          |
| GET    | `/relatorios/vendas`              | Relatório de vendas                |
| POST   | `/admin/reset-db`                 | Limpa todas as tabelas             |
| POST   | `/admin/query`                    | Executa SQL de manutenção          |
