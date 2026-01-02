"""Configuration management for Wallet Watch."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ChainConfig(BaseModel):
    """Configuration for a blockchain provider."""

    name: str
    provider: str
    api_key: str = ""
    rpc_url: str = ""
    webhook_url: str = ""
    webhook_id: str = ""
    webhook_secret: str = ""


class NotifierConfig(BaseModel):
    """Configuration for a notification provider."""

    type: str
    bot_token: str = ""
    webhook_url: str = ""
    chat_id: str = ""


class WatchConfig(BaseModel):
    """Configuration for a wallet watch."""

    address: str
    chain: str
    label: str = ""
    notify: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)


class FilterConfig(BaseModel):
    """Global filter configuration."""

    min_usd_value: float = 0
    tx_types: list[str] = Field(default_factory=list)


class StorageConfig(BaseModel):
    """Storage configuration."""

    type: str = "sqlite"
    path: str = "./data/wallet_watch.db"
    url: str = ""


class ServerConfig(BaseModel):
    """Webhook server configuration."""

    port: int = int(os.getenv("PORT", "8080"))
    host: str = "0.0.0.0"
    secret: str = ""


class Config(BaseModel):
    """Main configuration."""

    chains: list[ChainConfig] = Field(default_factory=list)
    notifiers: list[NotifierConfig] = Field(default_factory=list)
    watches: list[WatchConfig] = Field(default_factory=list)
    filters: FilterConfig = Field(default_factory=FilterConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)


def expand_env_vars(value: Any) -> Any:
    """Recursively expand environment variables in config values.

    Supports ${VAR} and ${VAR:-default} syntax.
    """
    if isinstance(value, str):
        if value.startswith("${") and value.endswith("}"):
            inner = value[2:-1]
            # Support ${VAR:-default} syntax
            if ":-" in inner:
                env_var, default = inner.split(":-", 1)
                return os.getenv(env_var, default)
            return os.getenv(inner, "")
        return value
    elif isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [expand_env_vars(item) for item in value]
    return value


def load_config(config_path: str | Path = "config.yaml") -> Config:
    """Load configuration from YAML file."""
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    # Expand environment variables
    expanded_config = expand_env_vars(raw_config)

    return Config(**expanded_config)


def get_default_config() -> Config:
    """Get default configuration."""
    return Config(
        chains=[
            ChainConfig(
                name="solana",
                provider="helius",
                api_key=os.getenv("HELIUS_API_KEY", ""),
                webhook_id=os.getenv("HELIUS_WEBHOOK_ID", ""),
                webhook_url=os.getenv("WEBHOOK_URL", ""),
                webhook_secret=os.getenv("WEBHOOK_SECRET", ""),
            )
        ],
        notifiers=[
            NotifierConfig(
                type="telegram",
                bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            )
        ],
    )
