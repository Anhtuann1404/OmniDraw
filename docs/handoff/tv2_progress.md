# TV2 research baseline handoff

## 2026-10-03 — DEV H_ref/top-m first slice

**Owner / decisions:** TV2; Q02/Q04/Q06/Q09/Q11/Q16 remain PENDING. Review request to TV4 for method/ranker and TV3 for independent QA; this entry is not their acknowledgement or sign-off.

**Source / commit:** branched clean worktree `codex/tv2-research-baselines-20261002` from shared `cb38f64949b9c07a86f6a78002a842320adb4250` (includes TV4 code `510f4e1` and fixed-configuration interface). Implementation `eef5c8e9a2dca7d7a80c98e172957db4832259df`. No merge of historical TV2 branch; S0 review at `docs/reviews/tv2_joint_contract_s0_review_20261002.md` is the unchanged AI-assisted draft targeting `8dcfe66`, not a human sign-off for this DP.

**Contract/policy/scope:** `joint-contract-v1-draft`, `joint-artifact-v1-draft`, `tv4-dev-dyadic-primitive-cost-v1`; DEV exact-endpoint contact and all-pairs geometry policy only. `staged_top_m_h_ref` ranks every complete Cartesian configuration by reference schedule at explicit `theta0` and tuple candidate-ID tie. Reference uses body order, then mark IDs in ascending order, all forward/LIFT, with p0/p_end and cycle cost. A geometry-invalid or schedule-invalid reference receives an internal infinity rank and remains in G. Exhaustive enumeration is the only ranking evidence in this slice; no k-best claim. Inner calls use the original ResearchCase/hash and shared TV4 fixed-configuration solve. `OPTIMAL`/`NO_FEASIBLE_IN_PREFIX` require complete ranking and all prefix inner searches; budget interruption retains incomplete flags/scope. No HTTP adapter or HOLDOUT path.

**Reproduction:** from worktree root on Windows, using `C:\Users\ASUS-PRO\OmniDraw-develop\backend\venv\Scripts\python.exe` (Python 3.12, pytest 7.4.0, pydantic 2.13.5):

```powershell
& 'C:\Users\ASUS-PRO\OmniDraw-develop\backend\venv\Scripts\python.exe' -m pytest tests/research backend/test_handwriting_validation.py -q --basetemp 'C:\Users\ASUS-PRO\OmniDraw-tv2-research\output\research_dev\pytest-tv2-20261003'
```

**Result:** 215 passed, 1 pre-existing Starlette/TestClient warning. Pytest's default temp directory gave five setup permission errors on this host; a fresh worktree-local basetemp fixed that environment issue. Synthetic fixture `tv4-method-geometry-schedule-gap`, manifest SHA-256 `8b2b8d073b88ebe8ea9623d2cdf7bbdeaa19913e64876dea14fef270331681eb`, candidate-set SHA-256 `04d6bd6b29a190d37bc59f2373e3566d34c1d2b8e32a7eae5ff21db93e37be14`; at DEV rho=.5, lambda=2, budget 10s/100000 states/100 configurations/64 MiB, G=2, H_ref top-1 J=11.121320343559642 mm and top-2 J=10.0 mm, both with N_cycle=3. Both outcomes are inner-model/prefix `OPTIMAL` claims under DEV policy, independent checker `NOT_RUN`; these values are not approved corpus results. Tests also cover invalid reference retained, ranking resource-limit incomplete, empty case and no-feasible prefix. Stage timing and peak allocated memory are diagnostic, not benchmarked here; RSS is not measured.

**Cost/model recheck:** the TV4 replay counts first/last pen cycles via LIFT and includes p0/p_end UP travel; internally it compares dyadic exact sums of already-binary64 stroke/UP primitives, not rounded display J. That is consistent with Docs 31's J within this declared DEV arithmetic policy. It does not certify Euclidean primitive/geometry error or physical time. Near-contact with distinct endpoints is unsupported by DEV and remains Q04; no connector/bridge was added.

**Not done / next gates:** H_geom cannot be honestly ranked yet: `ReferenceGeometry` currently carries source hash and mapping policy ID, not reference stroke coordinates/correspondence (Q03). Beam and versioned JSONL runner are separate TV2 slices; no gap/equivalence or lambda cutoff claim is emitted (Q07–Q12). TV1 quality gate/reference/custody, TV3 oracle/primitive, numeric tolerance, exact scope/completion budget and human reviews remain open. Balas/RTSP/PCGTSP page-level full-text table remains Q16 PENDING; publisher abstracts from the S0 review were not upgraded to full-text evidence. HOLDOUT stays closed, PR3 remains closed, and no other owner's work or hardware was changed.
