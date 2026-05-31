# Guia Prático — Produção de Conteúdo com IA (Do Zero ao Agendamento)

> Para quem tem conhecimento de marketing, mas pouco ou nenhum de sistemas.
> Versão mais simples possível. Sem programação. Sem ferramentas complicadas.

---

## O que você vai ter no final

Você coloca algumas informações sobre o cliente → Claude produz o conteúdo → você revisa rapidamente → copia e cola no agendador da rede social.

**Ferramentas necessárias:**
- Claude.ai (você já usa)
- O agendador que você já usa (Meta Business Suite, Buffer, Later, etc.)

**Nada mais.**

---

## PARTE 1 — CONFIGURAÇÃO (faz uma vez por cliente, leva ~20 minutos)

### O que é um "Projeto" no Claude?

Um Projeto é uma conversa que tem memória permanente.
Você configura o cliente UMA vez, e o Claude nunca esquece.
Cada cliente = um Projeto separado.

---

### Passo 1 — Criar o Projeto do cliente

1. Acesse claude.ai
2. No menu lateral esquerdo, clique em **"Projects"** (ou "Projetos")
3. Clique em **"New Project"** (Novo Projeto)
4. Dê o nome do cliente (ex: "Conteúdo — Empresa X")
5. Clique em **"Project Instructions"** (ou "Instruções do Projeto")
6. Cole o texto abaixo, preenchendo os campos com as informações do cliente:

```
MEMÓRIA DO CLIENTE
──────────────────────────────────────────

EMPRESA: [nome da empresa]
SEGMENTO: [ex: escola de natação, clínica odontológica, construtora]
PRODUTO/SERVIÇO PRINCIPAL: [o que vende]

PÚBLICO-ALVO:
- Quem é: [ex: mães de 30 a 45 anos, classe B/C, interior de SP]
- Principal dor/desejo: [ex: quer que o filho aprenda a nadar com segurança]
- Onde está: [ex: Instagram principalmente, alguns no Facebook]

TOM DE VOZ:
- Como a marca fala: [ex: acolhedor, próximo, sem termos técnicos]
- O que NUNCA fazer: [ex: não usar gírias, não prometer milagre]
- Referência de estilo: [ex: como um professor amigo, não como uma corporação]

PLATAFORMAS QUE PRODUZIMOS:
- [ex: Instagram feed, Instagram stories, LinkedIn]

PILARES DE CONTEÚDO (os assuntos principais):
1. [ex: Dicas práticas de natação]
2. [ex: Bastidores da escola]
3. [ex: Depoimentos de alunos]
4. [ex: Curiosidades sobre o esporte]

CTA PADRÃO (como terminamos os posts):
- [ex: "Fale com a gente pelo link na bio"]
- [ex: "Agende uma aula experimental gratuita"]

EXEMPLOS DE POST QUE JÁ FUNCIONARAM:
[Cole aqui 1 ou 2 legendas de posts que tiveram bom desempenho]

EXEMPLOS DE POST QUE NÃO QUEREMOS:
[Cole aqui se tiver algum exemplo do que não quer]
```

7. Salve. Pronto — o Claude agora "conhece" esse cliente para sempre.

---

### Passo 2 — Testar se funcionou

Ainda no mesmo Projeto, envie essa mensagem:

```
Me apresente esse cliente em 3 linhas para eu confirmar se
as informações estão certas.
```

Se o resumo fizer sentido, está configurado. Se algo estiver errado, corrija nas instruções do Projeto.

---

## PARTE 2 — RITUAL MENSAL (faz uma vez por mês, ~20 minutos)

### Passo 3 — Gerar o calendário editorial do mês

Abra o Projeto do cliente e cole essa mensagem:

```
Vamos planejar o conteúdo de [MÊS/ANO].

Informações deste mês:
- Objetivo principal: [ex: aumentar agendamentos de aula experimental]
- Datas importantes: [ex: volta às aulas dia 5, feriado dia 15]
- Novidade ou promoção: [ex: desconto de matrícula em janeiro]
- O que funcionou bem no mês passado: [ex: post de depoimento teve muito alcance]
- O que não funcionou: [ex: posts muito longos tiveram pouco engajamento]

Com base nisso, crie um calendário editorial para o mês com:
- 12 ideias de post (3 por semana)
- Para cada ideia: tema, formato sugerido (carrossel/foto/vídeo/stories) e pilar
- 1 campanha ou sequência temática do mês
```

O Claude vai entregar um calendário completo.

**O que você faz:** Lê, risca o que não faz sentido, pede para trocar o que não gostou. Quando estiver bom, salva no Prod Grão.

---

## PARTE 3 — PRODUÇÃO SEMANAL (faz uma vez por semana, ~30 minutos)

### Passo 4 — Pedir as pautas da semana

