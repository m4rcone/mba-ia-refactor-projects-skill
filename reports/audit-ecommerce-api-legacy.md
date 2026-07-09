================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js, CommonJS) + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets no código (AP-01)
File: src/utils.js:1-7
Description: O objeto `config` contém segredos em texto literal no código-fonte: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` e `smtpUser`. A chave de gateway é usada em `src/AppManager.js:45`.
Impact: Qualquer clone/fork do repositório expõe credenciais de produção; impossível variar segredos por ambiente e o histórico do git preserva o vazamento.
Recommendation: Mover todos os segredos para variáveis de ambiente carregadas via `.env` (aplicar PB de configuração — camada `config/`), fornecer `.env.example` sem valores reais e nunca logar a chave.

### [CRITICAL] Senhas em texto plano / hash fraco (AP-03)
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68
Description: A senha do seed é gravada em texto plano (`AppManager.js:18` — `pass` = `'123'`). Novos usuários têm a senha "protegida" por `badCrypto` (`utils.js:17-23`), um hash artesanal que faz base64 truncado em loop, sem salt e não reversível de forma segura — não é uma função de hash criptográfica.
Impact: Vazamento do banco compromete todas as contas; o hash caseiro não oferece proteção real e é trivialmente quebrável.
Recommendation: Substituir `badCrypto` por `bcrypt` (ou `scrypt`/`argon2`) com salt, isolado em uma camada de serviço/segurança. Nunca persistir nem retornar senhas em texto plano.

### [CRITICAL] God Class / God File (AP-04)
File: src/AppManager.js:1-141
Description: `AppManager` concentra responsabilidades de todas as camadas: criação da conexão de banco (`:7`), DDL + seeds (`initDb`, `:10-23`), declaração de rotas (`setupRoutes`, `:25`), regra de negócio de checkout (`:28-78`), montagem de relatório (`:80-129`), acesso a dados (SQL inline em todos os handlers) e formatação de respostas HTTP.
Impact: Impossível testar qualquer parte em isolamento; toda mudança tem raio de explosão sobre o arquivo inteiro; nenhuma camada é reutilizável.
Recommendation: Decompor em camadas MVC — `config/database.js`, `models/` (repositórios por entidade), `controllers/`, `routes/`, `services/` para regra de negócio. Aplicar os padrões do playbook de extração de camadas.

### [CRITICAL] Tratamento de erros que corrompe integridade e mascara falha (AP-11)
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` executa `DELETE FROM users` ignorando completamente o `err` do callback (`:133`) e sempre responde `200` com a mensagem "Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco." Não há remoção em cascata nem transação; enrollments/payments do usuário ficam órfãos.
Impact: Integridade referencial quebrada por design; erros de banco são silenciados e retornados como sucesso; dados órfãos acumulam.
Recommendation: Remover em transação (usuário + enrollments + payments) ou impedir exclusão com dependências; tratar `err` e retornar status apropriado (500/409). Centralizar tratamento de erro (aplicar PB de error handler).

### [HIGH] Lógica de negócio no handler de rota (AP-05)
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: O handler de `/api/checkout` implementa toda a regra de negócio inline (buscar curso, criar/reutilizar usuário, decidir aprovação do pagamento por `cc.startsWith("4")`, matricular, registrar auditoria) em callbacks aninhados. O handler de `/api/admin/financial-report` calcula receita e agrega alunos dentro do próprio handler.
Impact: Regra de negócio inseparável do HTTP; não testável sem subir o servidor; callbacks aninhados dificultam manutenção.
Recommendation: Extrair para `services/` (ex.: `CheckoutService`, `ReportService`) usando `async/await`; o controller apenas orquestra request/response. Aplicar PB de extração de service.

### [HIGH] Estado global mutável (AP-06)
File: src/utils.js:9-10, src/utils.js:12-15, src/AppManager.js:59
Description: `globalCache` e `totalRevenue` são variáveis de escopo de módulo (`utils.js:9-10`). `logAndCache` (`:12-15`) muta `globalCache` e é chamada pelo handler de checkout (`AppManager.js:59`). `totalRevenue` é exportada mas nunca usada (código morto).
Impact: Dados perdidos a cada restart; condições de corrida entre requisições; testes interdependentes; estado compartilhado impossível de escalar horizontalmente.
Recommendation: Remover o cache global e `totalRevenue`; se cache for necessário, encapsulá-lo em um serviço com ciclo de vida explícito. Aplicar PB de eliminação de estado global.

