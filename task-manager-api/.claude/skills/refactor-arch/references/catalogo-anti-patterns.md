# Catálogo de Anti-Patterns

Guia para a **Fase 2**. Cruze cada arquivo-fonte contra este catálogo.
Cada finding deve citar **arquivo e linha(s) exatos** — leia o código para confirmar, não estime.

## Escala de severidade

- **CRITICAL:** falhas graves de arquitetura ou segurança — impedem funcionamento correto, expõem dados sensíveis ou violam completamente a separação de responsabilidades.
- **HIGH:** fortes violações de MVC/SOLID que dificultam muito manutenção e testes.
- **MEDIUM:** padronização, duplicação, gargalos moderados de performance, validações ausentes.
- **LOW:** legibilidade, nomenclatura, magic numbers.

---

## AP-01 — Hardcoded Credentials / Secrets no código — CRITICAL

**Sinais de detecção:**
- Atribuições literais a nomes como `SECRET_KEY`, `API_KEY`, `PASSWORD`, `TOKEN`, `DATABASE_URL` com valor em string no código
- Strings de conexão com usuário/senha embutidos
- Chaves em arquivos commitados (não `.env` ignorado)

**Impacto:** exposição de credenciais em qualquer clone/fork do repositório; impossível variar por ambiente.

## AP-02 — SQL Injection (queries por concatenação/interpolação) — CRITICAL

**Sinais de detecção:**
- SQL montado com f-string, `%`, `.format()`, template literal ou concatenação contendo input do usuário: `f"SELECT * FROM users WHERE id = {user_id}"`, `` `SELECT ... ${req.params.id}` ``
- `cursor.execute(query)` sem parâmetros quando a query contém variáveis

**Impacto:** leitura/alteração arbitrária do banco por qualquer cliente da API.

## AP-03 — Senhas em texto plano / hash fraco — CRITICAL

**Sinais de detecção:**
- Senha salva ou comparada sem hashing (`user.password == password`)
- Uso de `md5`/`sha1` para senhas
- Senha retornada em payloads de resposta da API

**Impacto:** comprometimento total das contas em caso de vazamento do banco.

## AP-04 — God Class / God File — CRITICAL

**Sinais de detecção:**
- Um arquivo/classe concentra 2+ responsabilidades de camadas distintas: roteamento + regra de negócio + SQL + formatação de resposta
- Arquivo com centenas de linhas cobrindo múltiplos domínios (produtos + pedidos + usuários no mesmo módulo)
- Nomes como `AppManager`, `utils`, `helpers` fazendo "de tudo"

**Impacto:** impossível testar em isolamento; qualquer mudança tem raio de explosão total.

## AP-05 — Lógica de negócio no Controller/Handler de rota — HIGH

**Sinais de detecção:**
- Corpo do handler de rota com cálculos de negócio (totais, descontos, regras de status), acesso direto a banco e montagem de resposta no mesmo bloco
- Handlers com dezenas de linhas e múltiplos níveis de if/else de regra de negócio

**Impacto:** regra de negócio inseparável do HTTP; não testável sem subir o servidor.

## AP-06 — Estado global mutável — HIGH

**Sinais de detecção:**
- Listas/dicts/arrays no escopo de módulo usados como "banco de dados" e mutados por handlers
- Variáveis globais de contadores, caches ou sessões (`global` em Python; `let` de módulo em JS mutado por handlers)

**Impacto:** dados perdidos a cada restart, condições de corrida, testes interdependentes.

## AP-07 — Acoplamento forte / ausência de injeção de dependência — HIGH

**Sinais de detecção:**
- Conexão de banco criada dentro de cada função/handler em vez de recebida ou centralizada
- Módulos que se importam mutuamente (imports circulares) ou camada de baixo nível importando a de cima
- Instanciação direta de colaboradores concretos dentro da regra de negócio

**Impacto:** impossível substituir dependências em teste; mudanças propagam por todo o código.

## AP-08 — Queries N+1 / query dentro de loop — MEDIUM

**Sinais de detecção:**
- `for`/`forEach`/`map` contendo `execute(...)`, `query(...)` ou chamada de ORM por item
- Buscar lista e depois buscar detalhes item a item em vez de um JOIN/`IN`

**Impacto:** degradação linear de performance com o volume de dados.

## AP-09 — Validação de entrada ausente nas rotas — MEDIUM

**Sinais de detecção:**
- Handlers usando `request.json["campo"]` / `req.body.campo` diretamente sem verificar presença, tipo ou faixa
- Nenhuma resposta 400 para payload malformado (erro estoura como 500)

**Impacto:** erros 500 não intencionais; dados inconsistentes persistidos.

