#!/usr/bin/env python3
"""Fetch the full list of Coinbase tokenized stocks.

Source: https://api.coinbase.com/v1/tokenized-stocks (public, no API key).
Pagination via page_token, page_size max 500.
Output: data/tokens.json (trimmed fields) + data/nav_feeds.json
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

BASE = "https://api.coinbase.com/v1/tokenized-stocks"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

KEEP = [
    "contract_address",
    "symbol",
    "name",
    "decimals",
    "multiplier",
    "total_supply",
    "isin",
    "icon_url",
    "first_mint_date",
]


def fetch_all():
    tokens = []
    page_token = None
    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        r = requests.get(BASE, params=params, timeout=30)
        r.raise_for_status()
        d = r.json()
        batch = d.get("tokens", [])
        tokens.extend(batch)
        page_token = d.get("next_page_token") or d.get("page_token")
        if not page_token or not batch:
            break
        time.sleep(0.5)
    return tokens


def fetch_nav_prices(feeds):
    """Read live NAV from the Chainlink aggregator contracts.

    /nav-feeds only lists feed ADDRESSES. The price comes from
    latestAnswer() (selector 0x50d25bcd) via the public Base RPC.
    Chainlink USD feeds use 8 decimals. Best-effort: a failed feed is
    skipped, never fatal.
    """
    prices = {}
    for item in feeds:
        addr = (item.get("contract_address") or "").lower()
        feed = item.get("nav_feed_address")
        if not addr or not feed:
            continue
        ok = False
        for attempt in range(3):
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [{"to": feed, "data": "0x50d25bcd"}, "latest"],
                    "id": 1,
                }
                r = requests.post("https://mainnet.base.org", json=payload, timeout=20)
                r.raise_for_status()
                res = r.json().get("result")
                if res:
                    raw = int(res, 16)
                    if raw > (1 << 255):  # negative int256, ignore
                        ok = True
                        break
                    prices[addr] = raw / 1e8
                    ok = True
                    break
            except Exception as e:  # noqa: BLE001 - retry, then skip the feed
                if attempt == 2:
                    print(f"nav feed {feed} failed: {e}", file=sys.stderr)
                time.sleep(1.0)
        if ok:
            time.sleep(0.2)
    return prices


def fetch_nav_feeds():
    try:
        r = requests.get(BASE + "/nav-feeds", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:  # noqa: BLE001 - NAV feed is best-effort
        print(f"nav-feeds fetch failed (non-fatal): {e}", file=sys.stderr)
        return None


def main():
    os.makedirs(DATA, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    tokens = fetch_all()
    # The API lists every token ever created (435); only the 138 with
    # positive total_supply are actually live/minted.
    tokens = [t for t in tokens if (t.get("total_supply") or 0) > 0]
    trimmed = [{k: t.get(k) for k in KEEP} for t in tokens]
    out = {
        "fetched_at_utc": now,
        "count": len(trimmed),
        "source": BASE,
        "tokens": trimmed,
    }
    with open(os.path.join(DATA, "tokens.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"tokens: {len(trimmed)} saved to data/tokens.json")

    nav = fetch_nav_feeds()
    if nav is not None:
        with open(os.path.join(DATA, "nav_feeds.json"), "w") as f:
            json.dump({"fetched_at_utc": now, "data": nav}, f, indent=2)
        feeds = nav.get("nav_feeds", [])
        print(f"nav-feeds saved ({len(feeds)} feeds)")
        prices = fetch_nav_prices(feeds)
        with open(os.path.join(DATA, "nav_prices.json"), "w") as f:
            json.dump({"fetched_at_utc": now, "prices": prices}, f, indent=2)
        print(f"nav prices read: {len(prices)} live NAV values")


if __name__ == "__main__":
    main()
