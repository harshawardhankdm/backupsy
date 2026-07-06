"""A small ASCII-art startup banner for the CLI.

Purely cosmetic -- if pyfiglet isn't available for some reason, or the
terminal doesn't support it well, we fall back gracefully to a plain
text line instead of crashing the tool.
"""

from __future__ import annotations

import os

import click

from . import __version__

# Cycle through a little gradient so the logo isn't a flat single color.
_GRADIENT = ["bright_cyan", "cyan", "bright_blue", "blue"]

_TAGLINE = "back up folders to S3-compatible storage, on autopilot"


def _colorize_lines(text: str) -> str:
    lines = text.rstrip("\n").split("\n")
    colored = []
    for i, line in enumerate(lines):
        color = _GRADIENT[i % len(_GRADIENT)]
        colored.append(click.style(line, fg=color, bold=True))
    return "\n".join(colored)


def print_banner() -> None:
    """Print the startup banner, unless the user opted out or output isn't a TTY."""
    if os.environ.get("BACKUPSY_NO_BANNER"):
        return
    if not click.get_text_stream("stdout").isatty():
        # Don't spam ASCII art into logs, pipes, or CI output.
        return

    try:
        import pyfiglet

        art = pyfiglet.figlet_format("backupsy", font="slant")
        click.echo(_colorize_lines(art))
    except Exception:
        # ASCII art is a nice-to-have, never let it block the actual tool.
        click.echo(click.style("backupsy", fg="bright_cyan", bold=True))

    click.echo(click.style(f"  {_TAGLINE}", fg="bright_black") + "\n" + click.style(f"  v{__version__}", fg="bright_black"))
    click.echo("")
