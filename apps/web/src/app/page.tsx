import { ShoppingExperience } from "@/components/shopping-experience";
import type { CustomerContext } from "@/lib/retailmind-types";

const apiUrl =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

async function getLearnedPreferences() {
  try {
    const response = await fetch(
      `${apiUrl}/v1/customers/demo-customer/context`,
      {
        cache: "no-store",
      },
    );
    if (!response.ok) return [];
    const context = (await response.json()) as CustomerContext;
    return [
      ...new Set(
        context.memories
          .filter(
            (fact) =>
              fact.attribute === "material" && fact.sentiment === "negative",
          )
          .map((fact) => `Avoid ${fact.value}`),
      ),
    ];
  } catch {
    return [];
  }
}

export default async function Home() {
  const learnedPreferences = await getLearnedPreferences();

  return (
    <main className="min-h-screen">
      <header className="mx-auto flex max-w-[1440px] items-center justify-between px-5 py-5 sm:px-8 lg:px-12">
        <a
          className="flex items-center gap-3"
          href="#top"
          aria-label="RetailMind home"
        >
          <span className="grid size-9 place-items-center rounded-full bg-[var(--ink)] text-sm font-semibold text-white">
            R
          </span>
          <span className="text-lg font-semibold tracking-[-0.03em]">
            RetailMind
          </span>
        </a>
        <div className="flex items-center gap-3">
          <span className="hidden text-sm text-[var(--muted)] sm:inline">
            Shopping as Maya
          </span>
          <span className="size-8 rounded-full bg-[linear-gradient(145deg,#d9aa79,#7d4c36)] ring-2 ring-white" />
        </div>
      </header>

      <ShoppingExperience initialLearnedPreferences={learnedPreferences} />
    </main>
  );
}
