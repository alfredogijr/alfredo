"""Ad management tools."""
from google.ads.googleads.client import GoogleAdsClient


def list_ads(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    date_range: str = "LAST_30_DAYS",
) -> list[dict]:
    """List ads with performance metrics."""
    service = client.get_service("GoogleAdsService")

    conditions = [
        f"segments.date DURING {date_range}",
        "ad_group_ad.status != 'REMOVED'",
    ]
    if campaign_id:
        conditions.append(f"campaign.id = {campaign_id}")
    if ad_group_id:
        conditions.append(f"ad_group.id = {ad_group_id}")

    query = f"""
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.ad.type_,
            ad_group_ad.ad.final_urls,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            ad_group_ad.status,
            ad_group_ad.ad_strength,
            ad_group.name,
            campaign.name,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc
        FROM ad_group_ad
        WHERE {' AND '.join(conditions)}
        ORDER BY metrics.cost_micros DESC
    """
    response = service.search(customer_id=customer_id, query=query)
    ads = []
    for row in response:
        ad = row.ad_group_ad.ad
        m = row.metrics

        headlines = []
        descriptions = []
        if ad.type_.name == "RESPONSIVE_SEARCH_AD" and ad.responsive_search_ad:
            headlines = [h.text.text for h in ad.responsive_search_ad.headlines]
            descriptions = [d.text.text for d in ad.responsive_search_ad.descriptions]

        ads.append({
            "id": str(ad.id),
            "name": ad.name,
            "type": ad.type_.name,
            "status": row.ad_group_ad.status.name,
            "ad_strength": row.ad_group_ad.ad_strength.name,
            "final_urls": list(ad.final_urls),
            "headlines": headlines,
            "descriptions": descriptions,
            "ad_group": row.ad_group.name,
            "campaign": row.campaign.name,
            "cost": round(m.cost_micros / 1_000_000, 2),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 1),
            "ctr": round(m.ctr * 100, 2),
            "avg_cpc": round(m.average_cpc / 1_000_000, 2),
        })
    return ads
