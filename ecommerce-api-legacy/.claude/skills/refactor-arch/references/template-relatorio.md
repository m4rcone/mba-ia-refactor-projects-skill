# Template do Relatório de Auditoria (Fase 2)

Use exatamente esta estrutura. Substitua os `<placeholders>`.
Findings ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW) e,
dentro da mesma severidade, por arquivo.

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<M> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERIDADE>] <Nome do anti-pattern (ID do catálogo)>
File: <arquivo>:<linha ou intervalo, ex.: models.py:1-350>
Description: <o que foi encontrado, concreto e específico — cite o trecho quando ajudar>
Impact: <consequência prática do problema>
Recommendation: <como corrigir, apontando o padrão do playbook quando aplicável>

<... repetir o bloco acima para cada finding ...>

## Deprecated APIs
<uma entrada por API deprecated encontrada, no mesmo formato de finding;
se nenhuma for encontrada, escrever: "Nenhuma API deprecated detectada.">

================================
Total: <N> findings
================================
```

## Regras de preenchimento

1. **Arquivo e linha exatos:** confira no código antes de escrever. Um finding sem localização verificável é inválido.
2. **Um finding por ocorrência relevante.** Ocorrências do mesmo anti-pattern em pontos distintos podem ser agrupadas em um finding único **somente** se listadas todas as localizações (`File:` com múltiplas entradas).
3. **Description ≠ Impact:** description diz *o que está no código*; impact diz *o que acontece por causa disso*.
4. **Recommendation acionável:** deve permitir que a Fase 3 saiba o que fazer (referencie o padrão do playbook, ex.: "aplicar PB-02").
5. O relatório impresso no terminal e o salvo em arquivo devem ser **idênticos** — gere uma vez, use nos dois destinos.
6. Após imprimir e salvar o relatório, exiba a pergunta de confirmação obrigatória:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
