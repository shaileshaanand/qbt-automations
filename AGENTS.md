# Agent Instructions for qb-automations

This document provides guidelines and instructions for AI agents working on the `qb-automations` repository.

## 1. Project Overview
`qb-automations` is a Python-based automation tool for managing qBittorrent instances. It runs as a containerized application, automatically tagging torrents (private/public) and adjusting upload limits based on age.
- **Language**: Python 3.13+
- **Dependency Manager**: [uv](https://github.com/astral-sh/uv)
- **Build System**: Docker + Nuitka
- **Main Entry Point**: `main.py`

## 2. Build, Lint, and Test Commands

### Dependency Management
This project uses `uv` for fast Python package management.
- **Install dependencies**:
  ```bash
  uv sync
  ```
- **Add a dependency**:
  ```bash
  uv add <package_name>
  ```

### Running Locally
To run the automation script locally:
```bash
uv run main.py
```
*Note: Ensure environment variables (QBITTORRENT_HOST, etc.) are set or rely on defaults in `main.py`.*

### Linting and Formatting
The project uses `ruff` for both linting and formatting.
- **Lint (Check)**:
  ```bash
  uv run ruff check .
  ```
- **Lint (Fix)**:
  ```bash
  uv run ruff check --fix .
  ```
- **Format**:
  ```bash
  uv run ruff format .
  ```

### Testing
**Current Status**: There are currently no unit tests in the repository.
- If creating tests, use `pytest`.
- **Run Tests** (Future):
  ```bash
  uv run pytest
  ```
- **Run Single Test** (Future):
  ```bash
  uv run pytest path/to/test_file.py::test_function_name
  ```

### Docker Build
The project builds a standalone Alpine-based container using Nuitka.
- **Build Image**:
  ```bash
  docker build -t qb-automations .
  ```

## 3. Code Style & Conventions

### General
- **Python Version**: Target Python 3.13+.
- **Formatting**: Strictly follow `ruff` defaults.
- **Type Hinting**: Use Python type hints (PEP 484) for all function arguments and return values.
  ```python
  def is_private_torrent(torrent: TorrentDictionary) -> bool:
  ```

### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`

### Imports
- Group imports: Standard library first, then third-party, then local.
- Unused imports should be removed (handled by `ruff`).

### Error Handling
- Use specific exception handling where possible (e.g., `qbittorrentapi.LoginFailed`).
- Do not suppress errors silently; log them.

### Logging
- **DO NOT** use `print()`. Use the `logging` module.
- Log levels:
  - `DEBUG`: Detailed information for diagnosis (e.g., specific torrent details).
  - `INFO`: General operational events (e.g., "Created 'private' tag").
  - `ERROR`: Failures (e.g., login failed).
- Formatting: `logging.info(f"Message with {variable}")`

### Structure
- Keep logic modular. Separate qBittorrent API interactions from business logic where possible.
- `main.py` orchestrates the scheduling and execution.

## 4. Configuration
Configuration is handled via environment variables. When adding new configuration options:
1.  Add a default value in `main.py` using `os.getenv`.
2.  Update the `README.md` configuration table.
3.  Update `.env.example`.

## 5. Development Workflow
1.  **Understand**: Read `README.md` and `main.py` to grasp the current logic.
2.  **Lint**: Always run `uv run ruff check .` before submitting changes.
3.  **Verify**: creating a new feature? Ensure it doesn't break existing tagging logic.
