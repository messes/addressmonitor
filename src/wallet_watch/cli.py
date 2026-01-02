"""Command-line interface for Wallet Watch."""

import logging
import sys
from pathlib import Path

import click

from wallet_watch import __version__
from wallet_watch.config import load_config, get_default_config
from wallet_watch.core import WalletWatch


def setup_logging(level: str) -> None:
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.group()
@click.version_option(version=__version__)
def main():
    """Wallet Watch - Self-hosted blockchain wallet monitoring."""
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    default="config.yaml",
    help="Path to config file",
    type=click.Path(),
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    help="Logging level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
def start(config: str, log_level: str):
    """Start the wallet watcher."""
    setup_logging(log_level)
    logger = logging.getLogger("wallet_watch")

    try:
        if Path(config).exists():
            cfg = load_config(config)
            logger.info(f"Loaded config from {config}")
        else:
            cfg = get_default_config()
            logger.warning(f"Config file {config} not found, using defaults")

        watcher = WalletWatch(cfg)
        logger.info("Starting Wallet Watch...")
        watcher.run()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "-c",
    default="config.yaml",
    help="Path to config file",
    type=click.Path(),
)
def validate(config: str):
    """Validate configuration file."""
    try:
        cfg = load_config(config)
        click.echo(f"Config valid: {len(cfg.chains)} chains, {len(cfg.notifiers)} notifiers, {len(cfg.watches)} watches")
    except Exception as e:
        click.echo(f"Config invalid: {e}", err=True)
        sys.exit(1)


@main.command()
def health():
    """Health check for container orchestration."""
    click.echo("OK")
    sys.exit(0)


@main.command()
@click.argument("address")
@click.option("--chain", "-c", default="solana", help="Blockchain name")
def check(address: str, chain: str):
    """Check if an address is valid."""
    from wallet_watch.chains import get_chain_provider

    try:
        provider = get_chain_provider(chain)
        if provider.validate_address(address):
            click.echo(f"Valid {chain} address: {address}")
        else:
            click.echo(f"Invalid {chain} address: {address}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def init():
    """Initialize a new config file."""
    config_path = Path("config.yaml")

    if config_path.exists():
        if not click.confirm("config.yaml already exists. Overwrite?"):
            return

    example_config = """# Wallet Watch Configuration
# See https://github.com/yourusername/wallet-watch for documentation

chains:
  - name: solana
    provider: helius
    api_key: ${HELIUS_API_KEY}

notifiers:
  - type: telegram
    bot_token: ${TELEGRAM_BOT_TOKEN}

watches:
  - address: "YourWalletAddressHere"
    chain: solana
    label: "My Wallet"
    notify: [telegram]

filters:
  min_usd_value: 0
  tx_types: []  # empty = all types

storage:
  type: sqlite
  path: ./data/wallet_watch.db

server:
  port: 8080
  host: "0.0.0.0"
"""

    config_path.write_text(example_config)
    click.echo(f"Created {config_path}")
    click.echo("Edit the file and add your API keys, then run: wallet-watch start")


if __name__ == "__main__":
    main()
