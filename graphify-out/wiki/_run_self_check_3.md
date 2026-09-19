# _run_self_check()

> God node · 24 connections · `backend/handwriting/engine.py`

**Community:** [engine.py](engine.py.md)

## Connections by Relation

### calls
- [text_to_strokes()](text_to_strokes.md) `EXTRACTED`
- optimize_word_dag() `EXTRACTED`
- [generate_handwriting_svg()](generate_handwriting_svg.md) `EXTRACTED`
- _stroke_min_distance() `EXTRACTED`
- build_svg() `EXTRACTED`
- audit_font_pack_geometry() `EXTRACTED`
- bridge_collision_cost() `EXTRACTED`
- get_glyph_variants() `EXTRACTED`
- split_glyph_strokes() `EXTRACTED`
- segments_intersect() `EXTRACTED`
- resolve_font() `EXTRACTED`
- generate_accents() `EXTRACTED`
- build_ligature_bridge() `EXTRACTED`
- audit_vietnamese_lowercase_accents() `EXTRACTED`
- group_nfd_graphemes() `EXTRACTED`
- analyze_text_contexts() `EXTRACTED`
- normalize_vietnamese_final_uy_tone() `EXTRACTED`
- select_contextual_glyph() `EXTRACTED`

### contains
- [engine.py](engine.py.md) `EXTRACTED`
- stroke_fingerprint() `EXTRACTED`

### indirect_call
- _spy_eval() `INFERRED`
- _spy_bridge_tracked() `INFERRED`
- _spy_opt_tracked() `INFERRED`

### rationale_for
- Kiểm tra tự động module viết thư tay với các kiểu nét đã đăng ký. `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*