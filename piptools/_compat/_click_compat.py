"""
Compatibility helpers and wrappers for working with :external+click:doc:`click <index>`.
"""

from __future__ import annotations

import contextlib
import typing as _t

import click


def open_output_file(ctx: click.Context, filename: str) -> _t.BinaryIO:
    """
    Open a file with the desirable flags set for writing output.

    The file will be lazy and atomic unless it's stdout.
    """
    # open_file() returns a typing.IO , but we know it will be binary because of the
    # mode flag -- so type-ignore the assignment issue
    file: _t.BinaryIO = click.open_file(  # type: ignore[assignment]
        filename, "w+b", atomic=True, lazy=True
    )
    _defer_lazy_file_close(ctx, file)
    return file


def _defer_lazy_file_close(ctx: click.Context, fileobj: _t.BinaryIO) -> None:
    """Setup a click "lazy file" to close on exit."""
    ctx.call_on_close(lambda: _safe_close(fileobj))


def _safe_close(fileobj: _t.BinaryIO) -> None:
    """
    Suppress *all* errors and call ``close_intelligently()``.

    This will not error even if the object does not support ``close_intelligently()``.
    """
    # Note that the LazyFile type is not public, so we are passed a BinaryIO and we will
    # try to use the method (which we know `click` provides).
    with contextlib.suppress(Exception):
        fileobj.close_intelligently()  # type: ignore[attr-defined]
