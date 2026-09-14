"""
OmniDraw - Handwriting Engine Compatibility Shim
================================================
Thin wrapper re-exporting API from canonical package `backend.handwriting`.
Preserves backwards compatibility for callers importing `handwriting_engine`.
"""

import os
import sys
import types

# Ensure repository root is on sys.path so canonical backend package is always found
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from backend.handwriting import (
    TextOverflowError,
    UnsupportedCharacterError,
    UnsupportedLetterTypeError,
    generate_handwriting_svg,
    resolve_font,
    resolve_letter_type,
    text_to_strokes,
)
from backend.handwriting import engine

# Re-export key registries and constants directly from engine
FONT_PACKS = engine.FONT_PACKS
LETTER_VARIANT_SETS = engine.LETTER_VARIANT_SETS
RENDER_PROFILES = engine.RENDER_PROFILES
FONT_CONFIGS = engine.FONT_CONFIGS
STYLE_CONFIGS = engine.STYLE_CONFIGS
LETTER_TYPES = engine.LETTER_TYPES
DEFAULT_WIDTH = engine.DEFAULT_WIDTH
DEFAULT_CENTER = engine.DEFAULT_CENTER
GLYPHS = engine.GLYPHS
GLYPH_WIDTHS = engine.GLYPH_WIDTHS
GLYPH_CENTERS = engine.GLYPH_CENTERS
SUPPORTED_COMBINING_MARKS = engine.SUPPORTED_COMBINING_MARKS
STROKE_D_BAR = engine.STROKE_D_BAR
STROKE_CAP_D_BAR = engine.STROKE_CAP_D_BAR

# Self-check helper
_run_self_check = engine._run_self_check


def __getattr__(name):
    try:
        return getattr(engine, name)
    except AttributeError:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'") from None


def __dir__():
    return sorted(set(globals()) | set(dir(engine)))


def _is_module(name):
    if name in globals() and isinstance(globals()[name], types.ModuleType):
        return True
    if hasattr(engine, name) and isinstance(getattr(engine, name), types.ModuleType):
        return True
    return False


_EXCLUDE_FROM_ALL = {"os", "sys", "types", "engine"}
__all__ = sorted({
    name for name in (set(globals()) | set(dir(engine)))
    if not name.startswith("_")
    and name not in _EXCLUDE_FROM_ALL
    and not _is_module(name)
})


if __name__ == "__main__":
    _run_self_check()
