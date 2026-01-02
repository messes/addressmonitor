# Contributing to Wallet Watch

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/wallet-watch.git
   cd wallet-watch
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests:
   ```bash
   pytest
   ```

4. Run linting:
   ```bash
   ruff check src/
   ruff format src/
   ```

5. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```

6. Push and create a pull request

## Adding a New Chain Provider

1. Create a new file in `src/wallet_watch/chains/`:
   ```python
   # src/wallet_watch/chains/mychain.py
   from wallet_watch.chains.base import ChainBase

   class MyChainProvider(ChainBase):
       name = "mychain"

       def validate_address(self, address: str) -> bool:
           # Implement address validation
           pass

       def subscribe(self, address: str, callback) -> None:
           # Implement subscription logic
           pass

       def unsubscribe(self, address: str) -> None:
           # Implement unsubscription
           pass

       def get_balance(self, address: str) -> float:
           # Return balance in native token
           pass

       def run(self) -> None:
           # Start event loop
           pass
   ```

2. Register in `src/wallet_watch/chains/__init__.py`:
   ```python
   from wallet_watch.chains.mychain import MyChainProvider

   PROVIDERS = {
       "solana": SolanaProvider,
       "mychain": MyChainProvider,  # Add here
   }
   ```

3. Add tests in `tests/chains/test_mychain.py`

## Adding a New Notifier

1. Create a new file in `src/wallet_watch/notifiers/`:
   ```python
   # src/wallet_watch/notifiers/mynotifier.py
   from wallet_watch.notifiers.base import NotifierBase

   class MyNotifier(NotifierBase):
       name = "mynotifier"

       def send(self, message: str, **kwargs) -> bool:
           # Send to default recipient
           pass

       def send_to(self, recipient: str, message: str, **kwargs) -> bool:
           # Send to specific recipient
           pass
   ```

2. Register in `src/wallet_watch/notifiers/__init__.py`

3. Add tests

## Code Style

- We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for public functions and classes

## Testing

- Write tests for new features
- Maintain test coverage
- Use pytest fixtures for common setup

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wallet_watch

# Run specific test file
pytest tests/test_config.py
```

## Pull Request Guidelines

1. **One feature per PR** - Keep pull requests focused
2. **Update documentation** - Update README if adding new features
3. **Add tests** - New features should have tests
4. **Follow commit conventions**:
   - `feat: add new feature`
   - `fix: fix bug`
   - `docs: update documentation`
   - `refactor: code refactoring`
   - `test: add tests`

## Questions?

Open an issue for any questions or discussions.
