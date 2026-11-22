"""Business logic for note creation."""

from __future__ import annotations

import os
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path

DEFAULT_DIR_NAME = "secondbrain"
_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}")


def notes_dir() -> Path:
    """Return the notes directory, from `SECONDBRAIN_DIR` or `~/secondbrain`.

    Read lazily on every call so the environment stays authoritative.
    """
    return Path(
        os.environ.get("SECONDBRAIN_DIR", str(Path.home() / DEFAULT_DIR_NAME))
    ).expanduser()


def slugify(title: str) -> str:
    """Convert a title string into a filename-safe slug.

    Latin accents are folded to their ASCII base (`Café` -> `cafe`); other
    scripts are kept as-is (`日本` -> `日本`) rather than dropped, so that
    non-Latin titles stay distinguishable instead of all slugging to the
    same fallback.
    """
    # NFKD splits `é` into `e` + combining accent, so dropping the combining
    # marks (category Mn) leaves the ASCII base letter behind.
    decomposed = unicodedata.normalize("NFKD", title)
    slug = "".join(c for c in decomposed if not unicodedata.combining(c))
    slug = slug.lower()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"[\s-]+", "-", slug)
    slug = slug.strip("-_")
    return slug or "untitled"


def build_note_path(title: str, base_dir: Path, note_date: date) -> Path:
    """Build the full file path for a note, creating the directory if needed.

    If a file with the same name already exists, appends -1, -2, … to avoid
    overwriting.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(title)
    stem = f"{note_date.isoformat()}-{slug}"
    candidate = base_dir / f"{stem}.md"
    counter = 1
    # `exists()` follows symlinks, so a dangling one would look free while
    # exclusive creation still refuses it; `is_symlink()` closes that gap.
    while candidate.exists() or candidate.is_symlink():
        candidate = base_dir / f"{stem}-{counter}.md"
        counter += 1
    return candidate


def _clean_block(text: str) -> str:
    """Drop leading blank lines and trailing whitespace; blank text becomes ``""``."""
    return text.lstrip("\n").rstrip()


def split_title_body(title: str, body: str | None = None) -> tuple[str, str]:
    """Split raw user input into a single-line heading and a body.

    Line endings (`\\r\\n`, `\\r`) are normalised to `\\n`. The first non-blank
    line of `title` is the heading; any further lines of `title` become the start
    of the body, followed by the explicit `body`, separated by a blank line.

    Args:
        title: The title argument, which may contain newlines.
        body: Optional extra body text.

    Returns:
        A `(title, body)` tuple. Either part may be empty; the body never has
            leading blank lines or trailing whitespace.
    """
    lines = title.replace("\r\n", "\n").replace("\r", "\n").lstrip("\n").split("\n")
    heading = lines[0].strip()
    parts = [_clean_block("\n".join(lines[1:]))]
    if body is not None:
        parts.append(_clean_block(body.replace("\r\n", "\n").replace("\r", "\n")))
    return heading, "\n\n".join(p for p in parts if p)


def create_note(
    title: str,
    base_dir: Path,
    now: datetime | None = None,
    body: str | None = None,
) -> Path:
    """Create a markdown note file and return its absolute path.

    The note is `# <heading>`, the optional body, then an ISO timestamp. A
    multi-line `title` is split with `split_title_body`, so a newline can never
    leak into the heading or the filename.
    """
    now = now or datetime.now()
    heading, text = split_title_body(title, body)
    timestamp = now.replace(microsecond=0).isoformat()
    sections = [f"# {heading}", text, timestamp]
    content = "\n\n".join(s for s in sections if s) + "\n"
    while True:
        path = build_note_path(heading, base_dir, now.date())
        try:
            # Exclusive mode reserves the name atomically, so a concurrent
            # `new` that picked the same path can never be overwritten.
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError:
            continue  # lost the race; build_note_path now picks the next suffix
        return path.resolve()


def list_note_files(base_dir: Path) -> list[Path]:
    """Return the markdown notes in `base_dir`, newest first.

    `list` and `show` both number notes from this ordering, so the number
    printed by `list` is the one `show` accepts. Notes are ordered by the date
    in the filename, then by modification time (filenames carry no time of day,
    so the slug must not decide which same-day note is newer), then by name.
    Only regular files count; a directory named `*.md` is ignored.
    """

    def sort_key(path: Path) -> tuple[str, int, str]:
        match = _DATE_PREFIX.match(path.name)
        return (match.group() if match else "", path.stat().st_mtime_ns, path.name)

    notes = [p for p in base_dir.glob("*.md") if p.is_file()]
    return sorted(notes, key=sort_key, reverse=True)


def read_note(path: Path) -> str:
    """Read a note's contents, matching the UTF-8 encoding used to write it."""
    return path.read_text(encoding="utf-8")
