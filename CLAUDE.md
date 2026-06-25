# Google Ads MCC — Assistente IA

Este projeto conecta o Claude Code à sua conta MCC do Google Ads via MCP Server.
O Claude pode analisar, gerir e otimizar campanhas diretamente pelo chat.

## Ferramentas disponíveis

| Ferramenta | O que faz |
|---|---|
| `verificar_conexao` | Testa se as credenciais estão funcionando |
| `listar_contas` | Lista todas as contas da MCC |
| `resumo_conta` | Métricas consolidadas de uma conta |
| `resumo_executivo` | Visão geral: top campanhas, pior CPA, médias globais |
| `listar_campanhas` | Campanhas com gasto, CTR, conversões |
| `listar_grupos_anuncios` | Grupos de anúncios com métricas |
| `listar_anuncios` | Anúncios com headlines e performance |
| `listar_palavras_chave` | Keywords com Quality Score |
| `termos_de_busca` | Queries reais dos usuários |
| `analisar_oportunidades` | Detecta campanhas limitadas por budget, sem conversão, CTR baixo |
| `sugerir_palavras_negativas` | Analisa termos e sugere negativos com maior impacto |
| `analisar_quality_score` | Auditoria de QS com recomendações de melhoria |
| `adicionar_palavras_negativas` | Bloqueia tráfego irrelevante |
| `atualizar_budget` | Muda orçamento diário |
| `pausar_campanha` | Pausa campanha ativa |
| `ativar_campanha` | Reativa campanha pausada |
| `relatorio_performance` | Performance diária/semanal |
| `relatorio_conversoes` | Ações de conversão e custos |
| `relatorio_campanhas_detalhado` | Impression share e lost IS |

## Configuração inicial

Siga o guia passo a passo em **SETUP_GOOGLE.md** para obter as credenciais.

### Instalação rápida
```bash
pip install -r requirements.txt
cp .env.example .env
# preencha o .env com as credenciais (veja SETUP_GOOGLE.md)
python setup_auth.py     # gera o refresh_token
python test_connection.py  # verifica se tudo está ok
```

## Exemplos de uso no chat

**Visão geral e diagnóstico:**
```
"Faça um resumo executivo dos últimos 30 dias da conta 1234567890"
"Onde estou desperdiçando dinheiro nessa conta?"
"Quais campanhas têm mais oportunidade de impression share?"
```

**Otimização de palavras-chave:**
```
"Analise os termos de busca da campanha 456 e me diga o que negativar"
"Quais são as palavras com Quality Score abaixo de 5?"
"Adicione esses termos como negativos: [lista]"
```

**Gestão de campanhas:**
```
"Liste todas as campanhas com CPC acima de R$5 e CTR abaixo de 2%"
"Pause as campanhas que gastaram mais de R$200 sem nenhuma conversão"
"Atualize o budget da campanha 789 para R$150/dia"
```

**Análise de performance:**
```
"Mostre o desempenho semana a semana dos últimos 90 dias"
"Qual campanha tem o melhor custo por conversão este mês?"
"Compare o desempenho deste mês com o mês passado"
```

## Períodos de data disponíveis

- `TODAY`, `YESTERDAY`
- `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_90_DAYS`
- `THIS_MONTH`, `LAST_MONTH`
- `THIS_YEAR`, `LAST_YEAR`
