#!/usr/bin/env python3
"""StonkAgent signal engine v1 — transparent, rule-based daily picks.

Rules (documented, no black box):
- Momentum score = 0.5 * chg_h24 + 0.3 * chg_h6 + 0.2 * chg_h1 (percent).
  A token needs a Base pair, price, h24 change, volume_h24 > 0 and
  liquidity >= $10,000 to be pick-eligible (dust pairs excluded).
- Picks:
  * TOP 5 momentum (highest score) -> paper BUY, equal weight.
  * TOP 5 most active by volume_h24.
  * TOP 3 cheapest vs NAV (only the ~13 tokens with a Chainlink NAV feed):
    discount% = (nav_price - price) / nav_price * 100.
  * BOTTOM 5 losers by h24 change -> AVOID list.
- Paper portfolio: $10,000 virtual, rebalanced daily to the top-5
  momentum picks (equal weight). P&L is marked to current prices vs
  the previous briefing's portfolio value. Day 1 opens at $10,000.
- Output: data/briefing-YYYY-MM-DD.json + logs/briefing-YYYY-MM-DD.md

This is a research/simulation tool. NOT investment advice.
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LOGS = os.path.join(ROOT, "logs")
START_CAPITAL = 10_000.0
MIN_LIQUIDITY = 10_000.0
# A pick must actually trade: $26 of daily volume topping the list (as ARM
# did on day 1) is a dust artefact, not a signal.
MIN_VOLUME_H24 = 1_000.0


def load_json(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def nav_map():
    """Map contract address (lower) -> live nav_price from nav_prices.json."""
    path = os.path.join(DATA, "nav_prices.json")
    if not os.path.exists(path):
        return {}
    raw = json.load(open(path)).get("prices", {})
    return {k.lower(): float(v) for k, v in raw.items() if v}


def momentum(t):
    h24 = t.get("price_change_h24") or 0.0
    h6 = t.get("price_change_h6") or 0.0
    h1 = t.get("price_change_h1") or 0.0
    return 0.5 * h24 + 0.3 * h6 + 0.2 * h1


def eligible(t):
    return (
        t.get("price_usd") is not None
        and t.get("price_change_h24") is not None
        and (t.get("volume_h24") or 0) >= MIN_VOLUME_H24
        and (t.get("liquidity_usd") or 0) >= MIN_LIQUIDITY
    )


def fmt(x, suffix="%"):
    """Format a possibly-None number for the markdown log."""
    return f"{x:+.2f}{suffix}" if x is not None else "n/a"


def prev_portfolio():
    """Load the most recent previous briefing's portfolio, if any."""
    files = sorted(glob.glob(os.path.join(DATA, "briefing-*.json")))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    files = [f for f in files if not f.endswith(f"briefing-{today}.json")]
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f).get("paper_portfolio")


