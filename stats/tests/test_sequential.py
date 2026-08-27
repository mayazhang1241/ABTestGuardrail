from itertools import islice
import pytest
from stats.models import Event, ExperimentConfig
from stats.simulator import DataSimulator
from stats.sequential import MixtureSPRT

@pytest.fixture
def config():
    return ExperimentConfig(p_control=0.10, tau=0.02, alpha=0.05, max_n=10_000)

def run_experiment(config, true_effect, seed):
    sim = DataSimulator(config, true_effect=true_effect)
    engine = MixtureSPRT(config)
    for event in sim.stream(seed=seed):
        state = engine.update(event)
        if state.status != "running":
            return state
    return state

def test_threshold_is_one_over_alpha(config):
    assert MixtureSPRT(config).threshold == pytest.approx(1.0 / config.alpha)

def test_mixture_stat_zero_before_both_arms_observed(config):
    engine = MixtureSPRT(config)
    event = Event(timestamp=1.0, user_id="u0", arm="treatment", converted=True, revenue=0.0)
    state = engine.update(event)
    assert state.mixture_stat == 0.0
    assert state.status == "running"

def test_reset_clears_state(config):
    sim = DataSimulator(config, true_effect=0.05)
    engine = MixtureSPRT(config)
    for event in islice(sim.stream(seed=0), 200):
        engine.update(event)
    engine.reset()
    assert engine._n_t == 0 and engine._n_c == 0

def test_power():
    config = ExperimentConfig(p_control=0.10, tau=0.05, alpha=0.05, max_n=10_000)
    n_wins = sum(
        1 for seed in range(100)
        if run_experiment(config, true_effect=0.05, seed=seed).status == "winner"
    )
    assert n_wins / 100 >= 0.50

def test_type_i_error():
    config = ExperimentConfig(p_control=0.10, tau=0.02, alpha=0.05, max_n=2_000)
    n_false_positives = sum(
        1 for seed in range(300)
        if run_experiment(config, true_effect=0.0, seed=seed).status == "winner"
    )
    assert n_false_positives / 300 <= 0.10