Abra o mesmo Projeto e cole:

```
Vamos produzir os posts desta semana.

Posts planejados para esta semana (do calendário que fizemos):
1. [tema do post 1]
2. [tema do post 2]
3. [tema do post 3]

Para cada um, antes de escrever, me entregue:
- Gancho (primeira frase que para o scroll)
- Ângulo (qual aspecto do tema vamos explorar)
- Dados ou referência que embasam o post (se aplicável)

Aguarde minha aprovação antes de escrever as legendas.
```

Você vai receber os ganchos e ângulos. Lê cada um.
Se gostar → responde "aprovado, pode escrever todos"
Se quiser mudar algo → diz o que mudar antes de escrever.

---

### Passo 5 — Gerar as legendas

Depois de aprovar as pautas, mande:

```
Pode escrever as legendas agora.

Para cada post entregue:
- Legenda completa pronta para publicar
- Sugestão de hashtags (máximo 5, relevantes)
- Sugestão de horário de publicação
- Para stories: texto de apoio (se aplicável)
```

Você vai receber todos os posts prontos.

---

### Passo 6 — Revisar (o único passo que exige atenção)

Leia cada post e pergunte:
- Está com a voz certa do cliente? (Parece que a marca falou?)
- Está factualmente correto? (Nada errado sobre o produto/serviço)
- O CTA está presente?
- Tem algo constrangedor ou que o cliente não aprovaria?

Se tiver algo errado, diz pro Claude:
```
No post 2, troca o CTA por [o que você quer] e
deixa o tom mais [o que você quer].
```

Se estiver tudo bem, copia e agenda.

---

### Passo 7 — Copiar e agendar

Abre o agendador (Meta Business Suite, Buffer, Later, etc.)
Cola a legenda + hashtags
Adiciona a imagem/vídeo correspondente
Agenda no horário sugerido

Pronto.

---

## RESUMO — O que você faz cada vez

```
UMA VEZ (setup):
└── 20 min → Criar Projeto no Claude com as infos do cliente

TODO MÊS:
└── 20 min → Pedir o calendário editorial do mês

TODA SEMANA:
├── 5 min → Pedir as pautas da semana
├── 5 min → Aprovar os ângulos
├── 10 min → Revisar as legendas geradas
└── 10 min → Copiar e agendar
```

**Total de trabalho semanal: ~30 minutos por cliente.**

---

## Quando algo sair errado (e vai sair)

| Problema | O que fazer |
|---|---|
| Tom errado (ficou muito formal/informal) | Diz: "Ficou muito [X]. Reescreve com mais [Y]" |
| Conteúdo genérico demais | Diz: "Está genérico. Adicione um dado específico ou situação real do dia a dia do cliente" |
| Muito longo | Diz: "Corta pela metade. Só o essencial." |
| Claude não lembrou algo do cliente | Vai nas Instruções do Projeto e adiciona a informação que faltou |
| Post não funcionou bem | No próximo mês, inclui no campo "o que não funcionou" |

---

## O que vem depois (quando você quiser evoluir)

Esta versão é 100% manual — você cola os prompts e revisa.
Funciona. É suficiente para começar.

Quando quiser automatizar, a evolução natural é:

```
AGORA (manual):
Você → Claude → Você revisa → Agenda

PRÓXIMO PASSO (semi-automático):
Formulário → Você cola no Claude → Claude gera → Você revisa → Agenda

FUTURO (automático):
Formulário → n8n envia pro Claude → Claude gera → vai pro Prod Grão →
você aprova no Prod Grão → publica automaticamente
```

Mas isso só faz sentido depois que o processo manual estiver rodando bem.
Não pule etapas.

---

## Para a Grão de Mostarda (a agência em si)

Crie um Projeto chamado "Conteúdo — Grão de Mostarda" e preencha com:

```
EMPRESA: Agência Grão de Mostarda
SEGMENTO: Agência de marketing digital com especialização em IA
PRODUTO PRINCIPAL: Estratégia, automação de marketing e soluções de IA
  para PMEs de diversos segmentos

PÚBLICO-ALVO:
- Donos de pequenas e médias empresas
- Gestores de marketing que querem usar IA
- Empresas dos segmentos: educação, turismo esportivo,
  eventos, saúde, construção, serviços, varejo

TOM DE VOZ:
- Acessível mas especialista (não arrogante, não simplório)
- Concreto, com exemplos reais
- Sem jargão técnico desnecessário

PILARES DE CONTEÚDO:
1. Cases e resultados de clientes
2. IA na prática (como usar no dia a dia do negócio)
3. Opinião sobre marketing e tendências
4. Bastidores da agência

CTA PADRÃO:
- "Quer ver como isso funcionaria no seu negócio? Fala com a gente."
```
