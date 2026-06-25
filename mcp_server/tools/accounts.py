"""MCC account management tools."""
from google.ads.googleads.client import GoogleAdsClient


def list_accounts(client: GoogleAdsClient, mcc_id: str) -> list[dict]:
    """List all accounts under the MCC."""
    service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            customer_client.client_customer,
            customer_client.descriptive_name,
            customer_client.currency_code,
            customer_client.time_zone,
            customer_client.status,
            customer_client.id,
            customer_client.manager
        FROM customer_client
        WHERE customer_client.level <= 1
        ORDER BY customer_client.descriptive_name
    """
    response = service.search(customer_id=mcc_id, query=query)
    accounts = []
    for row in response:
        c = row.customer_client
        accounts.append({
            "id": str(c.id),
            "name": c.descriptive_name,
            "currency": c.currency_code,
            "timezone": c.time_zone,
            "status": c.status.name,
            "is_manager": c.manager,
            "resource_name": c.client_customer,
        })
    return accounts


def get_account_summary(client: GoogleAdsClient, customer_id: str, date_range: str = "LAST_30_DAYS") -> dict:
    """Get spend and performance summary for an account."""
    service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion
        FROM customer
        WHERE segments.date DURING {date_range}
    """
    response = service.search(customer_id=customer_id, query=query)
    totals = {
        "cost": 0.0,
        "impressions": 0,
        "clicks": 0,
        "conversions": 0.0,
        "ctr": 0.0,
        "avg_cpc": 0.0,
        "cost_per_conversion": 0.0,
        "date_range": date_range,
    }
    count = 0
    for row in response:
        m = row.metrics
        totals["cost"] += m.cost_micros / 1_000_000
        totals["impressions"] += m.impressions
        totals["clicks"] += m.clicks
        totals["conversions"] += m.conversions
        totals["ctr"] += m.ctr
        totals["avg_cpc"] += m.average_cpc / 1_000_000
        totals["cost_per_conversion"] += m.cost_per_conversion / 1_000_000
        count += 1
    if count > 0:
        totals["ctr"] = round(totals["ctr"] / count * 100, 2)
        totals["avg_cpc"] = round(totals["avg_cpc"] / count, 2)
        totals["cost_per_conversion"] = round(totals["cost_per_conversion"] / count, 2)
    totals["cost"] = round(totals["cost"], 2)
    totals["conversions"] = round(totals["conversions"], 1)
    return totals
