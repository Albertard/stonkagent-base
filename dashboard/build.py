#!/usr/bin/env python3
"""Build the public dashboard (dashboard/index.html) from the latest briefing.

The dashboard is a single self-contained HTML file (data embedded as JSON,
no fetch needed) so it works on GitHub Pages and opened locally.
Run after the daily run: python3 dashboard/build.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DASH = os.path.join(ROOT, "dashboard")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StonkAgent — Daily AI Research on Coinbase Tokenized Stocks (Base)</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:960px;margin:0 auto;padding:24px;color:#111;background:#fff}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin-top:28px;border-bottom:1px solid #ddd;padding-bottom:4px}
.sub{color:#555;margin:0 0 16px}.card{border:1px solid #ddd;border-radius:10px;padding:14px;margin:10px 0}
table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #eee;padding:7px 6px;text-align:left;font-size:14px}
th{color:#555}.up{color:#0a7d2c}.down{color:#c0392b}.pill{display:inline-block;background:#eef4ff;border-radius:999px;padding:2px 10px;font-size:12px;margin-right:6px}
a{color:#0b5fff}.foot{color:#777;font-size:12px;margin-top:28px}
code{background:#f4f4f4;padding:1px 5px;border-radius:4px}
</style>
</head>
<body>
<h1>📈 StonkAgent</h1>
<p class="sub">Daily AI research agent for Coinbase tokenized stocks on Base.
Paper trading simulation — <b>not investment advice</b>. Built for the
<a href="https://base.org/stocksmaxxing">Base Stocks Maxxing Season</a>
(Agentic Stock Finance track).</p>
<div id="meta"></div>
<h2>🎯 Today's picks (top momentum, paper BUY)</h2>
<div id="picks"></div>
<h2>🔥 Most active (24h volume)</h2>
<div id="active"></div>
<h2>💲 Cheapest vs NAV (Chainlink)</h2>
<div id="nav"></div>
<h2>📉 Avoid (biggest 24h losers)</h2>
<div id="losers"></div>
<h2>💼 Paper portfolio</h2>
<div id="portfolio"></div>
<h2>⛓️ Onchain journal</h2>
<div id="journal"></div>
<p class="foot">Data: Coinbase Tokenized Stocks API + DexScreener (Aerodrome/Base) +
Chainlink NAV feeds. Decisions are logged to the AgentJournal contract on
Base Sepolia testnet. StonkAgent holds no real assets and never gives buy/sell
recommendations. <span id="gen"></span></p>
<script>
const B = __BRIEFING_JSON__;
const J = __JOURNAL_JSON__;
const fmt = n => n==null ? 'n/a' : (n>=0?'+':'') + n.toFixed(2);
const money = n => n==null ? 'n/a' : '$' + n.toLocaleString(undefined,{maximumFractionDigits:2});
document.getElementById('meta').innerHTML =
 `<p><span class="pill">📅 ${B.date}</span><span class="pill">Universe: ${B.universe.tokens_total} tokens</span>`+
 `<span class="pill">Eligible: ${B.universe.eligible}</span><span class="pill">NAV feeds: ${B.universe.with_nav_feed}</span></p>`;
const rows = (list, cols) => '<table><tr>'+cols.map(c=>`<th>${c[0]}</th>`).join('')+'</tr>'+
 list.map(t=>'<tr>'+cols.map(c=>`<td>${c[1](t)}</td>`).join('')+'</tr>').join('')+'</table>';
document.getElementById('picks').innerHTML = rows(B.top_momentum, [
 ['Token', t=>`<b>${t.symbol}</b> ${t.name}`],
 ['Price', t=>money(t.price_usd)],
 ['24h', t=>`<span class="${t.price_change_h24>=0?'up':'down'}">${fmt(t.price_change_h24)}%</span>`],
 ['Score', t=>fmt(t.momentum_score)],
 ['Vol 24h', t=>money(t.volume_h24)],
 ['Pair', t=>`<a href="${t.pair_url}" target="_blank">DexScreener ↗</a>`],
]);
document.getElementById('active').innerHTML = rows(B.most_active, [
 ['Token', t=>`<b>${t.symbol}</b>`],
 ['Price', t=>money(t.price_usd)],
 ['24h', t=>`<span class="${t.price_change_h24>=0?'up':'down'}">${fmt(t.price_change_h24)}%</span>`],
 ['Vol 24h', t=>money(t.volume_h24)],
 ['Buys/Sells', t=>`${t.txns_h24_buys} / ${t.txns_h24_sells}`],
]);
document.getElementById('nav').innerHTML = B.cheapest_vs_nav.length ? rows(B.cheapest_vs_nav, [
 ['Token', t=>`<b>${t.symbol}</b>`],
 ['Price', t=>money(t.price_usd)],
 ['NAV', t=>money(t.nav_price)],
 ['Discount', t=>`<span class="up">${fmt(t.nav_discount_pct)}%</span>`],
]) : '<p>No NAV-priced token in the eligible pool today.</p>';
document.getElementById('losers').innerHTML = rows(B.avoid_losers, [
 ['Token', t=>`<b>${t.symbol}</b>`],
 ['Price', t=>money(t.price_usd)],
 ['24h', t=>`<span class="down">${fmt(t.price_change_h24)}%</span>`],
 ['Vol 24h', t=>money(t.volume_h24)],
]);
const P = B.paper_portfolio;
document.getElementById('portfolio').innerHTML =
 `<div class="card"><b>Capital ${money(P.capital_usd)}</b> (start $10,000) — `+
 `P&amp;L <span class="${P.pnl_usd>=0?'up':'down'}">${money(P.pnl_usd)} (${fmt(P.pnl_pct)}%)</span> — ${P.note}.`+
 `<br><br>` + rows(P.holdings, [
  ['Token', h=>`<b>${h.symbol}</b>`],
  ['Units', h=>h.units],
  ['Entry', h=>money(h.entry_price_usd)],
  ['Value', h=>money(h.value_usd)],
 ]) + '</div>';
document.getElementById('journal').innerHTML = J ?
 `<div class="card">Contract: <a href="${J.contract_basescan}" target="_blank"><code>${J.contract}</code> ↗</a><br>`+
 J.entries.map(e=>`• <b>${e.symbol}</b> ${e.action} — <a href="${e.basescan}" target="_blank">tx ↗</a> (block ${e.block})`).join('<br>')+'</div>' :
 '<p>Journal contract not deployed yet — first onchain entries land once the Base Sepolia deploy is funded.</p>';
document.getElementById('gen').textContent = 'Generated ' + B.generated_at_utc + ' (UTC).';
</script>
</body>
</html>
"""


def latest_briefing():
    files = sorted(glob.glob(os.path.join(DATA, "briefing-*.json")))
    if not files:
        raise SystemExit("no briefing found — run src/run_daily.py first")
    with open(files[-1]) as f:
        return json.load(f)


def latest_journal(date):
    path = os.path.join(DATA, f"journal-{date}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def main():
    os.makedirs(DASH, exist_ok=True)
    briefing = latest_briefing()
    journal = latest_journal(briefing["date"])
    html = (
        HTML.replace("__BRIEFING_JSON__", json.dumps(briefing))
        .replace("__JOURNAL_JSON__", json.dumps(journal))
    )
    out = os.path.join(DASH, "index.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"dashboard built: {out} ({len(html)} bytes, briefing {briefing['date']})")


if __name__ == "__main__":
    main()
