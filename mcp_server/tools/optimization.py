"""
AI-powered optimization analysis tools.
These tools analyze data and return structured insights for the Claude to interpret.
"""
from google.ads.googleads.client import GoogleAdsClient
from mcp_server.tools.keywords import get_search_terms, list_keywords
from mcp_server.tools.campaigns import list_campaigns
from mcp_server.tools.reports import get_campaign_performance_report


def analisar_oportunidades(client: GoogleAdsClient, customer_id: str, date_range: str = "LAST_30_DAYS") -> dict:
    """
    Full account analysis: finds budget waste, IS opportunities,
    keyword quality issues, and search term gaps.
    """
    result = {}

    # --- 1. Campaigns losing IS due to budget ---
    camp_data = list_campaigns(client, customer_id, date_range)
    budget_limited = [
        c for c in camp_data
        if c.get("budget_lost_is", 0) > 10 and c["status"] == "ENABLED"
    ] if camp_data and "budget_lost_is" in (camp_data[0] if camp_data else {}) else []

    rank_limited = [
        c for c in camp_data
        if c.get("rank_lost_is", 0) > 15 and c["status"] == "ENABLED"
    ] if camp_data and "rank_lost_is" in (camp_data[0] if camp_data else {}) else []

    result["campanhas_limitadas_budget"] = [
        {
            "id": c["id"],
            "nome": c["name"],
            "budget_diario": c["budget"],
            "is_perdido_budget": c.get("impression_share", 0),
            "custo_total": c["cost"],
        }
        for c in budget_limited
    ]

    result["campanhas_limitadas_qualidade"] = [
        {
            "id": c["id"],
            "nome": c["name"],
            "is_perdido_rank": c.get("rank_lost_is", 0),
            "avg_cpc": c["avg_cpc"],
        }
        for c in rank_limited
    ]

    # --- 2. Campaigns spending with zero conversions ---
    zero_conv = [
        c for c in camp_data
        if c["cost"] > 50 and c["conversions"] == 0 and c["status"] == "ENABLED"
    ]
    result["campanhas_sem_conversao"] = [
        {"id": c["id"], "nome": c["name"], "custo": c["cost"], "cliques": c["clicks"]}
        for c in zero_conv
    ]

    # --- 3. High CPC, low CTR campaigns ---
    low_perf = [
        c for c in camp_data
        if c["clicks"] > 20 and c["ctr"] < 2.0 and c["avg_cpc"] > 3.0 and c["status"] == "ENABLED"
    ]
    result["campanhas_ctr_baixo"] = [
        {"id": c["id"], "nome": c["name"], "ctr": c["ctr"], "avg_cpc": c["avg_cpc"], "custo": c["cost"]}
        for c in low_perf
    ]

    # --- 4. Summary ---
    total_cost = sum(c["cost"] for c in camp_data)
    total_conv = sum(c["conversions"] for c in camp_data)
    result["resumo"] = {
        "total_campanhas": len(camp_data),
        "campanhas_ativas": sum(1 for c in camp_data if c["status"] == "ENABLED"),
        "gasto_total": round(total_cost, 2),
        "total_conversoes": round(total_conv, 1),
        "custo_medio_por_conversao": round(total_cost / total_conv, 2) if total_conv > 0 else 0,
        "periodo": date_range,
    }

    return result


def sugerir_palavras_negativas(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str | None = None,
    date_range: str = "LAST_30_DAYS",
    min_clicks: int = 3,
    max_conversions: float = 0,
) -> dict:
    """
    Analyze search terms and flag candidates for negative keywords:
    - Clicked but zero conversions (above min_clicks threshold)
    - Terms with very low CTR
    - Branded terms in non-brand campaigns (heuristic)
    """
    terms = get_search_terms(client, customer_id, campaign_id, date_range, limit=200)

    wasted_spend = [
        t for t in terms
        if t["clicks"] >= min_clicks and t["conversions"] <= max_conversions and t["cost"] > 0
    ]
    wasted_spend.sort(key=lambda x: x["cost"], reverse=True)

    low_ctr = [
        t for t in terms
        if t["impressions"] > 50 and t["ctr"] < 1.0 and t["clicks"] == 0
    ]
    low_ctr.sort(key=lambda x: x["impressions"], reverse=True)

    return {
        "candidatos_negativos_por_gasto": [
            {
                "termo": t["search_term"],
                "custo_desperdicado": t["cost"],
                "cliques": t["clicks"],
                "conversoes": t["conversions"],
                "campanha": t["campaign"],
                "grupo": t["ad_group"],
            }
            for t in wasted_spend[:50]
        ],
        "candidatos_negativos_por_ctr": [
            {
                "termo": t["search_term"],
                "impressoes": t["impressions"],
                "ctr": t["ctr"],
                "campanha": t["campaign"],
            }
            for t in low_ctr[:30]
        ],
        "total_gasto_desperdicado": round(sum(t["cost"] for t in wasted_spend), 2),
        "total_termos_analisados": len(terms),
    }