def main():
    os.makedirs(LOGS, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prices = load_json("prices.json")
    tokens = prices["tokens"]
    nav = nav_map()

    pool = [t for t in tokens if eligible(t)]
    for t in pool:
        t["momentum_score"] = round(momentum(t), 4)
        np = nav.get(t["contract_address"].lower())
        t["nav_price"] = np
        t["nav_discount_pct"] = (
            round((np - t["price_usd"]) / np * 100, 2) if np and np > 0 else None
        )

    top_momentum = sorted(pool, key=lambda x: x["momentum_score"], reverse=True)[:5]
    most_active = sorted(pool, key=lambda x: x.get("volume_h24") or 0, reverse=True)[:5]
    with_nav = [t for t in pool if t.get("nav_discount_pct") is not None]
    cheapest_nav = sorted(with_nav, key=lambda x: x["nav_discount_pct"], reverse=True)[:3]
    losers = sorted(pool, key=lambda x: x.get("price_change_h24") or 0)[:5]

    # --- paper portfolio: rebalance daily to top-5 momentum, equal weight ---
    prev = prev_portfolio()
    if prev is None:
        capital = START_CAPITAL
        holdings_note = "opened today"
    else:
        # mark previous holdings to today's prices
        price_now = {t["symbol"]: t["price_usd"] for t in tokens}
        capital = 0.0
        for h in prev["holdings"]:
            p = price_now.get(h["symbol"])
            capital += h["units"] * p if p else h["units"] * h["entry_price_usd"]
        holdings_note = "rebalanced from previous day"
    per_pick = capital / len(top_momentum) if top_momentum else 0.0
    holdings = [
        {
            "symbol": t["symbol"],
            "units": round(per_pick / t["price_usd"], 6),
            "entry_price_usd": t["price_usd"],
            "value_usd": round(per_pick, 2),
        }
        for t in top_momentum
    ]
    pnl = round(capital - START_CAPITAL, 2)
    pnl_pct = round((capital - START_CAPITAL) / START_CAPITAL * 100, 2)

    briefing = {
        "date": today,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "universe": {
            "tokens_total": len(tokens),
            "eligible": len(pool),
            "with_nav_feed": len(with_nav),
            "prices_source": "DexScreener (Base/Aerodrome)",
            "tokens_source": "Coinbase Tokenized Stocks API",
        },
        "top_momentum": [
            {k: t[k] for k in ("symbol", "name", "price_usd", "price_change_h24",
                               "price_change_h6", "price_change_h1", "momentum_score",
                               "volume_h24", "liquidity_usd", "pair_url")}
            for t in top_momentum
        ],
        "most_active": [
            {k: t[k] for k in ("symbol", "name", "price_usd", "price_change_h24",
                               "volume_h24", "txns_h24_buys", "txns_h24_sells", "pair_url")}
            for t in most_active
        ],
        "cheapest_vs_nav": [
            {k: t[k] for k in ("symbol", "name", "price_usd", "nav_price",
                               "nav_discount_pct", "pair_url")}
            for t in cheapest_nav
        ],
        "avoid_losers": [
            {k: t[k] for k in ("symbol", "name", "price_usd", "price_change_h24",
                               "volume_h24", "pair_url")}
            for t in losers
        ],
        "paper_portfolio": {
            "capital_usd": round(capital, 2),
            "start_capital_usd": START_CAPITAL,
            "pnl_usd": pnl,
            "pnl_pct": pnl_pct,
            "note": holdings_note,
            "holdings": holdings,
        },
        "disclaimer": "Paper trading simulation only. Not investment advice. "
        "StonkAgent holds no real assets and gives no recommendation to buy or sell.",
    }

    with open(os.path.join(DATA, f"briefing-{today}.json"), "w") as f:
        json.dump(briefing, f, indent=2)

    # --- human-readable daily log (build-in-public material) ---
    lines = [
        f"# StonkAgent daily briefing — {today}",
        "",
        f"Universe: {len(tokens)} tokenized stocks, {len(pool)} eligible "
        f"(price + volume + liquidity >= ${MIN_LIQUIDITY:,.0f}), "
        f"{len(with_nav)} with NAV feed.",
        "",
        "## Top 5 momentum picks (paper BUY, equal weight)",
        "",
    ]
    for t in top_momentum:
        lines.append(
            f"- **{t['symbol']}** {t['name']} — ${t['price_usd']:.2f} | "
            f"h24 {fmt(t['price_change_h24'])} h6 {fmt(t['price_change_h6'])} "
            f"h1 {fmt(t['price_change_h1'])} | score {t['momentum_score']:+.2f} | "
            f"vol24 ${t['volume_h24']:,.0f}"
        )
    lines += ["", "## Most active (volume 24h)", ""]
    for t in most_active:
        lines.append(
            f"- **{t['symbol']}** — ${t['price_usd']:.2f} | "
            f"vol24 ${t['volume_h24']:,.0f} | buys {t.get('txns_h24_buys')} / "
            f"sells {t.get('txns_h24_sells')}"
        )
    lines += ["", "## Cheapest vs NAV", ""]
    if cheapest_nav:
        for t in cheapest_nav:
            lines.append(
                f"- **{t['symbol']}** — price ${t['price_usd']:.2f} vs NAV "
                f"${t['nav_price']:.2f} ({t['nav_discount_pct']:+.2f}%)"
            )
    else:
        lines.append("- No NAV-priced token in the eligible pool today.")
    lines += ["", "## Avoid (biggest 24h losers)", ""]
    for t in losers:
        lines.append(f"- **{t['symbol']}** — ${t['price_usd']:.2f} | h24 {t['price_change_h24']:+.2f}%")
    lines += [
        "",
        "## Paper portfolio",
        "",
        f"Capital ${capital:,.2f} (start $10,000) | P&L ${pnl:+,.2f} ({pnl_pct:+.2f}%) | {holdings_note}.",
        "",
        "_Paper trading simulation only. Not investment advice._",
    ]
    with open(os.path.join(LOGS, f"briefing-{today}.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"briefing {today}: {len(pool)} eligible, top pick "
          f"{top_momentum[0]['symbol'] if top_momentum else '-'} "
          f"(score {top_momentum[0]['momentum_score'] if top_momentum else 0:+.2f}), "
          f"capital ${capital:,.2f} ({pnl_pct:+.2f}%)")


if __name__ == "__main__":
    main()
