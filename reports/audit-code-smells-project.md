================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~490 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] SQL Injection por concatenação de strings (AP-02)
File: models.py:28, models.py:47-49, models.py:57-60, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155-160, models.py:163-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-297
Description: Todas as queries da camada de dados são montadas concatenando input do usuário diretamente na string SQL (ex.: `"SELECT * FROM produtos WHERE id = " + str(id)`, `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`, e o filtro `LIKE '%" + termo + "%'` em `buscar_produtos`). Nenhuma query usa parâmetros vinculados (`?`).
Impact: Qualquer cliente da API pode ler, alterar ou destruir o banco (ex.: `email = "' OR '1'='1"` no login autentica sem senha; `termo` malicioso vaza tabelas inteiras).
Recommendation: Converter 100% das queries para prepared statements com placeholders `?` e tupla de parâmetros (aplicar PB — camada Repository parametrizada). Nenhuma string de SQL pode conter valor vindo da requisição.

### [CRITICAL] Endpoint de execução de SQL arbitrário (AP-02 / backdoor)
File: app.py:59-78
Description: A rota `POST /admin/query` recebe uma string `sql` no corpo e a executa diretamente no banco (`cursor.execute(query)`), sem autenticação, autorização ou validação.
Impact: Backdoor total sobre o banco de dados exposto publicamente — leitura e escrita arbitrárias, `DROP TABLE`, etc. É a falha mais grave do sistema.
Recommendation: Remover o endpoint. Se houver necessidade legítima de manutenção, isolar fora da API pública, atrás de autenticação de admin e allowlist de operações. Manter o contrato removendo a rota (não faz parte do domínio de negócio).

