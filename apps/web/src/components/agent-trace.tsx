import type { AgentTraceStep } from "@/lib/retailmind-types";

interface AgentTraceProps {
  trace: AgentTraceStep[];
}

const agentLabels: Record<string, string> = {
  intent: "Understood your request",
  "customer-intelligence": "Recalled what matters",
  personalization: "Ranked the collection",
  inventory: "Checked live availability",
  "brand-voice": "Prepared your edit",
};

export function AgentTrace({ trace }: AgentTraceProps) {
  return (
    <details className="group rounded-2xl border border-black/8 bg-white/65 p-4">
      <summary className="flex cursor-pointer list-none items-center justify-between text-sm font-semibold focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--accent)]">
        <span className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-[var(--success)] shadow-[0_0_0_4px_rgb(75_132_99_/_12%)]" />
          How RetailMind chose these
        </span>
        <span className="text-lg font-normal transition group-open:rotate-45">
          +
        </span>
      </summary>
      <ol className="mt-5 grid gap-4 border-t border-black/8 pt-5 md:grid-cols-5">
        {trace.map((step, index) => (
          <li className="relative" key={step.agent}>
            <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-[var(--accent)]">
              0{index + 1}
            </p>
            <p className="mt-1 text-xs font-semibold">
              {agentLabels[step.agent] ?? step.agent}
            </p>
            <p className="mt-1 text-[11px] leading-4 text-[var(--muted)]">
              {step.summary}
            </p>
          </li>
        ))}
      </ol>
    </details>
  );
}
