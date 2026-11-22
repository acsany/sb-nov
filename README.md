# secondbrain

## Installation

Clone the repository, open the project directory, and install dependencies with uv.

```bash
uv sync
```

## Usage

```bash
uv run secondbrain new "My brilliant idea"          # save a note as markdown
uv run secondbrain new "Title" --body "More text"   # note with a body (or --body - for stdin)
uv run secondbrain list                             # list notes (newest first)
uv run secondbrain show 1                           # print the contents of note 1
uv run --env-file .env secondbrain list             # Development settings
uv run python -m secondbrain list                   # Python module
```

Notes are plain markdown files named `YYYY-MM-DD-<slug>.md`: the title as a heading, the optional body, then a timestamp. Existing files are never overwritten (`-1`, `-2`, … is appended). Results go to stdout and log lines to stderr. Run `uv run secondbrain --help` for details.

Console logs use local time to the second and three-letter level labels.

```text
2026-11-21 14:30:05 | INF | secondbrain.app:main:37 | Hello from secondbrain!
```

By default, the log file includes milliseconds, the UTC offset, full level names, and ` - ` before the message. `LOGURU_FORMAT` overrides the file format.

## Environment Variables

Copy the `.env.example` template to `.env` for development.

```bash
cp .env.example .env
```

| Variable | Default | Description |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | Console log level. Set it to `DEBUG` in `.env` for verbose console output. |
| `LOG_FILE` | `app.log` | Path to the log file. |
| `SECONDBRAIN_DIR` | `~/secondbrain/` | Directory where notes are stored. |

Load `.env` explicitly with `uv run --env-file .env secondbrain`. The application reads its settings from the process environment.

## Testing

```bash
uv run pytest        # Run tests
uv run pytest --cov  # Run tests with coverage
```

## Documentation

- [Flowcharts](docs/flowcharts.md) trace the CLI commands and how notes are stored.
- Open `secondbrain-tour.html` in a browser for an interactive walkthrough.
- The [Codex `sb` skill](.agents/skills/sb/SKILL.md) saves or updates a conversation summary as a Second Brain note.

```bash
uv run python scripts/serve_docs.py  # Preview locally and write to mkdocs.log
uv run mkdocs build                  # Build static docs in site/
```
