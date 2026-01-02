"""Storage providers."""

from wallet_watch.storage.base import StorageBase
from wallet_watch.storage.sqlite import SQLiteStorage
from wallet_watch.config import StorageConfig

STORAGE_PROVIDERS = {
    "sqlite": SQLiteStorage,
}

# Optional PostgreSQL support
try:
    from wallet_watch.storage.postgres import PostgresStorage
    STORAGE_PROVIDERS["postgres"] = PostgresStorage
except ImportError:
    pass


def get_storage(config: StorageConfig) -> StorageBase:
    """Get a storage provider from config."""
    storage_type = config.type

    if storage_type not in STORAGE_PROVIDERS:
        raise ValueError(f"Unknown storage type: {storage_type}. Available: {list(STORAGE_PROVIDERS.keys())}")

    if storage_type == "sqlite":
        return STORAGE_PROVIDERS[storage_type](path=config.path)
    elif storage_type == "postgres":
        return STORAGE_PROVIDERS[storage_type](url=config.url)

    return STORAGE_PROVIDERS[storage_type]()


__all__ = ["StorageBase", "SQLiteStorage", "get_storage"]
