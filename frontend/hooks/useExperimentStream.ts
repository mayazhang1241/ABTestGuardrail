import { useState, useRef, useCallback } from "react"
import { Snapshot, TestState, GuardrailState } from "@/lib/types"

const WS_BASE = "ws://localhost:8000"

export interface ChartPoint {
  n: number
  mixture_stat: number
  threshold: number
  z_score: number | null
}

export interface StreamState {
  experimentId: number | null
  testState: TestState | null
  guardrailState: GuardrailState | null
  chartData: ChartPoint[]
  connected: boolean
  finished: boolean
}

export function useExperimentStream() {
  const wsRef = useRef<WebSocket | null>(null)
  const [state, setState] = useState<StreamState>({
    experimentId: null,
    testState: null,
    guardrailState: null,
    chartData: [],
    connected: false,
    finished: false,
  })

  const start = useCallback((params: {
    p_control: number
    tau: number
    true_effect: number
    delay: number
  }) => {
    wsRef.current?.close()

    const qs = new URLSearchParams({
      p_control: String(params.p_control),
      tau: String(params.tau),
      true_effect: String(params.true_effect),
      delay: String(params.delay),
    })
    const ws = new WebSocket(`${WS_BASE}/ws/experiment?${qs}`)
    wsRef.current = ws

    setState({
      experimentId: null,
      testState: null,
      guardrailState: null,
      chartData: [],
      connected: false,
      finished: false,
    })

    ws.onopen = () => setState(s => ({ ...s, connected: true }))

    ws.onmessage = (e) => {
      const snap: Snapshot = JSON.parse(e.data)
      setState(s => ({
        ...s,
        experimentId: snap.experiment_id,
        testState: snap.test,
        guardrailState: snap.guardrail,
        chartData: [...s.chartData, {
          n: snap.test.n_control + snap.test.n_treatment,
          mixture_stat: snap.test.mixture_stat,
          threshold: snap.test.threshold,
          z_score: snap.guardrail?.z_score ?? null,
        }],
      }))
    }

    ws.onclose = () => setState(s => ({ ...s, connected: false, finished: true }))
  }, [])

  const stop = useCallback(() => {
    wsRef.current?.close()
  }, [])

  return { ...state, start, stop }
}
