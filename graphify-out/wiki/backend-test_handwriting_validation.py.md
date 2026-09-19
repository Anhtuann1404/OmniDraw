# backend/test_handwriting_validation.py

> 21 nodes · cohesion 0.13

## Key Concepts

- **APIResponse** (23 connections) — `backend/api_generator.py`
- **test_art_mode_optional_style_handling()** (3 connections) — `backend/test_handwriting_validation.py`
- **test_art_mode_style_defaults_downstream_verification()** (3 connections) — `backend/test_handwriting_validation.py`
- **test_art_mode_target_paper_size_validation()** (3 connections) — `backend/test_handwriting_validation.py`
- **test_art_mode_text_all_valid_styles_downstream_verification()** (3 connections) — `backend/test_handwriting_validation.py`
- **test_art_mode_text_line_art_regression()** (3 connections) — `backend/test_handwriting_validation.py`
- **test_art_mode_text_sketch_regression()** (3 connections) — `backend/test_handwriting_validation.py`
- **test_valid_requests_trigger_cleanup_exactly_once_before_pipeline()** (3 connections) — `backend/test_handwriting_validation.py`
- **test_art_mode_optional_style_handling()** (3 connections) — `test/test_handwriting_validation.py`
- **test_art_mode_style_defaults_downstream_verification()** (3 connections) — `test/test_handwriting_validation.py`
- **test_art_mode_target_paper_size_validation()** (3 connections) — `test/test_handwriting_validation.py`
- **test_art_mode_text_all_valid_styles_downstream_verification()** (3 connections) — `test/test_handwriting_validation.py`
- **test_art_mode_text_line_art_regression()** (3 connections) — `test/test_handwriting_validation.py`
- **test_art_mode_text_sketch_regression()** (3 connections) — `test/test_handwriting_validation.py`
- **test_valid_requests_trigger_cleanup_exactly_once_before_pipeline()** (3 connections) — `test/test_handwriting_validation.py`
- **Art Mode text-to-drawing với style='sketch' không bị handwriting validation…** (1 connections) — `test/test_handwriting_validation.py`
- **Art Mode khi style là None hoặc thiếu không bị crash ngoài kiểm soát (tự động…** (1 connections) — `test/test_handwriting_validation.py`
- **Art Mode khi style omitted hoặc None phải tự động resolve thành 'sketch' và…** (1 connections) — `test/test_handwriting_validation.py`
- **Text-to-Drawing với 4 style chuẩn (sketch, line_art, stipple, hatching) phải…** (1 connections) — `test/test_handwriting_validation.py`
- **Art Mode cũng phải validate nghiêm ngặt target_paper_size_mm trước khi gọi…** (1 connections) — `test/test_handwriting_validation.py`
- **Request hợp lệ phải gọi _clear_cached_svg_for_request đúng 1 lần trước khi…** (1 connections) — `test/test_handwriting_validation.py`

## Relationships

- [test_letter_type_omitted_defaults_to_general](test_letter_type_omitted_defaults_to_general.md) (8 shared connections)
- [test/test_handwriting_validation.py](test-test_handwriting_validation.py.md) (7 shared connections)
- [custom_error](custom_error.md) (5 shared connections)
- [api_generator.py](api_generator.py.md) (3 shared connections)

## Source Files

- `backend/api_generator.py`
- `backend/test_handwriting_validation.py`
- `test/test_handwriting_validation.py`

## Audit Trail

- EXTRACTED: 42 (82%)
- INFERRED: 9 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*