"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchExperiments } from "@/lib/api"
import { Experiment } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { StatusBadge } from "@/components/StatusBadge"
import Link from "next/link"

export function ExperimentHistory() {
  const { data: experiments = [], isLoading } = useQuery({
    queryKey: ["experiments"],
    queryFn: fetchExperiments,
    refetchInterval: 5000,
  })

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Past Runs</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 overflow-y-auto max-h-[600px]">
        {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
        {experiments.map((exp: Experiment) => (
          <Link key={exp.id} href={`/experiments/${exp.id}`}>
            <div className="flex items-center justify-between rounded-md border p-2 hover:bg-muted transition-colors cursor-pointer">
              <div className="text-sm">
                <p className="font-medium">Run #{exp.id}</p>
                <p className="text-muted-foreground">
                  p={exp.p_control} · effect={exp.true_effect}
                </p>
              </div>
              {exp.final_status && <StatusBadge status={exp.final_status} />}
            </div>
          </Link>
        ))}
      </CardContent>
    </Card>
  )
}