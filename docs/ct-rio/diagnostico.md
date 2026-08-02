# CT-Rio — Diagnóstico para o site novo

Levantamento feito antes de qualquer construção, cruzando a pasta do Drive (CT-RIO), os ativos já existentes no
Base44, o site atual e os concorrentes diretos.

**Data:** agosto de 2026
**Destino do site:** plataforma Base 44

---

## 1. Quem é o CT-Rio

**CT-Rio = Centro Técnico Rio de Janeiro.** Fundado em 2011 *(a validar — ver pendências)*.

A marca **funciona como duas empresas em uma**, e essa é a chave de todo o projeto. São dois públicos que
praticamente não se cruzam, com gatilhos de decisão opostos:

| | **Colégio CT-Rio** | **Escola Técnica CT-Rio** |
|---|---|---|
| Quem decide | Pais e responsáveis — **ênfase nas mães** | O próprio aluno, jovem ou adulto |
| Produtos | Fundamental 6º–9º, Médio, **Médio Técnico**, EJA | Técnicos pós-médio (12 a 24 meses) |
| O que compra | Segurança, valores, confiança, formação do filho | Emprego, salário, carreira, mudança de vida |
| Tom | Acolhedor, familiar, educativo | Direto, aspiracional, oportunidade |
| Imagem | Uniforme, sala de aula, professores, famílias | Jaleco, EPI, capacete, laboratório, indústria |

Há ainda uma **terceira linha esquecida**: o **Polo Unicesumar** (graduação e pós EAD), que aparece no wireframe
de 2021 e nos mockups da identidade visual de 2025, mas some da comunicação.

### Unidades

- **Bento Ribeiro** — Rua Divisória, 48. Unidade completa: Fundamental, Médio, Médio Técnico, EJA e o portfólio
  técnico inteiro. Ao lado da estação de trem de Bento Ribeiro.
- **Bangu** — unidade compacta, **somente cursos técnicos**, concentrada em Enfermagem, Administração e
  Segurança do Trabalho.

### O diferencial declarado

O aluno cursa o **Ensino Médio regular e sai com dupla formação** — diploma de Médio **e** diploma técnico. É o
que o cliente aponta como o maior nível de diferenciação, e é onde o site precisa ser mais forte.

---

## 2. O portfólio técnico

*Validado com o cliente em agosto de 2026.* As fontes internas divergiam bastante — o doc de marca listava 15
cursos, o app `ctrio` listava 10, e os códigos das planilhas sugeriam outros. A lista fechada é:

### 13 cursos técnicos

**Saúde** — Enfermagem · Radiologia

**Indústria e Construção** — Eletrotécnica · Eletrônica · Mecânica Industrial · Mecatrônica · Edificações ·
Segurança do Trabalho · Eletricista Predial e Residencial

**Tecnologia** — Informática

**Negócios e Educação** — Administração · Logística · Formação de Professores

### 2 especializações técnicas — categoria separada

Enfermagem do Trabalho · Instrumentação Cirúrgica

São formações para quem **já possui formação técnica compatível**, especialmente em Enfermagem. Precisam
aparecer separadas dos cursos técnicos para não confundir o candidato.

**Descartado:** *Automação Industrial* não existe como curso próprio — é conteúdo de Mecatrônica. *Análises
Clínicas*, que constava só no app `ctrio`, também saiu. Segue em aberto o *Preparatório para Carreira Militar*,
que aparece nas peças de 2025.

### Regra de comunicação sobre duração

O site atual informa 12 meses (noturno) e 18 meses (sábados), mas **não é possível confirmar quais cursos têm
turma de sábado hoje**. Por isso o site novo não afirma que todos os cursos têm as duas opções. O padrão é:

> **Duração: a partir de 12 meses\*** — *a duração pode variar conforme o curso, o turno e a organização da
> turma. Consulte nossa equipe para confirmar as turmas disponíveis e a previsão de início das aulas.*

Isso mantém a vantagem competitiva do "12 meses" (ver §4) sem prometer turma que pode não existir.

---

## 3. O que os dados reais de lead dizem

Fonte: `MATRÍCULAS 2025`, `Contatos PÓS 2026`, `CTT BANGU.xlsx` (Drive). Estes números não são opinião — são o
funil real da escola.

### De onde vem o lead — Janeiro/2026 (n = 727)

| Canal | Volume | % |
|---|---|---|
| **Google** | **382** | **53%** |
| Não informou | 132 | 18% |
| Instagram | 69 | 9% |
| Facebook | 68 | 9% |
| Indicação | 21 | 3% |
| Outros (mora perto, passou, outdoor, panfleto, rádio, e-mail) | 55 | 8% |

