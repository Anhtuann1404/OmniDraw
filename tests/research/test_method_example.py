"""Hand-derived TV4 witness, not TV2's baseline implementation or TV3 oracle."""

from math import sqrt
from pathlib import Path
import pytest

from backend.research.geometry import check_selected_geometry
from backend.research.joint_dp import solve_fixed_configuration, solve_joint
from backend.research.schedule_checker import check_schedule_cost
from backend.research.schemas import Budget, ResearchCase, Schedule, ScheduleAction, StrokeRef, Theta
from backend.research.service import load_manifest

FIXTURE = Path(__file__).parent / 'fixtures' / 'method_gap_example.json'
BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=2, memory_limit_mb=64)


def schedule(case, cid, late=False):
    refs = [(0, cid, 'body'), (0, cid, 'tone'), (1, 'b-fixed', 'body')]
    if late:
        refs = [refs[0], refs[2], refs[1]]
    return Schedule(candidate_ids=[cid, 'b-fixed'], boundary_convention_id=case.boundary.convention_id,
                    actions=[ScheduleAction(stroke=StrokeRef(owner_index=o, candidate_id=c, stroke_id=s),
                                            orientation='forward', transition='LIFT') for o, c, s in refs])


@pytest.mark.parametrize('forget', [False, True])
@pytest.mark.parametrize('rho,lam', [(.5, 2), (1, 0), (2, 4)])
def test_two_configurations_and_all_legal_orders_match_hand_values(forget, rho, lam):
    case = load_manifest(FIXTURE)[0]
    theta = Theta(rho=rho, lambda_mm=lam)
    expected_up = {('a-local', False): 3 * sqrt(2), ('a-local', True): 4 + sqrt(10),
                   ('a-delayed', False): 2 * sqrt(5) + sqrt(2), ('a-delayed', True): 2}
    values = {}
    for (cid, late), up in expected_up.items():
        pi = schedule(case, cid, late)
        replay = check_schedule_cost(case, pi, theta)
        assert check_selected_geometry(case, pi)['status'] == 'PASS'
        assert replay.L_down_mm == 3 and replay.N_cycle == 3
        assert replay.L_up_mm == pytest.approx(up)
        assert replay.J_mm == pytest.approx(3 + rho * up + 3 * lam)
        values[cid, late] = replay.J_mm
    # Reference immediate-mark order ranks local first, while optimal scheduling
    # chooses the other geometry. This checks the witness, not a TV2 ranker.
    assert values['a-local', False] < values['a-delayed', False]
    local = solve_fixed_configuration(case, ['a-local', 'b-fixed'], theta, BUDGET, safe_forget=forget)
    delayed = solve_fixed_configuration(case, ['a-delayed', 'b-fixed'], theta, BUDGET, safe_forget=forget)
    joint = solve_joint(case, theta, BUDGET, safe_forget=forget)
    for run in (local, delayed, joint):
        assert run.outcome == 'OPTIMAL' and run.search_complete
        assert run.independent_validation == 'NOT_RUN'
        assert run.candidate_set_sha256 == case.candidate_set_sha256
    assert local.replay.J_mm == pytest.approx(values['a-local', False])
    assert delayed.replay.J_mm == pytest.approx(values['a-delayed', True])
    assert joint.schedule == schedule(case, 'a-delayed', True)
    assert joint.replay.J_mm == pytest.approx(delayed.replay.J_mm)
    assert local.replay.J_mm > joint.replay.J_mm


@pytest.mark.parametrize('forget', [False, True])
def test_deadline_zero_removes_delayed_order_and_restores_local_winner(forget):
    original = load_manifest(FIXTURE)[0]
    data = original.model_dump(mode='json')
    data['delay_policy'] = {'synthetic-tone': 0}
    case = ResearchCase.prepare(data)
    assert case.candidate_set_sha256 != original.candidate_set_sha256
    theta = Theta(rho=.5, lambda_mm=2)
    with pytest.raises(ValueError, match='deadline'):
        check_schedule_cost(case, schedule(case, 'a-delayed', True), theta)
    joint = solve_joint(case, theta, BUDGET, safe_forget=forget)
    assert joint.outcome == 'OPTIMAL' and joint.schedule == schedule(case, 'a-local')
    assert joint.replay.J_mm == pytest.approx(9 + 1.5 * sqrt(2))
