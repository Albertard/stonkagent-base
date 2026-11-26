#!/usr/bin/env python3
"""Base Sepolia faucet helper for the StonkAgent deployer wallet.

Situation (27 Nov 2026): every no-login Base Sepolia faucet needs a
browser step (captcha / wallet-connect / device attestation) that curl
cannot do. This script:
  1. prints the agent wallet address + current balance,
  2. lists the exact faucet options (fastest first),
  3. polls the balance until funded (or timeout).

Fastest path: a browser task (or Albert) opens the QuickNode faucet
(no account, no mainnet balance), pastes the address below, passes the
bot check, and claims. 0.01 ETH is far more than enough: deploy costs
~0.001 ETH and each daily journal write is ~50k gas at ~0.01 gwei.
"""
import json
import os
import sys
import time

from web3 import Web3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACTS = os.path.join(ROOT, "contracts")
RPC = "https://sepolia.base.org"

FAUCETS = [
    ("QuickNode (recommended, no account, no mainnet balance)",
     "https://faucet.quicknode.com/base-sepolia"),
    ("Coinbase faucet (Cloudflare-protected, use browser)",
     "https://www.coinbase.com/faucets/base-sepolia-faucet"),
    ("Chainlink faucet (wallet connect + captcha, 0.5 ETH)",
     "https://faucets.chain.link/base-sepolia"),
    ("Alchemy faucet (needs 0.001 mainnet ETH + activity — our wallet has none)",
     "https://www.alchemy.com/faucets/base-sepolia"),
]


def wallet_address():
    with open(os.path.join(CONTRACTS, ".agent-wallet.json")) as f:
        return json.load(f)["address"]


def main():
    addr = wallet_address()
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
    print(f"agent wallet: {addr}")
    print(f"balance: {w3.from_wei(w3.eth.get_balance(addr), 'ether')} ETH")
    print()
    print("Faucet options (open in a browser, paste the address above):")
    for name, url in FAUCETS:
        print(f"  - {name}\n    {url}")
    print()
    print("Polling for funding (Ctrl+C to stop)...")
    try:
        while True:
            bal = w3.eth.get_balance(addr)
            if bal > 0:
                print(f"FUNDED: {w3.from_wei(bal, 'ether')} ETH — run deploy.py")
                return 0
            time.sleep(30)
    except KeyboardInterrupt:
        print("stopped.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
