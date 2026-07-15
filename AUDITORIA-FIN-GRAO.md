# Auditoria do Fin Grão

**Data:** 15/07/2026
**Escopo:** app "Fin Grão" no Base44 (ID `6894d3815a2cf68ddfeb0bd9`) — entidades, páginas, componentes de relatório e funções de backend (recorrência e notificações).

---

## Resumo executivo

O Fin Grão está bem organizado para um sistema feito por quem não é da área: as entidades fazem sentido (Contas, Categorias, Transações, Contatos, Notificações), a interface é boa e os fluxos do dia a dia (lançar, pagar, filtrar por mês) funcionam.

O problema central é **um só, mas grave**: o sistema guarda o saldo das contas num campo (`Account.balance`) e tenta mantê-lo atualizado "na mão" a cada operação. Essa abordagem está implementada com falhas que **corrompem o saldo silenciosamente** com o uso normal do app. Além disso, **cada tela calcula o saldo de um jeito diferente**, então Dashboard, Contas e Lançamentos podem mostrar três números diferentes para a mesma coisa.

A boa notícia: a correção recomendada **remove código em vez de adicionar** — fica mais simples e mais confiável, que é exatamente o que você quer.

---

## 1. Erros graves (afetam os números que você vê)

### E1 — Saldo corrompido ao editar transações pagas (o mais grave)

Em `src/pages/Transactions.jsx`, a função `updateAccountBalance` lê o saldo da conta **da memória da tela** (estado React carregado no início), não do banco. Ao editar o valor de uma transação já paga, o fluxo é:

1. "Reverter" o valor antigo → grava `saldo_antigo + 100` no banco.
2. "Aplicar" o valor novo → lê **de novo o saldo da memória** (que ainda é o antigo, sem a reversão) e grava `saldo_antigo - 50`.

O passo 2 **apaga** o passo 1. Exemplo: saldo R$ 900, despesa paga de R$ 100 editada para R$ 50. O correto seria R$ 950; o sistema grava **R$ 850**. Isso acontece em: edição de valor/tipo (`handleFieldUpdate`, `handleMultiFieldUpdate`, `handleSubmit`), e é ainda pior nas **operações em massa** (`handleBulkStatusChange`, `confirmBulkDelete`, edição "esta e futuras"), onde várias transações da mesma conta são processadas em loop sobre o mesmo saldo desatualizado — só o efeito da última sobrevive.

**Consequência:** cada edição/exclusão em massa deixa o saldo salvo um pouco mais errado, sem nenhum aviso.

### E2 — Três "verdades" diferentes para o saldo

- **Dashboard** (`Dashboard.jsx`): usa o campo salvo `account.balance` (que corrompe, ver E1).
- **Contas** (`Accounts.jsx`): ignora o campo salvo e **recalcula** somando as transações pagas/recebidas.
- **Lançamentos** (card "Caixa"): usa o campo salvo de novo.

Resultado: o mesmo saldo aparece com valores diferentes dependendo da tela. Não é impressão sua — é estrutural.

### E3 — "Ajuste de saldo" conta em dobro

`Accounts.jsx > handleAdjustBalanceSave` cria **uma transação paga** de ajuste **e também** soma o valor no campo `balance`. A tela de Contas conta a transação; o Dashboard conta o campo. O ajuste vale em dobro no total do sistema. Detalhes menores no mesmo fluxo: a observação vem fixa como "Ajuste de saldo para 2025", e a categoria "Ajuste de Saldo" é criada com o tipo (receita/despesa) do primeiro ajuste e reutilizada para sempre, mesmo quando o ajuste seguinte é do tipo oposto.

### E4 — Saldo manual não tem efeito na tela de Contas

O diálogo "saldo manual" grava `balance`, mas a própria tela de Contas recalcula tudo a partir das transações e **sobrescreve o que você digitou na exibição**. O valor manual só aparece no Dashboard. Confusão garantida.

### E5 — Recorrências: contagem dupla e duplicação ao regenerar

Em `base44/functions/generateRecurringOccurrences/entry.ts`:

