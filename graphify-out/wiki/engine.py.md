# engine.py

> 80 nodes · cohesion 0.05

## Key Concepts

- **engine.py** (50 connections) — `backend/handwriting/engine.py`
- **_run_self_check()** (24 connections) — `backend/handwriting/engine.py`
- **text_to_strokes()** (23 connections) — `backend/handwriting/engine.py`
- **bz()** (14 connections) — `backend/handwriting/font_packs/geometry.py`
- **optimize_word_dag()** (13 connections) — `backend/handwriting/engine.py`
- **_stroke_min_distance()** (12 connections) — `backend/handwriting/engine.py`
- **audit_font_pack_geometry()** (11 connections) — `backend/handwriting/engine.py`
- **eval_transition()** (11 connections) — `backend/handwriting/engine.py`
- **geometry.py** (11 connections) — `backend/handwriting/font_packs/geometry.py`
- **legacy.py** (11 connections) — `backend/handwriting/font_packs/legacy.py`
- **bridge_collision_cost()** (8 connections) — `backend/handwriting/engine.py`
- **generate_accents()** (7 connections) — `backend/handwriting/engine.py`
- **get_glyph_variants()** (7 connections) — `backend/handwriting/engine.py`
- **resolve_font()** (7 connections) — `backend/handwriting/engine.py`
- **segments_intersect()** (7 connections) — `backend/handwriting/engine.py`
- **split_glyph_strokes()** (7 connections) — `backend/handwriting/engine.py`
- **numpy** (7 connections)
- **audit_vietnamese_lowercase_accents()** (6 connections) — `backend/handwriting/engine.py`
- **build_ligature_bridge()** (6 connections) — `backend/handwriting/engine.py`
- **group_nfd_graphemes()** (6 connections) — `backend/handwriting/engine.py`
- **make_arch()** (6 connections) — `backend/handwriting/font_packs/geometry.py`
- **make_hook_stem()** (6 connections) — `backend/handwriting/font_packs/geometry.py`
- **make_oval()** (6 connections) — `backend/handwriting/font_packs/geometry.py`
- **omni_casual.py** (6 connections) — `backend/handwriting/font_packs/omni_casual.py`
- **analyze_text_contexts()** (5 connections) — `backend/handwriting/engine.py`
- *... and 55 more nodes in this community*

## Relationships

- [custom_error](custom_error.md) (19 shared connections)
- [path_optimizer.py](path_optimizer.py.md) (3 shared connections)
- [_run_self_check](_run_self_check.md) (2 shared connections)
- [backend/main.py](backend-main.py.md) (2 shared connections)
- [compute_svg_metrics](compute_svg_metrics.md) (1 shared connections)
- [test/main.py](test-main.py.md) (1 shared connections)
- [test_letter_type_omitted_defaults_to_general](test_letter_type_omitted_defaults_to_general.md) (1 shared connections)

## Source Files

- `backend/handwriting/engine.py`
- `backend/handwriting/font_packs/__init__.py`
- `backend/handwriting/font_packs/geometry.py`
- `backend/handwriting/font_packs/legacy.py`
- `backend/handwriting/font_packs/letter_variants.py`
- `backend/handwriting/font_packs/omni_casual.py`

## Audit Trail

- EXTRACTED: 182 (85%)
- INFERRED: 32 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*