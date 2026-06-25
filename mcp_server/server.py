"""
Google Ads MCC - MCP Server
Expõe ferramentas do Google Ads para o Claude Code.
"""
import json
import sys
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from mcp_server.auth import get_client, get_login_customer_id
from mcp_server.tools import accounts, campaigns, keywords, reports, ads, optimization

app = Server("google-ads-mcc")


def _ok(data: Any) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]


def _err(msg: str) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=f"ERRO: {msg}")]


# ── Tool definitions ──────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="listar_contas",
            description="Lista todas as contas gerenciadas pela MCC com status, moeda e timezone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mcc_id": {
                        "type": "string",
                        "description": "ID da MCC (deixe em branco para usar a padrão do .env)",
                    }
                },
            },
        ),
        types.Tool(
            name="resumo_conta",
            description="Retorna métricas consolidadas de uma conta: gasto, impressões, cliques, conversões, CTR, CPC médio e custo por conversão.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "ID da conta cliente"},
                    "date_range": {
                        "type": "string",
                        "description": "Período: LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS, THIS_MONTH, LAST_MONTH",
                        "default": "LAST_30_DAYS",
                    },
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="listar_campanhas",
            description="Lista campanhas de uma conta com métricas de performance (gasto, CTR, conversões, impression share).",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "ID da conta cliente"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="listar_grupos_anuncios",
            description="Lista grupos de anúncios com métricas. Filtra opcionalmente por campanha.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "ID da conta cliente"},
                    "campaign_id": {"type": "string", "description": "ID da campanha (opcional)"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="listar_anuncios",
            description="Lista anúncios com performance. Retorna headlines, descriptions e métricas.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string", "description": "Filtrar por campanha (opcional)"},
                    "ad_group_id": {"type": "string", "description": "Filtrar por grupo (opcional)"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="listar_palavras_chave",
            description="Lista palavras-chave com Quality Score, tipo de correspondência e métricas de performance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string", "description": "Filtrar por campanha (opcional)"},
                    "ad_group_id": {"type": "string", "description": "Filtrar por grupo (opcional)"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                    "limit": {"type": "integer", "default": 100, "description": "Máximo de palavras a retornar"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="termos_de_busca",
            description="Relatório de termos de busca: mostra as queries reais que ativaram seus anúncios. Útil para encontrar negativos e oportunidades.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string", "description": "Filtrar por campanha (opcional)"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                    "limit": {"type": "integer", "default": 100},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="adicionar_palavras_negativas",
            description="Adiciona palavras-chave negativas a uma campanha para evitar tráfego irrelevante.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string"},
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de palavras a tornar negativas",
                    },
                    "match_type": {
                        "type": "string",
                        "enum": ["BROAD", "PHRASE", "EXACT"],
                        "default": "BROAD",
                    },
                },
                "required": ["customer_id", "campaign_id", "keywords"],
            },
        ),
        types.Tool(
            name="atualizar_budget",
            description="Atualiza o orçamento diário de uma campanha.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string"},
                    "novo_budget": {"type": "number", "description": "Novo orçamento diário em reais (R$)"},
                },
                "required": ["customer_id", "campaign_id", "novo_budget"],
            },
        ),
        types.Tool(
            name="pausar_campanha",
            description="Pausa uma campanha ativa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string"},
                },
                "required": ["customer_id", "campaign_id"],
            },
        ),
        types.Tool(
            name="ativar_campanha",
            description="Ativa uma campanha pausada.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string"},
                },
                "required": ["customer_id", "campaign_id"],
            },
        ),
        types.Tool(
            name="relatorio_performance",
            description="Relatório de performance por dia ou semana. Ótimo para análise de tendências.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                    "segment_by": {
                        "type": "string",
                        "enum": ["day", "week"],
                        "default": "day",
                    },
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="relatorio_conversoes",
            description="Relatório de ações de conversão: quais conversões estão sendo geradas e a que custo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="relatorio_campanhas_detalhado",
            description="Relatório diário por campanha com impression share e lost IS. Ideal para identificar onde o budget ou quality score estão limitando.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        # ── Optimization tools ─────────────────────────────────────────────
        types.Tool(
            name="resumo_executivo",
            description="Resumo executivo completo da conta: top campanhas por gasto e conversão, pior CPA, médias globais. Bom ponto de partida para qualquer análise.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="analisar_oportunidades",
            description="Identifica automaticamente: campanhas limitadas por budget, campanhas sem conversão gastando dinheiro, campanhas com CTR baixo e CPC alto.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="sugerir_palavras_negativas",
            description="Analisa termos de busca e retorna candidatos a palavras negativas: termos com cliques mas zero conversão, e termos com CTR muito baixo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string", "description": "Filtrar por campanha (opcional)"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                    "min_clicks": {
                        "type": "integer",
                        "default": 3,
                        "description": "Mínimo de cliques sem conversão para sinalizar o termo",
                    },
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="analisar_quality_score",
            description="Auditoria de Quality Score: distribuição por faixa, palavras críticas (QS < 5) com maior gasto, e recomendações de melhoria.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "campaign_id": {"type": "string", "description": "Filtrar por campanha (opcional)"},
                    "date_range": {"type": "string", "default": "LAST_30_DAYS"},
                },
                "required": ["customer_id"],
            },
        ),
        types.Tool(
            name="verificar_conexao",
            description="Verifica se as credenciais estão corretas e a conexão com a API do Google Ads está funcionando.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


# ── Tool handler ──────────────────────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        client = get_client()
        mcc_id = get_login_customer_id()

        match name:
            case "listar_contas":
                cid = arguments.get("mcc_id", mcc_id)
                return _ok(accounts.list_accounts(client, cid))

            case "resumo_conta":
                return _ok(accounts.get_account_summary(
                    client,
                    arguments["customer_id"],
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "listar_campanhas":
                return _ok(campaigns.list_campaigns(
                    client,
                    arguments["customer_id"],
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "listar_grupos_anuncios":
                return _ok(campaigns.list_ad_groups(
                    client,
                    arguments["customer_id"],
                    arguments.get("campaign_id"),
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "listar_anuncios":
                return _ok(ads.list_ads(
                    client,
                    arguments["customer_id"],
                    arguments.get("campaign_id"),
                    arguments.get("ad_group_id"),
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "listar_palavras_chave":
                return _ok(keywords.list_keywords(
                    client,
                    arguments["customer_id"],
                    arguments.get("campaign_id"),
                    arguments.get("ad_group_id"),
                    arguments.get("date_range", "LAST_30_DAYS"),
                    arguments.get("limit", 100),
                ))

            case "termos_de_busca":
                return _ok(keywords.get_search_terms(
                    client,
                    arguments["customer_id"],
                    arguments.get("campaign_id"),
                    arguments.get("date_range", "LAST_30_DAYS"),
                    arguments.get("limit", 100),
                ))

            case "adicionar_palavras_negativas":
                result = keywords.add_negative_keywords(
                    client,
                    arguments["customer_id"],
                    arguments["campaign_id"],
                    arguments["keywords"],
                    arguments.get("match_type", "BROAD"),
                )
                return _ok({"resultado": result})

            case "atualizar_budget":
                result = campaigns.update_campaign_budget(
                    client,
                    arguments["customer_id"],
                    arguments["campaign_id"],
                    arguments["novo_budget"],
                )
                return _ok({"resultado": result})

            case "pausar_campanha":
                result = campaigns.pause_campaign(
                    client,
                    arguments["customer_id"],
                    arguments["campaign_id"],
                )
                return _ok({"resultado": result})

            case "ativar_campanha":
                result = campaigns.enable_campaign(
                    client,
                    arguments["customer_id"],
                    arguments["campaign_id"],
                )
                return _ok({"resultado": result})

            case "relatorio_performance":
                return _ok(reports.get_performance_report(
                    client,
                    arguments["customer_id"],
                    arguments.get("date_range", "LAST_30_DAYS"),
                    arguments.get("segment_by", "day"),
                ))

            case "relatorio_conversoes":
                return _ok(reports.get_conversion_report(
                    client,
                    arguments["customer_id"],
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "relatorio_campanhas_detalhado":
                return _ok(reports.get_campaign_performance_report(
                    client,
                    arguments["customer_id"],
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "resumo_executivo":
                return _ok(optimization.resumo_executivo(
                    client,
                    arguments["customer_id"],
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "analisar_oportunidades":
                return _ok(optimization.analisar_oportunidades(
                    client,
                    arguments["customer_id"],
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "sugerir_palavras_negativas":
                return _ok(optimization.sugerir_palavras_negativas(
                    client,
                    arguments["customer_id"],
                    arguments.get("campaign_id"),
                    arguments.get("date_range", "LAST_30_DAYS"),
                    arguments.get("min_clicks", 3),
                ))

            case "analisar_quality_score":
                return _ok(optimization.analisar_quality_score(
                    client,
                    arguments["customer_id"],
                    arguments.get("campaign_id"),
                    arguments.get("date_range", "LAST_30_DAYS"),
                ))

            case "verificar_conexao":
                accs = accounts.list_accounts(client, mcc_id)
                return _ok({
                    "status": "conectado",
                    "mcc_id": mcc_id,
                    "contas_encontradas": len(accs),
                })

            case _:
                return _err(f"Ferramenta desconhecida: {name}")

    except EnvironmentError as e:
        return _err(str(e))
    except Exception as e:
        return _err(f"{type(e).__name__}: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
