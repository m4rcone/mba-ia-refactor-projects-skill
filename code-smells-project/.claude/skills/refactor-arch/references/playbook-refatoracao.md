# Playbook de Refatoração

Guia para a **Fase 3**. Um padrão de transformação para cada anti-pattern do catálogo,
com exemplos antes/depois.

**Os padrões são agnósticos de linguagem** — o que cada um define é a transformação
(o que sai de onde e vai para onde), não a sintaxe. Os exemplos usam Python/Flask e
Node.js/Express apenas como ilustração; se a stack detectada for outra, traduza o padrão
para o equivalente idiomático dela (mesma responsabilidade, mecanismos nativos do
framework, biblioteca padrão da comunidade). Ex.: PB-03 em PHP usa `password_hash()`;
PB-11 em Spring usa `@ControllerAdvice`; PB-02 em Java usa `PreparedStatement`.

Aplique na ordem de severidade dos findings (CRITICAL primeiro).

> **Sobre os comentários nos exemplos:** os comentários que aparecem nos blocos de código
> abaixo são apenas didáticos, para você entender o padrão. **Não os copie para o código
> refatorado.** Comente apenas quando agregar valor real e nunca faça referência ao
> playbook, aos anti-patterns ou ao processo de refatoração.

---

## PB-01 — Extrair configuração para módulo de config (corrige AP-01)

**Antes** (`app.py`):

```python
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
DB_PATH = '/tmp/loja.db'
```

**Depois** (`config/settings.py`):

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-me')
    DB_PATH = os.environ.get('DB_PATH', 'loja.db')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
```

(`app.py`):

```python
from config.settings import Config
app.config.from_object(Config)
```

Crie também um `.env.example` documentando as variáveis (sem valores reais).

## PB-02 — Parametrizar queries (corrige AP-02)

**Antes:**

```python
cursor.execute(f"SELECT * FROM produtos WHERE id = {produto_id}")
```

**Depois:**

```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
```

**Antes (Node):**

```javascript
db.query(`SELECT * FROM users WHERE email = '${req.body.email}'`);
```

**Depois (Node):**

```javascript
db.query("SELECT * FROM users WHERE email = ?", [email]);
```

Regra: **nenhuma** variável dentro da string SQL; sempre placeholders do driver.

## PB-03 — Hash de senhas (corrige AP-03)

**Antes:**

```python
if usuario['senha'] == senha_informada: ...
```

**Depois:**

```python
from werkzeug.security import generate_password_hash, check_password_hash

# no cadastro
senha_hash = generate_password_hash(senha)
# no login
if check_password_hash(usuario['senha'], senha_informada): ...
```

Em Node, use `bcrypt` (`bcrypt.hash` / `bcrypt.compare`). Nunca retorne o campo de senha
em respostas da API — remova-o na serialização do model.

## PB-04 — Quebrar God Class por domínio e camada (corrige AP-04)

**Antes:** `models.py` com rotas + SQL + regras de 4 domínios.

**Depois:** um par model/controller por domínio, rotas na view:

```
models/produto_model.py      # SQL de produtos
controllers/produto_controller.py  # regras de produtos
views/produto_routes.py      # endpoints /produtos
```

Processo: (1) identifique os domínios pelas entidades; (2) para cada domínio, extraia
primeiro as funções de acesso a dados para o model; (3) extraia as regras para o controller;
(4) reduza cada rota a extrair→chamar→serializar; (5) delete o arquivo original.

## PB-05 — Extrair lógica de negócio do handler para controller (corrige AP-05)

**Antes** (`app.js`):

```javascript
app.post("/checkout", (req, res) => {
  let total = 0;
  for (const item of req.body.items) {
    const p = produtos.find((x) => x.id === item.id);
    total += p.preco * item.qtd;
  }
  if (total > 1000) total *= 0.9;
  pedidos.push({ id: nextId++, total });
  res.json({ total });
});
```

**Depois** (`views/checkoutRoutes.js`):

```javascript
router.post("/", (req, res, next) => {
  try {
    const pedido = checkoutController.criarPedido(req.body.items);
    res.status(201).json(pedido);
  } catch (err) {
    next(err);
  }
});
```

(`controllers/checkoutController.js`):

```javascript
function criarPedido(items) {
  const total = calcularTotal(items);
  return pedidoModel.create({ total: aplicarDesconto(total) });
}
```

O handler fica com ≤ 15 linhas; toda regra vai para o controller, todo acesso a dados para o model.

## PB-06 — Substituir estado global mutável por camada de persistência (corrige AP-06)

**Antes:**

```javascript
let carrinho = []; // módulo compartilhado, mutado pelos handlers
let contador = 0;
```

**Depois:** encapsular em um model com interface explícita (mantendo armazenamento em memória
se o projeto não tiver banco, ou movendo para o banco existente):

```javascript
// models/carrinhoModel.js
class CarrinhoModel {
  #itens = new Map();
  add(userId, item) { ... }
  list(userId) { ... }
}
module.exports = new CarrinhoModel();
```

O ganho: acesso só por métodos nomeados, estado testável e substituível — nenhum outro
módulo toca a estrutura diretamente.

## PB-07 — Centralizar conexão de banco (corrige AP-07)

**Antes:** cada função abre `sqlite3.connect('loja.db')`.

**Depois** (`database.py`):

```python
import sqlite3
from config.settings import Config

