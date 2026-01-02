"""Base class for blockchain providers."""

from abc import ABC, abstractmethod
from typing import Callable, Any


class ChainBase(ABC):
    """Abstract base class for blockchain providers."""

    name: str = "base"

    def __init__(self, api_key: str = "", rpc_url: str = "", **kwargs):
        self.api_key = api_key
        self.rpc_url = rpc_url
        self.subscriptions: dict[str, list[Callable]] = {}

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Validate if an address is valid for this chain.

        Args:
            address: The wallet address to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    def subscribe(self, address: str, callback: Callable) -> None:
        """Subscribe to transactions for an address.

        Args:
            address: The wallet address to watch
            callback: Function to call with Transaction when activity detected
        """
        pass

    @abstractmethod
    def unsubscribe(self, address: str) -> None:
        """Unsubscribe from an address.

        Args:
            address: The wallet address to stop watching
        """
        pass

    @abstractmethod
    def get_balance(self, address: str) -> float:
        """Get the native token balance for an address.

        Args:
            address: The wallet address

        Returns:
            Balance in native token units
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """Start the provider's event loop.

        This method should block and process incoming transactions.
        """
        pass

    def add_callback(self, address: str, callback: Callable) -> None:
        """Add a callback for an address."""
        if address not in self.subscriptions:
            self.subscriptions[address] = []
        self.subscriptions[address].append(callback)

    def remove_callbacks(self, address: str) -> None:
        """Remove all callbacks for an address."""
        if address in self.subscriptions:
            del self.subscriptions[address]

    def notify_callbacks(self, address: str, transaction: Any) -> None:
        """Notify all callbacks for an address."""
        if address in self.subscriptions:
            for callback in self.subscriptions[address]:
                try:
                    callback(transaction)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Callback error: {e}")
