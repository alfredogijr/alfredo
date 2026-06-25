"""Performance reporting tools."""
from google.ads.googleads.client import GoogleAdsClient


def get_performance_report(
    client: GoogleAdsClient,
    customer_id: str,
    date_range: str = "LAST_30_DAYS",
    segment_by: str = "day",
) -> list[dict]:
    """Get daily/weekly performance over a date range."""
    service = client.get_service("GoogleAdsService")

    segment_field = "segments.date" if segment_by == "day" else "segments.week"

    query = f"""
        SELECT
            {segment_field},
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion
        FROM customer
        WHERE segments.date DURING {date_range}
        ORDER BY {segment_field}
    """
    response = service.search(customer_id=customer_id, query=query)
    rows = []
    for row in response:
        m = row.metrics
        date_val = row.segments.date if segment_by == "day" else row.segments.week
        rows.append({
            "date": date_val,
            "cost": round(m.cost_micros / 1_000_000, 2),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 1),
            "ctr": round(m.ctr * 100, 2),
            "avg_cpc": round(m.average_cpc / 1_000_000, 2),
            "cost_per_conversion": round(m.cost_per_conversion / 1_000_000, 2) if m.cost_per_conversion else 0,
        })
    return rows


def get_campaign_performance_report(
    client: GoogleAdsClient,
    customer_id: str,
    date_range: str = "LAST_30_DAYS",
) -> list[dict]:
    """Campaign-level performance breakdown."""
    service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            segments.date,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion,
            metrics.search_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.search_rank_lost_impression_share
        FROM campaign
        WHERE segments.date DURING {date_range}
            AND campaign.status != 'REMOVED'
        ORDER BY campaign.name, segments.date
    """
    response = service.search(customer_id=customer_id, query=query)
    rows = []
    for row in response:
        m = row.metrics
        rows.append({
            "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name,
            "status": row.campaign.status.name,
            "channel": row.campaign.advertising_channel_type.name,
            "date": row.segments.date,
            "cost": round(m.cost_micros / 1_000_000, 2),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 1),
            "ctr": round(m.ctr * 100, 2),
            "avg_cpc": round(m.average_cpc / 1_000_000, 2),
            "cost_per_conversion": round(m.cost_per_conversion / 1_000_000, 2) if m.cost_per_conversion else 0,
            "impression_share": round(m.search_impression_share * 100, 1) if m.search_impression_share else 0,
            "budget_lost_is": round(m.search_budget_lost_impression_share * 100, 1) if m.search_budget_lost_impression_share else 0,
            "rank_lost_is": round(m.search_rank_lost_impression_share * 100, 1) if m.search_rank_lost_impression_share else 0,
        })
    return rows


def get_conversion_report(
    client: GoogleAdsClient,
    customer_id: str,
    date_range: str = "LAST_30_DAYS",
) -> list[dict]:
    """Conversion action breakdown report."""
    service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            conversion_action.name,
            conversion_action.category,
            conversion_action.type_,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion,
            metrics.cost_micros
        FROM conversion_action
        WHERE segments.date DURING {date_range}
            AND metrics.conversions > 0
        ORDER BY metrics.conversions DESC
    """
    response = service.search(customer_id=customer_id, query=query)
    rows = []
    for row in response:
        m = row.metrics
        rows.append({
            "conversion_name": row.conversion_action.name,
            "category": row.conversion_action.category.name,
            "type": row.conversion_action.type_.name,
            "conversions": round(m.conversions, 1),
            "conversion_value": round(m.conversions_value, 2),
            "cost": round(m.cost_micros / 1_000_000, 2),
            "cost_per_conversion": round(m.cost_per_conversion / 1_000_000, 2) if m.cost_per_conversion else 0,
        })
    return rows
