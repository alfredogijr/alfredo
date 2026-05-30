# Fase 5 — Aplicação Específica: Agência Grão de Mostarda

> Tradução prática da arquitetura para a realidade atual da agência, seguindo a sequência de maior impacto financeiro.

---

## Diagnóstico da Situação Atual (Hipóteses)

| Área | Situação Provável | Gargalo |
|---|---|---|
| Inteligência de Mercado | Ad hoc, baseada em percepção | Sem sistematização |
| Diagnóstico | Feito em reunião, sem estrutura replicável | Depende do fundador |
| Comercial | Reativo, poucos follow-ups consistentes | Pipeline não gerenciado |
| Propostas | Geradas manualmente, demoram horas | Volume limitado |
| Entrega | Boa execução, mas gestão informal | Escala limitada |
| Conteúdo | Capacidade de produção existe, estratégia fragmentada | Sem ritmo consistente |
| Pós-venda | Informal, sem NPS, sem programa de expansão | LTV não capturado |

---

## Sequência de Implementação para a Grão de Mostarda

### 1º — Inteligência de Mercado (Semana 1)

**Por quê primeiro:** Tomar decisões sem inteligência de mercado é operar no escuro. Com 30 minutos de setup, você tem um briefing semanal que alimenta todas as outras decisões.

**O que fazer:**

```
Agente IM-01 — Radar de Tendências
─────────────────────────────────────
Prompt base: "Você é um analista de mercado especializado em:
  - Marketing digital e IA aplicada a negócios
  - Segmentos: educação, turismo esportivo, eventos, saúde, construção

Toda segunda-feira, pesquise:
1. 3 tendências mais relevantes desta semana para esses segmentos
2. O que os maiores players estão fazendo de diferente
3. 2 oportunidades que a Agência Grão de Mostarda pode explorar agora
4. 1 ameaça ou risco que deve ser monitorado

Formato: relatório executivo em 500 palavras, com bullet points."

Ferramentas: Perplexity + Google Trends + NewsAPI
Automatização: Claude Projects ou n8n com trigger semanal
```

---

### 2º — Diagnóstico de Clientes (Semana 1–2)

**Por quê segundo:** O diagnóstico é a peça que transforma uma reunião de vendas em uma conversa de valor. Sem ele, você compete por preço.

**O que fazer:**

**Template de Diagnóstico por Segmento:**

```
DIAGNÓSTICO GRÃO DE MOSTARDA — v1.0
────────────────────────────────────

BLOCO 1 — SITUAÇÃO ATUAL (15 min)
├── Qual é o principal desafio de marketing/vendas hoje?
├── O que você já tentou? O que funcionou e o que não funcionou?
├── Como você está gerando leads atualmente?
└── Qual é o ticket médio e o ciclo de venda?

BLOCO 2 — OBJETIVOS (10 min)
├── Qual é a meta de faturamento para os próximos 6 meses?
├── Quantos novos clientes você precisa por mês?
└── Qual é o maior risco se nada mudar?

BLOCO 3 — MATURIDADE DIGITAL (10 min)
├── Quais ferramentas digitais usam hoje?
├── Têm site? Anunciam? Têm CRM?
└── Já usaram IA em algum processo? Como foi?

BLOCO 4 — CONTEXTO DE DECISÃO (5 min)
├── Quem decide sobre esse investimento?
├── Qual é o budget disponível/esperado?
└── Qual é o prazo ideal para começar?
```

**Agente de Diagnóstico (DC-01):**

```
Prompt pós-reunião: "Com base nessas respostas [colar transcrição],
gere um relatório de diagnóstico com:
1. Resumo da situação atual (3 bullets)
2. Principais gargalos identificados (priorizado)
3. Nível de maturidade digital (1–5 com justificativa)
4. Oportunidades de intervenção imediata
5. Urgência de decisão (baixa/média/alta) com justificativa
6. Serviços da Grão de Mostarda mais adequados para esse caso"
```

---

### 3º — Sistema Comercial e Follow-up (Semana 2–3)

**Por quê terceiro:** A maior perda de receita em agências não é falta de leads — é falta de consistência no follow-up.

**Cadência de Follow-up Grão de Mostarda:**

