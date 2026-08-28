import re

import requests
from bs4 import BeautifulSoup

from app.config import settings

PRICE_RE = re.compile(
    r"(?:[\$£€]|USD|EUR|GBP)?\s?(\d+(?:[ .,]\d{3})*(?:[.,]\d{2})?)\b",
    re.IGNORECASE,
)

FALLBACK_SELECTORS = [
    '[id^="product-price-"]', #ww.ozone.bg
    'body > div.ad2023 > div.right > div > div > div.Price', #www.mobile.bg
    '#main-content > div > div:nth-child(1) > div > div.offer-price > div > div:nth-child(1)', #www.cars.bg
    'body > div:nth-child(2) > div.ad2023 > div.left > div.adPrice > div.price > div.cena', #www.imot.bg
    '#mainContent > div > div.css-118kolg > div:nth-child(3) > div.css-1bcde92 > div:nth-child(2) > div > div.css-1bz5rm8 > div > div > h3' #www.olx.bg
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
            headers={"User-Agent": settings.user_agent},
            timeout=settings.request_timeout_seconds,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ScrapeError(f"Failed to fetch URL: {exc}") from exc
    return resp.text


def _element_price_text(el) -> str:

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
