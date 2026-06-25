"""Keyword management and analysis tools."""
from google.ads.googleads.client import GoogleAdsClient


def list_keywords(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    date_range: str = "LAST_30_DAYS",
    limit: int = 100,
) -> list[dict]:
    """List keywords with performance metrics."""
    service = client.get_service("GoogleAdsService")

    conditions = [
        f"segments.date DURING {date_range}",
        "ad_group_criterion.type = 'KEYWORD'",
        "ad_group_criterion.status != 'REMOVED'",
    ]
    if campaign_id:
        conditions.append(f"campaign.id = {campaign_id}")
    if ad_group_id:
        conditions.append(f"ad_group.id = {ad_group_id}")

    query = f"""
        SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.quality_info.search_predicted_ctr,
            ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score,
            ad_group.id,
            ad_group.name,
            campaign.id,
            campaign.name,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion
        FROM ad_group_criterion
        WHERE {' AND '.join(conditions)}
        ORDER BY metrics.cost_micros DESC
        LIMIT {limit}
    """
    response = service.search(customer_id=customer_id, query=query)
    keywords = []
    for row in response:
        kw = row.ad_group_criterion
        m = row.metrics
        keywords.append({
            "criterion_id": str(kw.criterion_id),
            "keyword": kw.keyword.text,
            "match_type": kw.keyword.match_type.name,
            "status": kw.status.name,
            "quality_score": kw.quality_info.quality_score if kw.quality_info.quality_score else "N/A",
            "ad_group_id": str(row.ad_group.id),
            "ad_group_name": row.ad_group.name,
            "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name,
            "cost": round(m.cost_micros / 1_000_000, 2),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 1),
            "ctr": round(m.ctr * 100, 2),
            "avg_cpc": round(m.average_cpc / 1_000_000, 2),
            "cost_per_conversion": round(m.cost_per_conversion / 1_000_000, 2) if m.cost_per_conversion else 0,
        })
    return keywords


def get_search_terms(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str | None = None,
    date_range: str = "LAST_30_DAYS",
    limit: int = 100,
) -> list[dict]:
    """Get search term report — shows actual queries users searched."""
    service = client.get_service("GoogleAdsService")

    conditions = [
        f"segments.date DURING {date_range}",
        "metrics.impressions > 0",
    ]
    if campaign_id:
        conditions.append(f"campaign.id = {campaign_id}")

    query = f"""
        SELECT
            search_term_view.search_term,
            search_term_view.status,
            ad_group.name,
            campaign.name,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc
        FROM search_term_view
        WHERE {' AND '.join(conditions)}
        ORDER BY metrics.cost_micros DESC
        LIMIT {limit}
    """
    response = service.search(customer_id=customer_id, query=query)
    terms = []
    for row in response:
        m = row.metrics
        terms.append({
            "search_term": row.search_term_view.search_term,
            "status": row.search_term_view.status.name,
            "ad_group": row.ad_group.name,
            "campaign": row.campaign.name,
            "cost": round(m.cost_micros / 1_000_000, 2),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 1),
            "ctr": round(m.ctr * 100, 2),
            "avg_cpc": round(m.average_cpc / 1_000_000, 2),
        })
    return terms


def add_negative_keywords(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    keywords: list[str],
    match_type: str = "BROAD",
) -> str:
    """Add negative keywords to a campaign."""
    campaign_service = client.get_service("CampaignCriterionService")
    operations = []

    for keyword_text in keywords:
        op = client.get_type("CampaignCriterionOperation")
        criterion = op.create
        criterion.campaign = client.get_service("CampaignService").campaign_path(customer_id, campaign_id)
        criterion.negative = True
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.KeywordMatchType[match_type]
        operations.append(op)

    campaign_service.mutate_campaign_criteria(
        customer_id=customer_id,
        operations=operations,
    )
    return f"{len(keywords)} palavra(s)-chave negativa(s) adicionada(s) à campanha {campaign_id}"
