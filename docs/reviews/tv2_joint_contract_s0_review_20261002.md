# TV2 — S0 review of joint solver cost, ranking and runner contract

**Date:** 2026-10-02. **Reviewer:** TV2 (AI-assisted draft for Trần Hồng Khải to inspect). **Input:** TV4 `codex/tv4-pr3-slices@8dcfe663df61745b9b0cfe2d2dc5a1fd3c283b22`, Docs 03, 29–32. **Disposition:** `REVIEWED_WITH_OPEN_GATES`, not a human sign-off or approval of a solver. Prior TV2 PR3/E1 sign-offs retain only their original scope.

## Contract review

1. **Cost and cycles — conditionally coherent.** Docs 31 §2/§4/§5 count `N_cycle` as maximal pen-down runs, including first and last lowering/raising; `L_up` includes p0 and p_end travel. Thus `J=L_down+rho L_up+lambda N_cycle` follows from the stated constant-speed time model. A LIFT at coincident endpoints still starts a new run. Empty schedule has `N_cycle=0` but may have p0→p_end UP travel. The model is not measured physical elapsed time and excludes acceleration/jerk.
2. **CONNECT tolerance — clarification required before implementation.** Docs 31 §2 permits endpoints coincident *within tolerance*, while §5.2 assigns CONNECT zero transition length and forbids an undeclared bridge. For distinct coordinates within tolerance, specify one shared rule: snap endpoints in the hashed world geometry before solving, or represent/measure/check the nonzero pen-down connector as declared geometry. Otherwise cost, collision check, trace and rendered SVG can disagree. Both DP and independent oracle need the same *rule*, but not shared checker code. Include a near-contact example on each side of tolerance.
3. **Hard feasibility and ranking are different scopes.** `G` in Docs 31 §6 is the full Cartesian set of complete configurations after a shared candidate-quality gate, not merely configurations with a feasible reference schedule. `H_ref=+∞` is an internal ordering sentinel, not JSON, and invalid reference schedules remain in `G`. The runner must retain them in the ranked tail and distinguish `NO_FEASIBLE_IN_PREFIX` from whole-set `INFEASIBLE`. Do not prune a configuration merely because its reference schedule is invalid.
4. **H_ref/H_geom decomposition is unproved.** A k-best DAG may replace full enumeration only after a path↔configuration bijection, additive rank score including boundary, valid global `(H,configuration_id)` tie order, and exact handling of invalid references. H_ref validity can depend on nonadjacent geometry. H_geom's mean over strokes can have a configuration-dependent denominator or missing correspondence, so naïve per-owner additive scores are not justified. Until those proofs/tests exist, use finite enumeration plus a bounded heap on small DEV cases; report incomplete ranking when the budget ends before exhaustive enumeration.
5. **Exact comparison gates.** `J_joint ≤ J_(m+1) ≤ J_m` and equality at `m=|G|` are auditable only for the same candidate/policy hashes and theta, certified global prefix, and exact inner search. `enumeration_complete`, `ranking_complete`, and `search_complete` are independent. Beam yields a feasible upper bound, never an exact lower bound by itself. A tie in objective does not require identical action sequences unless tie policies match.
6. **Artifact consistency.** Docs 32 has the needed outcome/scope/provenance fields. The TV2 runner should create one JSONL record per case×method×theta×m, preserve errors/timeouts/infeasible outcomes, and include total cost of candidate generation, ranking and solve separately. An HTTP gateway limit is not a research acceptance budget. `m_star` cannot be inferred from sparse m values; use `smallest_tested_m` there.

## DEV-only fixtures requested for S0/S1

| Fixture | Required assertion |
|---|---|
| Empty case, p0≠p_end | `L_down=0`, `N_cycle=0`, `L_up=distance(p0,p_end)`; no invented stroke. |
| Two strokes sharing an exact endpoint | Compare CONNECT versus LIFT; same geometry, LIFT adds one cycle. |
| Two endpoints distinct but within contact tolerance | Resolve the open connector rule above; trace, hash, geometry checker and cost must agree. |
| Reversible stroke with different endpoints | Orientation changes UP travel, not stroke ID or `L_down`. |
| A mark with k=0 and another with k=1 | Verify body-completion deadline, interleaving and pending-mask behavior. |
| H_ref reference invalid, another schedule feasible | Keep configuration in G; rank it at the tail; inner solve may be feasible. |
| Equal H values and missing H_geom correspondence | Stable configuration-ID tie; missing correspondence last; report coverage. |
| A top-1 infeasible prefix but feasible configuration later | `NO_FEASIBLE_IN_PREFIX`; full-set result feasible; no false infeasibility. |
| Tiny complete G, all m=1…|G| | Certified nested prefixes and monotonic J; last m agrees with joint/oracle within registered tolerance. |
| Budget interrupted during ranking or inner solve | Correct `explored_subset`/flags/outcome; no gap or equivalence claim. |

