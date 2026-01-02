"""Notification providers."""

from wallet_watch.notifiers.base import NotifierBase
from wallet_watch.notifiers.telegram import TelegramNotifier
from wallet_watch.notifiers.webhook import WebhookNotifier

NOTIFIERS = {
    "telegram": TelegramNotifier,
    "webhook": WebhookNotifier,
}


def get_notifier(name: str, **kwargs) -> NotifierBase:
    """Get a notifier by name."""
    if name not in NOTIFIERS:
        raise ValueError(f"Unknown notifier: {name}. Available: {list(NOTIFIERS.keys())}")

    return NOTIFIERS[name](**kwargs)


__all__ = ["NotifierBase", "TelegramNotifier", "WebhookNotifier", "get_notifier"]