## AP-10 — Código duplicado — MEDIUM

**Sinais de detecção:**
- Blocos praticamente idênticos repetidos em múltiplos handlers (abrir conexão, serializar entidade, tratar erro)
- Mesma regra de negócio implementada em mais de um lugar (fonte de divergência)

**Impacto:** correções precisam ser replicadas manualmente; divergência silenciosa entre cópias.

## AP-11 — Tratamento de erros ausente ou genérico — MEDIUM

**Sinais de detecção:**
- `except:` / `except Exception: pass` engolindo erros; `catch (e) {}` vazio
- Ausência de error handler central; stack traces vazando na resposta HTTP
- Status codes errados (200 para erro, 500 para input inválido)

**Impacto:** falhas silenciosas, debugging difícil, vazamento de detalhes internos.

## AP-12 — Magic numbers / magic strings — LOW

**Sinais de detecção:**
- Números literais com significado de negócio soltos no código (`if total > 1000: desconto = 0.1`, `status == 3`)
- Strings de status repetidas (`"pendente"`, `"pago"`) sem constante/enum

**Impacto:** significado obscuro; mudança exige caça a todas as ocorrências.

## AP-13 — Nomenclatura ruim — LOW

**Sinais de detecção:**
- Variáveis de 1 letra fora de índices de loop; nomes genéricos (`data`, `x`, `aux`, `temp`, `do_stuff`)
- Nomes que mentem sobre o conteúdo ou misturam idiomas de forma inconsistente

**Impacto:** custo de leitura elevado; erros por mal-entendido.

## AP-14 — Print/console.log como logging — LOW

**Sinais de detecção:**
- `print(...)` / `console.log(...)` espalhados para debug/registro em código de produção
- Ausência de logger configurável com níveis

**Impacto:** sem controle de nível/destino de log; ruído em produção.

---

## APIs Deprecated — verificação obrigatória

Esta verificação vale para **qualquer stack**. Procedimento:

1. Identifique a versão declarada da linguagem, do framework e das bibliotecas relevantes (Fase 1).
2. Para cada API usada no código, avalie com base no seu conhecimento do ecossistema:
   ela foi deprecated ou removida até a versão em uso (ou até a versão estável atual)?
3. Sinais no próprio código também contam: comentários `# deprecated`, avisos de deprecation
   no boot da aplicação, pacotes que a comunidade abandonou em favor de recursos nativos.
4. Para cada ocorrência, reporte a API, arquivo:linha e o **equivalente moderno** recomendado.

Severidade padrão **MEDIUM**, ou HIGH se a API já foi removida na versão em uso.

As tabelas abaixo são **exemplos** para as stacks mais comuns — não são uma lista exaustiva
nem limitam a verificação a essas linguagens:

### Python / Flask
| Deprecated | Equivalente moderno |
|---|---|
| `@app.before_first_request` | removido no Flask 2.3+ — mover para inicialização no factory/`with app.app_context()` |
| `flask.escape` | `markupsafe.escape` |
| `datetime.utcnow()` | `datetime.now(timezone.utc)` (deprecated no Python 3.12) |
| `os.popen` para comandos | `subprocess.run` |

### Node.js / Express
| Deprecated | Equivalente moderno |
|---|---|
| `body-parser` como pacote separado | `express.json()` / `express.urlencoded()` (embutidos desde Express 4.16) |
| `new Buffer(...)` | `Buffer.from(...)` / `Buffer.alloc(...)` |
| `url.parse(...)` | `new URL(...)` (WHATWG) |
| Callbacks `fs` aninhados para fluxo | `fs/promises` + `async/await` |

### Outras stacks (exemplos do mesmo raciocínio)
| Deprecated | Equivalente moderno |
|---|---|
| PHP: `mysql_*` | `PDO` ou `mysqli` com prepared statements |
| Java: `new Date()` / `Calendar` para lógica de datas | `java.time` (JSR-310) |
| Ruby: `URI.escape` | `CGI.escape` / `URI::DEFAULT_PARSER` |
| C#: `WebClient` | `HttpClient` |

**Como reportar:** finding próprio com o nome da API, arquivo:linha, e a recomendação do equivalente moderno.

---

## Checklist de cobertura da auditoria

Antes de fechar o relatório, confirme:

- [ ] Todos os arquivos-fonte foram cruzados contra os 14 anti-patterns
- [ ] APIs deprecated verificadas contra as versões declaradas
- [ ] Mínimo de 5 findings, com pelo menos 1 CRITICAL ou HIGH
- [ ] Cada finding tem arquivo:linha verificados no código real
- [ ] Findings ordenados CRITICAL → HIGH → MEDIUM → LOW
