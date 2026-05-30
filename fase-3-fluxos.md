# Fase 3 — Fluxos e Workflows

> Diagramas completos dos fluxos de operação. Começando pelo fluxo que gera dinheiro.

---

## Fluxo 1 — Fluxo Principal de Receita (Prioridade Máxima)

### Descrição Textual

```
[INTELIGÊNCIA DE MERCADO]
       ↓
Radar de Tendências + Monitor de Concorrentes + Caçador de Oportunidades
       ↓
[DIAGNÓSTICO]
       ↓
Lead entra → Qualificação → Entrevista de Diagnóstico → Auditoria Digital → GAP Analysis
       ↓
[COMERCIAL]
       ↓
Prospecção ativa + Monitor de Gatilhos → Qualificação → Follow-up → CRM atualizado
       ↓
[PROPOSTA]
       ↓
Precificação → Construção → Revisão → Envio → Follow-up de proposta
       ↓
[FECHAMENTO]
       ↓
Contrato assinado → Kickoff → Gestão de Projeto
       ↓
[ENTREGA]
       ↓
Execução → QA → Entrega → Relatório
       ↓
[PÓS-VENDA]
       ↓
NPS → Health Score → Expansão → Referral
```

---

### Diagrama Mermaid — Fluxo de Receita

```mermaid
flowchart TD
    A([🌐 Inteligência de Mercado]) --> B[IM-01 Radar de Tendências]
    A --> C[IM-02 Monitor Concorrentes]
    A --> D[IM-03 Caçador de Oportunidades]
    A --> E[IM-04 Analista Maturidade IA]

    D --> F([📋 Diagnóstico])
    E --> F

    G[Lead Entra] --> H[COM-02 Qualificador]
    H -->|Lead Qualificado| F
    H -->|Lead Frio| I[Nurturing Automático]

    F --> J[DC-01 Entrevistador]
    J --> K[DC-02 Auditor Digital]
    K --> L[DC-03 GAP Analysis]

    L --> M([💼 Proposta])
    M --> N[PROP-02 Precificador]
    N --> O[PROP-01 Construtor]
    O --> P[PROP-03 Revisor]
    P --> Q[Proposta Enviada]

    Q --> R[COM-03 Follow-up]
    R -->|Aceito| S([✅ Fechamento])
    R -->|Em negociação| R
    R -->|Perdido| T[Análise de Perda]

    S --> U[OP-01 Gestor Projeto]
    U --> V[Execução]
    V --> W[OP-04 QA]
    W --> X[Entrega ao Cliente]

    X --> Y([🤝 Pós-venda])
    Y --> Z[PV-01 Satisfação/NPS]
    Z -->|NPS alto| AA[PV-03 Referral]
    Z -->|Oportunidade| AB[PV-02 Expansão]
    AB --> M
    AA --> G

    B --> AC[FIN-03 Projeção]
    COM-05 --> AC
    AC --> AD[FIN-01 Saúde Financeira]

    style A fill:#4A90D9,color:#fff
    style F fill:#7B68EE,color:#fff
    style M fill:#32CD32,color:#fff
    style S fill:#228B22,color:#fff
    style Y fill:#FF8C00,color:#fff
```

---

## Fluxo 2 — Fluxo de Conteúdo

### Descrição Textual

```
Análise de Performance Anterior
       ↓
Estratégia Mensal
       ↓
Pesquisa de Pauta (x N pautas)
       ↓
Redação
       ↓
Revisão Editorial
       ↓
Aprovação
       ↓
Distribuição por Canal
       ↓
Monitoramento de Performance
       ↓
→ (retroalimenta Estratégia)
```

### Diagrama Mermaid — Fluxo de Conteúdo

```mermaid
flowchart LR
    A[CONT-05\nAnálise de Performance] --> B[CONT-01\nEstratégia Mensal]
    B --> C{Pautas\nPriorizadas}
    C --> D[CONT-02\nPesquisador]
    D --> E[CONT-03\nRedator]
    E --> F[CONT-04\nRevisor]
    F -->|Reprovado| E
    F -->|Aprovado| G[Aprovação Final]
    G --> H{Distribuição}
    H --> I[Instagram]
    H --> J[LinkedIn]
    H --> K[YouTube]
    H --> L[Newsletter]
    H --> M[Blog/SEO]
    I & J & K & L & M --> N[Monitoramento\n7 dias]
    N --> A

    style A fill:#FF6B6B,color:#fff
    style B fill:#4ECDC4,color:#fff
    style G fill:#45B7D1,color:#fff
```

---

## Fluxo 3 — Fluxo de Prospecção Inteligente

### Diagrama Mermaid

```mermaid
flowchart TD
    A[IM-03 Oportunidades\nde Mercado] --> B[COM-01 Prospector\nInteligente]
    C[COM-04 Monitor\nde Gatilhos] --> D{Lead Detectado}
    B --> D

    D --> E[COM-02 Qualificador\nde Leads]
    E -->|Score >= 70| F[DC-01 Agendamento\nde Diagnóstico]
    E -->|Score 40-69| G[Nurturing\nAutomático]
    E -->|Score < 40| H[Arquivo\n90 dias]

    G -->|Reaquecido| E
    H -->|Gatilho detectado| E

    F --> I[Diagnóstico\nCompleto]
    I --> J[PROP-01 Proposta]

    style A fill:#667eea,color:#fff
    style C fill:#667eea,color:#fff
    style F fill:#48bb78,color:#fff
    style J fill:#ed8936,color:#fff
```

---

## Fluxo 4 — Fluxo de Pós-venda e Expansão

### Diagrama Mermaid

