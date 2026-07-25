"""Serialize functions for expression CLI output — handle file I/O.

Each ``serialize_*`` function writes a file and returns a path string
for the caller to print as a result.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any


def serialize_export_chapter(
    store: Any,
    chapter_expression: str,
    output: Path,
    clean: bool,
    _err: Callable[[str], None] | None = None,
) -> str:
    """Export a Chapter Expression manuscript to a file.

    Returns the output path string on success.
    Raises ``FileExistsError`` if the output already exists.
    """
    if output.exists():
        raise FileExistsError(str(output))
    text: str = (
        store.clean_export(chapter_expression)
        if clean
        else store._metadata_path(chapter_expression)
        .with_suffix(".md")
        .read_text(encoding="utf-8")
    )
    output.write_text(text, encoding="utf-8")
    if clean:
        msg = "Warning: clean export removes Scene markers and is not round-trip-safe."
        if _err:
            _err(msg)
        else:
            print(msg, file=sys.stderr)
    return str(output)


def serialize_export_book(
    store: Any,
    book_expression: str,
    output: Path,
) -> str:
    """Export a Book manuscript to a file.

    Returns the output path string on success.
    """
    store.export(book_expression, output)
    return str(output)
