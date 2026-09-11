"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

interface Props {
    onStart: (params: {
        p_control: number
        tau: number
        true_effect: number
        delay: number
    }) => void
    onStop: () => void
    running: boolean
}

export function ExperimentControls({ onStart, onStop, running }: Props) {
    const [pControl, setPControl] = useState("0.10")
    const[tau, setTau] = useState("0.02")
    const[trueEffect, setTrueEffect] = useState("0.03")
    const[delay, setDelay] = useState("0.05")

    const handleStart = () => {
        onStart({
            p_control: parseFloat(pControl),
            tau: parseFloat(tau),
            true_effect: parseFloat(trueEffect),
            delay: parseFloat(delay),
        })
    }

      return (
    <Card>
      <CardHeader>
        <CardTitle>Experiment Config</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label>Control conversion rate</Label>
          <Input value={pControl} onChange={e => setPControl(e.target.value)} disabled={running} />
        </div>
        <div className="space-y-1">
          <Label>Tau (effect size prior)</Label>
          <Input value={tau} onChange={e => setTau(e.target.value)} disabled={running} />
        </div>
        <div className="space-y-1">
          <Label>True effect</Label>
          <Input value={trueEffect} onChange={e => setTrueEffect(e.target.value)} disabled={running} />
        </div>
        <div className="space-y-1">
          <Label>Delay (seconds/event)</Label>
          <Input value={delay} onChange={e => setDelay(e.target.value)} disabled={running} />
        </div>
        <div className="col-span-2">
          {running
            ? <Button variant="destructive" className="w-full" onClick={onStop}>Stop</Button>
            : <Button className="w-full" onClick={handleStart}>Start Experiment</Button>
          }
        </div>
      </CardContent>
    </Card>
  )
}