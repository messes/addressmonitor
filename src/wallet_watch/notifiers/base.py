"""Base class for notification providers."""

from abc import ABC, abstractmethod
from typing import Any


class NotifierBase(ABC):
    """Abstract base class for notification providers."""

    name: str = "base"

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def send(self, message: str, **kwargs) -> bool:
        """Send a notification.

        Args:
            message: The message to send
            **kwargs: Additional provider-specific options

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def send_to(self, recipient: str, message: str, **kwargs) -> bool:
        """Send a notification to a specific recipient.

        Args:
            recipient: The recipient identifier (chat_id, channel, etc.)
            message: The message to send
            **kwargs: Additional provider-specific options

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    def format_message(self, message: str) -> str:
        """Format message for this notifier.

        Override in subclasses for provider-specific formatting.
        """
        return message
