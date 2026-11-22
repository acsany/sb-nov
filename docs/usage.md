# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

The CLI exposes three subcommands so far:

```bash
uv run secondbrain new "My brilliant idea"   # save a note as markdown
uv run secondbrain list                      # list notes (newest first)
uv run secondbrain show 1                    # print the contents of note 1
```

Notes are plain markdown files named `YYYY-MM-DD-<slug>.md`. Each contains the
title as a heading followed by an ISO timestamp. If a file with that name
already exists, `-1`, `-2`, … is appended instead of overwriting it.

### Multi-line notes

Add a body with `--body` (short: `-b`), or `--body -` to read it from stdin:

```bash
uv run secondbrain new "Caching idea" --body $'Use an LRU.\n\nCheck memory limits.'
cat draft.md | uv run secondbrain new "Draft" --body -
```

If the title contains newlines, only its first line is used as the heading and
the filename slug; the remaining lines are put at the start of the body. `\r\n`
line endings are normalised to `\n`. The note is written as the heading, the
body (if any) and the timestamp, separated by blank lines.

With dev settings loaded:

```bash
uv run --env-file .env secondbrain new "My brilliant idea"
```

Or as a Python module:

```bash
uv run python -m secondbrain new "My brilliant idea"
```

`list` prints the full path of the notes directory followed by a numbered list of
the note filenames, newest first. `show N` prints the content of note `N` from that list; an
unknown number, an empty or missing notes directory exits with status 1 and an
error on stderr.

## Built-in help

Every command describes itself, with examples, so people and agents can
discover how to use it without reading the docs:

```bash
uv run secondbrain --help          # overview, workflow, environment variable
uv run secondbrain new --help      # titles, --body, stdin, multi-line examples
uv run secondbrain list --help
uv run secondbrain show --help     # numbering and error behaviour
```

Command results (paths, listings, note contents) are written to stdout; log
lines and errors go to stderr, so stdout can be piped or captured safely.

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
| `SECONDBRAIN_DIR` | `~/secondbrain/` | Directory where notes are stored |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.
