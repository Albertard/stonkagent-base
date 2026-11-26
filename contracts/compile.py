#!/usr/bin/env python3
"""Compile AgentJournal.sol and save ABI + bytecode.

Uses py-solc-x (downloads solc 0.8.20 on first run).
Output: contracts/build/AgentJournal.json
"""
import json
import os

import solcx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACTS = os.path.join(ROOT, "contracts")
BUILD = os.path.join(CONTRACTS, "build")
SOLC_VERSION = "0.8.20"


def main():
    os.makedirs(BUILD, exist_ok=True)
    try:
        solcx.get_solc_version()
    except Exception:
        print(f"installing solc {SOLC_VERSION} ...")
        solcx.install_solc(SOLC_VERSION)
    solcx.set_solc_version(SOLC_VERSION)
    with open(os.path.join(CONTRACTS, "AgentJournal.sol")) as f:
        source = f.read()
    compiled = solcx.compile_source(
        source, output_values=["abi", "bin"], solc_version=SOLC_VERSION
    )
    _, iface = compiled.popitem()
    out = {
        "contract": "AgentJournal",
        "solc": SOLC_VERSION,
        "abi": iface["abi"],
        "bytecode": iface["bin"],
    }
    with open(os.path.join(BUILD, "AgentJournal.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"compiled OK: {len(iface['abi'])} ABI entries, "
          f"bytecode {len(iface['bin']) // 2} bytes")


if __name__ == "__main__":
    main()
