# Gitflow Operacional

## Objetivo
Padronizar um ciclo simples, seguro e repetível para desenvolvimento em equipe, sem overengineering.

## Branches Oficiais
- `main`: branch canônica do código.
- `develop`: integração contínua de entregas concluídas.
- `staging`: validação pré-produção.
- `production`: espelho do que está em produção.

## Branches Temporárias
Toda branch de trabalho segue `<tipo>/<task-id>`, em que `<task-id>` é o ID do ticket no tracker da equipe.

- `feat/<task-id>`: nova funcionalidade.
- `fix/<task-id>`: correção não urgente.
- `docs/<task-id>`, `refactor/<task-id>`, `test/<task-id>`, `chore/<task-id>`: demais tipos de trabalho (mesmo vocabulário dos Conventional Commits).
- `hotfix/<task-id>`: correção urgente de produção.
- `release/<task-id>`: estabilização para entrega.

## Fluxo Padrão de Entrega
1. Criar `<tipo>/<task-id>` a partir de `develop`.
2. Implementar com teste (ou plano de teste) antes do Pull Request.
3. Atualizar memory-bank v2.1 na própria branch (`progress.md` delivery log, `learnings.md`, `decision-log.md`; task em `completed_tasks/` após harvest).
4. Abrir Pull Request de `<tipo>/<task-id>` para `develop`; o merge acontece após revisão da equipe.
5. Promover `develop` para `staging`.
6. Validar checklist de release.
7. Promover `staging` para `production`.
8. Sincronizar `production` com `main`.

## Fluxo de Hotfix
1. Criar `hotfix/<task-id>` a partir de `production` (ou `main` se for o espelho de produção).
2. Corrigir + criar teste de regressão.
3. Merge em `production` e `main`.
4. Reaplicar em `develop` para evitar divergência.

## Regras de Segurança
- Sem commit direto em `main`/`production`/`staging`/`develop`.
- Sem merge local de branch de trabalho em `develop`: a integração é por Pull Request.
- Toda entrega precisa de evidência de teste.
- Toda entrega precisa atualizar memory-bank.
- Se não há critério de aceite claro, a tarefa não inicia.
- Toda task tem um responsável (`owner`) e um ID de tracker.

## Convenções de Nome
- Funcionalidade: `feat/PROJ-123`
- Correção: `fix/PROJ-456`
- Hotfix: `hotfix/PROJ-789`
- Release: `release/PROJ-800`

## Checklist de Promoção (staging -> production)
- Testes do escopo executados.
- Regressão mínima executada.
- Memory-bank atualizado.
- Aprendizado de ciclo registrado.
