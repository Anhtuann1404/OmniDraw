"""Numeric regressions authored by TV4; primitive accuracy/oracle still PENDING."""

from fractions import Fraction
from math import inf, nextafter
from pathlib import Path
import sys

import pytest

from backend.research.cost_arithmetic import COST_POLICY, cost_interval, rounded_cost, weighted_cost
from backend.research.dev_solve import result_packet
from backend.research.geometry import compile_geometry
from backend.research.joint_dp import solve_fixed_configuration, solve_joint
from backend.research.schemas import Domain, ResearchCase, Theta
from backend.research.service import load_manifest
from backend.research.vertex_analysis import analyze_fixed_schedule
from tests.research.test_joint_dp import tiny_case, BUDGET


def rounding_case(two_owners=True):
    cases = load_manifest(Path(__file__).parent / 'fixtures' / 'numeric_rounding_cases.json')
    return cases[0 if two_owners else 1]


@pytest.mark.parametrize('forget', [False, True])
@pytest.mark.parametrize('two_owners', [False, True])
def test_large_cycle_cost_does_not_swallow_geometry_difference(forget, two_owners):
    case = rounding_case(two_owners)
    theta = Theta(rho=1, lambda_mm=2**53)
    tail = ['v0'] if two_owners else []
    a = solve_fixed_configuration(case, ['v0'] + tail, theta, BUDGET, safe_forget=forget)
    b = solve_fixed_configuration(case, ['v1'] + tail, theta, BUDGET, safe_forget=forget)
    joint = solve_joint(case, theta, BUDGET, safe_forget=forget)
    assert a.objective_exact > b.objective_exact == joint.objective_exact
    assert joint.schedule.candidate_ids == ['v1'] + tail
    assert joint.objective_exact == joint.replay.objective_exact
    assert joint.replay.J_mm == float(joint.objective_exact)
    assert joint.cost_policy_id == COST_POLICY
    if two_owners:
        assert a.replay.J_mm > b.replay.J_mm  # Old DP picked the worse displayed J.
    else:
        assert a.replay.J_mm == b.replay.J_mm  # Display rounding must not define ties.
    packet = result_packet(case, theta, BUDGET, joint, ('a' * 40, None), 0)
    lo = packet['result']['bounds']['lower_bound_J_mm']
    hi = packet['result']['bounds']['upper_bound_J_mm']
    assert Fraction(lo) <= joint.objective_exact <= Fraction(hi)
    assert packet['objective_exact_ratio'] == str(joint.objective_exact)
    assert packet['config']['cost_policy_id'] == COST_POLICY


@pytest.mark.parametrize('forget', [False, True])
def test_true_dyadic_tie_uses_stable_action_order(forget):
    case = tiny_case([[[[0, 0], [1, 0]], [[0, 0], [1, 0]]]])
    data = case.model_dump(mode='json')
    data['candidates'][0]['variants'].reverse()
    reversed_case = ResearchCase.prepare(data)
    for current in (case, reversed_case):
        run = solve_joint(current, Theta(rho=.5, lambda_mm=2), BUDGET, safe_forget=forget)
        assert run.schedule.candidate_ids == ['v0']


def test_vertex_regret_is_not_difference_of_rounded_totals():
    case = rounding_case(False)
    theta = Theta(rho=1, lambda_mm=2**53)
    pi = solve_fixed_configuration(case, ['v0'], theta, BUDGET).schedule
    domain = Domain(rho_min=1, rho_max=1, lambda_min_mm=2**53, lambda_max_mm=2**53)
    result = analyze_fixed_schedule(case, pi, domain, BUDGET)
    assert result['certificate_status'] == 'NOT_CERTIFIED'
    for vertex in result['vertices']:
        assert vertex['J_pi_mm'] == vertex['dev_optimum_J_mm']
        assert vertex['dev_regret_mm'] == pytest.approx(.3)


def test_subnormal_product_survives_until_output_and_is_enclosed():
    theta = Theta(rho=nextafter(0, 1), lambda_mm=0)
    exact = weighted_cost(0., .1, 0, theta)
    assert exact > 0 and theta.rho * .1 == 0
    assert rounded_cost(exact) == 0
    lo, hi = cost_interval(exact)
    assert lo == 0 and hi == nextafter(0, 1)
    assert Fraction(lo) <= exact <= Fraction(hi)


@pytest.mark.parametrize('value', [inf, -inf, float('nan')])
def test_nonfinite_primitives_rejected(value):
    with pytest.raises(ValueError, match='Non-finite'):
        weighted_cost(value, 0., 0, Theta(rho=1, lambda_mm=0))


def test_overflow_and_unrepresentable_enclosure_rejected():
    with pytest.raises(ValueError, match='Non-finite'):
        rounded_cost(Fraction(sys.float_info.max) * 2)
    with pytest.raises(ValueError, match='enclosure'):
        cost_interval(Fraction(sys.float_info.max) + 1)


@pytest.mark.parametrize('gap,infeasible', [(nextafter(.2, 0), True), (.2, False),
                                           (nextafter(.2, inf), False)])
def test_adjacent_binary64_floor_keeps_hard_boundary(gap, infeasible):
    case = tiny_case([[[[0, 0], [1, 0]]], [[[0, gap], [1, gap]]]])
    run = solve_joint(case, Theta(rho=1, lambda_mm=0), BUDGET)
    assert (run.outcome == 'INFEASIBLE') == infeasible


def test_one_ulp_near_contact_not_silently_snapped():
    case = load_manifest(Path(__file__).parent / 'fixtures' / 'solver_dev_cases.json')[0]
    data = case.model_dump(mode='json')
    data['candidates'][1]['variants'][0]['strokes'][1]['polyline_mm'][0][0] = nextafter(4., inf)
    with pytest.raises(ValueError, match='endpoint'):
        compile_geometry(ResearchCase.prepare(data))


def test_cli_does_not_accept_same_displayed_j_with_different_exact_cost(monkeypatch, tmp_path):
    from dataclasses import replace
    from backend.research import dev_solve
    case = rounding_case(False)
    theta = Theta(rho=1, lambda_mm=2**53)
    a = replace(solve_fixed_configuration(case, ['v0'], theta, BUDGET), scope='full_candidate_set')
    b = replace(solve_fixed_configuration(case, ['v1'], theta, BUDGET), scope='full_candidate_set')
    assert a.replay.J_mm == b.replay.J_mm and a.objective_exact != b.objective_exact
    monkeypatch.setattr(dev_solve, 'load_manifest', lambda path: [case])
    monkeypatch.setattr(dev_solve, 'solve_joint', lambda *args, safe_forget=False: b if safe_forget else a)
    monkeypatch.setattr(dev_solve, 'git_snapshot', lambda: ('a' * 40, None))
    target = tmp_path / 'run.json'
    args = ['--manifest', str(Path(__file__)), '--case-id', case.case_id, '--rho', '1',
            '--lambda-mm', str(2**53), '--mode', 'both', '--wall-time-ms', '10000',
            '--max-states', '100000', '--memory-limit-mb', '64', '--output', str(target)]
    assert dev_solve.main(args) == 1
    import json
    assert json.loads(target.read_text())['compare_modes'] == 'FAIL'
