from itertools import islice
import pytest
from stats.models import ExperimentConfig
from stats.simulator import DataSimulator

N = 5000
SEED = 42

@pytest.fixture
def config():
    return ExperimentConfig(p_control=0.10, tau=0.02)

@pytest.fixture
def events(config):
    sim = DataSimulator(config, true_effect=0.03)
    return list(islice(sim.stream(seed=SEED), N))

def test_arm_balance(events):
    n_treatment = sum(1 for e in events if e.arm == "treatment")
    assert 0.45 <= n_treatment / N <= 0.55

def test_control_conversion_rate(events, config):
    control = [e for e in events if e.arm == "control"]
    rate = sum(e.converted for e in control) / len(control)
    assert abs(rate - config.p_control) < 0.03

def test_treatment_conversion_rate(events, config):
    treatment = [e for e in events if e.arm == "treatment"]
    rate = sum(e.converted for e in treatment) / len(treatment)
    assert abs(rate - (config.p_control + 0.03)) < 0.03

def test_revenue_nonnegative(events):
    assert all(e.revenue >= 0.0 for e in events)

def test_revenue_zero_when_not_converted(events):
    assert all(e.revenue == 0.0 for e in events if not e.converted)

def test_timestamps_increasing(events):
    timestamps = [e.timestamp for e in events]
    assert all(t2 > t1 for t1, t2 in zip(timestamps, timestamps[1:]))

def test_seeded_reproducibility(config):
    sim = DataSimulator(config, true_effect=0.03)
    a = list(islice(sim.stream(seed=SEED), 100))
    b = list(islice(sim.stream(seed=SEED), 100))
    assert all(e1.arm == e2.arm and e1.converted == e2.converted for e1, e2 in zip(a, b))