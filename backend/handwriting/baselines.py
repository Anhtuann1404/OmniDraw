"""Independent CA-VHC baseline adapters used by the experiment runner."""

from __future__ import annotations

import numpy as np


B1_STATIC = "b1_static"
B2_GREEDY = "b2_greedy"
B3_CURRENT_TRELLIS = "b3_current_trellis"
BASELINE_METHOD_TAGS = (B1_STATIC, B2_GREEDY, B3_CURRENT_TRELLIS)


def _variants_and_world_strokes(char_info_list):
    # Local import avoids making engine initialization depend on this adapter module.
    from .engine import get_glyph_variants, split_glyph_strokes

    variants_per_char = [
        get_glyph_variants(item["char"], item["raw_s"])
        for item in char_info_list
    ]
    world_primary = []
    for item, variants in zip(char_info_list, variants_per_char):
        per_variant = []
        for variant in variants:
            primary, _ = split_glyph_strokes(item["char"], variant.strokes)
            per_variant.append([
                stroke.astype(float) * item["scale_vec"] + item["offset"]
                for stroke in primary
            ])
        world_primary.append(per_variant)
    return variants_per_char, world_primary


def static_glyph_baseline(char_info_list):
    """B1: canonical glyphs only; always lift between characters."""
    variants_per_char, _ = _variants_and_world_strokes(char_info_list)
    return {
        "variants": [variants[0] for variants in variants_per_char],
        "conns": [False] * max(0, len(char_info_list) - 1),
    }


def greedy_contextual_baseline(char_info_list, weights, force_lift=False):
    """B2: choose the cheapest next variant from the already-selected state only."""
    from .engine import eval_transition

    if not char_info_list:
        return {"variants": [], "conns": []}

    variants_per_char, world_primary = _variants_and_world_strokes(char_info_list)
    first_index = min(
        range(len(variants_per_char[0])),
        key=lambda index: (variants_per_char[0][index].cost_legibility, index),
    )
    chosen_indices = [first_index]
    connections = []

    for index in range(1, len(char_info_list)):
        prev_item = char_info_list[index - 1]
        curr_item = char_info_list[index]
        prev_index = chosen_indices[-1]
        prev_variant = variants_per_char[index - 1][prev_index]
        p_exit = prev_variant.exit_pt * prev_item["scale_vec"] + prev_item["offset"]
        v_exit = prev_variant.v_exit * prev_item["scale_vec"]
        v_exit /= np.linalg.norm(v_exit) + 1e-6
        scale_hint = float(np.mean(prev_item["scale_vec"]))

        candidates = []
        for curr_index, curr_variant in enumerate(variants_per_char[index]):
            p_entry = curr_variant.entry_pt * curr_item["scale_vec"] + curr_item["offset"]
            v_entry = curr_variant.v_entry * curr_item["scale_vec"]
            v_entry /= np.linalg.norm(v_entry) + 1e-6
            if force_lift:
                cost = (
                    weights[0] * float(np.linalg.norm(p_entry - p_exit))
                    + weights[1]
                    + weights[4] * curr_variant.cost_legibility
                )
                connects = False
            else:
                cost, connects = eval_transition(
                    prev_variant,
                    curr_variant,
                    p_exit,
                    p_entry,
                    weights,
                    v_exit_world=v_exit,
                    v_entry_world=v_entry,
                    prev_strokes_world=world_primary[index - 1][prev_index],
                    curr_strokes_world=world_primary[index][curr_index],
                    scale_hint=scale_hint,
                )
            candidates.append((cost, curr_index, connects))

        _, best_index, connects = min(candidates, key=lambda item: (item[0], item[1]))
        chosen_indices.append(best_index)
        connections.append(connects)

    return {
        "variants": [
            variants_per_char[index][variant_index]
            for index, variant_index in enumerate(chosen_indices)
        ],
        "conns": connections,
    }


def solve_baseline(char_info_list, method_tag, weights, force_lift=False):
    """Dispatch one explicitly named baseline without changing the public renderer API."""
    if method_tag == B1_STATIC:
        return static_glyph_baseline(char_info_list)
    if method_tag == B2_GREEDY:
        return greedy_contextual_baseline(char_info_list, weights, force_lift=force_lift)
    if method_tag == B3_CURRENT_TRELLIS:
        from .engine import optimize_word_dag

        return optimize_word_dag(char_info_list, weights=weights, force_lift=force_lift)
    raise ValueError(
        f"Unknown baseline method '{method_tag}'. Expected one of {BASELINE_METHOD_TAGS}."
    )