TV3's independent oracle and geometry primitives remain separate from TV2/TV4 implementation. These fixtures do not authorize HOLDOUT use.

## TV2 baseline/runner protocol to register on DEV

- Freeze candidate-set hash and full Cartesian `G` order, H_ref/H_geom definitions, configuration-ID tie, `theta0`, contact/numeric policy and reference source *before* comparing methods. All methods use the same G, feasibility and J. Log ranking coverage and proof/evidence for every claimed prefix.
- Start with complete tiny synthetic/DEV cases and all m, then a preregistered geometric m grid for larger cases. Record ranking/enumeration/search completeness independently, plus candidate-generation, enumeration, score, rank and solve time; peak states/RAM and total wall time. Beam width, tie, seed and budget need their own manifest entries.
- Register a fixed-rho lambda sweep on DEV, including endpoints and ties; count (a) cases with multiple feasible `N_cycle`, (b) multiple nondominated `(L_down,L_up,N_cycle)` triples, (c) actual optimizer changes. If enumeration is incomplete, mark the corresponding diagnostic `UNKNOWN`, not zero. The lambda cutoff for simplifying later analysis remains **PENDING** until DEV evidence and team approval.
- Keep `gap_m` null unless both values are exact/feasible, ranking is certified, hashes/theta match and `J_m>0`. Preserve denominators and missing-reason counts. Report computational runtime apart from modeled `T_hat`; physical timing requires TV3 measurement. `epsilon_eq`, completion thresholds, exact scope, budgets, rho/lambda domain, numeric tolerance, sample size and Holdout custody remain **PENDING**.

## Source audit (three-way comparison; not yet a page-level literature handoff)

| Primary source | Verified claim relevant to this contract | Limitation / next action |
|---|---|---|
| [Balas (1999), *Annals of Operations Research* 86, 529–558](https://doi.org/10.1023/A:1018939709890) | Publisher abstract: certain precedence/position-restricted TSP classes reduce to source–sink shortest paths in layered networks, linear in n but exponential in k. | Publisher preview is abstract only; exact theorem/page mapping and applicability to glyph frontier/pending state remain **UNVERIFIED**. Do not claim this paper proves OmniDraw complexity. |
| [Balas & Simonetti (2001), *INFORMS Journal on Computing* 13(1), 56–75](https://doi.org/10.1287/ijoc.13.1.56.9748) | Publisher abstract: implements restricted-TSP DP with city-specific k(j) and a layered-network path/tour correspondence. | Full-text theorem/page table still **PENDING**; the paper's k and OmniDraw's mark deadline require an explicit mapping, not name similarity. |
| [Suárez-Ruiz, Lembono & Pham (2017), RoboTSP](https://arxiv.org/abs/1709.09343) | Author abstract: robot task order and configuration choice interact; reports a fast near-optimal method and comparison to GTSP-style approaches. | Different task/kinematics; analogy only, not evidence that joint optimization wins on Vietnamese glyphs. Page-level comparison pending full-text review. |
| [Khachai et al. (2023), PCGTSP](https://doi.org/10.1016/j.ejor.2023.01.039) | Publication metadata and author conference abstract identify cluster-choice plus precedence-constrained routing. | Full journal text/page-specific formulation was not verified. Do not equate PCGTSP's tour/cluster constraints with the present stroke/contact model without a formal reduction. |

This is a scoped source-verification pass, not the requested completed “Balas table with pages.” Paywalled/otherwise inaccessible full text was not treated as read. Search terms: exact paper titles, author names, DOI, and “RoboTSP”; inclusion limited to publisher pages and author manuscripts/abstracts. AI-assisted search and synthesis were used; TV2 must verify source passages and page numbers before citing them as full-text evidence.

## Handoff / next gates

TV4: decide the CONNECT near-contact rule and expose candidate/trace hashing accordingly; demonstrate any k-best ranker decomposition or keep exhaustive DEV ranking. TV1: provide reference correspondence/anchors and fixed candidate IDs/hash; settle contact and candidate quality policy with TV3. TV3: provide independent fixtures/checker and oracle feasibility/value. TV2: after those S0/S1 inputs, implement H_ref/H_geom/beam and the versioned runner on TV2 branch, register numerical limits and lambda protocol on DEV, then request owner review. No new joint solver, baseline, oracle or certifier is approved by this document. HOLDOUT stays closed; H1.1/PR5 and physical calibration remain open.