- A transação "pai" (modelo da recorrência) **é uma transação normal no banco** e a primeira ocorrência é gerada **na mesma data do pai**. Nenhuma tela ou relatório exclui o pai (`is_recurring: true`) dos somatórios → **o primeiro mês conta em dobro**.
- `next_occurrence_date` é atualizado para a data da **última ocorrência gerada** (e não a próxima após ela). Como o gerador começa **em** `next_occurrence_date` (inclusive), clicar em "Gerar" de novo (botão em Transações Recorrentes) **duplica a última ocorrência** e cria mais 12 meses.
- Recorrência mensal com dia 29–31: o código faz `setMonth(+1)` antes de ajustar o dia; 31/jan vira 3/mar e depois "31/mar" — **fevereiro é pulado**.
- Se o pai não tiver `due_date`, `new Date(undefined)` gera data inválida e **nenhuma ocorrência é criada**, sem mensagem de erro.
- Detalhe: `toast.warning(...)` não existe no react-hot-toast — se a geração falhar, o próprio aviso de erro quebra.

### E6 — Dashboard calcula o mês com só 100 transações

`Dashboard.jsx` carrega `Transaction.list("-date", 100)`. Receitas/despesas do mês e o gráfico de 6 meses são calculados só sobre essas 100. Com volume de empresa, os números do Dashboard **ficam menores que a realidade** — e o gráfico de 6 meses fica cada vez mais furado nos meses antigos.

### E7 — Fuso horário: lançamentos do dia 1º caem no mês errado

Dashboard, CashFlowChart e relatórios usam `new Date(t.date)` (interpretado como meia-noite **UTC**) e comparam com `startOfMonth` (horário **local**, Brasil = UTC-3). Efeito prático: transação datada de 01/07 é tratada como 30/06 21h → **sai do mês de julho**; e uma de 01/08 **entra em julho**. A tela de Lançamentos não tem esse problema porque usa `+ 'T00:00:00'` — ou seja, os meses de Lançamentos e do Dashboard **não batem entre si**.

### E8 — Relatório de Patrimônio soma tudo em dobro

`NetWorthReport.jsx` parte do **saldo atual** das contas e vai **somando por cima todo o fluxo histórico** de receitas/despesas — mas o saldo atual **já contém** esse histórico. O "Patrimônio Atual" mostrado é aproximadamente `saldo real + tudo que você já movimentou`, um número sem significado. Também conta transações **pendentes** como se fossem dinheiro realizado.

### E9 — Evolução do Saldo: saldo inicial errado com filtros

`BalanceEvolutionReport.jsx` estima o saldo inicial como `saldo atual das contas − impacto das transações filtradas`. Como o cálculo usa as transações **já filtradas** (período/conta/categoria) e inclui **pendentes**, o "Saldo Inicial" e o "Saldo Atual" do relatório só batem com a realidade por coincidência. Transferências também são ignoradas, o que distorce quando há filtro por conta.

### E10 — Cada relatório usa um "regime" diferente sem avisar

- **Receitas × Despesas** e **Patrimônio**: somam tudo, **incluindo pendentes** (parece realizado, mas é projeção).
- **DRE**: só pagas/recebidas (regime de caixa).
- **Fluxo de Caixa (Dashboard)**: tudo menos canceladas.
- **Filtro de datas dos Relatórios**: usa `date` (lançamento); a tela de Lançamentos usa `payment_date` (pagamento).

Comparar duas telas do próprio sistema dá números diferentes — e mina a confiança no app inteiro.

### E11 — Cartão de crédito tratado como conta comum

`Account.type` aceita `credit_card`, mas não existe conceito de fatura/limite/dívida. No Balanço, o "saldo" do cartão entra como **ativo** (dinheiro), quando na prática é passivo. Para uso simples, melhor lançar despesas de cartão como despesas normais e remover o tipo, ou aceitar a limitação de forma consciente.

### E12 — Excluir conta ou categoria não protege o histórico

Excluir uma conta com transações deixa lançamentos órfãos ("Conta não encontrada" nos relatórios/CSV) e o saldo some dos totais sem aviso.

---

## 2. Pontos de melhora (não são bugs, mas atrapalham)

