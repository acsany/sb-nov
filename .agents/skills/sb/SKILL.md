---
name: sb
description: Interact with the secondbrain CLI. Use when secondbrain or notes are mentioned.
---

Save a summary of the current conversation as a note with a matching title,
using the `secondbrain` CLI (`secondbrain new "<title>" --body -`, body via stdin).

- Put these lines in the note body: `Session: $CODEX_THREAD_ID`, the project
  directory (`pwd`), and `Resume: codex resume $CODEX_THREAD_ID`.
- If a note containing this session id already exists in the notes directory
  (grep for the id), edit that file to extend the summary instead of creating a new note.
- Always reply with the file path of the note.