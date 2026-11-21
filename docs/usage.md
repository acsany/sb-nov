# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run secondbrain                   # production defaults
uv run --env-file .env secondbrain    # dev settings
```

Or as a Python module:

```bash
uv run python -m secondbrain
```

Console logs use local time to the second and three-letter level labels.

```text
2026-11-21 14:30:05 | INF | secondbrain.app:main:37 | Hello from secondbrain!
```

By default, the log file includes milliseconds, the UTC offset, full level names, and ` - ` before the message. `LOGURU_FORMAT` overrides the file format.

## Environment Variables

| Variable    | Default    | Description                         |
|-------------|------------|-------------------------------------|
| `LOG_LEVEL` | `INFO`     | Console log level (DEBUG, INFO, …) |
| `LOG_FILE`  | `app.log`  | Path to the log file                |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.