### [HIGH] Acoplamento forte / ausência de injeção de dependência (AP-07)
File: src/AppManager.js:7, src/AppManager.js:1
Description: A conexão SQLite é criada diretamente no construtor de `AppManager` (`:7`) e o driver é importado no topo do módulo (`:1`). Todos os handlers acessam `this.db` diretamente; não há camada de repositório nem injeção da conexão.
Impact: Impossível substituir o banco por um dublê em testes; a regra de negócio depende do driver concreto; mudança de banco propaga por todo o arquivo.
Recommendation: Centralizar a criação da conexão em `config/database.js` e injetá-la em repositórios (`models/`); serviços recebem repositórios por injeção. Aplicar PB de injeção de dependência.

### [MEDIUM] Queries N+1 / query dentro de loop (AP-08)
File: src/AppManager.js:89-127
Description: O relatório financeiro busca todos os cursos e, para cada curso, faz `forEach` disparando uma query de enrollments (`:92`); para cada enrollment, dispara uma query de usuário (`:104`) e uma de pagamento (`:106`). O agregado é montado via contadores manuais de callbacks pendentes.
Impact: Número de queries cresce linearmente com cursos × matrículas; degradação de performance e complexidade de controle de fluxo alta.
Recommendation: Substituir por uma única query com JOIN entre courses, enrollments, users e payments (ou agregação SQL), executada em uma camada de repositório. Aplicar PB de consolidação de query.

### [MEDIUM] Validação de entrada insuficiente nas rotas (AP-09)
File: src/AppManager.js:29-35, src/AppManager.js:131-132
Description: `/api/checkout` valida apenas presença de `u/e/cid/cc` (`:35`), sem verificar tipos, formato de e-mail, `c_id` numérico ou formato de cartão; a senha (`pwd`) não é validada e recebe fallback `"123456"` (`:68`). `DELETE /api/users/:id` usa `req.params.id` sem validar que é numérico (`:131-132`).
Impact: Payloads malformados podem gerar erros 500 ou dados inconsistentes; `id` não numérico gera comportamento indefinido.
Recommendation: Adicionar validação de entrada (middleware de validação ou checagens explícitas) com respostas 400 padronizadas. Aplicar PB de middleware de validação.

### [MEDIUM] Erros de banco silenciados em operações de escrita (AP-11)
File: src/AppManager.js:57-61
Description: A inserção em `audit_logs` (`:57`) ignora o parâmetro `err` do callback e prossegue direto para `logAndCache` e resposta de sucesso, sem verificar falha.
Impact: Falha ao registrar auditoria passa despercebida; a operação reporta sucesso mesmo com escrita parcialmente falha.
Recommendation: Tratar `err` de cada escrita e envolver o fluxo de checkout em transação; centralizar o tratamento de erro. Aplicar PB de error handler.

### [LOW] Magic strings / magic numbers (AP-12)
File: src/AppManager.js:46-48, src/AppManager.js:54
Description: Regras de negócio expressas por literais soltos: aprovação do pagamento por `cc.startsWith("4")` (`:46`) e status `"PAID"`/`"DENIED"` repetidos (`:46-48`, `:54`, também no seed `:21`).
Impact: Significado obscuro; alterar a regra ou os status exige caçar todas as ocorrências.
Recommendation: Extrair status para constantes/enum e isolar a decisão de aprovação em um método nomeado no serviço de pagamento.

### [LOW] Nomenclatura ruim (AP-13)
File: src/AppManager.js:29-33
Description: Variáveis de uma letra sem significado no handler de checkout: `u`, `e`, `p`, `cid`, `cc` (`:29-33`); campos de request abreviados (`usr`, `eml`, `pwd`, `c_id`, `card`).
Impact: Custo de leitura elevado e risco de erro por má interpretação.
Recommendation: Renomear para nomes descritivos (`userName`, `email`, `password`, `courseId`, `card`) ao extrair a lógica para o serviço.

### [LOW] console.log usado como logging (AP-14)
File: src/utils.js:13, src/AppManager.js:45, src/app.js:13
Description: `console.log` espalhado para registro/debug em código de produção, incluindo o log do número do cartão e da chave do gateway (`AppManager.js:45` — vazamento de dado sensível), o log de cache (`utils.js:13`) e o boot (`app.js:13`).
Impact: Sem controle de nível/destino de log; ruído em produção; `AppManager.js:45` vaza cartão e chave de API para o stdout.
Recommendation: Remover o log de dados sensíveis imediatamente; adotar um logger com níveis configuráveis. Aplicar PB de logging.

## Deprecated APIs
Nenhuma API deprecated detectada. O código já usa `express.json()` embutido (`app.js:6`) em vez de `body-parser`, e `Buffer.from(...)` (`utils.js:21`) em vez de `new Buffer(...)`. Observação (não é deprecation): o driver `sqlite3` em estilo de callbacks aninhados é legado em relação a alternativas baseadas em Promises (`node:sqlite` / `better-sqlite3`), mas não está deprecated na versão declarada.

================================
Total: 13 findings
================================
