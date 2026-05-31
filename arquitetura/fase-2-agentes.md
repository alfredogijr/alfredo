# Fase 2 — Estrutura Completa de Agentes

> 36 agentes organizados por área, cada um com: Nome, Objetivo, Entradas, Saídas, Ferramentas, Frequência, Dependências e Indicadores.

---

## ÁREA 1 — INTELIGÊNCIA DE MERCADO

### Agente IM-01 · Radar de Tendências

| Campo | Detalhe |
|---|---|
| **Objetivo** | Monitorar tendências de mercado nos segmentos atendidos pela agência e por cada cliente. |
| **Entradas** | Segmentos-alvo, palavras-chave por nicho, fontes de notícias, LinkedIn, Google Trends, relatórios setoriais. |
| **Saídas** | Briefing semanal de tendências com: resumo executivo, implicações estratégicas, oportunidades identificadas. |
| **Ferramentas** | Web search, Google Trends API, RSS readers, LinkedIn scraping, Perplexity. |
| **Frequência** | Toda segunda-feira às 7h. |
| **Dependências** | Nenhuma. É agente raiz. |
| **Indicadores** | % de briefings entregues no prazo; qualidade avaliada pelo usuário (1–5); insights transformados em ação. |

---

### Agente IM-02 · Monitor de Concorrentes

| Campo | Detalhe |
|---|---|
| **Objetivo** | Rastrear movimentos de concorrentes diretos da agência e dos clientes: novos serviços, preços, conteúdo, contratações. |
| **Entradas** | Lista de concorrentes por cliente, sites, perfis sociais, LinkedIn das empresas. |
| **Saídas** | Relatório quinzenal de inteligência competitiva: o que mudou, o que significa, como reagir. |
| **Ferramentas** | Web scraping, LinkedIn, Similarweb, SEMrush, alertas Google. |
| **Frequência** | Monitoramento diário, relatório quinzenal. |
| **Dependências** | IM-01 (contexto de mercado). |
| **Indicadores** | Nº de movimentos capturados; tempo médio de detecção de mudança; ações geradas. |

---

### Agente IM-03 · Caçador de Oportunidades

| Campo | Detalhe |
|---|---|
| **Objetivo** | Identificar oportunidades de novos projetos, editais, parcerias, eventos relevantes e momentos de entrada no mercado. |
| **Entradas** | Segmentos atendidos, perfil de cliente ideal (ICP), base de prospects, agenda de eventos do setor. |
| **Saídas** | Lista semanal de oportunidades rankeadas por potencial de receita e facilidade de acesso. |
| **Ferramentas** | Web search, LinkedIn, plataformas de editais, agenda de eventos. |
| **Frequência** | Semanal. |
| **Dependências** | IM-01, IM-02. |
| **Indicadores** | Nº de oportunidades identificadas; % convertidas em pipeline; valor potencial gerado. |

---

### Agente IM-04 · Analista de Maturidade em IA

| Campo | Detalhe |
|---|---|
| **Objetivo** | Avaliar o nível de adoção de IA nos segmentos atendidos para identificar onde está o maior gap (e portanto maior oportunidade). |
| **Entradas** | Relatórios de adoção de IA, pesquisas setoriais, entrevistas com prospects, dados de mercado. |
| **Saídas** | Mapa de maturidade por segmento com score de oportunidade. |
| **Ferramentas** | Web search, síntese de relatórios, análise comparativa. |
| **Frequência** | Mensal. |
| **Dependências** | IM-01. |
| **Indicadores** | Precisão do mapa vs. realidade percebida; decisões estratégicas influenciadas. |

---

## ÁREA 2 — DIAGNÓSTICO DE CLIENTES

### Agente DC-01 · Entrevistador de Diagnóstico

| Campo | Detalhe |
|---|---|
| **Objetivo** | Conduzir ou estruturar uma entrevista de diagnóstico completa com o prospecto, coletando informações estratégicas para qualificação e proposta. |
| **Entradas** | Formulário de briefing inicial, perfil do prospect (LinkedIn, site, redes sociais), segmento de atuação. |
| **Saídas** | Relatório de diagnóstico: situação atual, desafios, objetivos, maturidade digital, budget estimado, nível de urgência. |
| **Ferramentas** | Formulário customizado, análise de site/redes sociais, template de diagnóstico por segmento. |
| **Frequência** | A cada novo lead qualificado. |
| **Dependências** | COM-02 (qualificação de lead). |
| **Indicadores** | Completude do diagnóstico; correlação com proposta fechada; NPS do cliente após diagnóstico. |

