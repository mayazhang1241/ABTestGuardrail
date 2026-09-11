export interface TestState {
    n_control: number
    n_treatment: number
    p_hat_control: number
    p_hat_treatment: number
    mixture_stat: number
    threshold: number
    status: "running" | "winner" | "inconclusive"
}

export interface GuardrailState {
    n_pairs: number
    mean_diff: number
    std_diff: number
    z_score: number
    status: "ok" | "flagged" | "paused"
    consecutive_flags: number
}

export interface Snapshot {
    experiment_id: number
    test: TestState
    guardrail: GuardrailState | null
}

export interface Experiment {
    id: number
    p_control: number
    tau: number
    true_effect: number
    started_at: string
    ended_at: string | null
    final_status: string | null
}

export interface HistorySnapshot {
    ts: string
    n_control: number
    n_treatment: number
    p_hat_control: number
    p_hat_treatment: number
    mixture_stat: number
    test_status: string
    guardrail_n_pairs: number | null
    guardrail_mean_diff: number | null
    guardrail_z_score: number | null
    guardrail_status: string | null
}