### [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: app.py:7, app.py:8, controllers.py:287-289, database.py:5
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` e `DEBUG = True` estão no código-fonte; `db_path` também fixo. Pior: `health_check` devolve na resposta HTTP `"secret_key": "minha-chave-super-secreta-123"`, `"debug": True` e `"db_path": "loja.db"`.
Impact: Segredo exposto em qualquer clone do repositório e, ainda por cima, vazado publicamente pelo endpoint `/health`. Impossível variar config por ambiente. `DEBUG=True` em produção expõe o debugger Werkzeug (execução remota de código).
Recommendation: Mover segredos e flags para variáveis de ambiente / arquivo de config lido de `.env` (criar `.env.example`). Remover segredos do payload de `/health`. Aplicar PB — camada `config`.

### [CRITICAL] Senhas em texto plano (AP-03)
File: database.py:75-79, models.py:105-111, models.py:122-131, models.py:83, models.py:99
Description: Usuários são semeados com senha em texto plano (`"admin123"`, `"123456"`), `criar_usuario` persiste a senha como veio, o `login_usuario` compara `senha = '<senha>'` literalmente, e `get_todos_usuarios`/`get_usuario_por_id` retornam o campo `senha` no payload da API.
Impact: Vazamento do banco compromete todas as contas imediatamente; a senha ainda trafega de volta nas respostas de listagem/detalhe de usuários.
Recommendation: Hashear senhas com algoritmo forte (`werkzeug.security.generate_password_hash`/`check_password_hash` ou bcrypt); nunca retornar `senha` em respostas. Ajustar o seed. Aplicar PB — Model/serializer que exclui campos sensíveis.

### [CRITICAL] God Files — múltiplas responsabilidades por módulo (AP-04)
File: models.py:1-315, controllers.py:1-293, app.py:47-78
Description: `models.py` mistura acesso a dados (SQL), regra de negócio (cálculo de total e baixa de estoque em `criar_pedido` 133-169; regras de desconto/ticket médio em `relatorio_vendas` 235-273) e montagem de dicionários de resposta, cobrindo produtos + usuários + pedidos + relatórios no mesmo arquivo. `controllers.py` acumula validação, regra de negócio, efeitos colaterais (notificações) e acesso direto ao banco (`health_check` 266-274). `app.py` mistura bootstrap, rotas e handlers com SQL cru inline.
Impact: Nada é testável em isolamento; qualquer mudança tem raio de explosão sobre todos os domínios.
Recommendation: Separar em camadas por domínio: `models/` (entidade + persistência parametrizada), `services/` (regra de negócio), `controllers/` (só HTTP), `routes/` (só binding). Aplicar guidelines MVC + PB de extração de camadas.

### [HIGH] Lógica de negócio no controller e efeitos colaterais na camada errada (AP-05)
File: controllers.py:43-54, controllers.py:208-210, controllers.py:247-250, models.py:133-169, models.py:235-273
Description: Regras de negócio estão espalhadas: validações de faixa/categoria dentro de `criar_produto`/`atualizar_produto`, "envio" de e-mail/SMS/push via `print` dentro do handler `criar_pedido`, notificações por status no handler `atualizar_status_pedido`; enquanto cálculo de total, baixa de estoque e regras de desconto vivem em `models.py`.
Impact: Regra de negócio inseparável do HTTP e do SQL; não testável sem subir o servidor; regras duplicadas/divergentes.
Recommendation: Extrair uma camada `services/` que concentre validação de domínio, cálculos e orquestração de notificações; controllers apenas traduzem HTTP ↔ service. Aplicar PB de service layer.

### [HIGH] Estado global mutável — conexão única compartilhada (AP-06 / AP-07)
File: database.py:4, database.py:7-11, app.py:4
Description: Conexão do SQLite guardada em variável global de módulo (`db_connection = None`) e reaproveitada por todas as requisições com `check_same_thread=False`.
Impact: Condições de corrida entre threads sobre o mesmo cursor/conexão; estado global dificulta teste e substituição; falhas intermitentes sob concorrência.
Recommendation: Gerenciar conexão por requisição (padrão factory + `g`/context do Flask, ou pool), fechando ao fim. Centralizar em camada `config`/`db` com injeção. Aplicar PB de gerência de conexão.

### [HIGH] Acoplamento forte / ausência de injeção de dependência (AP-07)
File: controllers.py:3, controllers.py:266-274, models.py:1, models.py:5
Description: Toda função chama `get_db()` global diretamente; o controller `health_check` acessa o banco sem passar pela camada de dados; módulos dependem de singletons concretos importados por nome.
Impact: Impossível substituir a dependência de banco em testes; mudanças de infraestrutura propagam por todas as camadas.
Recommendation: Injetar o repositório/serviço nas camadas superiores; controllers não devem tocar o banco. Aplicar guidelines MVC de direção de dependência.

### [MEDIUM] Queries N+1 (AP-08)
File: models.py:187-199, models.py:219-231
Description: `get_pedidos_usuario` e `get_todos_pedidos` iteram sobre pedidos e, para cada pedido, buscam itens e, para cada item, fazem outra query buscando o nome do produto (loops aninhados com `execute` por item).
Impact: Degradação linear (na verdade multiplicativa) de performance conforme cresce o número de pedidos/itens.
Recommendation: Substituir por `JOIN` (pedidos × itens × produtos) ou consulta com `IN`, montando o resultado em memória. Aplicar PB de otimização de consulta.

### [MEDIUM] Validação de entrada ausente/insuficiente (AP-09)
File: controllers.py:169-171, controllers.py:239-240, controllers.py:118-121
Description: `login` e `atualizar_status_pedido` chamam `request.get_json()` e usam `.get(...)` sem verificar se o corpo é `None` (payload ausente estoura `AttributeError` → 500 em vez de 400); `buscar_produtos` faz `float()` de `preco_min`/`preco_max` sem tratar valor não numérico.
Impact: Erros 500 não intencionais em vez de 400; experiência de API inconsistente.
Recommendation: Validar presença/tipo do payload numa camada dedicada (schema/validator) antes do service, retornando 400 padronizado. Aplicar PB de validação.

### [MEDIUM] Código duplicado (AP-10)
File: models.py:171-201 vs models.py:203-233, controllers.py:30-50 vs controllers.py:74-90, models.py:12-21/31-40/304-313
Description: `get_pedidos_usuario` e `get_todos_pedidos` são quase idênticos; os blocos de validação de produto em `criar_produto` e `atualizar_produto` repetem as mesmas regras; a serialização de `produto` (mesmo dicionário de campos) é reescrita em três funções.
Impact: Correções precisam ser replicadas manualmente; divergência silenciosa entre cópias.
Recommendation: Extrair funções/serializers reutilizáveis e centralizar as regras de validação na camada de service. Aplicar PB de DRY.

### [MEDIUM] Tratamento de erros genérico com vazamento de detalhes (AP-11)
File: controllers.py:10-12, controllers.py:21-22, controllers.py:60-62 (e demais handlers), controllers.py:291-292
Description: Todo handler captura `except Exception as e` e devolve `str(e)` no corpo da resposta (`{"erro": str(e)}`), expondo detalhes internos (inclusive SQL). Não há error handler central; status codes dependem de cada handler.
Impact: Vazamento de informações internas ao cliente; debugging difícil; tratamento inconsistente.
Recommendation: Error handler centralizado (Flask `errorhandler`) que loga o detalhe e devolve mensagem genérica + status adequado. Aplicar PB de tratamento de erros central.

### [LOW] Magic numbers / magic strings (AP-12)
File: models.py:257-262, models.py:280, controllers.py:52, controllers.py:242
Description: Faixas e percentuais de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) soltos em `relatorio_vendas`; listas de categorias válidas e de status válidos repetidas como strings literais em controllers e sem enum/constante.
Impact: Significado obscuro; alterar uma regra exige caçar todas as ocorrências.
Recommendation: Extrair constantes/enums (status de pedido, categorias, faixas de desconto). Aplicar PB de constantes de domínio.

### [LOW] Nomenclatura ruim / sombreamento de builtin (AP-13)
File: controllers.py:14, controllers.py:56, models.py:24, models.py:187-193, models.py:219-225
Description: Parâmetro `id` sombreia o builtin em várias funções; nomes genéricos `dados`; cursores auxiliares `cursor2`/`cursor3` sem significado.
Impact: Custo de leitura elevado e risco de erro por mal-entendido.
Recommendation: Renomear (`produto_id`, `payload`, cursores nomeados por propósito). Aplicar PB de nomenclatura.

### [LOW] print() usado como logging (AP-14)
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:219, controllers.py:248-250, app.py:56, app.py:83-85
Description: Dezenas de `print(...)` espalhados para registro/debug e "notificações"; sem logger com níveis nem destino configurável.
Impact: Sem controle de nível/destino; ruído em produção; logs não estruturados.
Recommendation: Adotar o módulo `logging` com níveis (`info`/`warning`/`error`) configurável por ambiente. Aplicar PB de logging.

## Deprecated APIs
Nenhuma API deprecated detectada. As versões em uso (Flask 3.1.1, flask-cors 5.0.1, sqlite3 stdlib) não empregam APIs removidas/obsoletas — não há uso de `@app.before_first_request`, `flask.escape` ou `datetime.utcnow()`. Observação (não é deprecation): a inicialização do banco é feita no bloco `__main__` e via `get_db()` global, padrão que deve migrar para inicialização via app factory na Fase 3.

================================
Total: 15 findings
================================
