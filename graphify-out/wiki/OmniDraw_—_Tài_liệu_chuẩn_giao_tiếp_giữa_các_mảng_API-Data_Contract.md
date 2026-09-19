# OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)

> 3 nodes · cohesion 0.67

## Key Concepts

- **test_art_mode_empty_payload_rejected_without_side_effects()** (2 connections) — `backend/test_handwriting_validation.py`
- **test_art_mode_empty_payload_rejected_without_side_effects()** (2 connections) — `test/test_handwriting_validation.py`
- **Art Mode thiếu prompt (text) hoặc thiếu image_base64 (image) phải bị reject…** (1 connections) — `test/test_handwriting_validation.py`

## Relationships

- [test_letter_type_omitted_defaults_to_general](test_letter_type_omitted_defaults_to_general.md) (1 shared connections)
- [test/test_handwriting_validation.py](test-test_handwriting_validation.py.md) (1 shared connections)

## Source Files

- `backend/test_handwriting_validation.py`
- `test/test_handwriting_validation.py`

## Audit Trail

- EXTRACTED: 4 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*