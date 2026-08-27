from typing import Generator, Optional
import numpy as np
from stats.models import Event, ExperimentConfig

class DataSimulator:
    def __init__(self, config: ExperimentConfig, true_effect: float = 0.0):
        self.config = config
        self.p_treatment = config.p_control + true_effect
        self._rev_log_mu = np.log(
            config.revenue_mu ** 2 / np.sqrt(config.revenue_sigma ** 2 + config.revenue_mu ** 2)
        )
        self._rev_log_sigma = np.sqrt(
            np.log(1 + (config.revenue_sigma ** 2) / (config.revenue_mu ** 2))
        )

    def stream(self, seed: Optional[int] = None) -> Generator[Event, None, None]:
        rng = np.random.default_rng(seed)
        t = 0.0
        user_idx = 0

        while True:
            t += rng.exponential(1.0 / self.config.event_rate)
            arm = "treatment" if rng.random() < 0.5 else "control"
            p = self.p_treatment if arm == "treatment" else self.config.p_control
            converted = bool(rng.random() < p)
            revenue = float(rng.lognormal(self._rev_log_mu, self._rev_log_sigma)) if converted else 0.0

            yield Event(
                timestamp=t,
                user_id=f"user_{user_idx}",
                arm=arm,
                converted=converted,
                revenue=revenue
            )
            user_idx += 1