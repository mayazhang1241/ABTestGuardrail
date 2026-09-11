"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useExperimentStream } from "@/hooks/useExperimentStream"
import { ExperimentControls } from "@/components/ExperimentControls"
import { LiveChart } from "@/components/LiveChart"
import { GuardrailChart } from "@/components/GuardrailChart"
import { StatusBadge } from "@/components/StatusBadge"
import { ExperimentHistory } from "@/components/ExperimentHistory"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const queryClient = new QueryClient()

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  )
}

function Dashboard() {
  const { start, stop, connected, finished, testState, guardrailState, chartData } = useExperimentStream()
  const running = connected && !finished

  return (
    <main className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">

        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">A/B Test Guardrail</h1>
          {testState && <StatusBadge status={testState.status} />}
        </div>

        <div className="grid grid-cols-4 gap-6">
          <div className="col-span-3 space-y-6">
            <ExperimentControls onStart={start} onStop={stop} running={running} />

            <Card>
              <CardHeader>
                <CardTitle>Sequential Test — Mixture Statistic</CardTitle>
              </CardHeader>
              <CardContent>
                <LiveChart data={chartData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Guardrail — Revenue Z-Score</CardTitle>
                {guardrailState && <StatusBadge status={guardrailState.status} />}
              </CardHeader>
              <CardContent>
                <GuardrailChart data={chartData} />
              </CardContent>
            </Card>

            {testState && (
              <Card>
                <CardHeader><CardTitle>Live Stats</CardTitle></CardHeader>
                <CardContent className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Control N</p>
                    <p className="font-medium">{testState.n_control}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Treatment N</p>
                    <p className="font-medium">{testState.n_treatment}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">p̂ Control</p>
                    <p className="font-medium">{testState.p_hat_control.toFixed(3)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">p̂ Treatment</p>
                    <p className="font-medium">{testState.p_hat_treatment.toFixed(3)}</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="col-span-1">
            <ExperimentHistory />
          </div>
        </div>
      </div>
    </main>
  )
}
