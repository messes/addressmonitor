"""Solana blockchain provider using Helius."""

import json
import logging
import time
from datetime import datetime
from typing import Callable

import base58
import requests
from flask import Flask, request, jsonify

from wallet_watch.chains.base import ChainBase
from wallet_watch.models import Transaction


logger = logging.getLogger(__name__)


class SolanaProvider(ChainBase):
    """Solana blockchain provider using Helius for webhooks."""

    name = "solana"

    def __init__(self, api_key: str = "", rpc_url: str = "", **kwargs):
        super().__init__(api_key=api_key, rpc_url=rpc_url, **kwargs)

        self.helius_api_key = api_key
        self.base_url = rpc_url or f"https://mainnet.helius-rpc.com/?api-key={api_key}"
        self.webhook_id = kwargs.get("webhook_id", "")
        self.webhook_secret = kwargs.get("webhook_secret", "")
        self.webhook_url = kwargs.get("webhook_url", "")

        # Flask app for receiving webhooks
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes for webhook handling."""

        @self.app.route("/webhook", methods=["POST"])
        def handle_webhook():
            # Verify auth header if configured
            if self.webhook_secret:
                auth = request.headers.get("Authorization", "")
                if auth != self.webhook_secret:
                    return jsonify({"error": "Unauthorized"}), 401

            try:
                data = request.get_json()
                self._process_webhook_data(data)
                return jsonify({"status": "ok"}), 200
            except Exception as e:
                logger.error(f"Webhook processing error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "healthy"}), 200

    def _process_webhook_data(self, data: list | dict):
        """Process incoming webhook data from Helius."""
        if isinstance(data, dict):
            data = [data]

        for tx_data in data:
            try:
                # Extract transaction info
                signature = tx_data.get("signature", "")
                description = tx_data.get("description", "")
                tx_type = tx_data.get("type", "unknown")
                timestamp = tx_data.get("timestamp")

                # Find which watched address this relates to
                account_data = tx_data.get("accountData", [])
                native_transfers = tx_data.get("nativeTransfers", [])
                token_transfers = tx_data.get("tokenTransfers", [])

                # Collect all addresses involved
                addresses_involved = set()
                for acc in account_data:
                    addresses_involved.add(acc.get("account", ""))
                for transfer in native_transfers:
                    addresses_involved.add(transfer.get("fromUserAccount", ""))
                    addresses_involved.add(transfer.get("toUserAccount", ""))
                for transfer in token_transfers:
                    addresses_involved.add(transfer.get("fromUserAccount", ""))
                    addresses_involved.add(transfer.get("toUserAccount", ""))

                # Notify subscribers
                for address in addresses_involved:
                    if address in self.subscriptions:
                        tx = Transaction(
                            signature=signature,
                            chain="solana",
                            address=address,
                            tx_type=tx_type,
                            description=description,
                            timestamp=datetime.fromtimestamp(timestamp) if timestamp else None,
                            raw=tx_data,
                        )
                        self.notify_callbacks(address, tx)

            except Exception as e:
                logger.error(f"Error processing transaction: {e}")

    def validate_address(self, address: str) -> bool:
        """Validate Solana address format."""
        try:
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        except Exception:
            return False

    def subscribe(self, address: str, callback: Callable) -> None:
        """Subscribe to transactions for an address."""
        if not self.validate_address(address):
            raise ValueError(f"Invalid Solana address: {address}")

        self.add_callback(address, callback)
        logger.info(f"Subscribed to Solana address: {address}")

        # Update Helius webhook with new address list
        self._update_webhook()

    def unsubscribe(self, address: str) -> None:
        """Unsubscribe from an address."""
        self.remove_callbacks(address)
        logger.info(f"Unsubscribed from Solana address: {address}")

        # Update Helius webhook
        self._update_webhook()

    def _update_webhook(self):
        """Update Helius webhook with current address list."""
        if not self.webhook_id or not self.helius_api_key:
            logger.warning("Webhook ID or API key not configured, skipping webhook update")
            return

        url = f"https://api.helius.xyz/v0/webhooks/{self.webhook_id}?api-key={self.helius_api_key}"

        addresses = list(self.subscriptions.keys())

        payload = {
            "webhookURL": self.webhook_url,
            "transactionTypes": ["Any"],
            "accountAddresses": addresses,
            "webhookType": "enhanced",
        }

        if self.webhook_secret:
            payload["authHeader"] = self.webhook_secret

        try:
            response = requests.put(url, json=payload)
            response.raise_for_status()
            logger.info(f"Helius webhook updated with {len(addresses)} addresses")
        except Exception as e:
            logger.error(f"Failed to update Helius webhook: {e}")

    def get_balance(self, address: str) -> float:
        """Get SOL balance for an address."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address],
        }

        try:
            response = requests.post(self.base_url, json=payload)
            result = response.json()
            lamports = result.get("result", {}).get("value", 0)
            return lamports / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0

    def get_recent_transactions(self, address: str, limit: int = 10) -> list[dict]:
        """Get recent transactions for an address."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [address, {"limit": limit}],
        }

        try:
            response = requests.post(self.base_url, json=payload)
            result = response.json()
            return result.get("result", [])
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []

    def run(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Start the webhook server."""
        logger.info(f"Starting Solana webhook server on {host}:{port}")
        self.app.run(host=host, port=port, threaded=True)
