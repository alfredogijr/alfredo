"""
Stage 1 — Coletor RSS
Coleta manchetes do dia dos portais mapeados via feeds RSS.
Retorna lista de dicts {source, title, link, published, summary}.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone, timedelta
from typing import TypedDict

import feedparser
import httpx

# ---------------------------------------------------------------------------
# Feeds RSS mapeados
# ---------------------------------------------------------------------------
# Critério de escolha: portais relevantes para o público do Turista FC,
# priorizando feeds estáveis sem paywall no RSS.
FEEDS = [
    {
        "name": "BBC Sport",
        "url": "https://feeds.bbci.co.uk/sport/rss.xml",
        "lang": "en",
    },
    {
        "name": "ESPN Brasil",
        "url": "https://www.espn.com.br/espn/rss/noticias",
        "lang": "pt",
    },
    {
        "name": "Marca",
        "url": "https://www.marca.com/rss/portada.xml",
        "lang": "es",
    },
    {
        "name": "GE Globo",
        "url": "https://ge.globo.com/dynamo/futebol/rss2.xml",
        "lang": "pt",
    },
    # Gazzetta dello Sport não possui RSS público gratuito confiável;
    # adicionada como placeholder — substituir quando confirmar URL.
    # {"name": "Gazzetta", "url": "https://www.gazzetta.it/rss/home.xml", "lang": "it"},
]

LOOKBACK_HOURS = 24   # janela de tempo para considerar notícias "do dia"
MAX_PER_FEED   = 15   # limite por feed para não sobrecarregar o curador


class Headline(TypedDict):
    source: str
    title: str
    link: str
    published: str   # ISO 8601
    summary: str


def _parse_published(entry: feedparser.FeedParserDict) -> datetime:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(tz=timezone.utc)


def _deduplicate(headlines: list[Headline]) -> list[Headline]:
    """Remove manchetes duplicadas por hash do título normalizado."""
    seen: set[str] = set()
    result: list[Headline] = []
    for h in headlines:
        key = hashlib.md5(h["title"].lower().strip().encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            result.append(h)
    return result


def collect(lookback_hours: int = LOOKBACK_HOURS) -> list[Headline]:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=lookback_hours)
    all_headlines: list[Headline] = []

    headers = {
        "User-Agent": "TuristaFC-Pipeline/1.0 (news aggregator; contact: marketing@turistafc.com.br)"
    }

    for feed_cfg in FEEDS:
        try:
            resp = httpx.get(feed_cfg["url"], headers=headers, timeout=15, follow_redirects=True)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.text)
        except Exception as exc:
            print(f"  [collector] AVISO — {feed_cfg['name']}: {exc}")
            continue

        count = 0
        for entry in parsed.entries:
            if count >= MAX_PER_FEED:
                break
            pub = _parse_published(entry)
            if pub < cutoff:
                continue
            all_headlines.append({
                "source":    feed_cfg["name"],
                "title":     entry.get("title", "").strip(),
                "link":      entry.get("link", ""),
                "published": pub.isoformat(),
                "summary":   entry.get("summary", "")[:400].strip(),
            })
            count += 1

        print(f"  [collector] {feed_cfg['name']}: {count} manchetes")

    deduped = _deduplicate(all_headlines)
    print(f"  [collector] Total após dedup: {len(deduped)} manchetes")
    return deduped


if __name__ == "__main__":
    headlines = collect()
    for h in headlines[:5]:
        print(f"\n[{h['source']}] {h['title']}")
        print(f"  {h['published']}")
