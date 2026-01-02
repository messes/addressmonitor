"""Tests for chain providers."""

import pytest

from wallet_watch.chains import get_chain_provider
from wallet_watch.chains.solana import SolanaProvider


class TestSolanaProvider:
    """Tests for Solana chain provider."""

    def test_validate_address_valid(self):
        """Test valid Solana address validation."""
        provider = SolanaProvider(api_key="test")

        # Valid Solana addresses (base58, 32 bytes decoded)
        valid_addresses = [
            "11111111111111111111111111111111",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "So11111111111111111111111111111111111111112",
        ]

        for addr in valid_addresses:
            assert provider.validate_address(addr), f"Should be valid: {addr}"

    def test_validate_address_invalid(self):
        """Test invalid Solana address validation."""
        provider = SolanaProvider(api_key="test")

        invalid_addresses = [
            "",
            "not-a-valid-address",
            "0x1234567890abcdef",  # Ethereum format
            "too-short",
            "!!!invalid!!!",
        ]

        for addr in invalid_addresses:
            assert not provider.validate_address(addr), f"Should be invalid: {addr}"

    def test_get_chain_provider(self):
        """Test getting chain provider by name."""
        provider = get_chain_provider("solana", api_key="test")
        assert isinstance(provider, SolanaProvider)
        assert provider.name == "solana"

    def test_get_chain_provider_unknown(self):
        """Test getting unknown chain provider raises error."""
        with pytest.raises(ValueError, match="Unknown chain provider"):
            get_chain_provider("unknown-chain")
