# secondbrain

## Installation

Clone the repository, open the project directory, and install dependencies with uv.

```bash
uv sync
```

## Usage

```bash
uv run secondbrain                  # CLI entry point
uv run --env-file .env secondbrain   # Development settings
uv run python -m secondbrain        # Python module
```

## Environment Variables

Copy the `.env.example` template to `.env` for development.

```bash
cp .env.example .env
```

| Variable | Default | Description |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | Console log level. Set it to `DEBUG` in `.env` for verbose console output. |
| `LOG_FILE` | `app.log` | Path to the log file. |

Load `.env` explicitly with `uv run --env-file .env secondbrain`. The application reads its settings from the process environment.

## Testing

```bash
uv run pytest        # Run tests
uv run pytest --cov  # Run tests with coverage
```

## Documentation

```bash
uv run python scripts/serve_docs.py  # Preview locally and write to mkdocs.log
uv run mkdocs build                  # Build static docs in site/
```
