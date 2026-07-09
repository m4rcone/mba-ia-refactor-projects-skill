================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3 + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1)
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets no código (AP-01)
File: app.py:11-13, services/notification_service.py:7-10
Description: `SECRET_KEY = 'super-secret-key-123'` e o URI do banco estão fixos em `app.py`. Em `notification_service.py` o host, usuário e senha de SMTP (`email_password = 'senha123'`) estão embutidos no código.
Impact: qualquer clone/fork expõe a chave de assinatura da aplicação e credenciais de e-mail; impossível variar por ambiente e risco direto de comprometimento.
Recommendation: mover para variáveis de ambiente carregadas via `python-dotenv` (já declarado) num módulo `config/`. Aplicar PB-config (camada de configuração) + fornecer `.env.example`.

### [CRITICAL] Hash de senha fraco (MD5) (AP-03)
File: models/user.py:27-32
Description: `set_password`/`check_password` usam `hashlib.md5(pwd.encode()).hexdigest()`. MD5 é criptograficamente quebrado e sem salt.
Impact: comprometimento total das contas em caso de vazamento do banco — hashes MD5 são reversíveis por rainbow tables em segundos.
Recommendation: usar `werkzeug.security.generate_password_hash` / `check_password_hash` (já disponível via Flask) na camada de model.

### [CRITICAL] Senha exposta em respostas da API (AP-03)
File: models/user.py:16-25, routes/user_routes.py:85-86, routes/user_routes.py:207-211
Description: `User.to_dict()` inclui o campo `'password'` (o hash) no payload. Esse dict é retornado em `POST /users` (create_user) e em `POST /login`, além de qualquer rota que serialize usuário.
Impact: o hash da senha vaza para qualquer cliente da API em criação de usuário e login.
Recommendation: remover `password` da serialização do model; criar serialização segura na camada de views/schema.

### [CRITICAL] God File — controller acumulando responsabilidades de múltiplas camadas (AP-04)
File: routes/task_routes.py:1-299, routes/report_routes.py:1-224, routes/user_routes.py:1-211
Description: os blueprints concentram roteamento HTTP + regras de negócio + acesso a dados (queries SQLAlchemy) + serialização manual no mesmo bloco. `report_routes.py` mistura ainda dois domínios distintos (relatórios e CRUD de categorias). Nenhuma camada de service/repository é usada (o `services/` existente está morto).
Impact: impossível testar regras em isolamento; qualquer mudança tem raio de explosão total; violação completa da separação MVC.
Recommendation: extrair services (regra de negócio) e repositories/models (acesso a dados); controllers só orquestram request→service→response. Separar categorias em seu próprio módulo. Aplicar PB-01/PB-02.

### [HIGH] Lógica de negócio no controller (fat controllers) (AP-05)
File: routes/task_routes.py:12-63, routes/task_routes.py:273-299, routes/report_routes.py:13-101, routes/report_routes.py:104-155
Description: `get_tasks` monta o dict campo a campo, calcula "overdue" e enriquece com nome de usuário/categoria; `task_stats`, `summary_report` e `user_report` executam agregações de negócio (contagens por status/prioridade, completion_rate, produtividade por usuário) direto no handler.
Impact: regra de negócio inseparável do HTTP; não testável sem subir o servidor; lógica de "overdue" e agregações duplicadas em vários pontos.
Recommendation: mover cálculos e agregações para uma camada de service (`TaskService`, `ReportService`). Aplicar PB-02.

### [HIGH] Acoplamento forte / ausência de injeção de dependência (AP-07)
File: services/notification_service.py:5-25, models/task.py:38-48
Description: `NotificationService` instancia SMTP e credenciais internamente, sem injeção — impossível mockar em teste (e o serviço nem é referenciado no app). O model `Task` contém métodos de validação (`validate_status`, `validate_priority`) que também são reimplementados nas rotas, indicando responsabilidades mal alocadas.
Impact: dependências concretas não substituíveis em teste; regras espalhadas entre model e controller.
Recommendation: injetar colaboradores (config/cliente SMTP) e centralizar validação numa camada de service/schema. Aplicar PB-02/PB-config.

### [HIGH] Tratamento de erros genérico engolindo exceções (AP-11)
File: routes/task_routes.py:62-63, routes/task_routes.py:137, routes/task_routes.py:236-238, routes/user_routes.py:130-132, routes/user_routes.py:149-151, routes/report_routes.py:186-188, routes/report_routes.py:207-209, routes/report_routes.py:221-223
Description: uso repetido de `except:` / `except Exception` retornando `500` genérico e sem log estruturado; o `except:` em `get_tasks` mascara qualquer falha real. Não há error handler central.
Impact: falhas silenciosas, debugging difícil, causa raiz perdida; status codes por vezes imprecisos.
Recommendation: adotar error handlers centralizados do Flask (`@app.errorhandler`) e capturar exceções específicas; logar com logger. Aplicar PB-04 (tratamento centralizado de erros).

