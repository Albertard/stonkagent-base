// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AgentJournal
/// @notice StonkAgent's public decision log on Base Sepolia testnet.
/// @dev Every daily paper-trading decision (ticker, action, reason hash,
///      NAV price at decision time) is written here so anyone can verify
///      on Basescan that the agent actually ran and what it decided.
///      No funds, no real assets, no access control beyond the writer.
///      Paper trading simulation only. Not investment advice.
contract AgentJournal {
    struct Decision {
        uint256 day;          // YYYYMMDD, e.g. 20261126
        string ticker;        // e.g. "MRVLc"
        string action;        // "BUY" | "SELL" | "HOLD" (paper)
        bytes32 reasonHash;   // keccak256 of the human-readable reason text
        uint256 priceUsd;     // DEX price at decision time, 6 decimals (USDC)
        uint256 navPriceUsd;  // Chainlink NAV at decision time, 6 decimals (0 if none)
        uint256 timestamp;    // block.timestamp of the log
    }

    Decision[] public decisions;
    address public writer;

    event DecisionLogged(
        uint256 indexed day,
        string ticker,
        string action,
        bytes32 reasonHash,
        uint256 priceUsd,
        uint256 navPriceUsd
    );

    constructor() {
        writer = msg.sender;
    }

    /// @notice Log one paper decision. Only the deployer (the agent) may write.
    function logDecision(
        uint256 day,
        string calldata ticker,
        string calldata action,
        bytes32 reasonHash,
        uint256 priceUsd,
        uint256 navPriceUsd
    ) external {
        require(msg.sender == writer, "only writer");
        decisions.push(
            Decision({
                day: day,
                ticker: ticker,
                action: action,
                reasonHash: reasonHash,
                priceUsd: priceUsd,
                navPriceUsd: navPriceUsd,
                timestamp: block.timestamp
            })
        );
        emit DecisionLogged(day, ticker, action, reasonHash, priceUsd, navPriceUsd);
    }

    /// @notice Total decisions logged so far.
    function decisionCount() external view returns (uint256) {
        return decisions.length;
    }

    /// @notice Read one decision by index.
    function getDecision(uint256 index) external view returns (Decision memory) {
        return decisions[index];
    }
}
