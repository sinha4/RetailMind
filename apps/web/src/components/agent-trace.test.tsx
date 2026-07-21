import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AgentTrace } from "@/components/agent-trace";

describe("AgentTrace", () => {
  it("shows provider, latency, and safe fallback details", () => {
    render(
      <AgentTrace
        trace={[
          {
            agent: "intent",
            summary: "AI unavailable; used validated intent fallback.",
            mode: "deterministic",
            provider: "fallback",
            latencyMs: null,
            promptVersion: null,
          },
          {
            agent: "brand-voice",
            summary: "Presented a warm response.",
            mode: "ai",
            provider: "google-gemini",
            latencyMs: 42,
            promptVersion: "brand-v1",
          },
        ]}
      />,
    );

    expect(screen.getByText("How RetailMind chose these")).toBeInTheDocument();
    expect(screen.getByText(/deterministic · fallback/i)).toBeInTheDocument();
    expect(screen.getByText(/ai · google-gemini · 42ms/i)).toBeInTheDocument();
  });

  it("renders unknown data agents without optional provider metadata", () => {
    render(
      <AgentTrace
        trace={[
          {
            agent: "policy-check",
            summary: "No restricted claim was found.",
            mode: "data",
            provider: null,
            latencyMs: 0,
            promptVersion: null,
          },
        ]}
      />,
    );

    expect(screen.getByText("policy-check")).toBeInTheDocument();
    expect(screen.getByText("data")).toBeInTheDocument();
  });
});
