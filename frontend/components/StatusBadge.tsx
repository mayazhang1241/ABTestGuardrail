import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

const config: Record<string, { label: string; className: string }> = {
    running: { label: "Running", className: "bg-blue-500 text-white" },
    winner: { label: "Winner", className: "bg-green-500 text-white" },
    inconclusive: { label: "Inconclusive", className: "bg-yellow-500 text-white" },
    ok: { label: "OK", className: "bg-green-500 text-white" },
    flagged: { label: "Flagged", className: "bg-orange-500 text-white" },
    paused: { label: "Paused", className: "bg-red-500 text-white" },
}

export function StatusBadge({ status }: { status: string }) {
    const { label, className } = config[status] || { label: status, className: "bg-gray-400 text-white" }
    return <Badge className={cn(className)}>{label}</Badge>
}