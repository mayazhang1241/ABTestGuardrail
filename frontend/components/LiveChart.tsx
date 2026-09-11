"use client"

import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Legend
} from "recharts"
import { ChartPoint } from "@/hooks/useExperimentStream"

export function LiveChart({ data }: { data: ChartPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="n" label={{ value: "Events", position: "insideBottom", offset: -2 }} />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" />
        <ReferenceLine
          y={data[0]?.threshold}
          stroke="red"
          strokeDasharray="6 3"
          label={{ value: "Threshold", fill: "red", fontSize: 12 }}
        />
        <Line
          type="monotone"
          dataKey="mixture_stat"
          stroke="#3b82f6"
          dot={false}
          name="Mixture Statistic"
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

