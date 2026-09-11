"use client"

import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Legend
} from "recharts"
import { ChartPoint } from "@/hooks/useExperimentStream"

export function GuardrailChart({ data }: { data: ChartPoint[] }) {
    const filtered = data.filter(d => d.z_score !== null)

    return (
        <ResponsiveContainer width="100%" height={300}>
      <LineChart data={filtered} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="n" label={{ value: "Events", position: "insideBottom", offset: -2 }} />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" />
        <ReferenceLine
          y={-2.326}
          stroke="red"
          strokeDasharray="6 3"
          label={{ value: "p=0.01 threshold", fill: "red", fontSize: 12 }}
        />
        <Line
          type="monotone"
          dataKey="z_score"
          stroke="#f97316"
          dot={false}
          name="Revenue Z-Score"
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>  
    )
}