### [MEDIUM] Queries N+1 dentro de loop (AP-08)
File: routes/task_routes.py:41-57, routes/report_routes.py:53-68
Description: em `get_tasks`, para cada task executa `User.query.get()` e `Category.query.get()`; em `summary_report`, para cada usuário executa `Task.query.filter_by(user_id=...)`. Uma query por item.
Impact: degradação linear de performance conforme cresce o volume de dados.
Recommendation: usar `joinedload`/`selectinload` ou agregações SQL (`GROUP BY`) na camada de repository. Aplicar PB-05.

### [MEDIUM] Código duplicado — cálculo de "overdue" e serialização de task (AP-10)
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:283-288, routes/user_routes.py:171-180, routes/report_routes.py:34-37, routes/report_routes.py:132-135, models/task.py:50-60
Description: o mesmo bloco aninhado de decisão de "overdue" está reescrito em 6 locais (existindo já `Task.is_overdue()` no model, não usado). A serialização de task é feita manualmente em `get_tasks` e `get_user_tasks` em vez de reusar `to_dict()`.
Impact: correções precisam ser replicadas manualmente; risco de divergência silenciosa entre cópias.
Recommendation: centralizar em `Task.is_overdue()` e num serializer único. Aplicar PB-03 (eliminar duplicação).

### [MEDIUM] Validação de entrada frágil gerando 500 (AP-09)
File: routes/task_routes.py:261, routes/task_routes.py:264, routes/user_routes.py:42-72
Description: `search_tasks` faz `int(priority)`/`int(user_id)` direto sobre query params sem try — um valor não numérico estoura 500. A validação de payload é manual, repetida e inconsistente entre create/update; `marshmallow` está declarado mas não é usado.
Impact: erros 500 não intencionais para input malformado; regras de validação divergentes.
Recommendation: introduzir schemas (marshmallow) na camada de views para validar/coagir entrada e devolver 400 padronizado. Aplicar PB-06.

### [MEDIUM] API deprecated — `datetime.utcnow()` (Deprecated APIs)
File: models/task.py:15-16,52; models/user.py:14; routes/task_routes.py:31,72,215,285; routes/user_routes.py:172; routes/report_routes.py:35,42,45,71,133; utils/helpers.py:38,45; seed.py:66-74
Description: uso pervasivo de `datetime.utcnow()`, deprecated no Python 3.12 (retorna datetime naïve).
Impact: warnings de deprecation e datetimes sem timezone; remoção futura quebrará o código.
Recommendation: substituir por `datetime.now(timezone.utc)`. Centralizar em util de data.

### [LOW] Print como logging (AP-14)
File: routes/task_routes.py:149,153,219,234; routes/user_routes.py:83,89,147; services/notification_service.py:21,24; utils/helpers.py:38-40
Description: `print(...)` usado para registro/debug em código de aplicação; sem logger com níveis.
Impact: sem controle de nível/destino de log; ruído em produção.
Recommendation: usar o módulo `logging` configurado na camada de config.

### [LOW] Nomenclatura ruim (AP-13)
File: routes/task_routes.py:16,268; routes/user_routes.py:14; routes/report_routes.py:24-28,55,161; models/category.py:14; seed.py:16-61
Description: variáveis de uma letra fora de índices de loop (`t`, `u`, `c`, `td`, `d`) e nomes numerados sem significado (`p1`..`p5`, `c1`..`c4`, `u1`..`u3`).
Impact: custo de leitura elevado; risco de mal-entendido.
Recommendation: renomear para nomes descritivos (`task`, `user`, `category`).

### [LOW] Magic numbers / magic strings (AP-12)
File: routes/task_routes.py:110,113,177,182; routes/user_routes.py:64-72; models/task.py:39,46; routes/task_routes.py:96-100
Description: strings de status (`'pending'`, `'in_progress'`, `'done'`, `'cancelled'`), roles, faixa de prioridade 1–5 e limites de título 3/200 repetidos literalmente em vários arquivos. Já existem constantes em `utils/helpers.py:110-116`, mas não são usadas.
Impact: significado obscuro; mudança exige caçar todas as ocorrências.
Recommendation: centralizar em constantes/enums reutilizados por models e views. Aplicar PB-07.

## Deprecated APIs
- `datetime.utcnow()` — reportado acima como finding MEDIUM (Python 3.12). Equivalente moderno: `datetime.now(timezone.utc)`.

================================
Total: 14 findings
================================
