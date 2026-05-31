# Agência Grão de Mostarda — Sistema de IA

> Arquitetura completa de operação com agentes de IA:
> estratégia, clientes, prompts, produtos e operacional.

---

## Estrutura da Pasta

```
/
├── arquitetura/          → Planejamento estratégico (7 fases)
├── clientes/             → Um arquivo por cliente com memória do projeto
│   ├── _template/        → Modelos para novos clientes
│   ├── grao-mostarda/    → A própria agência
│   └── turista-fc/       → Cliente ativo
├── prompts/              → Prompts prontos por área de trabalho
│   ├── conteudo/         → ✅ Calendário, pautas, legendas
│   ├── comercial/        → 🔜 Follow-up, qualificação, gatilhos
│   ├── diagnostico/      → 🔜 Entrevista, auditoria, GAP analysis
│   └── proposta/         → 🔜 Construção, precificação, revisão
├── produtos/             → Descrição e pitch dos produtos da agência
└── operacional/          → Guias práticos e checklists do dia a dia
```

---

## Por onde começar

**Novo cliente:**
1. Copie `clientes/_template/briefing-novo-cliente.md`
2. Cole em qualquer chat e traga as respostas
3. Cole em `clientes/_template/instrucoes-projeto.md` e adapte
4. Crie um novo Projeto no claude.ai e cole o resultado

**Produção de conteúdo (cliente já configurado):**
1. Mês novo → `prompts/conteudo/01-prompt-calendario-mensal.md`
2. Toda semana → `prompts/conteudo/02-prompt-pautas-semanais.md`
3. Escrever → `prompts/conteudo/03-prompt-escrever-legendas.md`
4. Checklist → `operacional/checklist-semanal.md`

---

## Status atual

| Área | Status |
|---|---|
| Arquitetura estratégica (7 fases) | ✅ Completo |
| Workflow de conteúdo | ✅ Operacional |
| Clientes configurados | 🔄 Em andamento (Turista FC) |
| Workflow comercial | 🔜 Próxima fase |
| Workflow de diagnóstico | 🔜 Próxima fase |
| Workflow de proposta | 🔜 Próxima fase |
| Produtos documentados | 🔜 Próxima fase |

---

## Clientes Ativos

| Cliente | Projeto Claude | Workflow ativo |
|---|---|---|
| Grão de Mostarda | `Conteúdo — Grão de Mostarda` | Conteúdo |
| Turista FC | `Conteúdo — Turista FC` | Conteúdo |
