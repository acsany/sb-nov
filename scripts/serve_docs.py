#!/usr/bin/env python3
"""Serve MkDocs with output captured to mkdocs.log."""

import subprocess
import sys


def main():
    with (
        open("mkdocs.log", "w", encoding="utf-8") as log,
        subprocess.Popen(
            [sys.executable, "-m", "mkdocs", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        ) as proc,
    ):
        try:
            for line in proc.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
            return proc.wait()
        except KeyboardInterrupt:
            return 130
        finally:
            if proc.poll() is None:
                proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
