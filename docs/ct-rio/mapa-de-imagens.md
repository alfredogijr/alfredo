# CT-Rio — Mapa de imagens por espaço do site

Que imagem entra em cada lugar, o que já está pronto e o que ainda falta.

**Site destino:** https://ctrio2026novo.base44.app
**Atualizado:** agosto de 2026

---

## Regra de ouro: suba a foto limpa

O tratamento da marca (gradiente azul, faixa laranja, texto por cima) é aplicado pelo **site, via CSS**. Então:

- ✅ Suba a foto **limpa**, sem overlay, sem texto
- ❌ Não suba foto já escurecida ou com texto queimado

Assim dá para trocar o texto da campanha sem refazer a arte, e a mesma foto serve em vários lugares. O arquivo
`DEMO_split_home.jpg` mostra como fica depois do tratamento — é só demonstração, não é para subir.

---

## Pronto para subir — 10 arquivos

Tratados a partir das suas fotos: rotação corrigida (todas vinham deitadas por EXIF), recorte com o rosto
preservado, redimensionadas e otimizadas. Total de 2,2 MB.

### Hero da home — split dos dois mundos

| Arquivo | Espaço | Formato |
|---|---|---|
| `hero-colegio.jpg` | **Hero, lado esquerdo (Colégio)** — aluna do Fundamental, logo nítida, turma desfocada ao fundo | 1200×1600 (3:4) |
| `hero-colegio-alt-medio.jpg` | Alternativa — duas alunas do Médio, parede azul que casa com a marca | 1200×1600 |
| `hero-colegio-alt-menino.jpg` | Alternativa — menino do Fundamental, ótimo contraponto de gênero | 1200×1600 |

> **Recomendo `hero-colegio.jpg`** para o lado do Colégio: rosto centralizado, olhar na câmera, logo legível e
> muita profundidade de campo. O espaço vazio embaixo é exatamente onde o texto entra.

### Banners largos

| Arquivo | Espaço | Formato |
|---|---|---|
| `banner-vida-escolar.jpg` | **Vida escolar / Médio** — quatro alunas com pompons e balões. Melhor foto de energia do lote | 1920×1080 |
| `banner-proposta-pedagogica.jpg` | **Proposta pedagógica / corpo docente** — professora com a camisa `#vempropct`. A assinatura da marca aparece na própria foto | 1920×1080 |
| `banner-entrada-escola.jpg` | **Institucional / como chegar** — alunos entrando, mochilas, rua. Boa como textura de fundo | 1920×1080 |
| `banner-sala-evento.jpg` | Apoio — sala em evento. A mais fraca do lote, usar só se faltar | 1920×1080 |

### Cards

| Arquivo | Espaço | Formato |
|---|---|---|
| `card-fundamental.jpg` | **Card Ensino Fundamental** | 1200×900 (4:3) |
| `card-fundamental-dupla.jpg` | **Card Ensino Médio** ou convivência | 1200×900 |
| `card-estrutura-sala.jpg` | **Estrutura / salas** — sala ampla | 1200×900 |

---

## O buraco que sobrou: Escola Técnica

**As 10 fotos são todas de Colégio.** Não há uma única de jaleco, EPI, laboratório ou oficina — e a Escola
Técnica é metade do site e a origem da maior parte da procura (Enfermagem é o curso mais buscado do funil).

### Faltam, em ordem de prioridade

| # | Espaço | O que precisa | Formato |
|---|---|---|---|
| 1 | **Hero, lado direito (Escola Técnica)** | Aluno de **jaleco ou EPI** em laboratório, olhando para a câmera, espaço livre embaixo | 3:4 |
| 2 | Card área **Saúde** | Laboratório de enfermagem, jaleco, manequim ou equipamento | 4:3 |
| 3 | Card área **Indústria** | Bancada, painel elétrico ou oficina, com EPI | 4:3 |
| 4 | Card área **Tecnologia** | Laboratório de informática | 4:3 |
| 5 | Card área **Negócios** | Sala de administração | 4:3 |
| 6 | **Fachada Bento Ribeiro** | Marca visível, de dia | 4:3 |
| 7 | **Fachada Bangu** | Marca visível. O acervo só tem WhatsApp comprimido, não serve | 4:3 |

### Onde buscar antes de gerar

1. **Google Drive → `Fotos 2025 CT-Rio` → `Fotos Pós-Médio (Visita fevereiro)` → `Profissional/`**
   Ensaio de câmera, 3 a 5 MB por arquivo. É o melhor material técnico que existe no acervo — **eu consigo
   acessar essa pasta** e trato os arquivos como fiz com estes.
2. **Álbum do Google Fotos dos cursos técnicos** — a rede deste ambiente bloqueia `photos.app.goo.gl`, então
   **não consigo abrir**. Se você baixar e me mandar, eu trato.
3. **Gerar por IA** — só onde não existir foto real. Recomendo evitar em rosto de aluno; usar em plano aberto
   de laboratório ou ambiente, sem rosto identificável.

---

## Quando a produção nova chegar

O código marca imagem provisória com `provisoria: true` e `imagensProvisorias()` lista tudo que precisa ser
trocado. Ver `brief-producao-imagens.md` para a lista de tomadas.

Estas 10 **não são provisórias** — são fotos reais, dos alunos, com o uniforme certo e a logo nova. Podem ficar.
