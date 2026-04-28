import asyncio
import hashlib
from typing import List
from pydantic import BaseModel, Field
from db.client import url_exists, save_lead


def _h(u: str) -> str:
    return hashlib.md5(u.encode()).hexdigest()[:16]


def _to_md(html: str) -> str:
    import html2text
    h = html2text.HTML2Text()
    h.ignore_links = False
    return h.handle(html)


async def _crawl(u: str, headed: bool = False) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        br = await pw.chromium.launch(headless=not headed)
        pg = await br.new_page()
        await pg.goto(u, wait_until="domcontentloaded", timeout=30000)
        html = await pg.content()
        await br.close()
    return _to_md(html)


class _Lead(BaseModel):
    title:       str
    company:     str
    url:         str
    platform:    str = ""
    description: str = ""   # brief summary of the role / requirements


class _Leads(BaseModel):
    leads: List[_Lead] = Field(default_factory=list)


def _parse(md: str, src: str) -> list:
    from llm import call_llm
    o = call_llm(
        "You are a job-lead extractor. Given scraped job-board markdown, "
        "return every distinct job posting you find. "
        "For each posting extract: title, company, url, and a 2-3 sentence "
        "description summarising the role, required tech stack, and seniority level. "
        "If the page is a single job, return just that one. "
        "If no jobs found, return an empty list.",
        f"Source URL: {src}\n\n{md}",
        _Leads,
        step="scout",
    )
    return [l.model_dump() for l in o.leads]


async def apify(actor: str, inp: dict, tok: str) -> list:
    import httpx
    async with httpx.AsyncClient(timeout=60) as cx:
        run = await cx.post(
            f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items",
            params={"token": tok},
            json=inp,
        )
        run.raise_for_status()
        return run.json()


def _ensure_scheme(u: str) -> str:
    """Prepend https:// if the URL has no scheme — Playwright requires a full URL."""
    if u.startswith("site:") or u.startswith("http://") or u.startswith("https://"):
        return u
    return "https://" + u


def scrape(u: str, headed: bool = False) -> list:
    u = _ensure_scheme(u)
    md = asyncio.run(_crawl(u, headed=headed))
    return _parse(md, u)


async def _scrape_rss(u: str) -> list:
    import httpx
    import xml.etree.ElementTree as ET
    async with httpx.AsyncClient(timeout=30) as cx:
        r = await cx.get(u)
        root = ET.fromstring(r.text)
        items = []
        for item in root.findall(".//item"):
            t = item.find("title").text if item.find("title") is not None else ""
            l = item.find("link").text if item.find("link") is not None else ""
            items.append({"title": t, "company": "RSS Feed", "url": l, "platform": "rss"})
        return items


async def _scrape_remoteok() -> list:
    import httpx
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    async with httpx.AsyncClient(timeout=30, headers=headers) as cx:
        r = await cx.get("https://remoteok.com/api")
        data = r.json()
        return [{"title": j.get("position"), "company": j.get("company"), "url": j.get("url"), "platform": "remoteok"} for j in data if isinstance(j, dict)]


def run(
    urls: list[str] | None = None,
    queries: list[str] | None = None,
    apify_token: str | None = None,
    apify_actor: str | None = None,
    headed: bool = False,
) -> list:
    leads = []
    
    # Handle Special Targets (RSS/API)
    all_targets = urls or []
    processed_leads = []

    for target in all_targets:
        target = _ensure_scheme(target)
        if "remoteok.com/api" in target:
            processed_leads.extend(asyncio.run(_scrape_remoteok()))
        elif target.endswith(".rss") or "weworkremotely.com" in target:
            processed_leads.extend(asyncio.run(_scrape_rss(target)))
        elif target.startswith("site:"):
            # Google Dork Logic
            query = target.replace(" ", "+")
            google_url = f"https://www.google.com/search?q={query}&tbs=qdr:d"
            # Scrape Google Results
            for item in scrape(google_url, headed=headed):
                processed_leads.append(item)
        else:
            # Standard Web Scrape
            processed_leads.extend(scrape(target, headed=headed))

    # Apify fallback
    if apify_token and apify_actor and queries:
        raw = asyncio.run(apify(apify_actor, {"queries": queries}, apify_token))
        for item in raw:
            processed_leads.append({
                "title": item.get("title", ""),
                "company": item.get("company", ""),
                "url": item.get("url", ""),
                "platform": "apify"
            })

    # Save and Deduplicate
    for item in processed_leads:
        u = item.get("url", "")
        if not u: continue
        jid = _h(u)
        if not url_exists(jid):
            t    = item.get("title", "")
            co   = item.get("company", "")
            plat = item.get("platform", "scout")
            desc = item.get("description", "")
            save_lead(jid, t, co, u, plat, desc)
            leads.append({"job_id": jid, "title": t, "company": co, "url": u, "platform": plat, "description": desc})

    return leads