def analisar_quality_score(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str | None = None,
    date_range: str = "LAST_30_DAYS",
) -> dict:
    """
    Quality Score audit: find keywords below threshold and classify by component.
    """
    kws = list_keywords(client, customer_id, campaign_id, None, date_range, limit=500)

    scored = [k for k in kws if isinstance(k["quality_score"], int)]
    below_5 = [k for k in scored if k["quality_score"] < 5]
    below_7 = [k for k in scored if 5 <= k["quality_score"] < 7]
    good = [k for k in scored if k["quality_score"] >= 7]

    avg_qs = round(sum(k["quality_score"] for k in scored) / len(scored), 1) if scored else 0

    return {
        "media_quality_score": avg_qs,
        "total_palavras_analisadas": len(scored),
        "distribuicao": {
            "critico_abaixo_5": len(below_5),
            "regular_5_a_6": len(below_7),
            "bom_7_ou_mais": len(good),
        },
        "palavras_criticas": [
            {
                "keyword": k["keyword"],
                "match_type": k["match_type"],
                "quality_score": k["quality_score"],
                "cost": k["cost"],
                "clicks": k["clicks"],
                "ad_group": k["ad_group_name"],
                "campaign": k["campaign_name"],
            }
            for k in sorted(below_5, key=lambda x: x["cost"], reverse=True)[:20]
        ],
        "recomendacoes": _qs_recommendations(avg_qs, len(below_5), len(scored)),
    }


def _qs_recommendations(avg_qs: float, critical_count: int, total: int) -> list[str]:
    recs = []
    if avg_qs < 5:
        recs.append("QS médio crítico — revise a relevância dos anúncios em relação às palavras-chave.")
        recs.append("Reorganize grupos de anúncios com temas mais específicos (SKAGs ou STAGs).")
    if avg_qs < 7:
        recs.append("Melhore os headlines dos anúncios para incluir a palavra-chave principal.")
        recs.append("Verifique se as landing pages carregam rápido e têm o conteúdo esperado pelo usuário.")
    if critical_count > total * 0.3:
        recs.append(f"{critical_count} palavras com QS < 5 — pause as de menor volume e foque nas que têm histórico de cliques.")
    if not recs:
        recs.append("Quality Scores dentro do esperado. Continue monitorando CTR esperado e relevância dos anúncios.")
    return recs


def resumo_executivo(client: GoogleAdsClient, customer_id: str, date_range: str = "LAST_30_DAYS") -> dict:
    """Top-level executive summary comparing key metrics."""
    camps = list_campaigns(client, customer_id, date_range)
    if not camps:
        return {"erro": "Nenhuma campanha encontrada para o período."}

    ativas = [c for c in camps if c["status"] == "ENABLED"]
    pausadas = [c for c in camps if c["status"] == "PAUSED"]

    total_gasto = sum(c["cost"] for c in camps)
    total_conv = sum(c["conversions"] for c in camps)
    total_clicks = sum(c["clicks"] for c in camps)
    total_impressions = sum(c["impressions"] for c in camps)

    top_spenders = sorted(camps, key=lambda x: x["cost"], reverse=True)[:5]
    top_converters = sorted(camps, key=lambda x: x["conversions"], reverse=True)[:5]
    worst_cpa = [c for c in camps if c["conversions"] > 0]
    worst_cpa.sort(key=lambda x: x["cost_per_conversion"], reverse=True)

    return {
        "periodo": date_range,
        "gasto_total": round(total_gasto, 2),
        "total_conversoes": round(total_conv, 1),
        "cpa_medio": round(total_gasto / total_conv, 2) if total_conv > 0 else 0,
        "total_cliques": total_clicks,
        "total_impressoes": total_impressions,
        "ctr_medio": round(total_clicks / total_impressions * 100, 2) if total_impressions > 0 else 0,
        "campanhas_ativas": len(ativas),
        "campanhas_pausadas": len(pausadas),
        "top_5_por_gasto": [
            {"nome": c["name"], "gasto": c["cost"], "conversoes": c["conversions"], "cpa": c["cost_per_conversion"]}
            for c in top_spenders
        ],
        "top_5_por_conversoes": [
            {"nome": c["name"], "conversoes": c["conversions"], "gasto": c["cost"], "cpa": c["cost_per_conversion"]}
            for c in top_converters
        ],
        "pior_cpa": [
            {"nome": c["name"], "cpa": c["cost_per_conversion"], "conversoes": c["conversions"], "gasto": c["cost"]}
            for c in worst_cpa[:5]
        ],
    }
