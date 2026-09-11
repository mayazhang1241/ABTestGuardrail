import { Experiment, HistorySnapshot } from "@/lib/types"

const API_BASE = "http://localhost:8000"

export async function fetchExperiments(): Promise<Experiment[]> {
    const res = await fetch(`${API_BASE}/experiments`)
    if (!res.ok) {
        throw new Error(`Failed to fetch experiments: ${res.statusText}`)
    }
    return res.json()
}

export async function fetchExperimentHistory(id: number): Promise<HistorySnapshot[]> {
    const res = await fetch(`${API_BASE}/experiments/${id}/history`)
    if (!res.ok) {
        throw new Error(`Failed to fetch experiment history: ${res.statusText}`)
    }
    return res.json()
}