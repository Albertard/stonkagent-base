# StonkAgent

Daily AI research agent for **Coinbase tokenized stocks on Base** — built for the
[Base Stocks Maxxing Season](https://base.org/stocksmaxxing) (Agentic Stock Finance track).

Every day StonkAgent:
1. Pulls all 138 live tokenized stocks from the official
   [Coinbase Tokenized Stocks API](https://api.coinbase.com/v1/tokenized-stocks)
   (public, no key) + live prices/volume from DexScreener (Aerodrome/Base)
   + live NAV from Chainlink feeds (Base mainnet RPC).
2. Scores momentum (`0.5·chg24h + 0.3·chg6h + 0.2·chg1h`), volume and NAV
   discount — transparent rules, see `src/signals.py` — and picks the top 5.
3. Logs every pick onchain to the `AgentJournal` contract on **Base Sepolia
   testnet** (real transactions, verifiable on Basescan).
4. Publishes a daily briefing on the public dashboard (`dashboard/index.html`)
   with picks, a $10,000 paper portfolio + P&L, and journal links.

**Paper trading simulation only. Not investment advice.** StonkAgent holds no
real assets, never trades real money, and never gives buy/sell recommendations.

## Run the daily cycle

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
python3 src/run_daily.py        # tokens -> prices -> signals -> journal -> briefing
python3 dashboard/build.py      # rebuild dashboard/index.html from latest briefing
```

Outputs: `data/briefing-YYYY-MM-DD.json`, `logs/briefing-YYYY-MM-DD.md`,
`data/journal-YYYY-MM-DD.json` (once the contract is deployed).

## Onchain journal (Base Sepolia testnet)

- Contract: `contracts/AgentJournal.sol` — `logDecision(day, ticker, action,
  reasonHash, priceUsd, navPriceUsd)`, one entry per pick per day.
- Deploy: `contracts/compile.py` → `contracts/deploy.py` (needs testnet ETH
  for the agent wallet; see `contracts/faucet.py`).
- The deployer wallet is a fresh agent-owned testnet wallet
  (`contracts/.agent-wallet.json`, gitignored, never shared). It is NOT the
  owner's wallet and holds no real funds.

## Repo layout

```
PLAN.md            rules, product plan, schedule, honest assessment
src/               fetch_tokens.py, fetch_prices.py, signals.py,
                   log_decision.py, run_daily.py (daily orchestrator)
contracts/         AgentJournal.sol, compile.py, deploy.py, faucet.py
dashboard/         build.py -> index.html (public dashboard)
data/              daily JSON snapshots (tokens, prices, briefings, journals)
logs/              human-readable daily briefing markdown (build-in-public)
```

## Key facts (verified 27 Nov 2026)

- 138 tokenized stocks with positive supply; 54 have a live Base DEX pair
  (the rest are dust mints with tiny supply and no liquidity yet).
- 14 Chainlink NAV feeds, all readable live from the Base public RPC.
- Eligibility for picks: price + 24h change + volume ≥ $1,000 + liquidity
  ≥ $10,000 (keeps dust pairs out of the picks).
- Costs $0: public APIs, Base Sepolia faucet ETH, GitHub Pages hosting.
