import asyncio

from click.testing import CliRunner

from secondbrain.cli import cli
from secondbrain.notes import create_note, read_note
from secondbrain.tui import NotesApp


def test_default_command(monkeypatch):
    launched = []
    monkeypatch.setattr(NotesApp, "run", lambda self: launched.append(self))
    assert CliRunner().invoke(cli, []).exit_code == 0
    assert len(launched) == 1


def test_note_workflow(tmp_note_dir):
    from textual.widgets import TextArea

    path = create_note("First", tmp_note_dir)
    original = read_note(path)

    async def exercise():
        app = NotesApp(tmp_note_dir)
        async with app.run_test(size=(120, 30)) as pilot:
            editor = app.query_one(TextArea)
            assert editor.read_only and "First" in editor.text
            await pilot.press("enter")
            assert not editor.read_only
            editor.load_text("# Discard")
            await pilot.click("#cancel")
            assert editor.read_only and read_note(path) == original
            await pilot.press("enter")
            editor.load_text("# Revised")
            await pilot.click("#save")
            assert "# Revised" in read_note(path)
            assert original.splitlines()[-1] in read_note(path)
            await pilot.click("#create")
            editor.load_text("# Second\n\nBody")
            await pilot.click("#save")
            assert len(list(tmp_note_dir.glob("*.md"))) == 2
            assert editor.read_only and "Body" in editor.text

    asyncio.run(exercise())


def test_click_previews_without_editing(tmp_note_dir):
    from textual.widgets import Static, TextArea

    create_note("Older", tmp_note_dir)
    create_note("Newer", tmp_note_dir)

    async def exercise():
        app = NotesApp(tmp_note_dir)
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.click("NoteList", offset=(3, 2))
            editor = app.query_one(TextArea)
            assert editor.read_only and "Older" in editor.text
            assert "Note 2" in str(app.query_one("#header", Static).content)

    asyncio.run(exercise())


def test_empty_directory_cancel_draft(tmp_note_dir):
    async def exercise():
        app = NotesApp(tmp_note_dir)
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.click("#create")
            await pilot.click("#cancel")
            assert app.query_one("#create").display
            assert not list(tmp_note_dir.glob("*.md"))

    asyncio.run(exercise())
