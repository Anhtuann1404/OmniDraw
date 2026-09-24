"""
OmniDraw Writer Profile Package (TV1 — AI Data & Writer Profile Lead).

Hệ thống trích xuất đặc trưng phong cách người viết và quản lý hồ sơ WriterProfile
phục vụ nghiên cứu cá nhân hóa P2 (Non-binding offline research).
"""

from .extractor import (
    WriterProfile,
    GlobalStyleFeatures,
    SpacingFeatures,
    DiacriticTendencyFeatures,
    WriterProfileExtractor,
    extract_writer_profile,
    validate_writer_profile,
)

__all__ = [
    "WriterProfile",
    "GlobalStyleFeatures",
    "SpacingFeatures",
    "DiacriticTendencyFeatures",
    "WriterProfileExtractor",
    "extract_writer_profile",
    "validate_writer_profile",
]
