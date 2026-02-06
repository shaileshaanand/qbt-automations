# qb-automations

A lightweight, containerized Python automation tool for managing qBittorrent. It automatically tags torrents as `public` or `private` and adjusts upload limits based on torrent age to help you manage your ratio and bandwidth effectively.

## Features

*   **Smart Tagging:** Automatically detects and tags torrents as `private` or `public` by analyzing tracker messages (specifically looking for `[DHT]` status).
*   **Dynamic Upload Limits:** Automatically adjusts upload limits for `public` torrents to prioritize newer content and free up bandwidth for private trackers:
    *   **New (< 30 days):** 500 KB/s
    *   **Medium (30 days - 1 year):** 200 KB/s
    *   **Old (> 1 year):** 50 KB/s
*   **Force Resume:** Automatically force-resumes all torrents to bypass queue limits, unless they are explicitly tagged as `paused`.
*   **Scheduled Execution:** Runs automatically at a configurable interval (default: every 5 minutes).
*   **Optimized Performance:** Uses [Nuitka](https://nuitka.net/) to compile the Python code into a standalone C binary, resulting in faster startup, lower memory usage, and a smaller container footprint compared to standard Python images.
*   **Dockerized:** Built as a standalone, dependency-free Alpine container using Nuitka for minimal footprint.

## Usage

### Using Docker

The easiest way to run `qb-automations` is with Docker.

1.  **Run the container:**

    ```bash
    docker run -d \
      --name qb-automations \
      -e QBITTORRENT_HOST="192.168.1.100" \
      -e QBITTORRENT_PORT="8080" \
      -e QBITTORRENT_USERNAME="admin" \
      -e QBITTORRENT_PASSWORD="your_password" \
      -e QBT_INTERVAL="10" \
      -e LOG_LEVEL="INFO" \
      qb-automations:latest
    ```

### Configuration

All configuration is handled via environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `QBITTORRENT_HOST` | `localhost` | IP address or hostname of your qBittorrent instance. |
| `QBITTORRENT_PORT` | `8080` | The WebUI port. |
| `QBITTORRENT_USERNAME` | `admin` | Your WebUI username. |
| `QBITTORRENT_PASSWORD` | `adminadmin` | Your WebUI password. |
| `QBT_INTERVAL` | `5` | How often (in minutes) the automation runs. |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

## Development

To run or modify the script locally:

1.  **Install dependencies** (requires [uv](https://github.com/astral-sh/uv)):
    ```bash
    uv sync
    ```

2.  **Run the script:**
    ```bash
    uv run main.py
    ```

3.  **Build the Docker image:**
    ```bash
    docker build -t qb-automations .
    ```

## License

[MIT](LICENSE)
