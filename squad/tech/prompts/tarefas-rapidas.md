# Prompts de Tarefas Rápidas

Referência rápida de prompts por tipo de tarefa. Copie, adapte e ative o agente correspondente.

---

## Produto e Estratégia

### Validar uma ideia de produto
**Agente**: Product Manager
```
[PM Mode] Tenho a seguinte ideia: [descrição em 2-3 frases]
Ajude-me a validar: É um problema real? Quem paga para resolver? Qual o tamanho do mercado?
Que perguntas eu deveria fazer a potenciais usuários para confirmar ou refutar esta hipótese?
```

### Priorizar features no backlog
**Agente**: Product Manager
```
[PM Mode] Preciso priorizar estas features: [lista]
Contexto do produto: [estágio: pré-lançamento / growth / consolidação]
Métrica principal: [retenção / conversão / receita]
Use RICE ou ICE score para ranquear e justifique cada decisão.
```

### Escrever OKRs do trimestre
**Agente**: Product Manager
```
[PM Mode] Crie os OKRs para o produto [nome] no Q[número].
Situação atual: [métricas atuais]. Meta de negócio: [objetivo].
Crie: 1 Objective + 3 Key Results mensuráveis e ambiciosos mas alcançáveis.
```

---

## Arquitetura e Código

### Escolher tecnologia
**Agente**: Tech Lead
```
[Tech Lead Mode] Preciso escolher entre [opção A] vs [opção B] para [caso de uso].
Contexto: [tamanho do time, escala esperada, prazo].
Faça uma análise comparativa de trade-offs e me dê uma recomendação fundamentada.
```

### Refatorar um módulo
**Agente**: Tech Lead / Full-Stack
```
[Tech Lead Mode] Este módulo precisa de refatoração: [código ou descrição]
Problemas identificados: [lista de problemas]
Propose uma refatoração que melhore [manutenibilidade / performance / testabilidade] sem alterar o comportamento externo.
```

### Implementar autenticação
**Agente**: Full-Stack Developer
```
[Full-Stack Mode] Implemente autenticação [JWT / OAuth2 / Magic Link] para o sistema.
Stack: [frontend + backend]. Requisitos: [login social / 2FA / etc].
Inclua: registro, login, refresh token, logout e proteção de rotas.
```

---

## Mobile

### Animar uma transição de tela
**Agente**: Mobile Developer
```
[Mobile Mode] Crie uma animação de transição entre [Tela A] e [Tela B].
Framework: [React Native / Flutter]. Tipo de animação desejada: [descrever].
Siga as guidelines de [iOS / Android / ambos] para animações nativas.
```

### Implementar notificações push
**Agente**: Mobile Developer
```
[Mobile Mode] Configure notificações push para o app [nome].
Plataformas: [iOS / Android / ambos]. Serviço: [Firebase / AWS SNS].
Inclua: permissão do usuário, recebimento em foreground/background e deep link ao clicar.
```

---

## Design

### Criar onboarding de app
**Agente**: UX/UI Designer
```
[UX Mode] Crie o fluxo de onboarding para [nome do app].
Proposta de valor principal: [1 frase]. Tipo de app: [categoria].
Projete: telas de apresentação (máx 3), cadastro simplificado e primeira ação de valor.
Evite: muitas telas, campos desnecessários e pedidos de permissão prematuros.
```

### Revisar usabilidade de uma tela
**Agente**: UX/UI Designer
```
[UX Mode] Revise a usabilidade desta tela: [descrição ou imagem]
Contexto: [para qual ação o usuário chega nessa tela? qual é o objetivo?]
Use as 10 heurísticas de Nielsen. Liste problemas por severidade com sugestões de melhoria.
```

---

## Qualidade e Testes

### Criar estratégia de testes para o projeto
**Agente**: QA Engineer
```
[QA Mode] Crie a estratégia de testes para o projeto [nome].
Stack: [tecnologias]. Plataformas: [web / iOS / Android].
Defina: pirâmide de testes (unitário / integração / E2E), ferramentas recomendadas, cobertura mínima e critérios de qualidade para release.
```

### Diagnosticar flakiness em testes
**Agente**: QA Engineer
```
[QA Mode] Tenho testes que falham de forma intermitente: [descrição dos testes]
Tecnologia: [Jest / Cypress / Detox / etc]. Frequência de falha: [estimativa].
Diagnostique as causas prováveis de flakiness e proponha correções.
```

---

## Dados

### Modelar entidades de um novo módulo
**Agente**: DBA / Data Architect
```
[DBA Mode] Modele as entidades para o módulo [nome].
Descrição funcional: [o que o módulo faz].
Banco de dados: [PostgreSQL / MongoDB / etc].
Entregue: schema SQL ou definição de coleções, com índices e justificativa das escolhas.
```

### Diagnosticar lentidão no banco
**Agente**: DBA / Data Architect
```
[DBA Mode] O banco está lento. Logs mostram: [slow queries ou descrição do problema].
Banco: [tipo e versão]. Volume de dados: [estimativa].
Ajude-me a diagnosticar as causas e priorizar as otimizações de maior impacto.
```

---

## Infraestrutura

### Estimar custo de infraestrutura
**Agente**: DevOps / Cloud Engineer
```
[DevOps Mode] Estime o custo mensal de infraestrutura para [produto].
Requisitos: [usuários ativos, transações/dia, armazenamento].
Cloud: [AWS / GCP / Azure]. Ambiente: [staging + produção].
Monte uma planilha de custos com as principais decisões de otimização.
```

### Configurar alertas de monitoramento
**Agente**: DevOps / Cloud Engineer
```
[DevOps Mode] Configure alertas de monitoramento para [produto].
Stack: [tecnologias]. Ferramenta: [Datadog / CloudWatch / Grafana].
Defina: alertas de disponibilidade, latência, taxa de erro e uso de recursos.
Inclua runbook de resposta para cada alerta crítico.
```
