# qb-automations

## Project Overview

`qb-automations` is a Python-based automation tool designed to manage qBittorrent instances. It interacts with the qBittorrent API to automatically tag torrents and adjust upload limits based on specific criteria.

**Key Features:**

*   **Automatic Tagging:** Scans torrents and tags them as `private` or `public` based on tracker status (specifically checking for "[DHT]" tracker messages).
*   **Dynamic Upload Limits:** Adjusts upload limits for torrents tagged as `public` based on their age:
    *   **< 30 days:** 500 KB/s
    *   **30 days - 1 year:** 200 KB/s
    *   **> 1 year:** 50 KB/s
*   **Scheduled Execution:** Runs the automation logic periodically (configurable, default is every 5 minutes).

## Technologies & Architecture

*   **Language:** Python 3.13+
*   **Dependency Management:** [uv](https://github.com/astral-sh/uv)
*   **Libraries:**
    *   `qbittorrent-api`: For interacting with qBittorrent.
    *   `schedule`: For running the periodic tasks.
*   **Build System:** Docker + Nuitka (compiles Python to a standalone executable).
*   **CI/CD:** Forgejo (suggested by `.forgejo` directory).

## Configuration

The application is configured via environment variables. A `.env.example` file is provided.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `QBITTORRENT_HOST` | `localhost` | Hostname or IP of the qBittorrent instance. |
| `QBITTORRENT_PORT` | `8080` | WebUI port of qBittorrent. |
| `QBITTORRENT_USERNAME` | `admin` | WebUI username. |
| `QBITTORRENT_PASSWORD` | `adminadmin` | WebUI password. |
| `QBT_INTERVAL` | `5` | Interval in minutes between automation runs. |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR). |

## Development

### Prerequisites

*   Python 3.13+
*   `uv` package manager

### Setup

1.  Install dependencies:
    ```bash
    uv sync
    ```

### Running Locally

You can run the script directly using Python:

```bash
uv run main.py
```

Ensure you have a qBittorrent instance available and configured in your environment variables.

### Linting

The project uses `ruff` for linting:

```bash
uv run ruff check .
```

### Building

The project uses `nuitka` to compile the Python script into a standalone executable. This is handled automatically within the Docker build process.

To build the Docker image:

```bash
docker build -t qb-automations .
```
