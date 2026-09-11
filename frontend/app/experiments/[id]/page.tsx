"use client"

import { useQuery } from "@tanstack/react-query"
import { useParams } from "next/navigation"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fetchExperimentHistory, fetchExperiments } from "@/lib/api"
import { HistorySnapshot } from "@/lib/types"
import { ChartPoint } from "@/hooks/useExperimentStream"
import { LiveChart } from "@/components/LiveChart"
import { GuardrailChart } from "@/components/GuardrailChart"
import { StatusBadge } from "@/components/StatusBadge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"

const queryClient = new QueryClient()

export default function ExperimentPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <ExperimentReplay />
    </QueryClientProvider>
  )
}

function ExperimentReplay() {
  const params = useParams()
  const id = Number(params.id)

  const { data: history = [], isLoading } = useQuery({
    queryKey: ["experiment-history", id],
    queryFn: () => fetchExperimentHistory(id),
  })

  const { data: experiments = [] } = useQuery({
    queryKey: ["experiments"],
    queryFn: fetchExperiments,
  })

  const experiment = experiments.find(e => e.id === id)

  const chartData: ChartPoint[] = history.map((s: HistorySnapshot) => ({
    n: s.n_control + s.n_treatment,
    mixture_stat: s.mixture_stat,
    threshold: 20,  // 1 / alpha (0.05), same default used by MixtureSPRT
    z_score: s.guardrail_z_score,
  }))

  if (isLoading) return <div className="p-6">Loading...</div>

  return (
    <main className="min-h-screen bg-background p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Link href="/" className="text-sm text-muted-foreground hover:underline">← Back</Link>
            <h1 className="text-3xl font-bold mt-1">Run #{id}</h1>
            {experiment && (
              <p className="text-muted-foreground text-sm">
                p_control={experiment.p_control} · tau={experiment.tau} · true_effect={experiment.true_effect}
              </p>
            )}
          </div>
          {experiment?.final_status && <StatusBadge status={experiment.final_status} />}
        </div>

        <Card>
          <CardHeader><CardTitle>Sequential Test — Mixture Statistic</CardTitle></CardHeader>
          <CardContent><LiveChart data={chartData} /></CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Guardrail — Revenue Z-Score</CardTitle></CardHeader>
          <CardContent><GuardrailChart data={chartData} /></CardContent>
        </Card>
      </div>
    </main>
  )
}
