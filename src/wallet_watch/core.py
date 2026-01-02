"""Core orchestration for Wallet Watch."""

import logging
from typing import Any

from wallet_watch.config import Config
from wallet_watch.models import Transaction
from wallet_watch.chains import get_chain_provider
from wallet_watch.notifiers import get_notifier
from wallet_watch.storage import get_storage


logger = logging.getLogger(__name__)


class WalletWatch:
    """Main wallet watcher orchestrator."""

    def __init__(self, config: Config):
        self.config = config
        self.chains: dict[str, Any] = {}
        self.notifiers: dict[str, Any] = {}
        self.storage = None
        self._setup()

    def _setup(self):
        """Initialize chains, notifiers, and storage."""
        # Setup storage
        self.storage = get_storage(self.config.storage)
        logger.info(f"Storage initialized: {self.config.storage.type}")

        # Setup chain providers
        for chain_config in self.config.chains:
            try:
                provider = get_chain_provider(
                    chain_config.name,
                    api_key=chain_config.api_key,
                    rpc_url=chain_config.rpc_url,
                    webhook_id=chain_config.webhook_id,
                    webhook_url=chain_config.webhook_url,
                    webhook_secret=chain_config.webhook_secret,
                )
                self.chains[chain_config.name] = provider
                logger.info(f"Chain provider initialized: {chain_config.name}")
            except Exception as e:
                logger.error(f"Failed to initialize chain {chain_config.name}: {e}")

        # Setup notifiers
        for notifier_config in self.config.notifiers:
            try:
                notifier = get_notifier(
                    notifier_config.type,
                    bot_token=notifier_config.bot_token,
                    webhook_url=notifier_config.webhook_url,
                    chat_id=notifier_config.chat_id,
                )
                self.notifiers[notifier_config.type] = notifier
                logger.info(f"Notifier initialized: {notifier_config.type}")
            except Exception as e:
                logger.error(f"Failed to initialize notifier {notifier_config.type}: {e}")

    def _should_notify(self, tx: Transaction) -> bool:
        """Check if transaction passes global filters."""
        filters = self.config.filters

        # Check minimum USD value
        if filters.min_usd_value > 0:
            if tx.amount_usd is None or tx.amount_usd < filters.min_usd_value:
                return False

        # Check transaction type
        if filters.tx_types:
            if tx.tx_type not in filters.tx_types:
                return False

        return True

    def _handle_transaction(self, tx: Transaction, watch_config):
        """Handle incoming transaction."""
        logger.info(f"New transaction: {tx.signature[:16]}... on {tx.chain}")

        # Check filters
        if not self._should_notify(tx):
            logger.debug(f"Transaction filtered out: {tx.signature[:16]}...")
            return

        # Format message
        message = tx.to_message(label=watch_config.label)

        # Send to configured notifiers
        for notifier_name in watch_config.notify:
            if notifier_name in self.notifiers:
                try:
                    self.notifiers[notifier_name].send(message)
                    logger.info(f"Notification sent via {notifier_name}")
                except Exception as e:
                    logger.error(f"Failed to send notification via {notifier_name}: {e}")

        # Store transaction
        if self.storage:
            self.storage.save_transaction(tx)

    def run(self):
        """Start watching addresses."""
        if not self.config.watches:
            logger.warning("No watches configured. Add watches to config.yaml")

        # Subscribe to all watches
        for watch in self.config.watches:
            chain_name = watch.chain

            if chain_name not in self.chains:
                logger.error(f"Chain not configured: {chain_name}")
                continue

            chain = self.chains[chain_name]

            if not chain.validate_address(watch.address):
                logger.error(f"Invalid address for {chain_name}: {watch.address}")
                continue

            logger.info(f"Watching {watch.label or watch.address} on {chain_name}")

            # Subscribe with callback
            chain.subscribe(
                address=watch.address,
                callback=lambda tx, w=watch: self._handle_transaction(tx, w),
            )

        # Start all chain providers (blocking)
        logger.info(f"Watching {len(self.config.watches)} addresses...")

        # Run the first chain's event loop (they typically share one)
        if self.chains:
            first_chain = list(self.chains.values())[0]
            first_chain.run(
                host=self.config.server.host,
                port=self.config.server.port,
            )
