"""
OmniDraw Writer Profile Package (TV1 — AI Data & Writer Profile Lead).

Hệ thống trích xuất đặc trưng phong cách người viết và quản lý hồ sơ WriterProfile
phục vụ nghiên cứu cá nhân hóa P2 (Non-binding offline research).

Ranh giới kiến trúc & Nghiên cứu:
- Writer Profile P2 tiếp tục độc lập hoàn toàn với CA-VHC P0.
- Đây là prototype kiểm thử ngoại tuyến bằng synthetic fixtures, chưa được xác thực trên mẫu viết tay thật và chưa bật trong luồng render/API chính.
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
