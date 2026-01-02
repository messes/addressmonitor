"""Base class for storage providers."""

from abc import ABC, abstractmethod
from typing import Any


class StorageBase(ABC):
    """Abstract base class for storage providers."""

    name: str = "base"

    @abstractmethod
    def save_watch(self, address: str, chain: str, label: str = "", **kwargs) -> bool:
        """Save a watch configuration.

        Args:
            address: Wallet address
            chain: Blockchain name
            label: User-friendly label
            **kwargs: Additional fields

        Returns:
            True if saved successfully
        """
        pass

    @abstractmethod
    def get_watches(self, chain: str = None) -> list[dict]:
        """Get all watches, optionally filtered by chain.

        Args:
            chain: Optional chain filter

        Returns:
            List of watch configurations
        """
        pass

    @abstractmethod
    def delete_watch(self, address: str) -> bool:
        """Delete a watch by address.

        Args:
            address: Wallet address to delete

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    def save_transaction(self, transaction: Any) -> bool:
        """Save a transaction record.

        Args:
            transaction: Transaction object to save

        Returns:
            True if saved successfully
        """
        pass

    @abstractmethod
    def get_transactions(self, address: str = None, limit: int = 100) -> list[dict]:
        """Get transactions, optionally filtered by address.

        Args:
            address: Optional address filter
            limit: Maximum number of transactions to return

        Returns:
            List of transaction records
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close any open connections."""
        pass
