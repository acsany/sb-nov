# Flowcharts

## Package files and functions

Solid arrows show imports or calls as labeled. The dashed arrow shows which
function the installed command points to.

```mermaid
flowchart LR
    subgraph entry [Package setup and launch]
        init["__init__.py<br/>Empty package initializer"]
        module["__main__.py<br/>Imports and runs cli()"]
        script["pyproject.toml<br/>Registers the secondbrain command"]
    end

    subgraph command [Terminal interface]
        cli["cli.py<br/>cli(), new(), list_notes(), show()"]
        click_lib["Click<br/>Parsing and terminal I/O"]
        cli -->|imports| click_lib
    end

    subgraph logs [Logging]
        app["app.py<br/>configure_logging(), main()<br/>Standard library imports: sys, os"]
        logger["Loguru logger"]
        app -->|imports| logger
    end

    subgraph storage [Note storage]
        notes["notes.py<br/>notes_dir(), create_note()<br/>list_note_files(), read_note()<br/>Standard library imports:<br/>os, re, unicodedata, datetime, pathlib"]
        writing["create_note() calls:<br/>split_title_body() → _clean_block()<br/>build_note_path() → slugify()"]
        sorting["list_note_files() uses<br/>its nested sort_key()"]
        notes -->|write helpers| writing
        notes -->|sort helper| sorting
    end

    module -->|imports cli| cli
    script -.->|targets cli| cli
    cli -->|imports configure_logging| app
    cli -->|imports logger| logger
    cli -->|imports four note functions| notes
```

Both `cli.py` and `notes.py` also enable postponed annotations with
`from __future__ import annotations`. Within `app.py`, `main()` calls
`configure_logging()` and logs a greeting.

## Entry points and arguments

Both terminal entry points use the same commands. `--help` works on its own or
after a subcommand. `SECONDBRAIN_DIR` selects the notes folder and defaults to
`~/secondbrain/`. `LOG_LEVEL` and `LOG_FILE` configure logging.

```mermaid
flowchart LR
    installed["uv run secondbrain"] --> cli["cli.py → cli()<br/>Sets up logging for subcommands"]
    module["uv run python -m secondbrain<br/>Runs __main__.py"] --> cli

    cli --> capture["new TITLE<br/>Optional --body TEXT or -b TEXT<br/>Use - as the body to read from standard input"]
    cli --> listing["list<br/>No arguments"]
    cli --> display["show NUMBER<br/>Required integer from the list"]
    cli --> help["--help<br/>Click prints command usage"]

    capture --> write["new()<br/>Uses notes_dir() and create_note()<br/>Saves Markdown and prints its path"]
    listing --> find["list_notes()<br/>Uses notes_dir() and list_note_files()<br/>Prints a numbered list, newest first"]
    display --> read["show()<br/>Checks the number against list_note_files()<br/>Prints the result of read_note()"]
    display --- invalid["Missing folder, no notes,<br/>or number out of range<br/>Prints an error and exits with status 1"]
```

## Example user flow

Run these commands from the project folder. Use the number from the latest
listing when opening a note.

```mermaid
flowchart LR
    setup["Install dependencies<br/>uv sync"]
    capture["Capture an idea<br/>uv run secondbrain new<br/>#quot;Weekend ideas#quot;<br/>--body #quot;Try the new bakery.#quot;"]
    list["Find the note<br/>uv run secondbrain list"]
    read["Read the latest note<br/>uv run secondbrain show 1"]
    edit["Open the Markdown file<br/>in a text editor<br/>Use the path printed by new"]

    setup --> capture --> list --> read
    capture -->|Edit the note directly| edit
```
