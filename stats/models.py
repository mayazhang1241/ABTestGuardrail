from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    p_control: float
    tau: float
    alpha: float = 0.05
    revenue_mu: float = 10.0
    revenue_sigma: float = 5.0
    event_rate: float = 10.0
    max_n: int = 10_000

@dataclass
class Event:
    timestamp: float
    user_id: str
    arm: str
    converted: bool
    revenue: float

@dataclass
class TestState:
    n_control: int
    n_treatment: int
    p_hat_control: float
    p_hat_treatment: float
    mixture_stat: float
    threshold: float
    status: str

@dataclass
class GuardrailState:
    n_pairs: int
    mean_diff: float
    std_diff: float
    z_score: float
    status: str
    consecutive_flags: int