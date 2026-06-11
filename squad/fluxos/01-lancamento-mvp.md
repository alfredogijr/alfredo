# Fluxo: Lançamento de MVP

Sequência de handoffs entre agentes para lançar um produto do zero ao mercado.

## Visão Geral

```
Semana 1-2        Semana 2-3       Semana 3-6        Semana 6-7       Semana 7-8
[PM]          →   [UX/UI]      →   [Dev + Mobile] →  [QA]         →   [DevOps]
Descoberta        Prototipação      Desenvolvimento    Validação        Deploy
```

---

## Fase 1: Descoberta (PM)

**Agente**: Product Manager  
**Entrega**: PRD do MVP + Métricas de sucesso

**Prompt**:
```
[PM Mode] Preciso lançar um MVP para [ideia do produto].
Problema que resolve: [descrição]. Público-alvo: [perfil].
Me ajude a: 
1) Validar se o problema é real e vale resolver
2) Definir as 3-5 funcionalidades essenciais do MVP
3) Estabelecer as métricas que vão dizer se o MVP foi um sucesso
4) Estruturar o PRD básico
```

---

## Fase 2: Arquitetura (Tech Lead)

**Agente**: Tech Lead  
**Entrada**: PRD do PM  
**Entrega**: Arquitetura técnica + stack escolhida

**Prompt**:
```
[Tech Lead Mode] Com base neste PRD: [colar PRD]
Defina:
1) Arquitetura do sistema (diagrama Mermaid)
2) Stack tecnológica recomendada (justificada para startup)
3) Decisões técnicas principais (ADRs)
4) Estimativa de esforço por componente
5) Riscos técnicos e mitigações
```

---

## Fase 3: Prototipação (UX/UI Designer)

**Agente**: UX/UI Designer  
**Entrada**: PRD + Arquitetura  
**Entrega**: Fluxos de UX + Especificações de design

**Prompt**:
```
[UX Mode] Com base no PRD [colar PRD], crie:
1) Fluxo de navegação principal do app/produto
2) Lista de telas necessárias com descrição de cada uma
3) Especificação do Design System inicial (cores, tipografia, componentes base)
4) Estados críticos de cada tela (loading, erro, vazio, sucesso)
5) Pontos de fricção a evitar na experiência
```

---

## Fase 4: Desenvolvimento (Full-Stack + Mobile)

**Agentes**: Full-Stack Developer + Mobile Developer (paralelo)  
**Entrada**: Arquitetura + Design  
**Entrega**: Produto funcionando

**Prompt Full-Stack**:
```
[Full-Stack Mode] Implemente o backend/API para o MVP descrito:
[colar arquitetura e PRD]
Priorize: [features do MVP em ordem]
Para cada feature: crie endpoint, validações e testes básicos.
```

**Prompt Mobile**:
```
[Mobile Mode] Implemente as telas do app para o MVP:
[colar fluxos de UX e design system]
Stack: [React Native / Flutter]
Priorize: [telas em ordem de fluxo principal]
```

---

## Fase 5: Testes (QA Engineer)

**Agente**: QA Engineer  
**Entrada**: MVP desenvolvido + critérios de aceite  
**Entrega**: Relatório go/no-go para lançamento

**Prompt**:
```
[QA Mode] O MVP está pronto para teste. Crie e execute:
1) Casos de teste para o fluxo principal do usuário
2) Testes de edge cases críticos
3) Relatório de bugs encontrados (priorizado)
4) Avaliação go/no-go para lançamento
Critérios de aceite: [colar do PRD]
```

---

## Fase 6: Deploy (DevOps)

**Agente**: DevOps / Cloud Engineer  
**Entrada**: Código aprovado pelo QA  
**Entrega**: Produto em produção + monitoramento

**Prompt**:
```
[DevOps Mode] Configure o ambiente de produção para o MVP:
Stack: [tecnologias]. Cloud: [provider]. 
Inclua: infraestrutura, CI/CD, monitoramento básico e processo de deploy das apps mobile nas lojas.
SLA esperado: [requisito de disponibilidade]
```

---

## Critérios de Saída de Cada Fase

| Fase | Critério de Saída |
|------|-------------------|
| Descoberta | PRD aprovado com métricas definidas |
| Arquitetura | ADRs documentados, stack definida |
| Prototipação | Protótipo validado com 3+ usuários reais |
| Desenvolvimento | Features implementadas com testes |
| QA | Zero bugs críticos / altos abertos |
| Deploy | Produto em ar, monitoramento ativo |
