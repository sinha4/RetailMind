const capabilities = [
  "Remembers preferences across visits",
  "Learns from returns and skipped products",
  "Explains why each recommendation fits",
  "Speaks in the retailer's own voice",
];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8 sm:px-10">
      <nav className="flex items-center justify-between border-b border-black/10 pb-5">
        <span className="text-lg font-semibold tracking-tight">RetailMind</span>
        <span className="rounded-full bg-[var(--accent)]/10 px-3 py-1 text-xs font-medium text-[var(--accent)]">
          Foundation ready
        </span>
      </nav>

      <section className="grid flex-1 items-center gap-12 py-16 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
            Hyper-personal shopping orchestrator
          </p>
          <h1 className="max-w-3xl text-5xl font-semibold leading-[1.02] tracking-[-0.04em] sm:text-7xl">
            Shopping that gets to know you.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-[var(--muted)]">
            Persistent customer memory, explainable recommendations, live inventory, and a brand
            voice that stays unmistakably yours.
          </p>
        </div>

        <aside className="rounded-3xl border border-black/10 bg-[var(--card)] p-7 shadow-[0_24px_70px_rgb(31_50_41_/_10%)]">
          <p className="text-sm font-semibold text-[var(--accent)]">What the MVP will prove</p>
          <ul className="mt-5 space-y-4">
            {capabilities.map((capability) => (
              <li className="flex gap-3 text-sm leading-6" key={capability}>
                <span className="mt-2 size-1.5 shrink-0 rounded-full bg-[var(--accent)]" />
                {capability}
              </li>
            ))}
          </ul>
        </aside>
      </section>
    </main>
  );
}