```mermaid
flowchart TD
    A[Projeto Entregue] --> B[PV-01 Health Score\nInicial]
    B --> C{Score?}

    C -->|≥ 8 NPS| D[PV-03 Ativar\nPrograma Referral]
    C -->|6-7 NPS| E[Check-in\nPersonalizado]
    C -->|< 6 NPS| F[Protocolo de\nRecuperação]

    E --> G[Identificar Causa\nde Insatisfação]
    G --> H[Plano de Ação]
    H --> B

    F --> I[Escalada para\nFundador]

    D --> J[Indicações\nGeradas]
    J --> K[Novos Leads]

    B --> L[PV-02 Análise\nde Expansão]
    L --> M{Oportunidade\nIdentificada?}
    M -->|Sim| N[Proposta de\nExpansão]
    M -->|Não| O[Revisão em\n30 dias]

    N --> P[PROP-01\nNova Proposta]

    style A fill:#48bb78,color:#fff
    style F fill:#fc8181,color:#fff
    style D fill:#4299e1,color:#fff
    style P fill:#ed8936,color:#fff
```

---

## Fluxo 5 — Fluxo de Inteligência Contínua (Loop de Aprendizado)

```mermaid
flowchart LR
    A[Dados de\nMercado] --> B[IM-01 a IM-04]
    B --> C[Insights\nEstratégicos]
    C --> D[Decisões\nComerciais]
    D --> E[Ações\nExecutadas]
    E --> F[Resultados\nMedidos]
    F --> G{Atingiu\nMeta?}
    G -->|Sim| H[Escalar\no que funciona]
    G -->|Não| I[Diagnotiscar\nCausa]
    I --> J[Ajustar\nEstratégia]
    J --> D
    H --> K[Documentar\nno Playbook]
    K --> L[Compartilhar\ncom Clientes]

    style B fill:#667eea,color:#fff
    style G fill:#ed8936,color:#fff
    style K fill:#48bb78,color:#fff
```

---

## Fluxo 6 — Fluxo Operacional Diário (Rotina de Agentes)

```
MANHÃ (7h–9h)
├── IM-01: Entrega briefing de tendências da semana
├── COM-04: Alerta de gatilhos de compra detectados
├── COM-03: Lista de follow-ups do dia
└── OP-01: Status dos projetos em andamento

DURANTE O DIA
├── COM-02: Qualifica novos leads entrantes
├── OP-03: Transcreve e resume reuniões realizadas
└── TRF-01: Monitora alertas de campanhas (CPL > limite, ROAS < mínimo)

FINAL DO DIA (17h–18h)
├── COM-05: Atualiza pipeline e destaca deals em risco
└── OP-04: Lista entregas que precisam de QA amanhã

SEMANAL (segunda-feira)
├── IM-01: Briefing semanal de mercado
├── TRF-01: Relatório de performance de mídia
└── FIN-01: Dashboard financeiro da semana

MENSAL (dia 1)
├── CONT-01: Estratégia de conteúdo do mês
├── PV-02: Oportunidades de expansão na base
├── FIN-02: Rentabilidade por cliente
└── FIN-03: Projeção de receita para os próximos 3 meses
```

---

## Mapa de Dependências entre Agentes

```mermaid
graph TD
    IM01[IM-01 Radar] --> IM02[IM-02 Concorrentes]
    IM01 --> IM03[IM-03 Oportunidades]
    IM01 --> IM04[IM-04 Maturidade IA]
    IM01 --> CONT01[CONT-01 Estratégia]

    IM03 --> COM01[COM-01 Prospector]
    COM01 --> COM02[COM-02 Qualificador]
    COM04[COM-04 Gatilhos] --> COM02

    COM02 --> DC01[DC-01 Entrevistador]
    DC01 --> DC02[DC-02 Auditor]
    DC02 --> DC03[DC-03 GAP]
    IM02 --> DC03

    DC01 --> PROP01[PROP-01 Proposta]
    DC02 --> PROP01
    DC03 --> PROP01
    PROP02[PROP-02 Precificador] --> PROP01
    PROP01 --> PROP03[PROP-03 Revisor]

    PROP01 --> COM03[COM-03 Follow-up]
    COM03 --> COM05[COM-05 CRM]
    COM05 --> FIN03[FIN-03 Projeção]

    PROP01 --> OP01[OP-01 Projetos]
    OP01 --> OP02[OP-02 Documentação]
    OP01 --> OP03[OP-03 Reuniões]
    OP01 --> OP04[OP-04 QA]

    OP01 --> PV01[PV-01 Satisfação]
    PV01 --> PV02[PV-02 Expansão]
    PV01 --> PV03[PV-03 Referral]
    PV02 --> PROP01

    CONT05[CONT-05 Performance] --> CONT01
    CONT01 --> CONT02[CONT-02 Pesquisa]
    CONT02 --> CONT03[CONT-03 Redação]
    CONT03 --> CONT04[CONT-04 Revisão]

    TRF01[TRF-01 Análise] --> TRF02[TRF-02 Otimização]
    TRF01 --> TRF03[TRF-03 Criativos]

    FIN01[FIN-01 Saúde] --> FIN02[FIN-02 Rentabilidade]
    COM05 --> FIN01
    OP01 --> FIN01
    FIN01 --> FIN03
    PV01 --> FIN03

    PROD01[PROD-01 Ideias] --> PROD02[PROD-02 Validação]
    PROD02 --> PROD03[PROD-03 Roadmap]
    IM01 --> PROD01
    PV01 --> PROD01
    DC01 --> PROD01

    style IM01 fill:#667eea,color:#fff
    style COM02 fill:#ed8936,color:#fff
    style PROP01 fill:#48bb78,color:#fff
    style PV01 fill:#fc8181,color:#fff
```
