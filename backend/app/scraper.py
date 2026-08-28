import re

import requests
from bs4 import BeautifulSoup

from app.config import settings

# Matches things like $1,299.99 / £49.00 / 49,99 EUR / 1 299,99 Lei / 1299 (no decimals).
# Thousands separators seen in the wild: comma, dot, or a plain space (e.g. Moldovan/
# Romanian "1 299,99 Lei").
PRICE_RE = re.compile(
    r"(?:[\$£€]|USD|EUR|GBP)?\s?(\d+(?:[ .,]\d{3})*(?:[.,]\d{2})?)\b",
    re.IGNORECASE,
)

# Where to look, in order, when no css_selector is provided. The `*=` operator is
# a substring match (soupsieve's equivalent of SQL's ILIKE '%...%') and the trailing
# `i` flag makes it case-insensitive -- together they catch id/class values with a
# per-product suffix, e.g. id="product-price-674978".
FALLBACK_SELECTORS = [
    '[itemprop="price"]',
    'meta[property="product:price:amount"]',
    'meta[property="og:price:amount"]',
    '.price',
    '#price',
    '[id*="price" i]',
    '[class*="price" i]',
]


class ScrapeError(Exception):
    pass


def _clean_price_text(text: str) -> float:
    match = PRICE_RE.search(text.replace("\xa0", " "))
    if not match:
        raise ScrapeError(f"Could not find a price in text: {text!r}")

    raw = match.group(1).replace(" ", "")
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
            # Accept/Accept-Language alongside the UA -- a bare UA with none of a
            # browser's other usual headers is itself a bot tell some sites 403 on.
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=settings.request_timeout_seconds,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ScrapeError(f"Failed to fetch URL: {exc}") from exc
    return resp.text


def _element_price_text(el) -> str:
    # No separator: many sites split a price into adjacent spans for styling,
    # e.g. <span>189<span class="precision">,00</span></span> -- inserting a
    # space here would break "189" and ",00" apart and truncate the decimals.
    return el.get("content") or el.get_text(strip=True)


def extract_price(html: str, css_selector: str | None = None) -> float:
    soup = BeautifulSoup(html, "lxml")

    if css_selector:
        el = soup.select_one(css_selector)
        if el is None:
            raise ScrapeError(f"CSS selector {css_selector!r} matched nothing")
        return _clean_price_text(_element_price_text(el))

    for selector in FALLBACK_SELECTORS:
        el = soup.select_one(selector)
        if el is None:
            continue
        try:
            return _clean_price_text(_element_price_text(el))
        except ScrapeError:
            continue

    # Last resort: search the whole page text for the first price-looking token.
    return _clean_price_text(soup.get_text(" ", strip=True))


def check_price(url: str, css_selector: str | None = None) -> float:
    html = fetch_page(url)
    return extract_price(html, css_selector)