---

### Agente DC-02 · Auditor de Presença Digital

| Campo | Detalhe |
|---|---|
| **Objetivo** | Fazer uma auditoria completa da presença digital do prospect: site, SEO, redes sociais, anúncios, reputação online. |
| **Entradas** | URL do site, perfis sociais, nome da empresa. |
| **Saídas** | Relatório de auditoria com score por área e lista priorizada de oportunidades de melhoria. |
| **Ferramentas** | SEMrush/Ahrefs API, PageSpeed Insights, SimilarWeb, análise de redes sociais, revisão de anúncios. |
| **Frequência** | A cada novo prospect qualificado. |
| **Dependências** | DC-01. |
| **Indicadores** | Tempo de geração do relatório; acurácia percebida pelo cliente; conversão pós-auditoria. |

---

### Agente DC-03 · Construtor de GAP Analysis

| Campo | Detalhe |
|---|---|
| **Objetivo** | Cruzar situação atual do cliente com melhores práticas do mercado e objetivos declarados, gerando um mapa claro de gaps e prioridades. |
| **Entradas** | Output de DC-01 e DC-02, benchmarks do segmento (IM-02), objetivos do cliente. |
| **Saídas** | GAP Analysis visual: onde está, onde quer estar, o que falta, por onde começar. |
| **Ferramentas** | Template de análise, dados de benchmark, síntese de inteligência de mercado. |
| **Frequência** | A cada novo prospect. |
| **Dependências** | DC-01, DC-02, IM-02. |
| **Indicadores** | Clareza percebida pelo cliente (NPS da reunião); influência na decisão de compra. |

---

## ÁREA 3 — COMERCIAL & FOLLOW-UP

### Agente COM-01 · Prospector Inteligente

| Campo | Detalhe |
|---|---|
| **Objetivo** | Identificar e qualificar prospectos que se encaixam no ICP da agência, gerando lista de contatos com contexto personalizado. |
| **Entradas** | ICP definido (segmento, porte, cargo, localização, estágio de crescimento), ferramentas de prospecção. |
| **Saídas** | Lista semanal de 20–50 prospects com: nome, cargo, empresa, contexto personalizado, canal de abordagem sugerido. |
| **Ferramentas** | LinkedIn Sales Navigator, Apollo.io, Hunter.io, pesquisa web. |
| **Frequência** | Semanal. |
| **Dependências** | IM-03 (oportunidades de mercado). |
| **Indicadores** | Taxa de aceitação de conexão; taxa de resposta; qualidade dos leads (% que avançam para diagnóstico). |

---

### Agente COM-02 · Qualificador de Leads

| Campo | Detalhe |
|---|---|
| **Objetivo** | Aplicar critérios objetivos de qualificação (BANT ou similar) para priorizar leads e decidir quais merecem reunião. |
| **Entradas** | Dados do prospect, histórico de interações, respostas iniciais, formulário de pré-qualificação. |
| **Saídas** | Score de qualificação (0–100), recomendação de próximo passo, nível de prioridade (Hot / Warm / Cold). |
| **Ferramentas** | CRM, formulário de qualificação, lógica de scoring. |
| **Frequência** | A cada novo lead gerado. |
| **Dependências** | COM-01. |
| **Indicadores** | Precisão do score (correlação com fechamento); % de reuniões agendadas; % de leads descartados corretamente. |

---

### Agente COM-03 · Gestor de Follow-up

| Campo | Detalhe |
|---|---|
| **Objetivo** | Executar sequências de follow-up personalizadas e no momento certo para cada lead, sem deixar nenhum contato cair no esquecimento. |
| **Entradas** | Histórico de interações, estágio no pipeline, perfil do lead, proposta enviada, objeções levantadas. |
| **Saídas** | Mensagens de follow-up personalizadas para e-mail e WhatsApp, agendamento automático, alertas de urgência. |
| **Ferramentas** | CRM, automação de e-mail, WhatsApp Business API, agenda. |
| **Frequência** | Diário (executa), semanal (revisa). |
| **Dependências** | COM-02, PROP-01. |
| **Indicadores** | Taxa de resposta; tempo médio de fechamento; % de leads reativados; receita gerada por follow-up. |

