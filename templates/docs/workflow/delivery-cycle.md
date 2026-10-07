# Ciclo de Entrega (Enxuto)

## Objetivo
Executar tarefas com previsibilidade e qualidade, mantendo documentação mínima e útil.

## Ciclo Padrão
1. **Intake da tarefa**
   - Partir de um ticket no tracker da equipe (o ID do ticket identifica a task).
   - Definir objetivo, escopo, responsável e critério de aceite.
2. **Plano rápido**
   - Definir abordagem em poucas linhas.
   - Definir plano de testes (positivo, negativo, regressão).
3. **Execução em `<tipo>/<task-id>`**
   - Implementar o mínimo necessário para entregar valor.
4. **Validação**
   - Executar testes definidos.
   - Validar impacto em áreas relacionadas.
5. **Registro (harvest v2.1)**
   - Acrescentar a entrada no delivery log de `docs/memory/ledger/progress.md` (com **Tags**); atualizar Current state quando houver bloqueio ou próximo passo do time.
   - Registrar recorrências em `docs/memory/ledger/learnings.md` quando houver incidente ou retrabalho.
   - Registrar decisões em `docs/memory/global/decision-log.md`.
   - Mover task concluída: `git mv active_tasks/ → completed_tasks/` (frontmatter `status: DONE`).
6. **Pull Request**
   - Push da branch e Pull Request para `develop`, com revisão da equipe.
7. **Promoção**
   - `develop` -> `staging` -> `production` -> `main`.

## Definição de Pronto
- Critério de aceite atendido.
- Testes previstos executados.
- Memory-bank atualizado.
- Pull Request aberto para a branch base.
- Sem pendência crítica não documentada.

## Guard Rail Anti-Overengineering
- Não criar abstração nova sem 2 casos reais.
- Não adicionar ferramenta nova sem substituir algo ou reduzir custo/tempo.
- Priorizar solução simples antes de solução “genérica”.
