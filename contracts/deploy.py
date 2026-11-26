#!/usr/bin/env python3
"""Deploy AgentJournal to Base Sepolia testnet.

Wallet: a FRESH agent-owned testnet wallet (NOT Albert's). The private key
lives only in contracts/.agent-wallet.json (0600, gitignored, never shared,
never committed, never printed). Testnet ETH has $0 value.
Funding: Base Sepolia faucet (see faucet.py / manual step if needed).
Output: contracts/deployment.json (address, tx hash, Basescan link).
"""
import json
import os
import stat
import sys

from eth_account import Account
from web3 import Web3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACTS = os.path.join(ROOT, "contracts")
RPC = "https://sepolia.base.org"
CHAIN_ID = 84532
WALLET_FILE = os.path.join(CONTRACTS, ".agent-wallet.json")
BUILD_FILE = os.path.join(CONTRACTS, "build", "AgentJournal.json")
DEPLOY_FILE = os.path.join(CONTRACTS, "deployment.json")


def load_or_create_wallet():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE) as f:
            data = json.load(f)
        return Account.from_key(data["private_key"])
    acct = Account.create()
    with open(WALLET_FILE, "w") as f:
        json.dump({"address": acct.address, "private_key": acct.key.hex()}, f)
    os.chmod(WALLET_FILE, stat.S_IRUSR | stat.S_IWUSR)
    print(f"created fresh agent testnet wallet: {acct.address}")
    return acct


def main():
    acct = load_or_create_wallet()
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
    if not w3.is_connected():
        print("ERROR: cannot reach Base Sepolia RPC", file=sys.stderr)
        sys.exit(1)
    bal = w3.eth.get_balance(acct.address)
    print(f"agent wallet: {acct.address}")
    print(f"balance: {w3.from_wei(bal, 'ether')} ETH (Base Sepolia)")
    if bal == 0:
        print("UNFUNDED: get testnet ETH from the Base Sepolia faucet first.",
              file=sys.stderr)
        print("Try: python3 contracts/faucet.py", file=sys.stderr)
        sys.exit(2)

    with open(BUILD_FILE) as f:
        build = json.load(f)
    contract = w3.eth.contract(abi=build["abi"], bytecode=build["bytecode"])
    tx = contract.constructor().build_transaction(
        {
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 500_000,
            "gasPrice": w3.eth.gas_price,
            "chainId": CHAIN_ID,
        }
    )
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"deploy tx sent: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    addr = receipt.contractAddress
    print(f"AgentJournal deployed at: {addr}")
    print(f"block: {receipt.blockNumber}, gas used: {receipt.gasUsed}")
    info = {
        "network": "Base Sepolia",
        "chain_id": CHAIN_ID,
        "contract": "AgentJournal",
        "address": addr,
        "deployer": acct.address,
        "deploy_tx": tx_hash.hex(),
        "block": receipt.blockNumber,
        "basescan": f"https://sepolia.basescan.org/address/{addr}",
        "abi_file": "contracts/build/AgentJournal.json",
    }
    with open(DEPLOY_FILE, "w") as f:
        json.dump(info, f, indent=2)
    print(f"deployment info saved to {DEPLOY_FILE}")


if __name__ == "__main__":
    main()
