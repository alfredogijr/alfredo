# CT-Rio — Plano do site novo

Blueprint de execução. Baseado no `diagnostico.md`; pendências em `pendencias-validacao.md`.

**Plataforma:** Base 44 (app novo)

---

## Decisões travadas

1. **App Base44 novo**, herdando o design system do app `ctrio` e a arquitetura de páginas/entidades do
   `LP Ensino Médio + Profissão`. Não evoluir nenhum dos dois — os dois carregam dívida (dados vazios, WhatsApp
   placeholder, quatro páginas de detalhe duplicadas).
2. **"Dois mundos, uma marca"** — home única que faz a triagem em segundos; cada mundo com tom, visual e jornada
   próprios. Sem splash de primeiro acesso (custa conversão e SEO).
3. **Preço fora do site nesta fase.** Foco no copy. **Duração entra com destaque** — 12 vs 18 meses é argumento
   de venda.
4. **Divergências de dados** não bloqueiam a construção; valores assumidos em `pendencias-validacao.md`.
   Por ora: **"+ de 10 mil formados"** e fundação em **2011**.

---

## Arquitetura

```
HOME  — triagem (Colégio · Escola Técnica · EAD) + prova social + unidades

├── COLÉGIO ................................ tom: família, mãe decisora
│   ├── Ensino Fundamental (6º ao 9º)
│   ├── Ensino Médio
│   ├── Ensino Médio Técnico  ★ CARRO-CHEFE — dupla formação
│   ├── EJA
│   ├── Proposta Pedagógica
│   └── Mostra Tecnológica
│
├── ESCOLA TÉCNICA ......................... tom: carreira, empregabilidade
│   ├── Todos os cursos — filtro Saúde · Indústria · Tecnologia · Negócios
│   ├── /curso/[slug] — UMA página dinâmica para os ~17 cursos
│   └── Especializações / Cursos Livres
│
├── EAD — Polo Unicesumar (graduação e pós)
│
├── INSTITUCIONAL — Nossa História · Unidades · Depoimentos
├── BOLSÃO / MATRÍCULAS — campanha sazonal, ligável e desligável
└── CONTATO
```

**Regra de ouro:** WhatsApp da **unidade correta** visível em toda página, com mensagem pré-preenchida contendo o
curso de origem. 53% do funil chega do Google e sai pelo WhatsApp — tudo converge para lá.

---

## Estratégia de copy

### Colégio — quem lê é mãe

Vende segurança e futuro do filho, não currículo.

- **Manchete do Médio Técnico** ataca a dupla formação de frente: *sai do 3º ano com diploma de Ensino Médio
  **e** de técnico — e já pode trabalhar.*
- Responder o que a mãe realmente pergunta: como é o dia a dia, quem são os professores, como é a estrutura, o
  filho vai estar seguro, isso ajuda no ENEM, e depois do 3º ano — e aí?
- **Prova:** fotos reais das unidades (acervo 2022–2026 no Drive), Mostra Tecnológica, depoimentos de
  responsáveis.

### Escola Técnica — quem lê é o próprio aluno

Jovem ou adulto decidindo mudar de vida. Tom direto, sem rodeio institucional.

- Assinaturas que a marca já usa e funcionam: *"Quer mudar de vida?"*, *"a forma mais rápida de entrar no
  mercado"*, `#vem pro ct`.
- **Toda página de curso responde acima da dobra:** duração (12 ou 18 meses) · turno · unidade · o que o
  profissional faz · onde trabalha.
- **Bloco anti-objeção obrigatório**, tirado direto do funil real:
  | Objeção no funil | Resposta na página |
  |---|---|
  | `"Distante"` | Mapa, duas unidades, trem/BRT, tempo de deslocamento |
  | `"achou longo 18 meses"` | Destacar os cursos de 12 meses; enquadrar 18 como investimento com data de retorno |
  | `"3º ANO"` / `"2º ANO"` | Ponte para o Médio Técnico — hoje esse lead é perdido |
  | `"HR DE MANHÃ"` / `"curso EAD"` | Turnos e modalidades visíveis |
- **Prova:** depoimentos em vídeo (Drive), laboratórios, empresas empregadoras.

### Home

Três blocos, sem splash: **quem você é** → **prova** (formados, cursos, unidades, MEC) → **unidades**.

### O que NÃO usar como manchete

- ❌ **"Tradição"** — CE Triângulo é de 1994, ETERJ de 1968. O CT-Rio perde.
- ❌ **"+10 mil formados"** como argumento principal — ETERJ declara 18 mil. Serve como prova de solidez, não
  como manchete.