1. **Conta padrão "Inter" fixa no código** (`Transactions.jsx`): o filtro inicial procura uma conta com "inter" no nome. Se renomear a conta, o comportamento muda. Melhor: guardar a preferência do usuário ou usar "todas".
2. **Criação de categoria como efeito colateral**: abrir a tela de Lançamentos cria a categoria "Transferência" se não existir (tipo fixo "despesa"). Funciona, mas é surpreendente — e se você apagar a categoria, ela renasce.
3. **CSV sem BOM UTF-8**: no Excel brasileiro, "Descrição" vira "DescriÃ§Ã£o". Basta prefixar o arquivo com `﻿`. O decimal com ponto (`1234.56`) também confunde o Excel pt-BR — ideal exportar com `;` como separador e vírgula decimal.
4. **Operações em massa uma a uma**: cada item faz 2–3 chamadas sequenciais ao banco. Com 50 selecionadas, são ~150 requisições. Depois de resolver E1, dá para usar `bulkCreate`/atualizações em paralelo.
5. **Nomenclatura contábil ambiciosa demais**: "DRE" e "Balanço Patrimonial" têm significado técnico (regime de competência, passivos completos). Como estão, são aproximações. Sugestão simples: renomear para "Resultado do Período" e "Posição Financeira" — entrega o mesmo valor sem prometer contabilidade formal.
6. **`Transaction.list()` sem limite explícito** nas telas de Lançamentos/Relatórios: confirme qual é o limite padrão do SDK do Base44; se houver teto (ex.: 1000 registros), relatórios anuais vão truncar silenciosamente no futuro.
7. **Notificações**: `generateDueNotifications` usa `settings[0]` sem filtrar por usuário e, quando roda agendada (service role), varre transações de todos os usuários do app. Para uso pessoal/single-user está OK; se um dia houver mais gente no app, precisa revisar.

---

## 3. A correção que resolve quase tudo (e simplifica o app)

**Pare de armazenar saldo. Calcule sempre.**

- Adicionar campo `initial_balance` (saldo inicial) em `Account`.
- **Apagar** `updateAccountBalance` e todas as suas chamadas (são ~15 pontos de código frágil).
- Saldo de qualquer conta = `initial_balance + Σ transações pagas/recebidas da conta` (transferência: sai da origem, entra no destino) — exatamente o cálculo que a tela de Contas já faz hoje.
- Criar **uma função utilitária única** (ex.: `computeBalances(accounts, transactions)`) usada por Dashboard, Contas, Lançamentos e Relatórios.

Efeitos: E1, E2, E3 e E4 desaparecem por construção (não existe mais campo para corromper), o código fica menor, e o saldo passa a ser sempre reconstruível a partir do histórico — que é o comportamento de qualquer sistema financeiro sério.

## 4. Plano sugerido, em ordem

| Fase | O quê | Resolve |
|------|-------|---------|
| 1 | Saldo calculado (item 3 acima) | E1–E4 |
| 2 | Datas: usar sempre `data + 'T00:00:00'` (ou comparar strings `yyyy-MM-dd`) em Dashboard/relatórios; padronizar regime: telas de caixa usam `payment_date`, projeções usam `due_date` — com etiqueta "Realizado × Projetado" | E7, E10 |
| 3 | Recorrência: excluir pais (`is_recurring: true`) de todos os somatórios; `next_occurrence_date` = dia **seguinte** à última gerada; corrigir regra do dia 29–31; validar `due_date` obrigatório para recorrentes | E5 |
| 4 | Dashboard: carregar transações do período necessário (6 meses) sem limite de 100 | E6 |
| 5 | Refazer Patrimônio e Evolução do Saldo em cima da função única de saldo | E8, E9 |
| 6 | Proteções: impedir excluir conta/categoria com lançamentos (ou arquivar em vez de excluir) | E12 |
| 7 | Polimentos: CSV com BOM, remover "Inter" fixo, renomear DRE/Balanço, revisar cartão de crédito | E11 + melhorias |

---

*Auditoria gerada por análise estática do código; nenhuma alteração foi feita no app.*
