"""SQLite storage provider."""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from wallet_watch.storage.base import StorageBase


logger = logging.getLogger(__name__)


class SQLiteStorage(StorageBase):
    """SQLite storage provider."""

    name = "sqlite"

    def __init__(self, path: str = "./data/wallet_watch.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

        logger.info(f"SQLite storage initialized at {self.path}")

    def _init_tables(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL UNIQUE,
                chain TEXT NOT NULL,
                label TEXT,
                notify TEXT,
                filters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature TEXT NOT NULL UNIQUE,
                chain TEXT NOT NULL,
                address TEXT NOT NULL,
                tx_type TEXT,
                description TEXT,
                amount_usd REAL,
                raw TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_address
            ON transactions(address)
        """)

        self.conn.commit()

    def save_watch(self, address: str, chain: str, label: str = "", **kwargs) -> bool:
        """Save a watch configuration."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO watches (address, chain, label, notify, filters)
                VALUES (?, ?, ?, ?, ?)
            """, (
                address,
                chain,
                label,
                json.dumps(kwargs.get("notify", [])),
                json.dumps(kwargs.get("filters", {})),
            ))
            self.conn.commit()
            logger.debug(f"Saved watch: {address}")
            return True
        except Exception as e:
            logger.error(f"Failed to save watch: {e}")
            return False

    def get_watches(self, chain: str = None) -> list[dict]:
        """Get all watches."""
        try:
            cursor = self.conn.cursor()

            if chain:
                cursor.execute("SELECT * FROM watches WHERE chain = ?", (chain,))
            else:
                cursor.execute("SELECT * FROM watches")

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get watches: {e}")
            return []

    def delete_watch(self, address: str) -> bool:
        """Delete a watch by address."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM watches WHERE address = ?", (address,))
            self.conn.commit()
            logger.debug(f"Deleted watch: {address}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete watch: {e}")
            return False

    def save_transaction(self, transaction: Any) -> bool:
        """Save a transaction record."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO transactions
                (signature, chain, address, tx_type, description, amount_usd, raw)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.signature,
                transaction.chain,
                transaction.address,
                transaction.tx_type,
                transaction.description,
                transaction.amount_usd,
                json.dumps(transaction.raw) if transaction.raw else None,
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save transaction: {e}")
            return False

    def get_transactions(self, address: str = None, limit: int = 100) -> list[dict]:
        """Get transactions."""
        try:
            cursor = self.conn.cursor()

            if address:
                cursor.execute(
                    "SELECT * FROM transactions WHERE address = ? ORDER BY created_at DESC LIMIT ?",
                    (address, limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM transactions ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("SQLite connection closed")
