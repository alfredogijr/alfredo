# Squad Dev

Time de agentes de IA especializados para desenvolvimento de aplicativos e produtos de tecnologia, baseado na metodologia Lean Startup.

## Estrutura do Squad

```
squad/tech/
├── agentes/          # Definição e prompts de cada agente
├── prompts/          # Prompts prontos para tarefas comuns
└── fluxos/           # Fluxos de trabalho entre agentes
```

## Time Principal (Core Squad)

| Agente | Papel | Foco Principal |
|--------|-------|----------------|
| [Product Manager](agentes/01-product-manager.md) | Estratégia e Produto | Visão, roadmap, priorização, métricas |
| [Tech Lead](agentes/02-tech-lead.md) | Arquitetura e Liderança Técnica | Arquitetura, decisões técnicas, code review |
| [Full-Stack Developer](agentes/03-fullstack-developer.md) | Desenvolvimento Web e API | Frontend, backend, integrações |
| [Mobile Developer](agentes/04-mobile-developer.md) | Desenvolvimento Mobile | iOS, Android, React Native, Flutter |
| [UX/UI Designer](agentes/05-ux-ui-designer.md) | Experiência e Interface | Pesquisa, wireframes, design system |
| [QA Engineer](agentes/06-qa-engineer.md) | Qualidade e Testes | Estratégia de testes, automação, bugs |

## Especialistas (Sob Demanda)

| Agente | Papel | Foco Principal |
|--------|-------|----------------|
| [DBA / Data Architect](agentes/07-dba-data-architect.md) | Dados e Banco de Dados | Modelagem, performance, integridade |
| [DevOps / Cloud Engineer](agentes/08-devops-cloud.md) | Infraestrutura e Deploy | CI/CD, cloud, monitoramento |

## Como Usar

### 1. Ativando um Agente

Cada arquivo em `agentes/` contém um **System Prompt** pronto para uso. Para ativar um agente:

- No **Claude.ai**: Cole o System Prompt no campo de instruções do sistema
- No **Claude Code**: Use `CLAUDE.md` com as instruções do papel
- Via **API**: Passe o system prompt no campo `system`

### 2. Fluxo Lean Startup

```
Descoberta → Validação → Desenvolvimento → Lançamento → Aprendizado
    PM     →   UX/UI   →   Dev + Mobile  →  DevOps    →    QA + PM
```

### 3. Tarefas Comuns por Agente

| Tarefa | Agente Principal | Agente de Suporte |
|--------|-----------------|-------------------|
| Definir MVP | Product Manager | UX/UI Designer |
| Criar arquitetura | Tech Lead | DBA / DevOps |
| Desenvolver feature | Full-Stack / Mobile | Tech Lead |
| Criar protótipo | UX/UI Designer | Product Manager |
| Escrever testes | QA Engineer | Desenvolvedor |
| Configurar deploy | DevOps | Tech Lead |
| Otimizar queries | DBA | Tech Lead |

## Princípios do Squad

1. **Build-Measure-Learn** — cada ciclo gera aprendizado validado
2. **MVP primeiro** — sempre a menor solução que valida a hipótese
3. **Dados acima de opiniões** — decisões baseadas em métricas
4. **Comunicação assíncrona** — contexto sempre documentado
5. **Qualidade não é negociável** — bugs em produção custam mais caro