---

### Agente COM-04 · Monitor de Gatilhos de Compra

| Campo | Detalhe |
|---|---|
| **Objetivo** | Monitorar eventos que sinalizam que um prospect está pronto para comprar agora: nova contratação, mudança de liderança, investimento captado, lançamento de produto, expansão. |
| **Entradas** | Lista de prospects e ex-clientes, LinkedIn, news, DOU, CNPJ.ws, fontes setoriais. |
| **Saídas** | Alerta imediato quando gatilho é detectado, com contexto e sugestão de abordagem personalizada. |
| **Ferramentas** | LinkedIn, Google Alerts, monitoramento de imprensa, fontes regulatórias. |
| **Frequência** | Monitoramento contínuo, alerta imediato. |
| **Dependências** | COM-01, IM-01. |
| **Indicadores** | Nº de gatilhos detectados; tempo de detecção; % de gatilhos que geraram contato; % convertidos. |

---

### Agente COM-05 · Analista de CRM

| Campo | Detalhe |
|---|---|
| **Objetivo** | Manter o CRM atualizado, identificar furos no pipeline, gerar alertas de deals em risco e produzir relatório semanal de pipeline. |
| **Entradas** | Dados do CRM, histórico de interações, propostas enviadas, datas de follow-up. |
| **Saídas** | Relatório semanal de pipeline, lista de deals em risco, recomendações de ação, projeção de receita. |
| **Ferramentas** | CRM (Pipedrive, HubSpot ou similar), análise de dados. |
| **Frequência** | Diário (monitoramento), semanal (relatório). |
| **Dependências** | COM-02, COM-03, PROP-01. |
| **Indicadores** | Completude dos dados de CRM; acurácia das previsões de fechamento; deals perdidos vs. recuperados. |

---

## ÁREA 4 — PROPOSTAS

### Agente PROP-01 · Construtor de Propostas

| Campo | Detalhe |
|---|---|
| **Objetivo** | Gerar uma proposta comercial personalizada, profissional e baseada no diagnóstico do cliente. |
| **Entradas** | Output de DC-01, DC-02, DC-03; objetivos do cliente; serviços disponíveis; tabela de preços. |
| **Saídas** | Proposta completa em formato PDF/Prod Grão: situação atual, solução proposta, escopo, cronograma, investimento, garantias, próximos passos. |
| **Ferramentas** | Template de proposta, geração de texto com IA, ferramenta de design (Canva/Beautiful.ai). |
| **Frequência** | Sob demanda (a cada oportunidade qualificada). |
| **Dependências** | DC-01, DC-02, DC-03, PROP-02. |
| **Indicadores** | Taxa de conversão da proposta; tempo de geração; NPS do cliente sobre a proposta; ticket médio. |

---

### Agente PROP-02 · Precificador Estratégico

| Campo | Detalhe |
|---|---|
| **Objetivo** | Calcular o preço ideal para cada proposta considerando: complexidade, valor entregue, benchmark de mercado, margem e momento do cliente. |
| **Entradas** | Escopo do projeto, horas estimadas, ferramentas necessárias, porte do cliente, benchmark de mercado. |
| **Saídas** | Sugestão de faixa de preço, justificativa de valor, opções de pacote (básico / completo / premium). |
| **Ferramentas** | Planilha de precificação, dados de benchmarking, histórico de projetos anteriores. |
| **Frequência** | Sob demanda. |
| **Dependências** | DC-01, IM-02. |
| **Indicadores** | Margem média por projeto; taxa de aceitação por faixa de preço; comparação vs. benchmark. |

---

### Agente PROP-03 · Revisor de Proposta

| Campo | Detalhe |
|---|---|
| **Objetivo** | Revisar propostas antes do envio verificando: clareza, coerência, ausência de erros, força da argumentação, adequação ao perfil do cliente. |
| **Entradas** | Proposta rascunho gerada por PROP-01. |
| **Saídas** | Proposta revisada + lista de pontos melhorados + score de qualidade (1–10). |
| **Ferramentas** | Revisão com IA, checklist de qualidade, análise de linguagem. |
| **Frequência** | A cada proposta gerada. |
| **Dependências** | PROP-01. |
| **Indicadores** | Score médio de qualidade; redução de retrabalho; taxa de aprovação pós-revisão. |

