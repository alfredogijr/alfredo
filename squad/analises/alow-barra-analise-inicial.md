# Alow Barra — Análise Inicial do Squad Dev

**App**: Alow Barra (Base44 ID: `6a03e0560a0db49416ab43fd`)  
**Data**: 2026-06-11  
**Modelo de negócio**: Plataforma de cupons local — 100% gratuito para lojistas e consumidores  
**Foco geográfico**: Barra da Tijuca, Rio de Janeiro

---

## Estado Atual (dados reais)

| Entidade | Quantidade | Observação |
|----------|-----------|------------|
| Empresas | 9 | 1 real (Grão de Mostarda) + 8 amostras |
| Cupons | 9 | Variados (restaurantes, beleza, pets, moda...) |
| Resgates | 3 | Todos com status `redeemed` (nenhum `used`) |
| Clientes | 3 | Inclui 1 teste com dado inválido |

---

## Análise por Agente

---

### 🎯 Product Manager

**O produto**  
Alow Barra é uma plataforma de cupons hiperlocal focada na Barra da Tijuca. O posicionamento de "100% gratuito" para os dois lados é uma estratégia inteligente de entrada no mercado — reduz fricção para adoção, especialmente de lojistas.

**Pontos fortes**
- Foco geográfico preciso (Barra da Tijuca) facilita aquisição e curadoria
- Variedade de categorias já cobertas: restaurantes, beleza, fitness, pets, moda
- Tipos de cupom bem pensados: aberto (código fixo) e controlado (código único por CPF)
- Dados de CPF + WhatsApp por resgate geram base de clientes valiosa para os lojistas

**Lacunas críticas**
1. **Sem onboarding do lojista**: 8 das 9 empresas não têm `owner_email` — estão sendo gerenciadas pelo admin. O lojista não tem como cadastrar e gerenciar seus próprios cupons de forma autônoma ainda.
2. **Sem notificação ao lojista**: quando um cupom é resgatado, o lojista não recebe aviso em tempo real.
3. **Sem analytics para o lojista**: quantos resgates? Qual faixa etária? Em que dias? Sem isso, o lojista não vê o valor da plataforma.
4. **Sem monetização definida**: o modelo gratuito é a porta de entrada — mas qual é o plano B? Cupons em destaque? Dados? Premium?
5. **Zero marketing para o consumidor**: não há mecanismo de descoberta além de acessar o app diretamente.

**Hipótese de teste para o MVP**  
> *"Acreditamos que lojistas da Barra que publicarem cupons no Alow receberão clientes novos suficientes para recomendar a plataforma a outros lojistas. Saberemos que funcionou quando tivermos 3 lojistas reportando clientes novos vindos da plataforma em 30 dias."*

**Prioridade para lançamento**
1. Onboarding autônomo do lojista (cadastro + publicação de cupom sem admin)
2. Notificação WhatsApp ao lojista quando houver resgate
3. Dashboard básico do lojista (resgates por cupom)
4. Canal de descoberta para o consumidor (link compartilhável, QR code)

---

### 🏗️ Tech Lead

**Arquitetura atual (Base44)**  
O modelo de dados está bem estruturado para um MVP. A escolha de desnormalizar `company_name` em Coupon e Redemption é pragmática para leituras rápidas. A separação em 4 entidades (Company, Coupon, Customer, Redemption) é limpa.

**Problemas críticos identificados**

**1. Bug de sincronização — `redeemed_count` desatualizado**
```
Coupon "Brunch grátis na compra de 2" → redeemed_count: 0
Redemptions vinculadas ao mesmo cupom: 2 registros encontrados
```
O contador não está sendo incrementado corretamente. Risco: cupons "sold_out" nunca disparam, extrapolando `total_quantity`.

**2. Condição de corrida no limite de CPF**
O campo `cpf_limit` por cupom requer verificação + write atômico. Se dois resgates chegarem simultaneamente do mesmo CPF, ambos podem passar. Requer transação ou lock.

**3. Sem cascata de desativação**
Se uma Company vai para `status: inactive`, seus Coupons permanecem `active`. Um usuário pode resgatar cupom de empresa inativa.

**4. Dados desnormalizados sem mecanismo de sync**
`company_name` em Coupon e Redemption não atualiza automaticamente se a empresa mudar o nome.

**Decisões de arquitetura a tomar antes do escalonamento**
- Estratégia de validação de resgate: quem confirma o `used`? (lojista via app, QR, código verbal?)
- Autenticação do lojista: hoje é por `owner_email` mas sem login separado real
- Push notifications: infraestrutura para notificar lojista em tempo real

**Dívida técnica atual**: baixa — produto jovem, modelo limpo. Momento certo para corrigir antes de crescer.

---

### 🎨 UX/UI Designer

**Experiência do consumidor**

O fluxo de resgate tem 3 tipos diferentes, gerando experiência inconsistente:
- `fixed_code` → usuário vê o código e usa na hora (simples, sem fricção)
- `unique_code` → gera código ALOW-XXXXX (boa experiência, rastreável)
- `whatsapp` → redireciona para WhatsApp (depende do lojista responder)

**Problemas de UX identificados**

1. **Resgate via WhatsApp é uma caixa preta para o consumidor**: o usuário não sabe se vai receber resposta, em quanto tempo, e como usar o cupom depois.
2. **Sem histórico de cupons do consumidor**: depois de resgatar, onde o usuário vê seus resgates? Não há "carteira".
3. **Sem feedback de expiração**: o consumidor não sabe quando um cupom vai vencer até expirar.
4. **Experiência de descoberta fraca**: como o usuário chega ao app? Sem mecanismo de compartilhamento ou notificação.
5. **Formulário de cadastro do cliente**: campo `full_name` está aceitando CPF como nome (dado: `"full_name": "12289360706"`). Falta validação e UX que guie o usuário.

