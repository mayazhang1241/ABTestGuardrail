import math
from stats.models import Event, GuardrailState

class GuardrailEngine:
    def __init__(self, z_threshold: float = -2.326, pause_after: int = 3):
        self.z_threshold = z_threshold
        self.pause_after = pause_after
        self.reset()

    def reset(self):
        self._n = 0
        self._mean = 0.0
        self._M2 = 0.0
        self._consecutive_flags = 0
        self._paused = False

    def update(self, control_event: Event, treatment_event: Event) -> GuardrailState:
        diff = treatment_event.revenue - control_event.revenue

        self._n += 1
        delta = diff - self._mean
        self._mean += delta / self._n
        delta2 = diff - self._mean
        self._M2 += delta * delta2

        std = math.sqrt(self._M2 / (self._n - 1)) if self._n >= 2 else 0.0
        z = self._mean / (std / math.sqrt(self._n)) if self._n >= 2 and std > 0.0 else 0.0

        flagged = self._n >= 2 and z < self.z_threshold

        if not self._paused:
            self._consecutive_flags = self._consecutive_flags + 1 if flagged else 0
            if self._consecutive_flags >= self.pause_after:
                self._paused = True

        if self._paused:
            status = "paused"
        elif flagged:
            status = "flagged"
        else:
            status = "ok"

        return GuardrailState(
            n_pairs=self._n,
            mean_diff=self._mean,
            std_diff=std,
            z_score=z,
            status=status,
            consecutive_flags=self._consecutive_flags,
        )