**Leitura:** mais da metade do funil entra pelo **Google**. O site não é vitrine institucional — é o destino do
tráfego pago e orgânico e o principal ponto de conversão da empresa.

Isso reordena as prioridades do projeto: **velocidade, indexabilidade e conversão para WhatsApp** vêm antes de
qualquer sofisticação visual. E torna o plano de redirect das URLs antigas do Wix uma questão de faturamento, não
de higiene técnica.

### Cursos mais procurados

Pelos códigos recorrentes nas planilhas: **ENF (Enfermagem) domina com folga**, seguido de ETT (Eletrotécnica),
SEG (Segurança do Trabalho), ADM, MEC/MECT, EJA, RAD, INF, EDF.

Na unidade **Bangu**, a concentração é ainda maior: ENF, SEG e ADM respondem por quase tudo.

### Por que o lead morre — nas palavras do próprio time comercial

Transcrito das colunas de observação das planilhas:

| Objeção | Como aparece | Frequência |
|---|---|---|
| **Preço** | `"não respondeu após avalores"`, `"Não pagou boleto"`, `"informou não ter condições"` | Dezenas de ocorrências — **objeção nº 1** |
| **Duração** | `"achou longo 18 meses"`, `"QUER DURAÇÃO 12 MESES"`, `"Quer de 12 meses"` | Recorrente — **objeção nº 2** |
| **Distância** | `"Distante"`, `"mora em Mauá"`, `"resolver pendência Bento Ribeiro"` | Muito recorrente |
| **Ainda no Médio** | `"3º ANO"`, `"2º ANO"`, `"Ensino médio"` | Muito recorrente |
| **Turno** | `"HR DE MANHÃ"` | Pontual mas repetido |
| **Modalidade** | `"curso EAD"`, `"quer formação à distância"` | Pontual mas repetido |
| **Concorrência** | `"já está cursando em outro lugar"` | Recorrente |

### O que isso obriga o site a fazer

1. **Duração acima da dobra** em toda página de curso. Quem quer 12 meses precisa achar os cursos de 12 meses
   sem falar com ninguém.
2. **Bloco de distância** — mapa, duas unidades, trem/BRT, tempo de deslocamento. A objeção `"Distante"` é a
   mais barata de resolver e ninguém está resolvendo.
3. **Ponte do Médio para o Técnico.** Uma quantidade enorme de lead está no 2º/3º ano do Ensino Médio. Hoje esse
   contato entra pedindo curso técnico e ninguém oferece o **Médio Técnico** — que é justamente o carro-chefe.
   É a maior oportunidade de cross-sell não trabalhada.
4. **Turno e modalidade visíveis** — noturno, sábados, EAD.
5. **Preço:** por decisão do cliente, fica fora do site nesta fase. Registrado que é a objeção nº 1 e que o time
   comercial queima leads nela todo mês.

---

## 4. Concorrência

| | **CE Triângulo** | **ETERJ** | **Grau Técnico** |
|---|---|---|---|
| Onde | Rua João Vicente, 1355 — **Bento Ribeiro** | Rio de Janeiro | Rede nacional |
| Desde | 1994 | 1968 / 1975 | — |
| Formados | — | **+18.000** | — |
| Posicionamento | "Colégio e Escola Técnica" — **rótulo idêntico ao do CT-Rio** | Tradição industrial, pioneirismo | Escala: "a maior rede de ensino técnico do Brasil" |
| Portfólio técnico | ~5: Administração, Informática, Enfermagem, Mecatrônica, Eletrônica | Indústria: Mecânica, Eletrotécnica, Informática, Automação, Administração | +30 cursos + graduação EaD |
| Médio + técnico | **Sim** | Não é o foco | Sim |
| Pós-médio | Sim | 1,5 ano, noturno 18h30–22h | Sim |
| Ativos digitais | Site com página por curso, selos **CREA/COREN/SISTEC**, Área do Aluno, Projeto ENEM | Site com página por curso | Site forte, Portal Acadêmico, domínio no Quero Bolsa |

### A conclusão desconfortável

O **CE Triângulo é concorrente de porta**: mesmo bairro (Bento Ribeiro), mesmo rótulo de categoria, mesma oferta
de Médio integrado ao técnico — e **17 anos mais velho**.

Isso invalida dois argumentos que o CT-Rio usa hoje:

