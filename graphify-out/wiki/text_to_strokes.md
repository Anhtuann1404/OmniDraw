# text_to_strokes()

> God node · 23 connections · `backend/handwriting/engine.py`

**Community:** [engine.py](engine.py.md)

## Connections by Relation

### calls
- [_run_self_check()](_run_self_check_3.md) `EXTRACTED`
- [generate_handwriting_svg()](generate_handwriting_svg.md) `EXTRACTED`
- optimize_word_dag() `EXTRACTED`
- resolve_letter_type() `EXTRACTED`
- UnsupportedCharacterError `EXTRACTED`
- resolve_font() `EXTRACTED`
- TextOverflowError `EXTRACTED`
- split_glyph_strokes() `EXTRACTED`
- generate_accents() `EXTRACTED`
- group_nfd_graphemes() `EXTRACTED`
- build_ligature_bridge() `EXTRACTED`
- normalize_vietnamese_final_uy_tone() `EXTRACTED`
- analyze_text_contexts() `EXTRACTED`
- find_unsupported_characters() `EXTRACTED`
- select_contextual_glyph() `EXTRACTED`
- apply_bio_variation() `EXTRACTED`
- test_direct_engine_style_strict_validation() `EXTRACTED`
- test_direct_engine_style_strict_validation() `INFERRED`

### contains
- [engine.py](engine.py.md) `EXTRACTED`

### imports
- [backend/test_handwriting_validation.py](backend-test_handwriting_validation.py.md) `EXTRACTED`
- handwriting/__init__.py `EXTRACTED`
- handwriting_engine.py `EXTRACTED`

### rationale_for
- Biến đổi văn bản tiếng Việt thành mảng các nét vẽ mm (List of ndarray (N, 2)).… `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*