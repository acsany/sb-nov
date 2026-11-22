"""Interactive Markdown note browser and editor."""

from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, OptionList, Static, TextArea

from secondbrain.notes import create_note, list_note_files, read_note


class NoteList(OptionList):
    """Highlight notes to preview them and press Enter to edit."""

    BINDINGS = [("enter", "edit", "Edit")]

    class Edit(Message):
        """Request editing the highlighted note."""

    def action_edit(self):
        self.post_message(self.Edit())


class NotesApp(App):
    """Browse and edit the CLI's Markdown files."""

    CSS = """
    Screen { layout: horizontal; }
    #sidebar { width: 32%; min-width: 16; border-right: solid $primary; }
    NoteList, TextArea { height: 1fr; }
    Button { width: 100%; }
    #header { padding: 0 1; background: $boost; }
    #save, #cancel { display: none; }
    """

    def __init__(self, directory: Path):
        super().__init__()
        self.directory = directory
        self.files: list[Path] = []
        self.path: Path | None = None
        self.original = ""
        self.trailer = ""
        self.editing = False
        self.started = datetime.now()

    def compose(self) -> ComposeResult:
        with Vertical(id="sidebar"):
            yield NoteList()
            yield Button("Create", id="create")
            yield Button("Save", variant="primary", id="save")
            yield Button("Cancel", id="cancel")
        with Vertical():
            yield Static(id="header")
            yield TextArea(read_only=True, tab_behavior="focus")

    def on_mount(self):
        self.refresh_notes()

    def refresh_notes(self, select: Path | None = None):
        self.files = list_note_files(self.directory)
        listing = self.query_one(NoteList)
        listing.clear_options().add_options(
            Text(f"{number}. {path.name}") for number, path in enumerate(self.files, 1)
        )
        if self.files:
            listing.highlighted = (
                self.files.index(select) if select in self.files else 0
            )
        self.preview()
        (listing if self.files else self.query_one("#create")).focus()

    @on(OptionList.OptionHighlighted)
    def preview(self):
        if self.editing:
            return
        index = self.query_one(NoteList).highlighted
        self.path = None
        self.trailer = ""
        editor = self.query_one(TextArea)
        header = self.query_one("#header", Static)
        if index is None:
            editor.load_text("")
            header.update("No notes")
            return
        path = self.files[index]
        try:
            self.original = read_note(path)
            timestamp = datetime.fromtimestamp(path.stat().st_mtime).isoformat(
                timespec="seconds"
            )
        except (OSError, UnicodeError) as error:
            editor.load_text("")
            header.update(f"Note {index + 1} · Unable to read")
            self.notify(str(error), severity="error")
            return
        self.path = path
        content, separator, tail = self.original.rpartition("\n\n")
        try:
            datetime.fromisoformat(tail.strip())
        except ValueError:
            pass
        else:
            if separator:
                timestamp = tail.strip()
                self.trailer = separator + tail
        editor.load_text(content if self.trailer else self.original)
        header.update(f"Note {index + 1} · {timestamp}")

    def set_editing(self, editing: bool):
        self.editing = editing
        self.query_one(NoteList).disabled = editing
        editor = self.query_one(TextArea)
        editor.read_only = not editing
        self.query_one("#create").display = not editing
        for selector in ("#save", "#cancel"):
            self.query_one(selector).display = editing
        if editing:
            editor.focus()

    @on(NoteList.Edit)
    def edit(self):
        if self.path is not None:
            self.set_editing(True)

    @on(Button.Pressed, "#create")
    def create(self):
        self.set_editing(True)
        self.path = None
        self.started = datetime.now().replace(microsecond=0)
        self.query_one("#header", Static).update(
            f"New note · {self.started.isoformat()}"
        )
        self.query_one(TextArea).load_text("")

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.set_editing(False)
        self.preview()
        (self.query_one(NoteList) if self.files else self.query_one("#create")).focus()

    @on(Button.Pressed, "#save")
    def save(self):
        draft = self.query_one(TextArea).text
        path = self.path
        try:
            if path is None:
                title, _, body = draft.strip().partition("\n")
                title = title.removeprefix("# ").strip()
                if not title:
                    self.notify("Enter a title on the first line.", severity="warning")
                    return
                path = create_note(title, self.directory, self.started, body)
            elif read_note(path) != self.original:
                self.notify(
                    "The file changed on disk. Cancel to reload.", severity="error"
                )
                return
            else:
                with NamedTemporaryFile(
                    dir=path.parent,
                    delete=False,
                    delete_on_close=False,
                    mode="w",
                    encoding="utf-8",
                ) as handle:
                    temporary = Path(handle.name)
                    try:
                        handle.write(draft + self.trailer)
                        handle.close()
                        temporary.chmod(path.stat().st_mode)
                        temporary.replace(path)
                    finally:
                        temporary.unlink(missing_ok=True)
        except (OSError, UnicodeError) as error:
            self.notify(str(error), severity="error")
            return
        self.set_editing(False)
        self.refresh_notes(self.directory / path.name)
