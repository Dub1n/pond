"""
Utilities for generating SVG diagrams procedurally.

The package exposes lightweight helpers used by the build_diagrams CLI.
"""

from .deck import DeckOption, render_deck_plan, render_deck_section
from .attachments import render_attachment_diagram
from .core import SvgScene

__all__ = [
    "DeckOption",
    "render_deck_plan",
    "render_deck_section",
    "render_attachment_diagram",
    "SvgScene",
]
