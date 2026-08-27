import numpy as np
from stats.models import Event
from stats.guardrail import GuardrailEngine

def make_event(arm, revenue, i=0):
    return Event(timestamp=float(i), user_id=f"{arm}_{i}", arm=arm, converted=revenue > 0.0, revenue=revenue)

def make_pairs(n, control_rev, treatment_rev, noise=1.0, seed=0):
    rng = np.random.default_rng(seed)
    return [
        (
            make_event("control", max(0.0, control_rev + rng.normal(0, noise)), i),
            make_event("treatment", max(0.0, treatment_rev + rng.normal(0, noise)), i)
        )
        for i in range(n)
    ]

def test_initial_state_is_ok():
    engine = GuardrailEngine()
    state = engine.update(make_event("control", 10.0), make_event("treatment", 10.0))
    assert state.status == "ok"
    assert state.n_pairs == 1

def test_no_revenue_drop_stays_ok():
    engine = GuardrailEngine()
    for ctrl, trt in make_pairs(50, control_rev=10.0, treatment_rev=10.0):
        state = engine.update(ctrl, trt)
    assert state.status == "ok"
    assert state.z_score > -2.326

def test_large_drop_triggers_flag():
    engine = GuardrailEngine()
    for ctrl, trt in make_pairs(20, control_rev=20.0, treatment_rev=5.0):
        state = engine.update(ctrl, trt)

        if state.status in ("flagged", "paused"):
            break
    assert state.status in ("flagged", "paused")

def test_pauses_after_consecutive_flags():
    engine = GuardrailEngine(pause_after=3)
    for ctrl, trt in make_pairs(30, control_rev=20.0, treatment_rev=1.0):
        state = engine.update(ctrl, trt)
    assert state.status == "paused"

def test_reset_clears_state():
    engine = GuardrailEngine()
    for ctrl, trt in make_pairs(20, control_rev=20.0, treatment_rev=5.0):
        engine.update(ctrl, trt)
    engine.reset()
    assert engine._n == 0 and engine._mean == 0.0 and not engine._paused

def test_running_mean_accuracy():
    engine = GuardrailEngine()
    for ctrl, trt in make_pairs(200, control_rev=10.0, treatment_rev=8.0, noise=0.5):
        state = engine.update(ctrl, trt)
    assert abs(state.mean_diff - (-2.0)) < 0.3