**Experiência do lojista**

1. Sem dashboard próprio — o lojista não tem visibilidade de performance
2. Sem notificação de resgate — não sabe quando alguém usou o cupom
3. Sem fluxo de validação — como o lojista confirma o `used`? Não está definido

**Recomendações de UX prioritárias**
- Tela "Meus Resgates" para o consumidor (carteira de cupons)
- Notificação de vencimento próximo (3 dias antes)
- Tela de validação para o lojista: digita ou scanneia código ALOW-XXXXX e marca como `used`
- Compartilhamento de cupom via link direto (deep link)

---

### 🔍 QA Engineer

**Bugs confirmados nos dados**

| # | Severidade | Bug | Evidência |
|---|-----------|-----|-----------|
| 1 | 🔴 Alto | `redeemed_count` não sincroniza com Redemptions reais | Brunch: 2 resgates, counter = 0 |
| 2 | 🔴 Alto | Campo `full_name` aceita CPF como nome (sem validação) | Customer `id: 6a0cf388...`, `full_name: "12289360706"` |
| 3 | 🟡 Médio | Redemptions com status `redeemed` nunca transitam para `used` | 3 resgates, nenhum `used` — fluxo de validação não existe |
| 4 | 🟡 Médio | Empresas sem `owner_email` mas com cupons ativos | 8 de 9 empresas sem dono definido |
| 5 | 🟢 Baixo | `end_date` vencida não muda status do cupom automaticamente | Verificar se há rotina de expiração |

**Casos de teste críticos a executar antes do lançamento**

**Fluxo 1 — Resgate com limite de CPF**
```gherkin
Dado que um cupom tem cpf_limit: 1
Quando o mesmo CPF tenta resgatar pela segunda vez
Então o sistema deve bloquear com mensagem clara
```

**Fluxo 2 — Resgate de cupom vencido**
```gherkin
Dado que um cupom tem end_date no passado
Quando um usuário tenta resgatar
Então o sistema deve impedir o resgate
```

**Fluxo 3 — Resgate até esgotamento**
```gherkin
Dado que um cupom tem total_quantity: 10
Quando o 10º resgate é feito
Então status deve mudar para sold_out
E o 11º resgate deve ser bloqueado
```

**Fluxo 4 — Validação pelo lojista**
```gherkin
Dado que um resgate existe com status: redeemed
Quando o lojista insere o código ALOW-XXXXX
Então o status deve mudar para used
E a data de used_date deve ser registrada
E validated_by deve ser preenchido
```

**Fluxo 5 — Dados obrigatórios do cliente**
```gherkin
Dado o formulário de resgate
Quando o usuário preenche full_name com apenas números
Então o sistema deve exibir erro de validação
```

**Cenários de borda a testar**
- Resgate simultâneo do mesmo CPF (race condition)
- Cupom com `total_quantity: 0` (ilimitado) — funciona corretamente?
- WhatsApp número inválido no campo `whatsapp` do lojista
- Cupom com `start_date` no futuro — aparece para o usuário?

---

### 🗄️ DBA / Data Architect

**Análise do modelo de dados**

O schema está funcional para MVP. Pontos de atenção:

**1. `redeemed_count` como campo calculado armazenado**
Manter um contador desnormalizado exige update atômico a cada resgate. Se o volume crescer, o risco de inconsistência aumenta. Alternativa: calcular na query com COUNT de Redemptions.

**2. CPF como chave de controle**
O CPF é usado para `cpf_limit` mas não tem unique constraint por cupom. Dois resgates do mesmo CPF no mesmo cupom podem coexistir se não houver validação na aplicação.

**3. Soft delete ausente**
Não há campo `deleted_at`. Empresas e cupons só têm `active/inactive` — sem histórico de exclusão.

**4. Ausência de índice explícito documentado**
Queries frequentes que precisam de índice:
- `Redemption` por `cpf + coupon_id` (verificação de limite)
- `Coupon` por `company_id + status` (listagem do lojista)
- `Redemption` por `unique_code` (validação pelo lojista)

---

## Roadmap de Melhorias (priorizado)

### Sprint 1 — Bugfix crítico (antes de qualquer divulgação)
- [ ] Corrigir sincronização do `redeemed_count`
- [ ] Adicionar validação de `full_name` (não aceitar apenas números)
- [ ] Implementar verificação de `cpf_limit` com proteção contra race condition
- [ ] Rotina de expiração automática de cupons vencidos

### Sprint 2 — Fluxo completo (fechar o ciclo lojista → consumidor)
- [ ] Tela de validação de resgate para o lojista (digitar/scanear código ALOW)
- [ ] Notificação WhatsApp ao lojista quando houver resgate
- [ ] Tela "Meus Resgates" para o consumidor
- [ ] Onboarding autônomo do lojista (cadastro sem precisar do admin)

### Sprint 3 — Crescimento
- [ ] Dashboard do lojista com métricas (resgates por dia, taxa de conversão)
- [ ] Compartilhamento de cupom via link direto
- [ ] Notificação de cupom prestes a vencer para o consumidor
- [ ] QR code por resgate para validação mais rápida

---

## Recomendação do Squad Dev para Lançamento

> ⚠️ **Não recomendamos divulgação pública antes de corrigir os bugs da Sprint 1.**  
> O `redeemed_count` desatualizado e a falta de validação de limite por CPF podem gerar experiências inconsistentes que prejudicam a credibilidade com os primeiros lojistas — que são os mais importantes para o boca a boca.

**Ação imediata sugerida**: fechar Sprint 1 (bugfix), fazer teste completo dos 5 fluxos críticos de QA, e só então divulgar para os primeiros lojistas parceiros.