def get_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

Models importam `get_connection()`; nenhum outro módulo conhece o driver.
Use context manager (`with get_connection() as conn:`) para garantir fechamento.

## PB-08 — Eliminar N+1 com JOIN ou IN (corrige AP-08)

**Antes:**

```python
pedidos = conn.execute("SELECT * FROM pedidos").fetchall()
for p in pedidos:
    itens = conn.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (p['id'],)).fetchall()
```

**Depois:**

```python
rows = conn.execute("""
    SELECT p.*, i.produto_id, i.quantidade
    FROM pedidos p LEFT JOIN itens_pedido i ON i.pedido_id = p.id
""").fetchall()
# agrupar em memória por pedido_id
```

Alternativa quando JOIN não cabe: uma segunda query com `WHERE pedido_id IN (...)`.

## PB-09 — Adicionar validação de entrada nas rotas (corrige AP-09)

**Antes:**

```python
nome = request.json['nome']   # KeyError → 500
```

**Depois:**

```python
data = request.get_json(silent=True) or {}
nome = data.get('nome')
preco = data.get('preco')
if not nome or not isinstance(preco, (int, float)) or preco < 0:
    raise ValidationError('nome e preco (>= 0) são obrigatórios')
```

`ValidationError` é uma exceção de domínio tratada pelo error handler central (PB-11) → responde 400.
Validação de **formato** fica na view; validação de **negócio** (ex.: estoque) fica no controller.

## PB-10 — Extrair código duplicado para função única (corrige AP-10)

**Antes:** serialização do mesmo dict de produto repetida em 4 handlers.

**Depois:**

```python
# models/produto_model.py
def to_dict(row):
    return {"id": row["id"], "nome": row["nome"], "preco": row["preco"]}
```

Regra: a cópia canônica vive na camada dona do conceito (serialização de entidade → model;
regra de negócio → controller; formatação de resposta → view/middleware).

## PB-11 — Centralizar tratamento de erros (corrige AP-11)

**Depois** (`middlewares/error_handler.py`):

```python
class AppError(Exception):
    status = 500
class NotFoundError(AppError):
    status = 404
class ValidationError(AppError):
    status = 400

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return {"error": str(e)}, e.status

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception(e)
        return {"error": "Internal server error"}, 500
```

Em Express: middleware `(err, req, res, next)` registrado por último no `app.js`.
Remova todos os try/except vazios; controllers e models **lançam** exceções de domínio, nunca respondem HTTP.

## PB-12 — Substituir magic numbers/strings por constantes (corrige AP-12)

**Antes:**

```python
if pedido['status'] == 3 and total > 1000:
    total = total * 0.9
```

**Depois:**

```python
# controllers/pedido_controller.py (ou constants.py do domínio)
STATUS_PAGO = 3               # ou um Enum
DESCONTO_LIMIAR = 1000.0
DESCONTO_PERCENTUAL = 0.10

if pedido['status'] == STATUS_PAGO and total > DESCONTO_LIMIAR:
    total *= (1 - DESCONTO_PERCENTUAL)
```

## PB-13 — Renomear identificadores ruins (corrige AP-13)

**Antes:** `def calc(x, y, f):` — **Depois:** `def calcular_total(itens, percentual_desconto):`

Regras: nome diz o que a coisa _é/faz_ no domínio; sem abreviações obscuras; consistência de
idioma com o restante do código. Renomeie com busca global para não deixar referências quebradas.

## PB-14 — Substituir print por logging estruturado (corrige AP-14)

**Antes:** `print("erro ao salvar", e)`

**Depois (Python):**

```python
import logging
logger = logging.getLogger(__name__)
logger.error("Falha ao salvar pedido %s", pedido_id, exc_info=True)
```

**Depois (Node):** use `console.error` apenas dentro do error handler central, ou um logger
(`pino`/`winston`) configurado no `config/`.

## PB-15 — Migrar APIs deprecated (corrige findings de Deprecated APIs)

Aplique a substituição indicada no catálogo. Exemplos:

**Antes (Flask ≥ 2.3):**

```python
@app.before_first_request
def init_db(): ...
```

**Depois:**

```python
def create_app():
    app = Flask(__name__)
    with app.app_context():
        init_db()
    return app
```

**Antes (Node):** `const bodyParser = require('body-parser'); app.use(bodyParser.json());`
**Depois:** `app.use(express.json());`

Após migrar, rode a aplicação e confirme que não há warnings de deprecation no boot.

---

## Ordem recomendada de execução

1. **PB-01 / PB-07** — config e conexão centralizadas (base para o resto)
2. **PB-02 / PB-03** — segurança (queries parametrizadas, hash de senha)
3. **PB-04 / PB-05 / PB-06** — separação de camadas (models, controllers, views)
4. **PB-11 / PB-09** — error handler central + validações
5. **PB-08 / PB-10 / PB-15** — performance, deduplicação, APIs deprecated
6. **PB-12 / PB-13 / PB-14** — legibilidade
7. **Validação final** — boot + smoke test de todos os endpoints do inventário da Fase 1
