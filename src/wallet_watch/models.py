"""Data models for Wallet Watch."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """Represents a blockchain transaction."""

    signature: str
    chain: str
    address: str
    tx_type: str
    description: str
    amount_usd: float | None = None
    timestamp: datetime | None = None
    raw: dict | None = None

    def to_message(self, label: str = "") -> str:
        """Format transaction as notification message."""
        wallet_name = label or self.address[:8] + "..."

        lines = [
            f"<b>{self.tx_type.upper()}</b> on {self.chain.title()}",
            f"Wallet: {wallet_name}",
        ]

        if self.description:
            lines.append(f"\n{self.description}")

        if self.amount_usd:
            lines.append(f"Value: <b>${self.amount_usd:,.2f}</b>")

        # Add explorer link
        if self.chain == "solana":
            url = f"https://solscan.io/tx/{self.signature}"
            lines.append(f"\n<a href='{url}'>View on Solscan</a>")
        elif self.chain == "ethereum":
            url = f"https://etherscan.io/tx/{self.signature}"
            lines.append(f"\n<a href='{url}'>View on Etherscan</a>")

        return "\n".join(lines)
