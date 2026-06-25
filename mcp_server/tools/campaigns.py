"""Campaign management tools."""
from google.ads.googleads.client import GoogleAdsClient


def list_campaigns(client: GoogleAdsClient, customer_id: str, date_range: str = "LAST_30_DAYS") -> list[dict]:
    """List campaigns with performance metrics."""
    service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign.start_date,
            campaign.end_date,
            campaign_budget.amount_micros,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion,
            metrics.search_impression_share
        FROM campaign
        WHERE segments.date DURING {date_range}
            AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """
    response = service.search(customer_id=customer_id, query=query)
    campaigns = []
    for row in response:
        c = row.campaign
        m = row.metrics
        budget = row.campaign_budget.amount_micros / 1_000_000 if row.campaign_budget.amount_micros else 0
        campaigns.append({
            "id": str(c.id),
            "name": c.name,
            "status": c.status.name,
            "channel": c.advertising_channel_type.name,
            "bidding_strategy": c.bidding_strategy_type.name,
            "budget": round(budget, 2),
            "start_date": c.start_date,
            "end_date": c.end_date,
            "cost": round(m.cost_micros / 1_000_000, 2),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 1),
            "ctr": round(m.ctr * 100, 2),
            "avg_cpc": round(m.average_cpc / 1_000_000, 2),
            "cost_per_conversion": round(m.cost_per_conversion / 1_000_000, 2) if m.cost_per_conversion else 0,
            "impression_share": round(m.search_impression_share * 100, 1) if m.search_impression_share else 0,
        })
    return campaigns


def update_campaign_budget(client: GoogleAdsClient, customer_id: str, campaign_id: str, new_budget: float) -> str:
    """Update campaign daily budget."""
    # First get the campaign budget resource name
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT campaign.campaign_budget
        FROM campaign
        WHERE campaign.id = {campaign_id}
    """
    response = ga_service.search(customer_id=customer_id, query=query)
    budget_resource = None
    for row in response:
        budget_resource = row.campaign.campaign_budget

    if not budget_resource:
        raise ValueError(f"Campanha {campaign_id} não encontrada")

    budget_service = client.get_service("CampaignBudgetService")
    budget_op = client.get_type("CampaignBudgetOperation")
    budget = budget_op.update
    budget.resource_name = budget_resource
    budget.amount_micros = int(new_budget * 1_000_000)

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("amount_micros")
    budget_op.update_mask.CopyFrom(field_mask)

    response = budget_service.mutate_campaign_budgets(
        customer_id=customer_id,
        operations=[budget_op]
    )
    return f"Budget atualizado para R$ {new_budget:.2f}/dia"


def pause_campaign(client: GoogleAdsClient, customer_id: str, campaign_id: str) -> str:
    """Pause a campaign."""
    return _set_campaign_status(client, customer_id, campaign_id, "PAUSED")


def enable_campaign(client: GoogleAdsClient, customer_id: str, campaign_id: str) -> str:
    """Enable a paused campaign."""
    return _set_campaign_status(client, customer_id, campaign_id, "ENABLED")


def _set_campaign_status(client: GoogleAdsClient, customer_id: str, campaign_id: str, status: str) -> str:
    campaign_service = client.get_service("CampaignService")
    campaign_op = client.get_type("CampaignOperation")
    campaign = campaign_op.update
    campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)

    status_enum = client.enums.CampaignStatusEnum.CampaignStatus[status]
    campaign.status = status_enum

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")
    campaign_op.update_mask.CopyFrom(field_mask)

    campaign_service.mutate_campaigns(
        customer_id=customer_id,
        operations=[campaign_op]
    )
    return f"Campanha {campaign_id} alterada para {status}"


def list_ad_groups(client: GoogleAdsClient, customer_id: str, campaign_id: str | None = None, date_range: str = "LAST_30_DAYS") -> list[dict]:
    """List ad groups with performance."""
    service = client.get_service("GoogleAdsService")
    where_clause = f"WHERE segments.date DURING {date_range} AND ad_group.status != 'REMOVED'"
    if campaign_id:
        where_clause += f" AND campaign.id = {campaign_id}"

    query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            campaign.id,
            campaign.name,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.quality_score
        FROM ad_group
        {where_clause}
        ORDER BY metrics.cost_micros DESC
    """
    response = service.search(customer_id=customer_id, query=query)
    ad_groups = []
    for row in response:
        ag = row.ad_group
        m = row.metrics
        ad_groups.append({
            "id": str(ag.id),
            "name": ag.name,
            "status": ag.status.name,
            "type": ag.type_.name,
            "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name,
            "cost": round(m.cost_micros / 1_000_000, 2),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 1),
            "ctr": round(m.ctr * 100, 2),
            "avg_cpc": round(m.average_cpc / 1_000_000, 2),
            "quality_score": m.quality_score if m.quality_score else "N/A",
        })
    return ad_groups
