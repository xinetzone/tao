#!/usr/bin/env python3
"""Invoke-only tasks for building the Sphinx documentation."""

from __future__ import annotations

import os
import shlex
import subprocess

from invoke import Exit, task


def _split_cli_args(value: str) -> list[str]:
    """Split a shell-style option string into argv tokens."""
    if not value.strip():
        return []
    return shlex.split(value, posix=os.name != "nt")


def _collect_sphinx_opts(opts: str = "") -> list[str]:
    """Preserve the established Sphinx option merge order."""
    args: list[str] = []
    for part in (os.environ.get("SPHINXOPTS", ""), os.environ.get("O", ""), opts):
        args.extend(_split_cli_args(part))
    return args


def _run_sphinx_make_mode(
    target: str,
    sourcedir: str,
    builddir: str,
    opts: str = "",
) -> None:
    sphinx_build = os.environ.get("SPHINXBUILD", "sphinx-build")
    command = [
        sphinx_build,
        "-M",
        target,
        sourcedir,
        builddir,
        *_collect_sphinx_opts(opts),
    ]

    try:
        completed = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise Exit(
            "The 'sphinx-build' command was not found. Set SPHINXBUILD to the "
            "full path of the executable or add it to PATH."
        ) from exc

    if completed.returncode != 0:
        raise Exit(code=completed.returncode)


@task(default=True)
def help(
    _ctx,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Show Sphinx make-mode help."""
    _run_sphinx_make_mode(
        target="help",
        sourcedir=sourcedir,
        builddir=builddir,
        opts=opts,
    )


@task
def build(
    _ctx,
    target: str,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Build docs via ``sphinx-build -M``."""
    _run_sphinx_make_mode(
        target=target,
        sourcedir=sourcedir,
        builddir=builddir,
        opts=opts,
    )
