import type { ProductRecommendation } from "@/lib/retailmind-types";

interface RecommendationComparisonProps {
  before: ProductRecommendation[];
  after: ProductRecommendation[];
  returnedName: string;
}

export function RecommendationComparison({
  before,
  after,
  returnedName,
}: RecommendationComparisonProps) {
  const beforeRank = new Map(before.map((item, index) => [item.product.id, index + 1]));

  return (
    <section className="mt-8 rounded-3xl border border-[var(--accent)]/20 bg-white p-6">
      <p className="eyebrow">Before vs after learning</p>
      <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em]">
        The ranking changed after returning {returnedName}
      </h3>
      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">Before</p>
          <ol className="mt-3 space-y-2">
            {before.map((item, index) => (
              <li className="rounded-xl bg-[var(--section)] px-4 py-3 text-sm" key={item.product.id}>
                #{index + 1} {item.product.name}
              </li>
            ))}
          </ol>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">After</p>
          <ol className="mt-3 space-y-2">
            {after.map((item, index) => {
              const previous = beforeRank.get(item.product.id);
              return (
                <li className="rounded-xl bg-[var(--soft)] px-4 py-3 text-sm" key={item.product.id}>
                  #{index + 1} {item.product.name}
                  {previous && previous !== index + 1 ? ` · was #${previous}` : ""}
                </li>
              );
            })}
          </ol>
        </div>
      </div>
    </section>
  );
}
