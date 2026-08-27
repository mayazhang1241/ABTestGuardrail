import math
from stats.models import Event, ExperimentConfig, TestState

class MixtureSPRT:
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.threshold = 1.0 / config.alpha
        self._tau2 = config.tau ** 2
        self.reset()

    def reset(self):
        self._n_t = 0
        self._n_c = 0
        self._s_t = 0
        self._s_c = 0

    def update(self, event: Event) -> TestState:
        if event.arm == "treatment":
            self._n_t += 1
            self._s_t += int(event.converted)
        else:
            self._n_c += 1
            self._s_c += int(event.converted)

        p_hat_t = self._s_t / self._n_t if self._n_t > 0 else 0.0
        p_hat_c = self._s_c / self._n_c if self._n_c > 0 else 0.0
        m_n = self._compute_mixture_stat(p_hat_t, p_hat_c) if self._n_t >= 1 and self._n_c >= 1 else 0.0

        if m_n >= self.threshold:
            status = "winner"
        elif self._n_t >= self.config.max_n:
            status = "inconclusive"
        else:
            status = "running"

        return TestState(
            n_control=self._n_c,
            n_treatment=self._n_t,
            p_hat_control=p_hat_c,
            p_hat_treatment=p_hat_t,
            mixture_stat=m_n,
            threshold=self.threshold,
            status=status
        )

    def _compute_mixture_stat(self, p_hat_t: float, p_hat_c: float) -> float:
        d_hat = p_hat_t - p_hat_c
        p_pooled = (self._s_t + self._s_c) / (self._n_t + self._n_c)
        sigma2_n = p_pooled * (1 - p_pooled) * (1 / self._n_t + 1 / self._n_c)

        if sigma2_n == 0.0:
            return 1.0

        denom = sigma2_n + self._tau2
        return math.sqrt(sigma2_n / denom) * math.exp(d_hat ** 2 * self._tau2 / (2 * sigma2_n * denom))