---

## ÁREA 5 — ENTREGA & OPERAÇÕES

### Agente OP-01 · Gestor de Projetos

| Campo | Detalhe |
|---|---|
| **Objetivo** | Criar e manter o cronograma de cada projeto, gerar alertas de atraso, organizar tarefas e garantir visibilidade sobre o status de entrega. |
| **Entradas** | Escopo do projeto (da proposta aprovada), prazos, responsáveis, dependências entre tarefas. |
| **Saídas** | Board de projeto atualizado, relatório semanal de status, alertas de risco, ata de reunião de kickoff. |
| **Ferramentas** | Prod Grão (Base44), ClickUp ou similar; templates de projeto por tipo de serviço. |
| **Frequência** | Diário (monitoramento), semanal (relatório). |
| **Dependências** | PROP-01 (escopo aprovado). |
| **Indicadores** | % de entregas no prazo; horas estimadas vs. realizadas; satisfação do cliente com a gestão. |

---

### Agente OP-02 · Documentador de Processos

| Campo | Detalhe |
|---|---|
| **Objetivo** | Capturar e documentar processos da agência e dos projetos de clientes, criando base de conhecimento operacional. |
| **Entradas** | Gravações de reunião, descrições de processos, fluxos executados. |
| **Saídas** | SOPs (Procedimentos Operacionais Padrão), fluxogramas, wikis de processo. |
| **Ferramentas** | Transcrição de áudio/vídeo, geração de documentação com IA, Prod Grão (Base44). |
| **Frequência** | Contínuo (captura), semanal (revisão). |
| **Dependências** | OP-01, OP-03. |
| **Indicadores** | Nº de processos documentados; redução de perguntas recorrentes; onboarding de novos membros mais rápido. |

---

### Agente OP-03 · Secretário de Reuniões

| Campo | Detalhe |
|---|---|
| **Objetivo** | Transcrever, resumir e transformar reuniões em atas com: decisões tomadas, responsáveis, prazos e próximos passos. |
| **Entradas** | Gravação ou transcrição da reunião. |
| **Saídas** | Ata estruturada, lista de ações com responsáveis e datas, resumo executivo. |
| **Ferramentas** | Whisper / Otter.ai / Fireflies para transcrição, resumo com IA. |
| **Frequência** | A cada reunião. |
| **Dependências** | Nenhuma. |
| **Indicadores** | Tempo de geração; precisão da ata (avaliação do participante); % de ações executadas. |

---

### Agente OP-04 · Analista de QA

| Campo | Detalhe |
|---|---|
| **Objetivo** | Revisar entregas antes de ir para o cliente, garantindo que atendem ao escopo, padrão de qualidade e expectativas combinadas. |
| **Entradas** | Entrega (copy, relatório, campanha, código, design), briefing original, critérios de aceite. |
| **Saídas** | Relatório de QA com: aprovado / reprovado, itens a corrigir, nível de qualidade. |
| **Ferramentas** | Checklist de qualidade por tipo de entrega, análise com IA, comparação com briefing. |
| **Frequência** | A cada entrega pré-envio ao cliente. |
| **Dependências** | OP-01. |
| **Indicadores** | Taxa de retrabalho após QA; NPS do cliente; número de revisões solicitadas pelo cliente. |

---

## ÁREA 6 — CONTEÚDO

### Agente CONT-01 · Estrategista de Conteúdo

| Campo | Detalhe |
|---|---|
| **Objetivo** | Definir a estratégia de conteúdo mensal alinhada aos objetivos de negócio, persona e momento de mercado. |
| **Entradas** | Objetivos do mês, persona detalhada, tendências (IM-01), performance do conteúdo anterior, calendário de datas. |
| **Saídas** | Estratégia mensal de conteúdo: pilares, formatos, temas, frequência, KPIs. |
| **Ferramentas** | Análise de dados, inteligência de mercado, benchmarking de conteúdo. |
| **Frequência** | Mensal (planejamento), semanal (ajustes). |
| **Dependências** | IM-01, CONT-05 (performance histórica). |
| **Indicadores** | Alinhamento com objetivos de negócio; alcance gerado; leads gerados pelo conteúdo. |

