# Guidelines de Arquitetura — Padrão MVC Alvo

Guia para a **Fase 3**. Define as camadas, as responsabilidades de cada uma
e as regras de dependência que o projeto refatorado deve seguir.

**Estas guidelines são agnósticas de linguagem e framework.** As regras descrevem
*responsabilidades e dependências* — conceitos que existem em qualquer stack.
A materialização (nomes de diretórios, mecanismos de rota, sintaxe) deve ser derivada
da stack detectada na Fase 1, seguindo o procedimento da seção "Como aplicar na stack detectada".

## As cinco camadas obrigatórias

Independente da linguagem, o projeto refatorado deve ter estas responsabilidades
**separadas em módulos/diretórios distintos**:

| Camada | Responsabilidade | Nunca faz |
|---|---|---|
| **Config** | Configuração centralizada, lida do ambiente | Conter segredos hardcoded |
| **Models** | Entidades de domínio + todo o acesso a dados | Conhecer HTTP (request/response/status) |
| **Controllers** | Regras de negócio e orquestração do fluxo | Conter SQL ou detalhes do driver de banco |
| **Views/Routes** | Declarar endpoints, extrair/validar formato de entrada, serializar saída | Conter lógica de negócio |
| **Middlewares** | Error handling centralizado e aspectos transversais | — |

Mais um **entry point (composition root)**: o único lugar que monta tudo — cria a
aplicação, carrega config, registra rotas e middlewares, inicializa o banco. Sem lógica
de negócio, sem rotas inline.

Para APIs sem interface gráfica, a camada **View** é a definição de rotas + serialização
da resposta. Não crie templates de UI se a aplicação original não os tinha.

## Estrutura de diretórios de referência

Quando o framework **não impõe** uma estrutura própria, use esta como base,
adaptando os nomes à convenção de nomenclatura da linguagem (snake_case, camelCase, PascalCase etc.):

```
src/  (ou a raiz, conforme o costume da linguagem)
├── config/          # Configuração centralizada
├── models/          # Um model por entidade de domínio
├── views/           # Definição de rotas por domínio
├── controllers/     # Um controller por domínio
├── middlewares/     # Error handler central e middlewares transversais
├── database.<ext>   # Conexão/inicialização do banco (infra)
└── app.<ext>        # Entry point / composition root
```

**Se o framework já tem uma convenção MVC nativa** (Rails, Laravel, Django, Spring MVC,
ASP.NET MVC, Phoenix...), **siga a convenção do framework** em vez de impor a árvore acima —
o objetivo é a separação de responsabilidades, não um layout específico de diretórios.
Ex.: em Django, "controllers" são as views do framework e os "models" são os models do ORM;
em Rails, use `app/models`, `app/controllers`, `config/`.

## Responsabilidades detalhadas

### Config
- Toda configuração em um único módulo, lida de **variáveis de ambiente** (ou o mecanismo
  de config idiomático do framework) com defaults seguros para desenvolvimento.
- Nenhum segredo hardcoded em nenhum outro arquivo.

### Models
- Encapsulam **todo o acesso a dados** (queries parametrizadas ou ORM).
- Expõem métodos com nomes de negócio: `find_by_id`, `create`, `update_status`.
- Nunca importam objetos HTTP nem retornam status codes.

### Controllers
- Recebem dados já extraídos da requisição, aplicam **regras de negócio**, chamam models
  e retornam dados + resultado para a view.
- Concentram validações de negócio e composição de operações (ex.: criar pedido =
  validar estoque + calcular total + persistir).
- Sinalizam falhas lançando exceções/erros de domínio — nunca montam resposta HTTP.

### Views / Routes
- Declaram endpoints e fazem apenas: extrair/validar formato da entrada, chamar o
  controller, serializar a saída.
- Handlers curtos (idealmente ≤ 15 linhas). Qualquer if/else de negócio pertence ao controller.

### Middlewares
- Error handler **centralizado**: converte exceções/erros de domínio em respostas HTTP
  consistentes (corpo de erro padronizado + status correto). Nenhum handler engole
  exceção por conta própria.
- Outros aspectos transversais (CORS, logging de requisição) também vivem aqui.

## Regras de dependência (direção única)

```
views/routes → controllers → models → database
       ↘ middlewares (transversal)
config ← importado por qualquer camada
```

- Camada só importa a camada imediatamente abaixo. **Nunca** o inverso (model não importa
  controller; controller não importa view).
- Proibido import circular. Se surgir, há responsabilidade na camada errada.
- Conexão de banco criada/gerida em um único módulo de infra e usada pelos models —
  nunca aberta dentro de handler ou controller.

## Como aplicar na stack detectada

Para materializar as camadas em **qualquer** linguagem/framework, responda a estas
perguntas consultando o conhecimento que você tem do framework detectado na Fase 1:

1. **Modularização de rotas:** qual é o mecanismo nativo para agrupar rotas por domínio?
   (Blueprints no Flask, `Router` no Express, `SimpleRouter` no DRF, grupos de rota no Gin/Echo,
   controllers anotados no Spring...) Use-o — não invente um mecanismo próprio.
2. **Error handling central:** qual é o hook nativo para interceptar erros globalmente?
   (`errorhandler` no Flask, middleware de 4 argumentos no Express, `@ControllerAdvice`
   no Spring, exception handlers no FastAPI...)
3. **Configuração:** qual é o mecanismo idiomático de config por ambiente?
   (`app.config` + env vars, `process.env`, `application.properties`, `.env` + biblioteca padrão da comunidade...)
4. **Composition root:** onde o framework espera que a aplicação seja montada?
   (application factory, `main`, arquivo de bootstrap...)
5. **Nomenclatura:** qual é a convenção de nomes de arquivos e identificadores da linguagem?

**Exemplos de materialização** (as duas stacks abaixo são apenas ilustrações do procedimento —
não são as únicas suportadas):

### Exemplo: Python / Flask
- Rotas em Blueprints por domínio (`views/produto_routes.py` → `produto_bp`), registrados
  no entry point via application factory (`create_app()`).
- Error handler com `@app.errorhandler` em `middlewares/error_handler.py`.
- Config via classe/módulo lendo `os.environ`.

### Exemplo: Node.js / Express
- Rotas em `express.Router()` por domínio, montadas no `app.js` com `app.use('/produtos', router)`.
- Error handler como middleware `(err, req, res, next)` registrado por último.
- Config via `process.env` centralizado em `config/`.

## Regras de preservação de comportamento

1. **Todos os endpoints do inventário da Fase 1 devem continuar existindo** com os mesmos
   métodos, paths e formato de resposta.
2. Não renomeie campos de payload nem altere status codes de sucesso existentes
   (corrigir status codes *errados* apontados na auditoria é permitido e desejável — registre a mudança).
3. Dados/seed existentes devem continuar acessíveis após a refatoração.
4. Refatore em passos pequenos e valide ao final: boot da aplicação + smoke test dos endpoints.

## Projetos parcialmente organizados

Se o projeto já tem camadas (ex.: `models/`, `routes/`, `services/`):

- **Preserve** a estrutura que já cumpre as responsabilidades acima; não mova arquivos por movimentação.
- Corrija os **vazamentos**: SQL em route → mover para model; regra de negócio em route →
  mover para controller/service; config hardcoded → mover para config.
- Uma camada `services/` existente pode assumir o papel de controller de negócio — nesse
  caso, mantenha o nome e garanta que as responsabilidades fiquem corretas, documentando
  o mapeamento no resumo final.
