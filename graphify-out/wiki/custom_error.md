# custom_error

> 73 nodes · cohesion 0.06

## Key Concepts

- **backend/main.py** (66 connections) — `backend/main.py`
- **handwriting/__init__.py** (18 connections) — `backend/handwriting/__init__.py`
- **handwriting_engine.py** (15 connections) — `backend/handwriting_engine.py`
- **generate_handwriting_svg()** (13 connections) — `backend/handwriting/engine.py`
- **generate_ai_image()** (13 connections) — `backend/main.py`
- **generate_ai_image()** (13 connections) — `test/main.py`
- **call_openai_image_api()** (12 connections) — `backend/api_generator.py`
- **save_image_and_metadata()** (9 connections) — `backend/api_generator.py`
- **resolve_letter_type()** (9 connections) — `backend/handwriting/engine.py`
- **PromptData** (8 connections) — `backend/api_generator.py`
- **UnsupportedCharacterError** (8 connections) — `backend/handwriting/engine.py`
- **TextOverflowError** (7 connections) — `backend/handwriting/engine.py`
- **UnsupportedLetterTypeError** (7 connections) — `backend/handwriting/engine.py`
- **custom_error()** (7 connections) — `backend/main.py`
- **post** (7 connections)
- **sys** (7 connections)
- **BaseModel** (6 connections)
- **get** (6 connections)
- **start_print()** (6 connections) — `backend/main.py`
- **log_experiment()** (5 connections) — `backend/main.py`
- **PauseCancelRequest** (5 connections) — `backend/main.py`
- **resume_print()** (5 connections) — `backend/main.py`
- **validate_skew_angle()** (5 connections) — `backend/main.py`
- **validate_skew_angle()** (5 connections) — `test/main.py`
- **delete_history_item()** (4 connections) — `backend/database.py`
- *... and 48 more nodes in this community*

## Relationships

- [test/main.py](test-main.py.md) (32 shared connections)
- [engine.py](engine.py.md) (19 shared connections)
- [api_generator.py](api_generator.py.md) (12 shared connections)
- [backend/test_handwriting_validation.py](backend-test_handwriting_validation.py.md) (5 shared connections)
- [qa_specimens.py](qa_specimens.py.md) (5 shared connections)
- [inspect_paper](inspect_paper.md) (5 shared connections)
- [test_letter_type_omitted_defaults_to_general](test_letter_type_omitted_defaults_to_general.md) (2 shared connections)
- [path_optimizer.py](path_optimizer.py.md) (2 shared connections)
- [_run_self_check](_run_self_check.md) (1 shared connections)
- [compute_svg_metrics](compute_svg_metrics.md) (1 shared connections)
- [test/test_handwriting_validation.py](test-test_handwriting_validation.py.md) (1 shared connections)
- [process](process.md) (1 shared connections)

## Source Files

- `backend/api_generator.py`
- `backend/database.py`
- `backend/handwriting/__init__.py`
- `backend/handwriting/engine.py`
- `backend/handwriting_engine.py`
- `backend/main.py`
- `test/main.py`

## Audit Trail

- EXTRACTED: 219 (92%)
- INFERRED: 18 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*