```
DIA 0: Reunião de diagnóstico realizada
DIA 1: E-mail de agradecimento + resumo dos principais insights
DIA 3: Envio da proposta
DIA 5: Follow-up leve (WhatsApp): "Conseguiu ver? Alguma dúvida?"
DIA 8: Follow-up com valor adicional (artigo, case, insight relevante)
DIA 12: Follow-up direto: "Qual é o principal impeditivo?"
DIA 18: Última tentativa com oferta de alternativa (escopo menor, piloto)
DIA 30: Mover para nurturing (1 contato por mês)
```

**Monitor de Gatilhos (COM-04) — Configuração:**

```
Monitorar para cada prospect na lista:
- LinkedIn: nova contratação no C-Level → abordar em 24h
- LinkedIn: novo produto/serviço lançado → oportunidade de campanha
- Imprensa: empresa mencionada positivamente → parabenizar + abrir conversa
- Imprensa: empresa mencionada negativamente → oferecer ajuda (cuidado!)
- DOU: nova licitação no segmento → oportunidade de B2G

Ferramentas: Phantombuster + Google Alerts + LinkedIn Alerts
```

---

### 4º — Sistema de Propostas (Semana 3–4)

**Por quê quarto:** Com diagnóstico feito e follow-up sistematizado, a proposta precisa ser rápida e de alta qualidade.

**Template de Proposta Grão de Mostarda:**

```
ESTRUTURA DA PROPOSTA
─────────────────────
1. CAPA
   Logo, nome do cliente, data, versão

2. SOBRE A GRÃO DE MOSTARDA (2 parágrafos)
   Posicionamento + prova social rápida

3. O QUE ENTENDEMOS DA SUA SITUAÇÃO
   (Baseado no diagnóstico — mostra que ouvimos)
   - Situação atual: [diagnóstico]
   - Principal desafio: [gap identificado]
   - O que está custando não resolver isso: [urgência]

4. NOSSA PROPOSTA DE SOLUÇÃO
   - Abordagem recomendada (e por quê)
   - O que será feito (escopo detalhado)
   - O que NÃO está incluído (evita surpresas)

5. CRONOGRAMA
   - Fases e marcos

6. INVESTIMENTO
   - Opção Essencial: R$ X
   - Opção Completa: R$ Y (recomendada)
   - Opção Acelerada: R$ Z
   (3 opções sempre aumentam ticket médio)

7. GARANTIAS E COMPROMISSOS
   (O que vocês garantem — diferenciador)

8. PRÓXIMOS PASSOS
   - Botão de aprovação / link de contrato
   - Prazo de validade da proposta

9. CASOS DE SUCESSO RELEVANTES
   (1–2 casos do mesmo segmento)
```

**Agente Construtor de Proposta (PROP-01):**

```
Prompt: "Com base no diagnóstico [colar DC-01 output],
gere uma proposta comercial seguindo o template da Grão de Mostarda.
Dados do cliente: [nome, empresa, segmento, desafio principal]
Serviços a propor: [lista]
Faixa de preço: [PROP-02 output]
Tom: consultivo, sem jargão excessivo, com evidências de valor."
```

---

### 5º — Entrega e Operações (Semana 4–6)

**Configuração mínima para escalar sem caos:**

```
Por cliente ativo, criar no Notion/ClickUp:
├── Board de projeto com fases padronizadas
├── Pasta de entregas com nomenclatura padrão
├── Canal no Slack/Teams com o cliente
├── Agenda de check-ins quinzenais automatizada
└── Relatório mensal automático com KPIs do projeto
```

**Agente OP-03 — Secretário de Reuniões:**

```
Ferramentas: Fireflies.ai ou Otter.ai (gravação automática)
Prompt pós-reunião: "Transcrição da reunião com [cliente] em [data].
Gere:
1. Resumo executivo (3–5 bullets)
2. Decisões tomadas
3. Ações definidas (formato: [Responsável] fará [ação] até [data])
4. Dúvidas que ficaram em aberto
5. Próximos passos"
Destino: Notion (página do cliente) + e-mail para participantes
```

---

### 6º — Conteúdo para a Grão de Mostarda (Semana 6–8)

**Estratégia de conteúdo para a própria agência:**

