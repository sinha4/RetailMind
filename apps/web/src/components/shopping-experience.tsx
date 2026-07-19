"use client";

import { FormEvent, useState } from "react";

import { AgentTrace } from "@/components/agent-trace";
import { RecommendationCard } from "@/components/recommendation-card";
import type { ConversationMessageResponse } from "@/lib/retailmind-types";

const suggestions = [
  "Beach holiday under ₹5,000",
  "A blue linen dress in size M",
  "Relaxed travel pieces",
];

const rememberedPreferences = [
  "Natural fabrics",
  "Relaxed fits",
  "Blue tones",
  "Avoid polyester",
];

export function ShoppingExperience() {
  const [message, setMessage] = useState(
    "Find me a beach holiday outfit under ₹5,000",
  );
  const [voice, setVoice] = useState<"warm" | "minimal">("warm");
  const [result, setResult] = useState<ConversationMessageResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submitRequest(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customerId: "demo-customer",
          message: trimmedMessage,
          brandVoice: voice,
        }),
      });

      if (!response.ok)
        throw new Error("RetailMind could not complete that request.");
      setResult((await response.json()) as ConversationMessageResponse);
    } catch {
      setError(
        "We couldn't reach the recommendation service. Make sure the API is running.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function selectSuggestion(suggestion: string) {
    setMessage(suggestion);
  }

  return (
    <>
      <section
        id="top"
        className="mx-auto max-w-[1440px] px-5 pb-12 pt-10 sm:px-8 lg:px-12 lg:pt-16"
      >
        <div className="grid items-end gap-10 lg:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.75fr)]">
          <div>
            <p className="eyebrow">Your personal edit</p>
            <h1 className="mt-5 max-w-4xl text-5xl font-medium leading-[0.96] tracking-[-0.06em] sm:text-7xl lg:text-[5.4rem]">
              Tell us where you&apos;re going. We&apos;ll remember the rest.
            </h1>
          </div>
          <div className="lg:pb-2">
            <p className="max-w-lg text-base leading-7 text-[var(--muted)]">
              Thoughtful recommendations shaped by your style, size, budget, and
              the pieces that didn&apos;t work before.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {rememberedPreferences.map((preference) => (
                <span className="preference-pill" key={preference}>
                  <span className="size-1.5 rounded-full bg-[var(--accent)]" />
                  {preference}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-12 rounded-[2rem] border border-black/8 bg-white/80 p-3 shadow-[0_28px_90px_rgb(35_53_43_/_10%)] backdrop-blur sm:p-4">
          <form onSubmit={submitRequest}>
            <label className="sr-only" htmlFor="shopping-request">
              What are you shopping for?
            </label>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="flex min-w-0 flex-1 items-center gap-3 px-3 sm:px-4">
                <span
                  className="text-xl text-[var(--accent)]"
                  aria-hidden="true"
                >
                  ✦
                </span>
                <input
                  autoComplete="off"
                  className="h-14 min-w-0 flex-1 bg-transparent text-base outline-none placeholder:text-black/35 sm:text-lg"
                  id="shopping-request"
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="What are you shopping for?"
                  value={message}
                />
              </div>
              <button
                className="h-14 rounded-full bg-[var(--ink)] px-7 text-sm font-semibold text-white transition hover:bg-[var(--accent)] disabled:cursor-wait disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
                disabled={isLoading || !message.trim()}
                type="submit"
              >
                {isLoading ? "Curating…" : "Find my edit"}
              </button>
            </div>

            <div className="mt-3 flex flex-col justify-between gap-3 border-t border-black/8 px-3 pt-3 sm:flex-row sm:items-center sm:px-4">
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion) => (
                  <button
                    className="rounded-full bg-[var(--soft)] px-3 py-1.5 text-xs text-[var(--muted)] transition hover:text-[var(--ink)] focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
                    key={suggestion}
                    onClick={() => selectSuggestion(suggestion)}
                    type="button"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
              <label className="flex shrink-0 items-center gap-2 text-xs text-[var(--muted)]">
                Voice
                <select
                  className="rounded-full border border-black/10 bg-white px-3 py-1.5 font-semibold text-[var(--ink)] outline-none focus:border-[var(--accent)]"
                  onChange={(event) =>
                    setVoice(event.target.value as "warm" | "minimal")
                  }
                  value={voice}
                >
                  <option value="warm">Warm</option>
                  <option value="minimal">Minimal</option>
                </select>
              </label>
            </div>
          </form>
        </div>

        <div aria-live="polite">
          {error ? (
            <p className="mt-4 rounded-2xl border border-red-900/10 bg-red-50 px-5 py-4 text-sm text-red-900">
              {error}
            </p>
          ) : null}
        </div>
      </section>

      <section className="border-t border-black/8 bg-[var(--section)]">
        <div className="mx-auto max-w-[1440px] px-5 py-12 sm:px-8 lg:px-12 lg:py-16">
          {isLoading ? (
            <div
              aria-label="Preparing recommendations"
              className="grid gap-5 md:grid-cols-3"
            >
              {[1, 2, 3].map((item) => (
                <div
                  className="h-[34rem] animate-pulse rounded-[1.75rem] bg-white/70"
                  key={item}
                />
              ))}
            </div>
          ) : result ? (
            <div className="animate-reveal">
              <div className="mb-8 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
                <div>
                  <p className="eyebrow">Selected for Maya</p>
                  <h2 className="mt-3 max-w-3xl text-3xl font-medium tracking-[-0.04em] sm:text-4xl">
                    {result.assistantMessage}
                  </h2>
                </div>
                <p className="text-sm text-[var(--muted)]">
                  {result.recommendations.length} of 30 pieces selected
                </p>
              </div>

              {result.recommendations.length ? (
                <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                  {result.recommendations.map((recommendation, index) => (
                    <RecommendationCard
                      key={recommendation.product.id}
                      position={index + 1}
                      recommendation={recommendation}
                    />
                  ))}
                </div>
              ) : (
                <div className="rounded-3xl border border-black/8 bg-white p-10 text-center">
                  <p className="text-lg font-semibold">No exact matches yet</p>
                  <p className="mt-2 text-sm text-[var(--muted)]">
                    Try a broader category, material, or budget.
                  </p>
                </div>
              )}

              <div className="mt-8">
                <AgentTrace trace={result.trace} />
              </div>
            </div>
          ) : (
            <div className="grid min-h-52 place-items-center text-center">
              <div>
                <span className="mx-auto grid size-11 place-items-center rounded-full border border-black/10 bg-white text-[var(--accent)]">
                  ✦
                </span>
                <p className="mt-4 text-sm font-semibold">
                  Your edit will appear here
                </p>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  Start with the prompt above or choose a suggestion.
                </p>
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