---

### Agente CONT-02 · Pesquisador de Pauta

| Campo | Detalhe |
|---|---|
| **Objetivo** | Pesquisar e validar pautas com base em busca ativa de dados, tendências e ângulos pouco explorados. |
| **Entradas** | Tema/pauta proposta, persona, plataforma de destino. |
| **Saídas** | Pauta completa com: gancho principal, dados de suporte, referências, ângulo diferenciado, estrutura sugerida. |
| **Ferramentas** | Web search, Google Trends, BuzzSumo, análise de conteúdo viral. |
| **Frequência** | Sob demanda (por peça de conteúdo). |
| **Dependências** | CONT-01. |
| **Indicadores** | Qualidade da pauta (avaliação do redator); taxa de uso das pesquisas; engajamento do conteúdo final. |

---

### Agente CONT-03 · Redator

| Campo | Detalhe |
|---|---|
| **Objetivo** | Produzir o conteúdo final (copy, post, artigo, roteiro, e-mail, legenda) no tom e voz da marca. |
| **Entradas** | Pauta (CONT-02), estratégia (CONT-01), guia de voz da marca, formato e plataforma. |
| **Saídas** | Conteúdo redigido pronto para revisão, em múltiplos formatos quando necessário. |
| **Ferramentas** | Claude/GPT com prompt customizado por marca, templates de formato. |
| **Frequência** | Sob demanda. |
| **Dependências** | CONT-02. |
| **Indicadores** | Qualidade editorial (score de revisão); velocidade de produção; taxa de aprovação sem reescrita. |

---

### Agente CONT-04 · Revisor Editorial

| Campo | Detalhe |
|---|---|
| **Objetivo** | Revisar conteúdo verificando: aderência ao tom de voz, precisão factual, clareza, ortografia, adequação à plataforma. |
| **Entradas** | Conteúdo produzido por CONT-03. |
| **Saídas** | Conteúdo revisado + relatório de alterações + score de qualidade. |
| **Ferramentas** | Revisão com IA, checklist editorial por plataforma, verificação de fatos. |
| **Frequência** | A cada peça produzida. |
| **Dependências** | CONT-03. |
| **Indicadores** | Score médio de qualidade; nº de correções; taxa de conteúdo aprovado sem nova rodada. |

---

### Agente CONT-05 · Analista de Performance de Conteúdo

| Campo | Detalhe |
|---|---|
| **Objetivo** | Monitorar e analisar a performance de cada peça de conteúdo, identificando o que funciona e alimentando a estratégia futura. |
| **Entradas** | Métricas das plataformas (Meta, Instagram, LinkedIn, YouTube, blog), conteúdo publicado. |
| **Saídas** | Relatório semanal/mensal de performance com: melhores conteúdos, padrões de sucesso, recomendações para o próximo ciclo. |
| **Ferramentas** | Meta Business Suite API, LinkedIn Analytics, Google Analytics, YouTube Studio. |
| **Frequência** | Semanal. |
| **Dependências** | Nenhuma (alimenta CONT-01). |
| **Indicadores** | Crescimento de alcance; engajamento médio; conteúdos que geraram leads; comparação de performance por formato. |

---

## ÁREA 7 — TRÁFEGO & PERFORMANCE

### Agente TRF-01 · Analista de Performance de Mídia

| Campo | Detalhe |
|---|---|
| **Objetivo** | Monitorar e analisar campanhas de tráfego pago, identificando oportunidades de otimização e entregando relatório acionável. |
| **Entradas** | Dados de campanhas (Meta Ads, Google Ads), orçamento, metas de conversão. |
| **Saídas** | Relatório semanal de performance com: CAC, ROAS, CPC, CTR, recomendações de ação imediata. |
| **Ferramentas** | Meta Ads API, Google Ads API, planilha de performance. |
| **Frequência** | Diário (monitoramento de alertas), semanal (relatório). |
| **Dependências** | CONT-05 (desempenho orgânico como contexto). |
| **Indicadores** | ROAS; CAC; % de melhoria mês a mês; decisões de otimização tomadas com base no relatório. |

---

### Agente TRF-02 · Otimizador de Campanhas

