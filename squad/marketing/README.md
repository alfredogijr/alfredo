# Squad Marketing

Time de agentes de IA para execução de marketing de conteúdo para clientes. Reutilizável em qualquer cliente da agência.

## Estrutura do Squad

```
squad/marketing/
├── agentes/
│   ├── 01-estrategista.md        # Planejamento e calendário editorial
│   ├── 02-criador-conteudo.md    # Pautas e legendas
│   ├── 03-editor-copy.md         # Revisão e tom de voz
│   └── 04-gestor-calendario.md   # Organização e publicação
└── fluxos/
    └── 01-fluxo-mensal.md        # Do calendário à publicação
```

## Time do Squad

| Agente | Papel | Quando usar |
|--------|-------|-------------|
| [Estrategista](agentes/01-estrategista.md) | Planejamento mensal e calendário editorial | Início do mês |
| [Criador de Conteúdo](agentes/02-criador-conteudo.md) | Pautas semanais e legendas | Toda semana |
| [Editor de Copy](agentes/03-editor-copy.md) | Revisão de tom, ajustes e versões white label | Após rascunhos prontos |
| [Gestor de Calendário](agentes/04-gestor-calendario.md) | Organização, agendamento e distribuição | Aprovação final |

## Fluxo Mensal

```
Início do mês        Toda semana          Aprovação           Publicação
[Estrategista]  →   [Criador]       →   [Editor]        →   [Gestor]
Calendário          Pautas + legendas    Revisão + WL        Agendamento
```

## Como ativar em um cliente novo

1. Abra um Projeto no Claude com as `instrucoes-projeto.md` do cliente
2. Rode o Estrategista para o calendário do mês
3. Toda semana: Criador gera pautas → você aprova → Criador escreve legendas
4. Editor revisa e gera versão white label se necessário
5. Gestor organiza para publicação

## Quando combinar com outros squads

- **+ criativo**: quando o cliente precisa de identidade visual junto com conteúdo
- **+ comercial**: quando o conteúdo faz parte de uma estratégia de prospecção
