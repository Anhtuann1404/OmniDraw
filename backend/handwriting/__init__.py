"""
OmniDraw - Vietnamese Handwriting Module
========================================
Single-stroke vector centerline handwriting engine for Vietnamese.
"""

if __name__ != "backend.handwriting":
    import os
    import sys

    _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

    import backend.handwriting as _canonical

    engine = _canonical.engine
    font_packs = _canonical.font_packs
    generate_handwriting_svg = _canonical.generate_handwriting_svg
    text_to_strokes = _canonical.text_to_strokes
    resolve_font = _canonical.resolve_font
    resolve_letter_type = _canonical.resolve_letter_type
    STYLE_CONFIGS = _canonical.STYLE_CONFIGS
    RENDER_PROFILES = _canonical.RENDER_PROFILES
    LETTER_TYPES = _canonical.LETTER_TYPES
    UnsupportedCharacterError = _canonical.UnsupportedCharacterError
    UnsupportedLetterTypeError = _canonical.UnsupportedLetterTypeError
    TextOverflowError = _canonical.TextOverflowError

    for mod_name, mod in list(sys.modules.items()):
        if mod_name.startswith("backend.handwriting."):
            direct_name = mod_name[len("backend.") :]
            sys.modules[direct_name] = mod

    __all__ = _canonical.__all__
else:
    from . import engine
    from . import font_packs
    from .engine import (
        generate_handwriting_svg,
        text_to_strokes,
        resolve_font,
        resolve_letter_type,
        STYLE_CONFIGS,
        RENDER_PROFILES,
        LETTER_TYPES,
        UnsupportedCharacterError,
        UnsupportedLetterTypeError,
        TextOverflowError,
    )

    __all__ = [
        "engine",
        "font_packs",
        "generate_handwriting_svg",
        "text_to_strokes",
        "resolve_font",
        "resolve_letter_type",
        "STYLE_CONFIGS",
        "RENDER_PROFILES",
        "LETTER_TYPES",
        "UnsupportedCharacterError",
        "UnsupportedLetterTypeError",
        "TextOverflowError",
    ]