| Campo | Detalhe |
|---|---|
| **Objetivo** | Sugerir e implementar otimizações em campanhas com base em dados: pausar anúncios ruins, escalar os bons, ajustar públicos e orçamentos. |
| **Entradas** | Dados de performance (TRF-01), criativos ativos, histórico de testes. |
| **Saídas** | Lista priorizada de otimizações com: o que mudar, por quê, impacto esperado. |
| **Ferramentas** | Meta Ads Manager, Google Ads, análise de dados. |
| **Frequência** | 2x por semana. |
| **Dependências** | TRF-01. |
| **Indicadores** | ROAS após otimização vs. antes; economia de budget; melhoria de CTR. |

---

### Agente TRF-03 · Criador de Criativos para Anúncios

| Campo | Detalhe |
|---|---|
| **Objetivo** | Gerar variações de copy e briefings de criativo para anúncios com foco em performance. |
| **Entradas** | Oferta a ser anunciada, persona, plataforma, histórico de criativos que funcionaram. |
| **Saídas** | 5–10 variações de copy por campanha, briefing de criativo visual, hipóteses de teste. |
| **Ferramentas** | Claude/GPT com prompt de performance, histórico de anúncios. |
| **Frequência** | A cada nova campanha ou ciclo de testes (quinzenal). |
| **Dependências** | TRF-01 (dados de performance histórica). |
| **Indicadores** | CTR das variações; custo por resultado; velocidade de produção. |

---

## ÁREA 8 — PÓS-VENDA & RELACIONAMENTO

### Agente PV-01 · Gestor de Satisfação

| Campo | Detalhe |
|---|---|
| **Objetivo** | Monitorar a satisfação do cliente durante e após o projeto, agindo proativamente antes que problemas se tornem perdas. |
| **Entradas** | Marcos do projeto, histórico de interações, check-ins programados, NPS e pesquisas. |
| **Saídas** | Score de saúde do cliente (health score), alertas de risco, relatório mensal de satisfação. |
| **Ferramentas** | Formulários de NPS, CRM, análise de sentimento em comunicações. |
| **Frequência** | Quinzenal (check-in), mensal (NPS). |
| **Dependências** | OP-01. |
| **Indicadores** | NPS médio; churn rate; tempo médio de detecção de insatisfação; % de clientes em risco salvos. |

---

### Agente PV-02 · Identificador de Expansão

| Campo | Detalhe |
|---|---|
| **Objetivo** | Identificar oportunidades de upsell, cross-sell e expansão dentro da base de clientes atual. |
| **Entradas** | Histórico do cliente, serviços contratados, resultados entregues, dados de maturidade (DC-03), tendências de mercado. |
| **Saídas** | Lista mensal de oportunidades de expansão por cliente com: serviço sugerido, justificativa, valor potencial, timing ideal. |
| **Ferramentas** | CRM, análise de dados, inteligência de mercado. |
| **Frequência** | Mensal. |
| **Dependências** | PV-01, DC-03, IM-01. |
| **Indicadores** | Receita gerada por expansão; % da base com proposta de expansão; LTV médio. |

---

### Agente PV-03 · Gestor de Referrals

| Campo | Detalhe |
|---|---|
| **Objetivo** | Estruturar e ativar o programa de indicações, identificando clientes com maior potencial de indicar e criando o momento certo para pedir. |
| **Entradas** | NPS alto (> 8), marcos de sucesso entregues, rede de contatos do cliente. |
| **Saídas** | Lista de clientes prontos para indicar, mensagem personalizada de solicitação, rastreamento de indicações. |
| **Ferramentas** | CRM, análise de NPS, templates de solicitação de referral. |
| **Frequência** | Mensal. |
| **Dependências** | PV-01. |
| **Indicadores** | Nº de indicações geradas; taxa de conversão de indicações; CAC via referral vs. outbound. |

---

## ÁREA 9 — FINANCEIRO & BUSINESS INTELLIGENCE

### Agente FIN-01 · Monitor de Saúde Financeira

| Campo | Detalhe |
|---|---|
| **Objetivo** | Monitorar indicadores financeiros críticos e gerar alertas quando algo sai do esperado. |
| **Entradas** | Dados financeiros (faturamento, custos, recebíveis, inadimplência), metas do mês. |
| **Saídas** | Dashboard financeiro semanal, alertas de desvio, projeção de fechamento do mês. |
| **Ferramentas** | Planilha/ERP, análise de dados. |
| **Frequência** | Semanal. |
| **Dependências** | COM-05 (pipeline), OP-01 (projetos em andamento). |
| **Indicadores** | Acurácia das projeções; tempo de detecção de desvio; decisões tomadas com base no alerta. |

