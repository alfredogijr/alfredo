# Fluxo: Produção Mensal de Conteúdo

Sequência completa do calendário à publicação para qualquer cliente.

## Visão Geral

```
Início do mês         Toda semana            Aprovação              Publicação
[Estrategista]  →    [Criador]         →    [Editor]          →    [Gestor]
Calendário           Pautas + legendas       Revisão + WL           Pacote final
```

---

## Fase 1: Planejamento (uma vez por mês)

**Agente**: Estrategista  
**Quando**: Últimos dias do mês anterior ou primeiro dia do mês  
**Entrega**: Calendário editorial aprovado

**Prompt**: Ver `agentes/01-estrategista.md`

**Critério de saída**: Calendário com 12 posts, 1 campanha temática e 3 ideias de stories aprovados por você.

---

## Fase 2: Produção Semanal

**Agente**: Criador de Conteúdo  
**Quando**: Segunda-feira de cada semana  
**Entrega**: Pautas → aprovação → legendas + briefings criativos

### Passo 2a — Pautas
Solicite as pautas dos posts da semana e aprove antes de continuar.

```
Se aprovado tudo → "Aprovado. Pode escrever todas as legendas."
Se mudar algo   → "Post 2: troca o ângulo para [X]. Aprovado o resto."
Se mudar tema   → "Post 2 não faz sentido. Troca por [tema]. Refaz a pauta."
```

### Passo 2b — Produção
Após aprovação, solicite legendas + material criativo.

**Critério de saída**: Legendas escritas com briefing criativo para cada post.

---

## Fase 3: Revisão e White Label

**Agente**: Editor de Copy  
**Quando**: Após legendas produzidas  
**Entrega**: Legendas revisadas + versões white label (quando aplicável)

**Prompt**: Ver `agentes/03-editor-copy.md`

**Critério de saída**: Copy revisada e aprovada. White label gerado para todos os posts que serão distribuídos para parceiros.

---

## Fase 4: Organização e Publicação

**Agente**: Gestor de Calendário  
**Quando**: Antes de publicar / enviar para parceiros  
**Entrega**: Checklist completo + pacote WhatsApp

**Critério de saída**: Todos os posts com criativo confirmado, agendados, pacote enviado para parceiros.

---

## Checklist por Semana

```
[ ] Calendário aprovado (fase 1, feito uma vez)
[ ] Pautas da semana aprovadas
[ ] Legendas escritas e revisadas
[ ] Briefing criativo feito para cada post
[ ] Versão white label gerada (se aplicável)
[ ] Pacote semanal consolidado
[ ] Enviado para parceiros (se aplicável)
[ ] Posts agendados
```

---

## Adaptação para Clientes sem Parceiros

Se o cliente não tem distribuição white label, pule a Fase 3 (Editor de White Label) e vá direto do Criador para o Gestor.

```
Estrategista → Criador → Gestor → Publicação
```