- ❌ **"Tradição"** — perde para o Triângulo (1994) e para a ETERJ (1968).
- ❌ **"Mais de 10 mil formados"** — perde para os 18 mil da ETERJ.

Ambos podem continuar como prova de solidez. Nenhum dos dois pode ser a manchete.

### Onde o CT-Rio ganha de verdade

1. **Portfólio quase 3x maior que o do vizinho** — 13 cursos técnicos mais 2 especializações, contra ~5 do Triângulo.
2. **Bloco de Saúde exclusivo na região** — Enfermagem, Radiologia, Análises Clínicas, Instrumentação Cirúrgica,
   Enfermagem do Trabalho. O Triângulo só tem Enfermagem; a ETERJ não tem saúde. **E Enfermagem é justamente o
   curso mais procurado do funil.** Este é o ativo competitivo mais forte e o mais subaproveitado.
3. **Duas unidades** — Zona Norte e Zona Oeste. Ataca de frente a objeção `"Distante"`; os dois concorrentes
   locais têm endereço único.
4. **Flexibilidade real** — 12 meses, noturno, aos sábados. Contra o pós-médio de 1,5 ano da ETERJ, "12 meses" é
   vantagem direta e mensurável.
5. **Médio com dupla formação** — o que a rede nacional não replica localmente.
6. **Jornada completa sob a mesma marca** — do 6º ano à pós-graduação (via Polo EAD). Ninguém na esquina faz isso.

### Higiene competitiva

O Triângulo exibe **CREA, COREN e SISTEC** no site. O CT-Rio precisa exibir os equivalentes. Isso não é
diferencial — é o piso da categoria. Falta confirmar quais registros o CT-Rio detém.

### Risco reputacional

Há reclamações registradas no Reclame Aqui (entrega de documentação, condições de sala de aula, computadores,
registro de histórico escolar). O site não deve fingir que não existem. A resposta correta é prova concreta:
fotos reais das unidades e laboratórios (há acervo 2022–2026 no Drive), depoimentos em vídeo (também no Drive) e
transparência sobre certificação e registro de diploma.

---

## 5. Auditoria dos ativos existentes no Base44

Não estamos partindo do zero. Existem **7 apps CT-Rio** na conta:

| App | ID | O que é | Estado |
|---|---|---|---|
| **CT-RIO LP Ensino Médio + Profissão** | `698b8de9f0e4212d02304bc8` | **Site quase completo** — 22 páginas, 4 entidades | Arquitetura boa, visual antigo, **entidades vazias** |
| **ctrio** | `6a110c345505247c26aed4f1` | Landing page única | **Melhor design system**, tem chat `chatCarlos` |
| CT-RIO LP ENSINO MÉDIO | `6945c372f1dc77f954101b36` | LP de campanha | — |
| CT-RIO LP ENSINO FUNDAMENTAL (Copy) | `69a1c544892029a92a4f0367` | LP de campanha | — |
| CT-RIO LP Outdoor | `69053735a640db55d3a8f5f1` | LP de outdoor | — |
| CT-Rio Matrículas | `6a456fb7c06d4d04ed182c60` | Fluxo de matrícula | — |
| Quiz CT-Rio | `69f93c7b5f22d55003c73a99` | Quiz vocacional | Reaproveitável como isca de lead |

### O que vale herdar

**Do `LP Ensino Médio + Profissão` — a arquitetura:**
páginas `Home`, `CursosTecnicos`, `CursoDetalhe`, `EnsinoMedio`, `EnsinoFundamental`, `EJA`, `CursosEAD`,
`Especializacoes`, `Unidades`, `Contato`, `NossaHistoria`, `PropostaPedagogica`, `Bolsao2026`, `Matriculas`,
`Mostratec`, `Admin`; entidades `Lead`, `CursoTecnico`, `CursoLivre`, `EspecializacaoTecnica`.

**Do `ctrio` — o design system:**
Barlow 900 nos títulos, azul `#1B3A6B`, laranja `#F5820A`, `RevealWrap` (animação de entrada), `CursoCard` +
`CursoCardSVGs` (ilustrações próprias por curso), filtro por área (Saúde/Indústria/Tecnologia/Negócios),
`WhatsAppIcon`, `Header`/`MobileNav`/`Footer`.

### Defeitos que não podem ser herdados

