#!/usr/bin/env python3
"""Fetch live DexScreener prices for all StonkAgent tokens on Base.

Source: https://api.dexscreener.com/latest/dex/tokens/{addr,...} (public,
no key, up to 30 addresses per call). For each token we keep the best
Base pair: quote USDC, highest USD liquidity, preferring Aerodrome.
Output: data/prices.json
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

DEX = "https://api.dexscreener.com/latest/dex/tokens/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
# Small batches: DexScreener truncates large multi-token responses, so a
# 30-address batch silently drops pairs for some tokens.
BATCH = 10
# Tokens with real supply that still have no pair get one individual retry.
RETRY_MIN_SUPPLY = 1000


def best_pair(pairs):
    """Pick the best Base/USDC pair from a token's pair list."""
    base_pairs = [p for p in pairs if p.get("chainId") == "base"]
    if not base_pairs:
        return None
    usdc = [p for p in base_pairs if (p.get("quoteToken") or {}).get("symbol") == "USDC"]
    pool = usdc or base_pairs
    # Prefer Aerodrome, then highest liquidity.
    pool.sort(
        key=lambda p: (
            1 if p.get("dexId") in ("aerodrome", "aero") else 0,
            (p.get("liquidity") or {}).get("usd") or 0,
        ),
        reverse=True,
    )
    return pool[0]


def fetch_batch(addresses):
    url = DEX + ",".join(addresses)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json().get("pairs") or []


def main():
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "tokens.json")) as f:
        tokens = json.load(f)["tokens"]

    by_addr = {}
    addrs = [t["contract_address"] for t in tokens]
    for i in range(0, len(addrs), BATCH):
        chunk = addrs[i : i + BATCH]
        try:
            pairs = fetch_batch(chunk)
        except Exception as e:  # noqa: BLE001 - one bad batch must not kill the run
            print(f"batch {i//BATCH + 1} failed: {e}", file=sys.stderr)
            continue
        for p in pairs:
            base = (p.get("baseToken") or {}).get("address", "").lower()
            by_addr.setdefault(base, []).append(p)
        time.sleep(0.4)

    # Individual retry for high-supply tokens that still have no pair
    # (protects against batch truncation / transient misses).
    for t in tokens:
        addr = t["contract_address"].lower()
        if addr not in by_addr and (t.get("total_supply") or 0) >= RETRY_MIN_SUPPLY:
            try:
                pairs = fetch_batch([t["contract_address"]])
                for p in pairs:
                    base = (p.get("baseToken") or {}).get("address", "").lower()
                    by_addr.setdefault(base, []).append(p)
                time.sleep(0.3)
            except Exception as e:  # noqa: BLE001 - best-effort retry
                print(f"retry {t['symbol']} failed: {e}", file=sys.stderr)

    now = datetime.now(timezone.utc).isoformat()
    out_tokens = []
    missing = []
    for t in tokens:
        addr = t["contract_address"].lower()
        pair = best_pair(by_addr.get(addr, []))
        if not pair:
            missing.append(t["symbol"])
            continue
        pc = pair.get("priceChange") or {}
        vol = pair.get("volume") or {}
        tx = pair.get("txns") or {}
        h24 = tx.get("h24") or {}
        out_tokens.append(
            {
                "symbol": t["symbol"],
                "name": t["name"],
                "contract_address": t["contract_address"],
                "price_usd": float(pair.get("priceUsd")) if pair.get("priceUsd") else None,
                "price_change_m5": pc.get("m5"),
                "price_change_h1": pc.get("h1"),
                "price_change_h6": pc.get("h6"),
                "price_change_h24": pc.get("h24"),
                "volume_h24": vol.get("h24"),
                "volume_h6": vol.get("h6"),
                "volume_h1": vol.get("h1"),
                "txns_h24_buys": h24.get("buys"),
                "txns_h24_sells": h24.get("sells"),
                "liquidity_usd": (pair.get("liquidity") or {}).get("usd"),
                "dex": pair.get("dexId"),
                "pair_address": pair.get("pairAddress"),
                "pair_url": pair.get("url"),
                "fdv": pair.get("fdv"),
                "market_cap": pair.get("marketCap"),
            }
        )

    out = {
        "fetched_at_utc": now,
        "count": len(out_tokens),
        "missing_no_base_pair": missing,
        "source": "DexScreener (Base)",
        "tokens": out_tokens,
    }
    with open(os.path.join(DATA, "prices.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"prices: {len(out_tokens)}/{len(tokens)} tokens with a Base pair")
    if missing:
        print(f"missing ({len(missing)}): {', '.join(missing[:20])}")


if __name__ == "__main__":
    main()
