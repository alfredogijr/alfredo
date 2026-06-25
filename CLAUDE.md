# Google Ads MCC — Assistente IA

Este projeto conecta o Claude Code à sua conta MCC do Google Ads via MCP Server.
O Claude pode analisar, gerir e otimizar campanhas diretamente pelo chat.

## Ferramentas disponíveis

| Ferramenta | O que faz |
|---|---|
| `listar_contas` | Lista todas as contas da MCC |
| `resumo_conta` | Métricas consolidadas de uma conta |
| `listar_campanhas` | Campanhas com gasto, CTR, conversões |
| `listar_grupos_anuncios` | Grupos de anúncios com métricas |
| `listar_anuncios` | Anúncios com headlines e performance |
| `listar_palavras_chave` | Keywords com Quality Score |
| `termos_de_busca` | Queries reais dos usuários |
| `adicionar_palavras_negativas` | Bloqueia tráfego irrelevante |
| `atualizar_budget` | Muda orçamento diário |
| `pausar_campanha` | Pausa campanha ativa |
| `ativar_campanha` | Reativa campanha pausada |
| `relatorio_performance` | Performance diária/semanal |
| `relatorio_conversoes` | Ações de conversão e custos |
| `relatorio_campanhas_detalhado` | Impression share e lost IS |

## Configuração inicial

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Criar o arquivo .env
```bash
cp .env.example .env
```

### 3. Obter credenciais da Google Ads API

**Developer Token:**
1. Acesse [Google Ads API Center](https://developers.google.com/google-ads/api/docs/get-started/introduction)
2. No Google Ads → Ferramentas → API Center → solicite acesso

**OAuth2 Credentials:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um projeto → Ative a "Google Ads API"
3. Credenciais → Criar → OAuth 2.0 → Aplicativo de computador
4. Baixe o `client_secret.json`

**Gerar Refresh Token:**
```bash
python setup_auth.py
```

### 4. Preencher o .env
```env
GOOGLE_ADS_DEVELOPER_TOKEN=xxxxx
GOOGLE_ADS_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=xxxxx
GOOGLE_ADS_REFRESH_TOKEN=xxxxx
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
```

## Exemplos de uso no chat

```
"Liste todas as contas da minha MCC"
"Mostre o desempenho dos últimos 7 dias da conta 1234567890"
"Quais campanhas têm CPC acima de R$5 e menos de 2% CTR?"
"Analise os termos de busca da campanha 456 e sugira negativos"
"Pause todas as campanhas com custo por conversão acima de R$100"
"Qual campanha tem a maior oportunidade de impression share?"
```

## Períodos de data disponíveis

- `TODAY`, `YESTERDAY`
- `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_90_DAYS`
- `THIS_MONTH`, `LAST_MONTH`
- `THIS_YEAR`, `LAST_YEAR`
