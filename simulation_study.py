import statistics
import numpy as np
from stats.models import ExperimentConfig, Event
from stats.simulator import DataSimulator
from stats.sequential import MixtureSPRT
from stats.guardrail import GuardrailEngine

N_TRIALS = 1000

def run_sprt_trial(config, true_effect, seed):
    sim = DataSimulator(config, true_effect=true_effect)
    engine = MixtureSPRT(config)
    for event in sim.stream(seed=seed):
        state = engine.update(event)
        if state.status != "running":
            return state.status, state.n_control + state.n_treatment
    return state.status, state.n_control + state.n_treatment

def run_guardrail_trial(control_rev, treatment_rev, n_pairs, seed):
    rng = np.random.default_rng(seed)
    engine = GuardrailEngine()
    for i in range(n_pairs):
        ctrl_rev = max(0.0, control_rev + rng.normal(0, 5.0))
        trt_rev = max(0.0, treatment_rev + rng.normal(0, 5.0))
        ctrl = Event(float(i), f"c_{i}", "control", ctrl_rev > 0, ctrl_rev)
        trt  = Event(float(i), f"t_{i}", "treatment", trt_rev > 0, trt_rev)
        state = engine.update(ctrl, trt)
        if state.status == "paused":
            return True, i + 1
    return False, n_pairs

def main():
    config_null = ExperimentConfig(p_control=0.10, tau=0.02, alpha=0.05, max_n=2_000)
    results_null = [run_sprt_trial(config_null, 0.0, seed) for seed in range(N_TRIALS)]
    fp_rate = sum(1 for s, _ in results_null if s == "winner") / N_TRIALS

    print(f"=== Null (true_effect=0.0) — {N_TRIALS} trials ===")
    print(f"  False positive rate : {fp_rate*100:.1f}%   (target ≤ 5%)")
    print(f"  Inconclusive rate   : {sum(1 for s,_ in results_null if s=='inconclusive')/N_TRIALS*100:.1f}%")
    print()

    config_alt = ExperimentConfig(p_control=0.10, tau=0.02, alpha=0.05, max_n=10_000)
    results_alt = [run_sprt_trial(config_alt, 0.03, seed) for seed in range(N_TRIALS)]
    power = sum(1 for s, _ in results_alt if s == "winner") / N_TRIALS
    winner_ns = [n for s, n in results_alt if s == "winner"]

    print(f"=== Alternative (true_effect=0.03) — {N_TRIALS} trials ===")
    print(f"  Power (win rate)    : {power*100:.1f}%")
    print(f"  Inconclusive rate   : {sum(1 for s,_ in results_alt if s=='inconclusive')/N_TRIALS*100:.1f}%")
    print(f"  Median N to detect  : {int(statistics.median(winner_ns)) if winner_ns else 'N/A'} events")
    print()

    results_gr = [run_guardrail_trial(10.0, 7.0, 200, seed) for seed in range(N_TRIALS)]
    detection_rate = sum(1 for d, _ in results_gr if d) / N_TRIALS
    detected_at = [n for d, n in results_gr if d]

    print(f"=== Guardrail (revenue drop -30%) — {N_TRIALS} trials ===")
    print(f"  Detection rate      : {detection_rate*100:.1f}%")
    print(f"  Median pairs to flag: {int(statistics.median(detected_at)) if detected_at else 'N/A'}")

if __name__ == "__main__":
    main()