- ❌ **"95% de empregabilidade"** — sem fonte, sai do ar.

### O que usar

1. **Portfólio 3x maior que o do vizinho** — ~17 cursos contra ~5 do CE Triângulo.
2. **Bloco de Saúde exclusivo na região** — e Enfermagem é o curso mais procurado do funil. Ativo mais forte e
   mais subaproveitado.
3. **Duas unidades** — Zona Norte e Zona Oeste; os concorrentes locais têm endereço único.
4. **12 meses** — contra o pós-médio de 1,5 ano da ETERJ, é vantagem direta.
5. **Médio com dupla formação.**
6. **Do 6º ano à pós** sob a mesma marca (com o Polo EAD).

---

## Design system

Do manual de identidade de 2025:

| Item | Definição |
|---|---|
| Marca | All-type, caixa baixa, `ctrio` **sem hífen**, dobras laranja nas letras c e t |
| Azul (Profundo) | `#1B3A6B` *(a confirmar no manual)* |
| Laranja (Suco) | `#F5820A` *(a confirmar no manual)* |
| Apoio | Branco · Preto · Claridade |
| Tipografia | **Montserrat** pelo manual — app `ctrio` usa Barlow *(a decidir)* |
| Padrão criativo | Dobras das letras + espaço vazio entre peças |
| Fotografia | Dois bancos: Colégio (uniforme, sala, famílias) · Técnica (jaleco, EPI, laboratório) |

**Componentes a herdar do app `ctrio`:** `RevealWrap`, `CursoCard`, `CursoCardSVGs`, filtro por área,
`WhatsAppIcon`, `Header` / `MobileNav` / `Footer`.

---

## Modelo de dados

- **`CursoTecnico`** — herdar o schema existente e adicionar `area` (saude/industria/tecnologia/negocios),
  `unidades` (array), `turnos`, `destaque` (bool). **Popular com os ~17 cursos** — hoje a entidade está vazia e
  a lista vive hardcoded no componente.
- **`Lead`** — herdar (`tipo_interesse`, `unidade_preferencia`, `origem`) e adicionar
  `utm_source` / `utm_medium` / `utm_campaign`. Sem isso não se mede de onde vem a matrícula.
- **`Depoimento`** — nova, alimentada pelo acervo do Drive.
- **`CursoLivre`** e **`EspecializacaoTecnica`** — manter.

Uma única página `/curso/[slug]` movida a dados, aposentando as quatro páginas de detalhe duplicadas.

---

## Ordem de execução

**Fase 1 — Fundação**
1. Extrair hex oficiais e logo de `ctrio_marca_final.ai` / `.pdf`
2. Criar o app Base44 novo com design system e Layout (Header, Footer, WhatsApp flutuante)
3. Criar as entidades e **popular `CursoTecnico`**

**Fase 2 — Espinha dorsal** *(o que gera matrícula)*
4. Home com a triagem dos dois mundos
5. `CursosTecnicos` (listagem + filtro) e `/curso/[slug]` dinâmica
6. `EnsinoMedioTecnico` — a página mais importante do site

**Fase 3 — Completar**
7. Fundamental, Médio, EJA, EAD, Especializações
8. Unidades (mapa e rota), Nossa História, Proposta Pedagógica, Depoimentos, Contato

**Fase 4 — Conversão e captação**
9. Formulários gravando em `Lead` com UTM; WhatsApp por unidade com mensagem pré-preenchida
10. **SEO — não negociável:** title/description por página, schema.org `EducationalOrganization` + `Course`,
    sitemap, e o **mapa de redirects 301 das URLs do Wix** (é 53% do funil)
11. Bolsão/Matrículas como campanha sazonal

**Fase 5 — Extras**
12. Quiz vocacional (reaproveitar `Quiz CT-Rio`) como isca de lead
13. Chat `chatCarlos` (reaproveitar do app `ctrio`)

---

## Verificação antes de publicar

- **Preview Base44** a cada fase, navegando como os dois públicos — mãe procurando Médio Técnico, adulto
  procurando Enfermagem — conferindo se cada um chega ao WhatsApp em **≤ 3 cliques**
- **Mobile primeiro** — o funil chega por Google e Instagram, majoritariamente celular
- **Lead ponta a ponta**: preencher formulário → confirmar registro na entidade `Lead` com UTM correto
- **WhatsApp**: cada CTA abre o número certo da unidade certa, com mensagem pré-preenchida
- **SEO**: titles/descriptions únicos, headings, schema.org, sitemap e mapa de redirects testado
- **Fatos**: nenhum número no ar que não esteja validado em `pendencias-validacao.md`
