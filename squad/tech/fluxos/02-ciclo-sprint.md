# Fluxo: Ciclo de Sprint (2 semanas)

Sequência de ativações por agente ao longo de uma sprint de desenvolvimento.

## Calendário do Sprint

```
Seg        Ter-Qui     Sex        ──── Semana 2 ────    Sex (último)
Planning   Dev + QA   Review     Dev + QA + Review    Retro + Deploy
[PM+TL]   [Dev+QA]   [UX+PM]    [Dev+QA]             [Todos]
```

---

## Segunda-feira: Sprint Planning

### 1. PM define as histórias priorizadas
```
[PM Mode] Sprint [número]. Objetivo do sprint: [meta].
Selecione do backlog as histórias que cabem em 2 semanas considerando:
- Capacidade do time: [número] devs
- Dependências técnicas: [listar]
- Prioridade de negócio: [contexto]
Monte o sprint backlog com estimativas em pontos.
```

### 2. Tech Lead valida viabilidade técnica
```
[Tech Lead Mode] Revise o sprint backlog proposto: [colar backlog]
Para cada história: confirme estimativa, identifique dependências técnicas ocultas e riscos.
Sugira ajustes se necessário.
```

---

## Durante o Sprint: Desenvolvimento

### Desenvolvedor inicia uma história
```
[Full-Stack Mode / Mobile Mode] Vou implementar: [nome da User Story]
Critérios de aceite: [colar]
Arquitetura atual: [contexto relevante]
Qual a melhor abordagem? Me ajude a quebrar em subtarefas técnicas.
```

### QA cria casos de teste em paralelo
```
[QA Mode] Crie casos de teste para a User Story: [colar história]
Antes do desenvolvimento terminar, quero os casos prontos para testar assim que o código estiver pronto.
Formato: Gherkin. Inclua: happy path, edge cases e cenários de erro.
```

---

## Code Review (Tech Lead)

```
[Tech Lead Mode] Revise este Pull Request:
[colar diff ou link]
Foco em: corretude, segurança, performance e aderência aos padrões do projeto.
Classifique comentários: blocker / importante / sugestão.
```

---

## Final do Sprint: Review e Retro

### PM prepara demonstração
```
[PM Mode] O sprint [número] entregou: [lista de histórias concluídas]
Prepare:
1) Roteiro de demonstração das features
2) Comparação com métricas de sucesso definidas
3) O que aprendemos e como isso afeta o próximo sprint?
```

### QA valida sprint completo
```
[QA Mode] Sprint review: execute os testes de regressão das features entregadas.
Lista de histórias: [colar]
Ambiente: [staging/produção]
Relatório go/no-go para deploy.
```

---

## Deploy pós-Sprint

```
[DevOps Mode] Deploy da sprint [número] para produção.
Features incluídas: [lista]
Estratégia: [blue-green / canary / rolling]
Checklist pré-deploy: confirme que CI está verde, migrações de banco estão prontas e rollback está testado.
```
