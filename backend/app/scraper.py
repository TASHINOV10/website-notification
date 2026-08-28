import re

import requests
from bs4 import BeautifulSoup

from app.config import settings

# Matches things like $1,299.99 / £49.00 / 49,99 EUR / 1299 (no decimals)
PRICE_RE = re.compile(
    r"(?:[\$£€]|USD|EUR|GBP)?\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\b",
    re.IGNORECASE,
)

# Where to look, in order, when no css_selector is provided.
FALLBACK_SELECTORS = [
    '[itemprop="price"]',
    'meta[property="product:price:amount"]',
    'meta[property="og:price:amount"]',
    '.price',
    '#price',
    '[class*="price"]',
]


class ScrapeError(Exception):
    pass


def _clean_price_text(text: str) -> float:
    match = PRICE_RE.search(text.replace("\xa0", " "))
    if not match:
        raise ScrapeError(f"Could not find a price in text: {text!r}")

    raw = match.group(1)
    # Normalize "1.299,99" or "1,299.99" style thousand/decimal separators.
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        # Ambiguous: "49,99" (decimal) vs "1,299" (thousands).
        if len(raw.split(",")[-1]) == 2:
            raw = raw.replace(",", ".")
        else:
            raw = raw.replace(",", "")

    return float(raw)


def fetch_page(url: str) -> str:
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": settings.user_agent},
            timeout=settings.request_timeout_seconds,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ScrapeError(f"Failed to fetch URL: {exc}") from exc
    return resp.text


def extract_price(html: str, css_selector: str | None = None) -> float:
    soup = BeautifulSoup(html, "lxml")

    if css_selector:
        el = soup.select_one(css_selector)
        if el is None:
            raise ScrapeError(f"CSS selector {css_selector!r} matched nothing")
        text = el.get("content") or el.get_text(" ", strip=True)
        return _clean_price_text(text)

    for selector in FALLBACK_SELECTORS:
        el = soup.select_one(selector)
        if el is None:
            continue
        text = el.get("content") or el.get_text(" ", strip=True)
        try:
            return _clean_price_text(text)
        except ScrapeError:
            continue

    # Last resort: search the whole page text for the first price-looking token.
    return _clean_price_text(soup.get_text(" ", strip=True))


def check_price(url: str, css_selector: str | None = None) -> float:
    html = fetch_page(url)
    return extract_price(html, css_selector)
