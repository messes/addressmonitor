# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run the application
wallet-watch start                    # Start with default config.yaml
wallet-watch start -c myconfig.yaml   # Start with custom config
wallet-watch start -l DEBUG           # Start with debug logging

# Other CLI commands
wallet-watch validate                 # Validate config file
wallet-watch init                     # Create example config.yaml
wallet-watch check <address>          # Validate a wallet address
wallet-watch health                   # Health check endpoint

# Testing
pytest                                # Run all tests
pytest tests/test_chains.py           # Run specific test file
pytest --cov=wallet_watch             # Run with coverage

# Linting
ruff check src/
ruff format src/
```

## Architecture

This is a Python blockchain wallet monitoring service that watches wallet addresses and sends notifications on transactions.

### Core Components

- **`core.py`** - `WalletWatch` orchestrator that coordinates chains, notifiers, and storage. Entry point is `run()` which subscribes to watches and starts the event loop.

- **`config.py`** - Pydantic-based configuration with YAML loading. Supports `${ENV_VAR}` expansion in config values.

- **`cli.py`** - Click-based CLI. The `start` command loads config and runs `WalletWatch.run()`.

### Plugin Architecture

The codebase uses a registry pattern for extensibility:

**Chains** (`src/wallet_watch/chains/`):
- `ChainBase` abstract class defines the interface: `validate_address()`, `subscribe()`, `unsubscribe()`, `get_balance()`, `run()`
- Implementations register in `PROVIDERS` dict in `__init__.py`
- `SolanaProvider` uses Helius webhooks via Flask server to receive transactions

**Notifiers** (`src/wallet_watch/notifiers/`):
- `NotifierBase` abstract class defines: `send()`, `send_to()`
- Implementations register in `NOTIFIERS` dict in `__init__.py`
- Currently: `TelegramNotifier`, `WebhookNotifier`

**Storage** (`src/wallet_watch/storage/`):
- `StorageBase` abstract class for transaction persistence
- `STORAGE_PROVIDERS` dict with optional PostgreSQL support
- Default: SQLite

### Data Flow

1. Config loaded from `config.yaml` with env var expansion
2. `WalletWatch` initializes chain providers, notifiers, and storage
3. For each watch config, subscribes address with callback to chain provider
4. Chain provider (e.g., Solana) runs Flask webhook server
5. On incoming webhook, parses transaction, notifies callbacks
6. Callback checks filters, formats message, sends via notifiers, stores transaction

### Adding New Providers

New chain provider:
1. Create `src/wallet_watch/chains/mychain.py` extending `ChainBase`
2. Register in `src/wallet_watch/chains/__init__.py` PROVIDERS dict

New notifier:
1. Create `src/wallet_watch/notifiers/mynotifier.py` extending `NotifierBase`
2. Register in `src/wallet_watch/notifiers/__init__.py` NOTIFIERS dict

## Key Environment Variables

- `HELIUS_API_KEY` - Helius API for Solana
- `HELIUS_WEBHOOK_ID` - Helius webhook ID
- `TELEGRAM_BOT_TOKEN` - Telegram notifications
- `WEBHOOK_SECRET` - Auth header for incoming webhooks
