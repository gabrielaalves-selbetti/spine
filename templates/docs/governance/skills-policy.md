# Skills Policy

Tag policy for tasks, progress, and learnings: `docs/governance/memory-tags-policy.md`.

## Objetivo
Manter somente skills com valor recorrente no workflow da equipe.

## Skills instaladas

`python spine.py install` copia todas as skills do Spine para `.spine/skills/`. O agente lê `.spine/skills/<nome>/SKILL.md` quando um comando ou esta política indica a skill.

### Core (sempre em uso)
- `writing-plans`
- `executing-plans`
- `test-driven-development`
- `systematic-debugging`
- `verification-before-completion`

### Workflow e Qualidade
- `gitflow`
- `testing-guidelines`
- `handoff-protocol`
- `grill-me` (descoberta condicional — ver Diretriz Operacional: Planejamento)

## Skills adicionais do projeto
- Skills próprias do projeto ficam fora de `.spine/` (essa pasta é gerenciada pelo `spine.py`) e devem ser listadas aqui, com o caminho do `SKILL.md`, para serem usadas como `execution_skill`.
- Critérios de entrada: uso recorrente no trabalho real, redução mensurável de retrabalho, risco ou tempo, e alinhamento com a stack principal do projeto.
- Critérios de remoção: sem uso recorrente nos últimos 30 dias, sobreposição com skill já ativa, ou indução de overengineering em tarefas simples.

## Diretriz Operacional: Planejamento

Use esta regra para evitar ambiguidade entre descoberta e estruturação de planos:

- **Pipeline fixo:** `grill-me` (descoberta, condicional) → `writing-plans` (preenche `_task-template.md`, obrigatório) → gate `/spine-plan`.
- **Contrato de tarefa:** frontmatter YAML + seções fixas; detalhe Task/Step opcional em `## Implementation Plan` (omitir se ≤3 critérios de aceite).
- **Default simples:** escopo claro e single-domain → pular `grill-me`, ir direto para `writing-plans`.
- **Escalar descoberta:** usar `grill-me` quando escopo for ambíguo, multi-domínio, ou houver decisões arquiteturais/segurança/schema/infra em aberto.

### Quando usar `grill-me`
- Escopo ambíguo ou amplo (ex.: "melhorar performance").
- Múltiplos domínios na mesma entrega (ex.: backend + infra + UI).
- Decisões arquiteturais ou de segurança ainda não resolvidas.
- Opt-in explícito em `/spine-plan`: `grill me`, `grill:`, `grill -`, `grill with docs`, `grill:docs`, `stress-test`, `challenge this`.
- Opt-in com documentação de domínio: `grill with docs` ou `grill:docs` — mesma skill, com expectativa de atualização inline de `domain-glossary.md` e `decision-log.md`.

### Quando pular `grill-me`
- Escopo claro, entregável único, single-domain.
- Opt-out explícito: `skip discovery`, `no grill`, `direct plan`.

### Regra de desempate (anti-overengineering)
- Se o escopo já define MVP, out-of-scope e domínio principal, não use `grill-me`.
- `grill-me` faz uma pergunta por vez; não escreva o plano completo até a descoberta terminar.
- Registre decisões em `## Discovery notes` no arquivo de tarefa ativa antes de `writing-plans`.
- **Promoção de conhecimento:** decisões de escopo da tarefa → `## Discovery notes`; termos canônicos de domínio → `domain-glossary.md`; decisões arquiteturais (critério triplo: difícil reverter, surpreendente sem contexto, trade-off real) → `decision-log.md`.

### Relação com outras skills de workflow
- **`writing-plans`:** sempre após descoberta (ou após skip). Preenche `_task-template.md` (frontmatter + seções); Task/Step só em `## Implementation Plan`.
- **`executing-plans`:** lê frontmatter e Implementation Plan; para em `REVIEW` — `/spine-harvest` fecha a entrega.
- **`handoff-protocol`:** aplica-se quando a task troca de responsável ou de agente; não substitui descoberta de escopo.

## Sincronização em Projetos Consumidor

Este arquivo é semeado em `docs/governance/skills-policy.md` pelo `python spine.py install` e nunca é sobrescrito depois. Ao atualizar o Spine, revisar manualmente as diferenças em relação a `templates/docs/governance/skills-policy.md` no clone do Spine e incorporar o que for relevante.
