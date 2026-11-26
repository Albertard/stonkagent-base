#!/usr/bin/env python3
"""Write today's top-5 momentum picks to the AgentJournal contract.

Reads data/briefing-<today>.json and contracts/deployment.json.
Each pick is one onchain logDecision() call (paper BUY) with:
  reasonHash = keccak256("<symbol> momentum <score>, h24 <x>%, vol24 $<v>")
  priceUsd   = DEX price, 6 decimals
  navPriceUsd = Chainlink NAV, 6 decimals (0 when no NAV feed)
Skips gracefully (exit 0, warning) when the contract is not deployed yet
so the daily data run never fails on the journal step.
Writes a receipt to data/journal-<today>.json (tx hashes + Basescan links).
"""
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACTS = os.path.join(ROOT, "contracts")
DATA = os.path.join(ROOT, "data")
RPC = "https://sepolia.base.org"
CHAIN_ID = 84532


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    day_int = int(today.replace("-", ""))
    deploy_file = os.path.join(CONTRACTS, "deployment.json")
    if not os.path.exists(deploy_file):
        print("journal: contract not deployed yet, skipping (run deploy.py).")
        return 0
    with open(deploy_file) as f:
        deploy = json.load(f)
    briefing_file = os.path.join(DATA, f"briefing-{today}.json")
    if not os.path.exists(briefing_file):
        print(f"journal: no briefing for {today}, skipping.", file=sys.stderr)
        return 0
    with open(briefing_file) as f:
        briefing = json.load(f)

    from eth_account import Account
    from web3 import Web3

    with open(os.path.join(CONTRACTS, ".agent-wallet.json")) as f:
        acct = Account.from_key(json.load(f)["private_key"])
    with open(os.path.join(CONTRACTS, "build", "AgentJournal.json")) as f:
        abi = json.load(f)["abi"]
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
    if not w3.is_connected():
        print("journal: RPC unreachable", file=sys.stderr)
        return 1
    contract = w3.eth.contract(address=deploy["address"], abi=abi)
    if contract.functions.writer().call() != acct.address:
        print("journal: wallet is not the contract writer", file=sys.stderr)
        return 1

    receipts = []
    nonce = w3.eth.get_transaction_count(acct.address)
    for pick in briefing["top_momentum"]:
        reason = (
            f"{pick['symbol']} momentum {pick['momentum_score']:+.2f}, "
            f"h24 {pick['price_change_h24']:+.2f}%, "
            f"vol24 ${pick['volume_h24']:,.0f}"
        )
        reason_hash = w3.keccak(text=reason)
        nav = None
        for t in briefing.get("cheapest_vs_nav", []):
            if t["symbol"] == pick["symbol"]:
                nav = t["nav_price"]
        price6 = int(round(pick["price_usd"] * 1e6))
        nav6 = int(round(nav * 1e6)) if nav else 0
        tx = contract.functions.logDecision(
            day_int, pick["symbol"], "BUY", reason_hash, price6, nav6
        ).build_transaction(
            {
                "from": acct.address,
                "nonce": nonce,
                "gas": 200_000,
                "gasPrice": w3.eth.gas_price,
                "chainId": CHAIN_ID,
            }
        )
        signed = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        nonce += 1
        receipts.append(
            {
                "symbol": pick["symbol"],
                "action": "BUY",
                "reason": reason,
                "tx": tx_hash.hex(),
                "block": receipt.blockNumber,
                "basescan": f"https://sepolia.basescan.org/tx/{tx_hash.hex()}",
            }
        )
        print(f"logged {pick['symbol']} BUY: {tx_hash.hex()[:18]}...")

    with open(os.path.join(DATA, f"journal-{today}.json"), "w") as f:
        json.dump(
            {
                "date": today,
                "contract": deploy["address"],
                "contract_basescan": deploy["basescan"],
                "entries": receipts,
            },
            f,
            indent=2,
        )
    print(f"journal: {len(receipts)} decisions logged onchain.")


if __name__ == "__main__":
    sys.exit(main())
