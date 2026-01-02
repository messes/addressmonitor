"""Blockchain chain providers."""

from wallet_watch.chains.base import ChainBase
from wallet_watch.chains.solana import SolanaProvider

PROVIDERS = {
    "solana": SolanaProvider,
}


def get_chain_provider(name: str, **kwargs) -> ChainBase:
    """Get a chain provider by name."""
    if name not in PROVIDERS:
        raise ValueError(f"Unknown chain provider: {name}. Available: {list(PROVIDERS.keys())}")

    return PROVIDERS[name](**kwargs)


__all__ = ["ChainBase", "SolanaProvider", "get_chain_provider"]
