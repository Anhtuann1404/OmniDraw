"""
TV1 Vietnamese Candidate Dataset Builder & Fixture Generator (Docs 31/32).

Author: TV1 (AI Data & Candidate Lead)
Scope: Research DEV set and initial Vietnamese diacritic candidates.
Provenance Notice:
- Glyphs in this module are curated parametric synthetic baseline polylines
  hand-authored by TV1 for algorithmic benchmarking on Vietnamese diacritic topology.
- Real third-party reference fonts and verifiable TTF/OTF font assets will be introduced
  in Font Pilot (Gate Q16). To remain faithful and avoid citation/reference hallucination,
  'reference_geometry' is explicitly set to None for DEV synthetic prototypes.
Features:
- NFD grapheme decomposition and strict Character/Variant schemas.
- Stacked diacritics (dấu chồng: e.g. circumflex + acute in "ấ").
- Mark below (dấu dưới: e.g. dot below in "ệ" / "ạ").
- Multi-body delayed mark with deadline k=2 and contact clearance whitelist.
- True distant interaction with incompatible candidate pairs across intervening letters.
- Reversible vs non-reversible stroke flags.
- Real world-mm coordinates satisfying minimum clearance c_min = 0.20 mm.
- Deterministic candidate set SHA-256 calculation via canonical_hash.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json
import unicodedata
from typing import Dict, Any, List

from backend.research.schemas import (
    ResearchCase,
    Character,
    Variant,
    Stroke,
    GeometryPolicy,
    Boundary,
    ReferenceGeometry,
    Contact,
    SeparationPair,
    StrokeRef,
    canonical_hash,
)
from backend.research.geometry import (
    FLATTEN_POLICY,
    NUMERIC_POLICY,
    SEPARATION_POLICY,
)
from backend.research.schedule_checker import EXACT_CONTACT_POLICY
from backend.research.service import manifest_hash


def authoring_digest(glyph_id: str, description: str) -> str:
    """Deterministic authoring digest documenting TV1 synthetic vector origin under CC-BY-4.0."""
    return canonical_hash({
        "author": "TV1 (OmniDraw AI Data & Candidate Lead)",
        "glyph_id": glyph_id,
        "type": "synthetic_vector_prototype",
        "license": "CC-BY-4.0",
        "description": description,
    })


def create_standard_geometry_policy() -> GeometryPolicy:
    """Return strict GeometryPolicy matching current TV4 DEV contract."""
    return GeometryPolicy(
        c_min_mm=0.20,
        flatten_policy_id=FLATTEN_POLICY,
        contact_policy_id=EXACT_CONTACT_POLICY,
        numeric_policy_id=NUMERIC_POLICY,
        separation_policy_id=SEPARATION_POLICY,
        allow_zero_length=False,
    )


def build_stacked_diacritic_case() -> ResearchCase:
    """
    Case 1: 'ấb' (NFD: 'ấb')
    - Stacked diacritics: circumflex (shape) + acute (tone) on letter 'a'.
    - Clear vertical hierarchy: body (y in [0, 2]), circumflex (y in [2.4, 2.9]), acute (y in [3.3, 3.8]).
    - Mark precedence: circumflex must be drawn before acute.
    - Delay policy: k(circumflex)=0 (flush before letter 1), k(acute)=1 (flush before letter 2).
    """
    raw_text = "ấb"
    norm_text = unicodedata.normalize("NFD", raw_text)

    # Variant 1 (standard)
    v1_strokes = [
        Stroke(
            stroke_id="a_body",
            role="body",
            owner_index=0,
            reversible=False,
            polyline_mm=[[0.2, 1.8], [0.0, 1.0], [0.2, 0.0], [1.5, 0.0], [1.5, 2.0]],
            mark_type=None,
        ),
        Stroke(
            stroke_id="shape_circumflex",
            role="mark",
            owner_index=0,
            reversible=True,
            polyline_mm=[[0.3, 2.4], [0.75, 2.9], [1.2, 2.4]],
            mark_type="tv1-circumflex",
        ),
        Stroke(
            stroke_id="tone_acute",
            role="mark",
            owner_index=0,
            reversible=True,
            polyline_mm=[[0.5, 3.3], [1.1, 3.9]],
            mark_type="tv1-acute",
        ),
    ]

    # Variant 2 (alt - slightly wider accent placement)
    v2_strokes = [
        Stroke(
            stroke_id="a_body",
            role="body",
            owner_index=0,
            reversible=False,
            polyline_mm=[[0.2, 1.8], [0.0, 1.0], [0.2, 0.0], [1.6, 0.0], [1.6, 2.0]],
            mark_type=None,
        ),
        Stroke(
            stroke_id="shape_circumflex",
            role="mark",
            owner_index=0,
            reversible=True,
            polyline_mm=[[0.4, 2.5], [0.8, 3.0], [1.3, 2.5]],
            mark_type="tv1-circumflex",
        ),
        Stroke(
            stroke_id="tone_acute",
            role="mark",
            owner_index=0,
            reversible=True,
            polyline_mm=[[0.6, 3.4], [1.2, 4.0]],
            mark_type="tv1-acute",
        ),
    ]

    char_a = Character(
        owner_index=0,
        grapheme=unicodedata.normalize("NFD", "ấ"),
        variants=[
            Variant(
                candidate_id="a-std",
                source_hash=authoring_digest("a-std", "standard oval body with circumflex and acute"),
                strokes=v1_strokes,
                body_order=["a_body"],
                mark_precedence=[("shape_circumflex", "tone_acute")],
            ),
            Variant(
                candidate_id="a-alt",
                source_hash=authoring_digest("a-alt", "wider oval body with elevated circumflex and acute"),
                strokes=v2_strokes,
                body_order=["a_body"],
                mark_precedence=[("shape_circumflex", "tone_acute")],
            ),
        ],
    )

    # Character 'b'
    b_strokes = [
        Stroke(
            stroke_id="b_stem",
            role="body",
            owner_index=1,
            reversible=False,
            polyline_mm=[[3.0, 4.0], [3.0, 0.0], [4.2, 0.0], [4.2, 1.8], [3.2, 1.8]],
            mark_type=None,
        )
    ]

    char_b = Character(
        owner_index=1,
        grapheme=unicodedata.normalize("NFD", "b"),
        variants=[
            Variant(
                candidate_id="b-std",
                source_hash=authoring_digest("b-std", "standard vertical stem and loop"),
                strokes=b_strokes,
                body_order=["b_stem"],
                mark_precedence=[],
            )
        ],
    )

    data = {
        "schema_version": "joint-artifact-v1-draft",
        "case_id": "tv1-dev-stacked-diacritic-01",
        "dataset_version": "tv1-vietnamese-dev-v1",
        "manifest_sha256": "0" * 64,
        "split": "dev",
        "original_text": raw_text,
        "normalized_text": norm_text,
        "normalization": "NFD",
        "candidates": [char_a.model_dump(mode="json"), char_b.model_dump(mode="json")],
        "contacts": [],
        "separation_pairs": [],
        "delay_policy": {"tv1-circumflex": 0, "tv1-acute": 1},
        "geometry_policy": create_standard_geometry_policy().model_dump(mode="json"),
        "boundary": {
            "p0_mm": [-1.0, 0.0],
            "p_end_mm": [6.0, 0.0],
            "initial_pen": "UP",
            "final_pen": "UP",
            "convention_id": "tv1-origin-margin-v1",
        },
        "reference_geometry": None,
    }
    return ResearchCase.prepare(data)


def build_mark_below_case() -> ResearchCase:
    """
    Case 2: 'ệc' (NFD: 'ệc')
    - Mark above (circumflex: y in [2.4, 2.9]) AND mark below (dot_below: y in [-0.8, -0.4]).
    - Mark precedence: circumflex before dot_below.
    - Delay policy: k(circumflex)=0, k(dot_below)=0.
    """
    raw_text = "ệc"
    norm_text = unicodedata.normalize("NFD", raw_text)

    e_strokes = [
        Stroke(
            stroke_id="e_body",
            role="body",
            owner_index=0,
            reversible=False,
            polyline_mm=[[0.2, 1.0], [1.5, 1.0], [1.5, 1.8], [0.2, 1.8], [0.0, 1.0], [0.2, 0.0], [1.5, 0.0]],
            mark_type=None,
        ),
        Stroke(
            stroke_id="shape_circumflex",
            role="mark",
            owner_index=0,
            reversible=True,
            polyline_mm=[[0.3, 2.4], [0.75, 2.9], [1.2, 2.4]],
            mark_type="tv1-circumflex",
        ),
        Stroke(
            stroke_id="tone_dot_below",
            role="mark",
            owner_index=0,
            reversible=True,
            polyline_mm=[[0.7, -0.5], [0.8, -0.5]],
            mark_type="tv1-dot-below",
        ),
    ]

    char_e = Character(
        owner_index=0,
        grapheme=unicodedata.normalize("NFD", "ệ"),
        variants=[
            Variant(
                candidate_id="e-std",
                source_hash=authoring_digest("e-std", "e loop with circumflex above and dot below baseline"),
                strokes=e_strokes,
                body_order=["e_body"],
                mark_precedence=[("shape_circumflex", "tone_dot_below")],
            )
        ],
    )

    c_strokes = [
        Stroke(
            stroke_id="c_body",
            role="body",
            owner_index=1,
            reversible=False,
            polyline_mm=[[4.0, 1.8], [2.8, 1.8], [2.6, 1.0], [2.8, 0.0], [4.0, 0.0]],
            mark_type=None,
        )
    ]

    char_c = Character(
        owner_index=1,
        grapheme=unicodedata.normalize("NFD", "c"),
        variants=[
            Variant(
                candidate_id="c-std",
                source_hash=authoring_digest("c-std", "open curve c glyph"),
                strokes=c_strokes,
                body_order=["c_body"],
                mark_precedence=[],
            )
        ],
    )

    data = {
        "schema_version": "joint-artifact-v1-draft",
        "case_id": "tv1-dev-mark-below-02",
        "dataset_version": "tv1-vietnamese-dev-v1",
        "manifest_sha256": "0" * 64,
        "split": "dev",
        "original_text": raw_text,
        "normalized_text": norm_text,
        "normalization": "NFD",
        "candidates": [char_e.model_dump(mode="json"), char_c.model_dump(mode="json")],
        "contacts": [],
        "separation_pairs": [],
        "delay_policy": {"tv1-circumflex": 0, "tv1-dot-below": 0},
        "geometry_policy": create_standard_geometry_policy().model_dump(mode="json"),
        "boundary": {
            "p0_mm": [-1.0, 0.0],
            "p_end_mm": [6.0, 0.0],
            "initial_pen": "UP",
            "final_pen": "UP",
            "convention_id": "tv1-origin-margin-v1",
        },
        "reference_geometry": None,
    }
    return ResearchCase.prepare(data)


def build_delayed_mark_case() -> ResearchCase:
    """
    Case 3: 'óto' (NFD: 'óto')
    - Scope: Delayed-mark multi-body fixture (evaluating k=2 diacritic postponement across multiple character bodies,
      and declared-contact clearance whitelist).
    - Letter 1 ('t') has a multi-stroke body (stem + top bar) with contact at [3.0, 3.5] acting as a clearance whitelist.
    """
    raw_text = "óto"
    norm_text = unicodedata.normalize("NFD", raw_text)

    # Character 0: 'ó'
    o_strokes = [
        Stroke(
            stroke_id="o_body",
            role="body",
            owner_index=0,
            reversible=False,
            polyline_mm=[[1.4, 1.8], [0.2, 1.8], [0.0, 1.0], [0.2, 0.0], [1.4, 0.0], [1.6, 1.0]],
            mark_type=None,
        ),
        Stroke(
            stroke_id="tone_acute",
            role="mark",
            owner_index=0,
            reversible=True,
            polyline_mm=[[0.5, 2.4], [1.1, 3.0]],
            mark_type="tv1-acute-distant",
        ),
    ]

    char_o1 = Character(
        owner_index=0,
        grapheme=unicodedata.normalize("NFD", "ó"),
        variants=[
            Variant(
                candidate_id="o-std",
                source_hash=authoring_digest("o-std", "standard oval body with acute tone"),
                strokes=o_strokes,
                body_order=["o_body"],
                mark_precedence=[],
            )
        ],
    )

    # Character 1: 't' (multi-stroke body: stem + top bar, contact at [3.0, 3.5])
    t_strokes = [
        Stroke(
            stroke_id="t_stem",
            role="body",
            owner_index=1,
            reversible=False,
            polyline_mm=[[3.0, 3.5], [3.0, 0.2], [3.3, 0.0], [3.8, 0.0]],
            mark_type=None,
        ),
        Stroke(
            stroke_id="t_crossbar",
            role="body",
            owner_index=1,
            reversible=True,
            polyline_mm=[[3.0, 3.5], [3.8, 3.5]],
            mark_type=None,
        ),
    ]

    contact_t = Contact(
        first=StrokeRef(owner_index=1, candidate_id="t-std", stroke_id="t_stem"),
        second=StrokeRef(owner_index=1, candidate_id="t-std", stroke_id="t_crossbar"),
        location_mm=[3.0, 3.5],
        radius_mm=0.25,
        policy_id="tv4-dev-exact-endpoint-v1",
    )

    char_t = Character(
        owner_index=1,
        grapheme=unicodedata.normalize("NFD", "t"),
        variants=[
            Variant(
                candidate_id="t-std",
                source_hash=authoring_digest("t-std", "t stem and crossbar with declared contact"),
                strokes=t_strokes,
                body_order=["t_stem", "t_crossbar"],
                mark_precedence=[],
            )
        ],
    )

    # Character 2: 'o'
    o2_strokes = [
        Stroke(
            stroke_id="o_body",
            role="body",
            owner_index=2,
            reversible=False,
            polyline_mm=[[5.4, 1.8], [4.2, 1.8], [4.0, 1.0], [4.2, 0.0], [5.4, 0.0], [5.6, 1.0]],
            mark_type=None,
        )
    ]

    char_o2 = Character(
        owner_index=2,
        grapheme=unicodedata.normalize("NFD", "o"),
        variants=[
            Variant(
                candidate_id="o2-std",
                source_hash=authoring_digest("o2-std", "final oval character body"),
                strokes=o2_strokes,
                body_order=["o_body"],
                mark_precedence=[],
            )
        ],
    )

    data = {
        "schema_version": "joint-artifact-v1-draft",
        "case_id": "tv1-dev-distant-interaction-03",
        "dataset_version": "tv1-vietnamese-dev-v1",
        "manifest_sha256": "0" * 64,
        "split": "dev",
        "original_text": raw_text,
        "normalized_text": norm_text,
        "normalization": "NFD",
        "candidates": [
            char_o1.model_dump(mode="json"),
            char_t.model_dump(mode="json"),
            char_o2.model_dump(mode="json"),
        ],
        "contacts": [contact_t.model_dump(mode="json")],
        "separation_pairs": [],
        "delay_policy": {"tv1-acute-distant": 2},
        "geometry_policy": create_standard_geometry_policy().model_dump(mode="json"),
        "boundary": {
            "p0_mm": [-1.0, 0.0],
            "p_end_mm": [8.0, 0.0],
            "initial_pen": "UP",
            "final_pen": "UP",
            "convention_id": "tv1-origin-margin-v1",
        },
        "reference_geometry": None,
    }
    return ResearchCase.prepare(data)


def build_distant_interaction_case() -> ResearchCase:
    """
    Case 4: 'óto' (NFD: 'óto')
    - Scope: True Distant Geometric Interaction with Incompatible Candidate Choices (Docs 30 §2).
    - Owner 0 has 2 variants: 'o-compact' and 'o-swash' (with a wide rightward flourishing tail ending at [3.95, 0.5]).
    - Owner 1 ('t') has variant 't-std' located in [2.5, 3.2].
    - Owner 2 has 2 variants: 'o2-compact' and 'o2-flourish' (with an entry flourish starting at [4.05, 0.5]).
    - Clearance between (0, 'o-swash') and (2, 'o2-flourish') is 4.05 - 3.95 = 0.10 mm < c_min = 0.20 mm!
    - This creates an incompatible pair and a non-empty future interaction edge:
      2 in future_neighbors[0] and 0 in future_neighbors[2].
    - Verifies that DP safe-forget retains Owner 0's frontier state across Owner 1 until Owner 2 is resolved.
    """
    raw_text = "óto"
    norm_text = unicodedata.normalize("NFD", raw_text)

    # Character 0 variants
    v0_compact = Variant(
        candidate_id="o-compact",
        source_hash=authoring_digest("o-compact", "standard compact oval body"),
        strokes=[
            Stroke(stroke_id="body", role="body", owner_index=0, reversible=False,
                   polyline_mm=[[0.2, 1.8], [0.0, 1.0], [0.2, 0.0], [1.5, 0.0], [1.5, 1.8]]),
            Stroke(stroke_id="mark", role="mark", owner_index=0, reversible=True,
                   polyline_mm=[[0.5, 2.4], [1.1, 3.0]], mark_type="tv1-acute-distant"),
        ],
        body_order=["body"],
        mark_precedence=[],
    )
    v0_swash = Variant(
        candidate_id="o-swash",
        source_hash=authoring_digest("o-swash", "oval body with long exiting swash tail extending to x=3.95"),
        strokes=[
            Stroke(stroke_id="body", role="body", owner_index=0, reversible=False,
                   polyline_mm=[[0.2, 1.8], [0.0, 1.0], [0.2, 0.0], [1.5, 0.0], [3.95, 0.5]]),
            Stroke(stroke_id="mark", role="mark", owner_index=0, reversible=True,
                   polyline_mm=[[0.5, 2.4], [1.1, 3.0]], mark_type="tv1-acute-distant"),
        ],
        body_order=["body"],
        mark_precedence=[],
    )
    char0 = Character(
        owner_index=0,
        grapheme=unicodedata.normalize("NFD", "ó"),
        variants=[v0_compact, v0_swash],
    )

    # Character 1: 't'
    v1_std = Variant(
        candidate_id="t-std",
        source_hash=authoring_digest("t-std", "standard centered t stem"),
        strokes=[
            Stroke(stroke_id="body", role="body", owner_index=1, reversible=False,
                   polyline_mm=[[2.5, 3.5], [2.5, 1.0]]),
        ],
        body_order=["body"],
        mark_precedence=[],
    )
    char1 = Character(
        owner_index=1,
        grapheme=unicodedata.normalize("NFD", "t"),
        variants=[v1_std],
    )

    # Character 2 variants
    v2_compact = Variant(
        candidate_id="o2-compact",
        source_hash=authoring_digest("o2-compact", "standard compact trailing oval"),
        strokes=[
            Stroke(stroke_id="body", role="body", owner_index=2, reversible=False,
                   polyline_mm=[[4.5, 1.8], [4.5, 0.0], [5.5, 0.0], [5.5, 1.8]]),
        ],
        body_order=["body"],
        mark_precedence=[],
    )
    v2_flourish = Variant(
        candidate_id="o2-flourish",
        source_hash=authoring_digest("o2-flourish", "trailing oval with entry flourish starting at x=4.05"),
        strokes=[
            Stroke(stroke_id="body", role="body", owner_index=2, reversible=False,
                   polyline_mm=[[4.05, 0.5], [4.5, 1.8], [4.5, 0.0], [5.5, 0.0], [5.5, 1.8]]),
        ],
        body_order=["body"],
        mark_precedence=[],
    )
    char2 = Character(
        owner_index=2,
        grapheme=unicodedata.normalize("NFD", "o"),
        variants=[v2_compact, v2_flourish],
    )

    data = {
        "schema_version": "joint-artifact-v1-draft",
        "case_id": "tv1-dev-distant-interaction-04",
        "dataset_version": "tv1-vietnamese-dev-v1",
        "manifest_sha256": "0" * 64,
        "split": "dev",
        "original_text": raw_text,
        "normalized_text": norm_text,
        "normalization": "NFD",
        "candidates": [
            char0.model_dump(mode="json"),
            char1.model_dump(mode="json"),
            char2.model_dump(mode="json"),
        ],
        "contacts": [],
        "separation_pairs": [],
        "delay_policy": {"tv1-acute-distant": 2},
        "geometry_policy": create_standard_geometry_policy().model_dump(mode="json"),
        "boundary": {
            "p0_mm": [-1.0, 0.0],
            "p_end_mm": [8.0, 0.0],
            "initial_pen": "UP",
            "final_pen": "UP",
            "convention_id": "tv1-origin-margin-v1",
        },
        "reference_geometry": None,
    }
    return ResearchCase.prepare(data)


def build_all_tv1_dev_cases() -> List[ResearchCase]:
    """Compile and return all initial TV1 Vietnamese research cases."""
    return [
        build_stacked_diacritic_case(),
        build_mark_below_case(),
        build_delayed_mark_case(),
        build_distant_interaction_case(),
    ]


def export_tv1_manifest(output_path: Path) -> str:
    """Build, serialize and write canonical TV1 research manifest."""
    cases = build_all_tv1_dev_cases()
    m_hash = manifest_hash(cases)

    cases_with_hash = []
    for c in cases:
        data = c.model_dump(mode="json")
        data["manifest_sha256"] = m_hash
        cases_with_hash.append(data)

    manifest_payload = {
        "schema_version": "joint-artifact-v1-draft",
        "manifest_sha256": m_hash,
        "cases": cases_with_hash,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2, ensure_ascii=False)

    return m_hash


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    dev_target = repo_root / "dataset" / "research" / "dev" / "tv1_dev_manifest.json"
    fixtures_target = repo_root / "tests" / "research" / "fixtures" / "tv1_candidates_dev.json"

    h1 = export_tv1_manifest(dev_target)
    h2 = export_tv1_manifest(fixtures_target)
    assert h1 == h2, f"Manifest hash mismatch between dev and fixtures: {h1} != {h2}"
    print(f"TV1 Manifest successfully exported to:")
    print(f" - {dev_target}")
    print(f" - {fixtures_target}")
    print(f"Manifest SHA-256: {h1}")