- **WhatsApp placeholder** `5521000000000` no app `ctrio` — todos os CTAs estão quebrados.
- **WhatsApp de Bangu malformado** no LP: `"552196807-6091"` (hífen no meio do número).
- **Quatro páginas de detalhe fazendo a mesma coisa**: `CursoDetalhe`, `CursoLivreDetalhe`,
  `EspecializacaoDetalhe` e `EletricistaPrediallDetalhe` — esta última com erro de digitação no nome.
- **Páginas vazias no ar**: `CursosEAD`, `EJA`, `Depoimentos`, `Institucional` são stubs de ~400 bytes.
- **Lista de cursos hardcoded** no componente em vez de vir da entidade `CursoTecnico` (que está vazia).
- **`"95% taxa de empregabilidade"`** publicado sem nenhuma fonte.

---

## 6. Identidade visual

Fonte: `apresentacao_ctrio.pdf` e `ctrio_marca_final.pdf` (Drive → CT-RIO → Identidade visual), agosto de 2025.

A marca foi redesenhada em 2025:

- **Atributos definidos no projeto**: robusto, sério, convencional, massificado; secundários: jovem/inovador.
- **Marca all-type** — só letras, caixa baixa, `ctrio` **sem hífen**. O hífen que separava "CT" e "RIO" foi
  retirado; a diferenciação agora está nos detalhes laranja das letras **c** e **t**.
- **Origem preservada**: as "chapas dobradas" do símbolo antigo viraram um elemento sutil dentro do texto.
- **Removido do projeto antigo**: degradês, sombras, composição símbolo+tipo, tipografia pesada.
- **Tipografia**: **Montserrat** — definida no manual como fonte de todos os projetos de comunicação.
- **Cores**: principais **Profundo** (azul), **Suco** (laranja) e **Branco**; apoio **Preto** e **Claridade**.
- **Padrão criativo**: os elementos laranja das letras C e T formam um padrão gráfico reaproveitável, assim como
  o espaço vazio entre as peças.
- **Fotografia**: dois bancos distintos — Colégio (uniforme, sala, famílias) e Técnica (jaleco, EPI, capacete,
  laboratório, indústria).
- **Assinaturas já em uso nas peças**: `#vem pro ct`, `10.000 alunos formados`, `Bolsão 2026`,
  `Pagamento Facilitado`.

⚠️ **Conflito registrado:** o manual de 2025 define **Montserrat**, mas o app `ctrio` (o mais recente) foi
construído em **Barlow**. E o doc de marca antigo cita **vermelho** como cor de apoio, enquanto o manual de 2025
define **laranja**. Ver pendências.

---

## 7. Divergências de dados encontradas

| Dado | Fonte A | Fonte B | Assumido por ora |
|---|---|---|---|
| Alunos formados | 10.000 (apresentação 2025, peças) | +8mil (app `ctrio`) | **"+ de 10 mil formados"** |
| Ano de fundação | 2011 (apresentação de identidade) | 2014 (diretórios externos) | **2011** |
| Nº de cursos | 15 (doc de marca e site) | 10 (app `ctrio`) | **13 + 2 especializações** — validado |
| Cor de apoio | Vermelho (doc de marca antigo) | Laranja "Suco" (manual 2025) | **Laranja** |
| Azul | `#143666` (LP antiga) | `#1B3A6B` (app `ctrio`) | **`#1B3A6B`** |
| Laranja | `#ff8500` (LP antiga) | `#F5820A` (app `ctrio`) | **`#F5820A`** |
| Tipografia | Montserrat (manual 2025) | Barlow (app `ctrio`) | **A decidir** |
| Empregabilidade | "95%" (app) | sem fonte | **Não publicar** |

Todas seguem para validação com o cliente — ver `pendencias-validacao.md`.

---

## 8. Limitação metodológica

O ambiente de execução usado neste levantamento bloqueia acesso de rede a qualquer host fora de
Google / Anthropic / GitHub. Não foi possível abrir diretamente `ct-rio.com.br`, `cetriangulo.com.br`,
`eterj.com.br` nem `grautecnico.com.br` — nem por requisição HTTP, nem por navegador headless.

A leitura desses sites foi reconstruída a partir de busca (títulos, URLs indexadas e resumos de conteúdo) e dos
ativos disponíveis no Drive e no Base44. A estrutura de URLs do site atual do CT-Rio foi confirmada por
indexação:

`/` · `/o-ctrio` · `/cursos-tecnicos` · `/medio-técnico` · `/fale-conosco` · `/unidade-bangu` ·
`/tecnico-enfermagem` · `/tecnico-eletronica` · `/tecnico-edificacao` · `/formacao-professores`

Onde a informação depende de leitura direta de página, está marcada como pendência.