```
PILARES DE CONTEÚDO DA GRÃO DE MOSTARDA
──────────────────────────────────────────
Pilar 1: CASES E RESULTADOS (40%)
  → Antes e depois de clientes
  → Resultados com dados
  → Bastidores de projetos

Pilar 2: EDUCAÇÃO EM IA (30%)
  → Como usar IA nos segmentos que atendemos
  → Ferramentas práticas para PMEs
  → Desmistificação e aplicações reais

Pilar 3: POSICIONAMENTO (20%)
  → Opinião sobre o mercado
  → Tendências com perspectiva própria
  → O que acreditamos sobre o futuro do marketing

Pilar 4: BASTIDORES DA AGÊNCIA (10%)
  → Como trabalhamos
  → Equipe e valores
  → Processo de construção de soluções
```

---

### 7º — Pós-venda (A partir do 2º mês)

**Sistema de NPS Grão de Mostarda:**

```
Timing:
├── 30 dias após início do projeto: NPS inicial (percepção do onboarding)
├── 90 dias: NPS de progresso (resultados intermediários)
├── Fim do projeto: NPS de entrega
└── 6 meses após: NPS de resultados reais

Pergunta principal:
"Em uma escala de 0 a 10, qual a probabilidade de você indicar a
Grão de Mostarda para um colega que precise desse tipo de serviço?"

Follow-up automático:
- Score 9–10: [PV-03] Solicitar indicação personalizada
- Score 7–8: [PV-02] Check-in e identificar oportunidade de expansão
- Score 0–6: [Fundador] Ligação em 24h
```

---

## Arquitetura de Ferramentas Recomendada

```
CAMADA DE IA
├── Claude (estratégia, proposta, conteúdo, análise)
├── GPT-4o (volume de conteúdo, variações)
└── Perplexity (pesquisa em tempo real)

CAMADA DE AUTOMAÇÃO
├── n8n (orquestração de workflows)
├── Make/Zapier (integrações simples)
└── Phantombuster (prospecção LinkedIn)

CAMADA DE CRM & PROJETOS
├── Pipedrive ou HubSpot (CRM)
├── Notion (base de conhecimento + projetos)
└── ClickUp (gestão de tarefas)

CAMADA DE COMUNICAÇÃO
├── WhatsApp Business API (follow-up)
├── Gmail + automação (e-mail sequences)
└── Slack (interno)

CAMADA DE ANALYTICS
├── Meta Business Suite (anúncios)
├── Google Analytics 4 (web)
└── Looker Studio (dashboards consolidados)

CAMADA DE CONTEÚDO
├── Canva (design)
├── Fireflies/Otter (transcrição)
└── Buffer/Meta Business (agendamento)
```

---

## Base44 — Oportunidades de Aplicação

**Aplicações que podem ser construídas no Base44 para a Grão de Mostarda:**

| App | Descrição | Prioridade |
|---|---|---|
| **Dashboard de Clientes** | Visão consolidada de health score, NPS, projetos e expansão | Nível 1 |
| **Gerador de Diagnóstico** | Formulário → análise IA → relatório PDF automático | Nível 1 |
| **Pipeline Inteligente** | CRM com scoring automático e alertas de risco | Nível 1 |
| **Portal do Cliente** | Cliente acessa relatórios, aprova entregas, faz check-in | Nível 2 |
| **Biblioteca de Cases** | Casos organizados por segmento para usar em propostas | Nível 2 |
| **Monitor de Concorrentes** | Interface para ver movimentos de concorrentes por segmento | Nível 3 |

---

## KPIs de Acompanhamento da Implementação

| KPI | Meta 30 dias | Meta 90 dias | Meta 180 dias |
|---|---|---|---|
| Leads qualificados/mês | +30% | +60% | +100% |
| Taxa de conversão de propostas | 20% → 30% | 30% → 40% | 40%+ |
| Tempo de geração de proposta | < 2h | < 1h | < 30min |
| NPS médio de clientes | Baseline | > 7.5 | > 8.5 |
| Receita de expansão | 0 | 10% da receita | 20% da receita |
| Horas do fundador em ops | Baseline | -30% | -50% |
| Conteúdos publicados/mês | Baseline | +50% | +100% |
