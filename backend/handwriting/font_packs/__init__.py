from .legacy import (
    GLYPHS,
    GLYPH_WIDTHS,
    GLYPH_CENTERS,
    DEFAULT_WIDTH,
    DEFAULT_CENTER,
)
from .omni_casual import (
    OMNI_CASUAL_CUSTOM_CHARS,
    OMNI_CASUAL_GLYPHS,
    OMNI_CASUAL_WIDTHS,
    OMNI_CASUAL_CENTERS,
    OMNI_CASUAL_WORD_FINAL_GLYPHS,
)
from .letter_variants import LETTER_VARIANT_SETS

# Add a font ID only when its real single-stroke glyph pack is available.
FONT_PACKS = {
    "omnidraw_legacy": {
        "name": "OmniDraw Legacy Stroke",
        "glyphs": GLYPHS,
        "widths": GLYPH_WIDTHS,
        "centers": GLYPH_CENTERS,
        "default_width": DEFAULT_WIDTH,
        "default_center": DEFAULT_CENTER,
        "supports_vietnamese_accents": True,
        "source_type": "builtin_stroke",
    },
    "omni_casual": {
        "name": "Omni Casual v1",
        "glyphs": OMNI_CASUAL_GLYPHS,
        "widths": OMNI_CASUAL_WIDTHS,
        "centers": OMNI_CASUAL_CENTERS,
        "default_width": DEFAULT_WIDTH,
        "default_center": DEFAULT_CENTER,
        "dot_below_x_offsets": {
            "y": 0.4,
            "Y": 0.0,
        },
        "contextual_glyphs": {
            "word_final": OMNI_CASUAL_WORD_FINAL_GLYPHS,
        },
        "supports_vietnamese_accents": True,
        "source_type": "builtin_single_stroke_adaptation",
        "derived_from": "omnidraw_legacy",
        "custom_glyphs": OMNI_CASUAL_CUSTOM_CHARS,
        "coverage_note": (
            "26 lowercase + 26 uppercase + 10 digits + 19 punctuation glyphs custom; "
            "Đ is derived from custom D; "
            "symbols outside the Omni Casual v1 charset may inherit legacy geometry"
        ),
    }
}