---

### Agente FIN-02 · Analista de Rentabilidade

| Campo | Detalhe |
|---|---|
| **Objetivo** | Calcular a margem real por cliente, projeto e serviço, identificando onde a agência perde e onde ganha dinheiro de fato. |
| **Entradas** | Horas dedicadas por projeto, custos de ferramentas, receita, salários (rateio). |
| **Saídas** | Relatório mensal de rentabilidade por cliente/serviço, ranking de rentabilidade, alertas de projetos no prejuízo. |
| **Ferramentas** | Planilha de custos, timesheet, análise de dados. |
| **Frequência** | Mensal. |
| **Dependências** | FIN-01, OP-01. |
| **Indicadores** | Margem média por cliente; % de projetos com margem abaixo do mínimo; melhoria de margem mês a mês. |

---

### Agente FIN-03 · Projetor de Receita

| Campo | Detalhe |
|---|---|
| **Objetivo** | Gerar projeções de receita para os próximos 3–6 meses com base no pipeline atual, churn histórico e sazonalidade. |
| **Entradas** | Pipeline de vendas (COM-05), contratos ativos, histórico de fechamento, taxas de churn. |
| **Saídas** | Projeção de receita (pessimista / realista / otimista) com premissas explícitas. |
| **Ferramentas** | Modelo de projeção, dados de CRM e histórico. |
| **Frequência** | Mensal. |
| **Dependências** | COM-05, FIN-01, PV-01. |
| **Indicadores** | Acurácia da projeção vs. realizado; utilidade na tomada de decisão de contratação/investimento. |

---

## ÁREA 10 — PRODUTO & INOVAÇÃO

### Agente PROD-01 · Gerador de Ideias de Produto

| Campo | Detalhe |
|---|---|
| **Objetivo** | Gerar ideias de novos produtos e serviços baseados em oportunidades de mercado, gaps identificados e pedidos recorrentes de clientes. |
| **Entradas** | Feedbacks de clientes, relatórios de mercado (IM-01), pedidos recorrentes, tendências de IA. |
| **Saídas** | Lista mensal de ideias de produto com: problema resolvido, mercado-alvo, potencial de receita, complexidade de execução. |
| **Ferramentas** | Análise de feedbacks, inteligência de mercado, frameworks de inovação. |
| **Frequência** | Mensal. |
| **Dependências** | IM-01, PV-01, DC-01. |
| **Indicadores** | Nº de ideias geradas; % avançadas para validação; produtos lançados por trimestre. |

---

### Agente PROD-02 · Validador de Hipóteses

| Campo | Detalhe |
|---|---|
| **Objetivo** | Validar rapidamente ideias de produto através de pesquisa de mercado, entrevistas rápidas e análise de demanda. |
| **Entradas** | Ideia de produto (PROD-01), ICP do produto, hipóteses a testar. |
| **Saídas** | Relatório de validação: evidências a favor e contra, nível de confiança, recomendação (avançar / pivotar / descartar). |
| **Ferramentas** | Pesquisa web, entrevistas, análise de busca, formulários de interesse. |
| **Frequência** | Sob demanda. |
| **Dependências** | PROD-01. |
| **Indicadores** | Velocidade de validação; precisão das hipóteses; % de produtos validados que avançam. |

---

### Agente PROD-03 · Construtor de Roadmap

| Campo | Detalhe |
|---|---|
| **Objetivo** | Priorizar e sequenciar o desenvolvimento de produtos e serviços com base em impacto, viabilidade e alinhamento estratégico. |
| **Entradas** | Lista de produtos/melhorias validados, recursos disponíveis, objetivos estratégicos. |
| **Saídas** | Roadmap trimestral com prioridades, dependências, marcos e responsáveis. |
| **Ferramentas** | Framework de priorização (RICE, ICE), visualização de roadmap. |
| **Frequência** | Trimestral. |
| **Dependências** | PROD-01, PROD-02. |
| **Indicadores** | % do roadmap executado no prazo; impacto dos produtos lançados. |
