"use client";

import { useState } from "react";

import { AgentTrace } from "@/components/agent-trace";
import type { DeliveryDelayResponse } from "@/lib/retailmind-types";

interface AgentOperationsProps {
  voice: "warm" | "minimal" | "bold";
}

export function AgentOperations({ voice }: AgentOperationsProps) {
  const [delayDays, setDelayDays] = useState(3);
  const [result, setResult] = useState<DeliveryDelayResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function simulateDelay() {
    setIsLoading(true);
    try {
      const response = await fetch("/api/delivery-delay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customerId: "demo-customer",
          orderId: "RM-1001",
          productId: "rm-dress-001",
          delayDays,
          brandVoice: voice,
        }),
      });
      if (response.ok)
        setResult((await response.json()) as DeliveryDelayResponse);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="border-t border-black/8 bg-white">
      <div className="mx-auto max-w-[1440px] px-5 py-12 sm:px-8 lg:px-12">
        <p className="eyebrow">Agent operations demo</p>
        <div className="mt-4 grid gap-6 lg:grid-cols-[0.75fr_1.25fr]">
          <div className="rounded-3xl bg-[var(--soft)] p-6">
            <h2 className="text-2xl font-semibold tracking-[-0.03em]">
              Simulate a delivery delay
            </h2>
            <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
              Tests post-purchase communication, brand voice, and human
              escalation together.
            </p>
            <label className="mt-5 block text-xs font-semibold uppercase tracking-[0.12em]">
              Delay: {delayDays} days
              <input
                className="mt-3 w-full accent-[var(--accent)]"
                max="10"
                min="1"
                onChange={(event) => setDelayDays(Number(event.target.value))}
                type="range"
                value={delayDays}
              />
            </label>
            <button
              className="mt-5 rounded-full bg-[var(--ink)] px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
              disabled={isLoading}
              onClick={simulateDelay}
              type="button"
            >
              {isLoading ? "Running agents…" : "Run post-purchase agents"}
            </button>
          </div>
          <div className="rounded-3xl border border-black/8 p-6">
            {result ? (
              <>
                <p className="text-lg font-semibold">{result.message}</p>
                <p className="mt-3 text-sm text-[var(--muted)]">
                  Human escalation:{" "}
                  {result.escalation.required ? "Required" : "Not required"} —{" "}
                  {result.escalation.reason}
                </p>
                <div className="mt-5">
                  <AgentTrace trace={result.trace} />
                </div>
              </>
            ) : (
              <p className="text-sm text-[var(--muted)]">
                The coordinated agent result will appear here.
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
