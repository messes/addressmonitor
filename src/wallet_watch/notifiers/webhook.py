"""Generic webhook notification provider."""

import json
import logging

import requests

from wallet_watch.notifiers.base import NotifierBase


logger = logging.getLogger(__name__)


class WebhookNotifier(NotifierBase):
    """Generic HTTP webhook notification provider."""

    name = "webhook"

    def __init__(self, webhook_url: str = "", **kwargs):
        super().__init__(**kwargs)

        if not webhook_url:
            raise ValueError("webhook_url is required")

        self.webhook_url = webhook_url
        self.headers = kwargs.get("headers", {"Content-Type": "application/json"})
        self.method = kwargs.get("method", "POST").upper()

    def send(self, message: str, **kwargs) -> bool:
        """Send notification to webhook URL."""
        return self.send_to(self.webhook_url, message, **kwargs)

    def send_to(self, recipient: str, message: str, **kwargs) -> bool:
        """Send notification to a specific webhook URL."""
        try:
            payload = {
                "message": message,
                "timestamp": kwargs.get("timestamp"),
                **kwargs.get("extra", {}),
            }

            if self.method == "POST":
                response = requests.post(
                    recipient,
                    json=payload,
                    headers=self.headers,
                    timeout=10,
                )
            elif self.method == "GET":
                response = requests.get(
                    recipient,
                    params={"message": message},
                    headers=self.headers,
                    timeout=10,
                )
            else:
                logger.error(f"Unsupported HTTP method: {self.method}")
                return False

            response.raise_for_status()
            logger.debug(f"Webhook notification sent to {recipient}")
            return True

        except requests.exceptions.Timeout:
            logger.error(f"Webhook request timed out: {recipient}")
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook request failed: {e}")
            return False

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
