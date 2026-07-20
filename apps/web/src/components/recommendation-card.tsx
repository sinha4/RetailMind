"use client";

import Image from "next/image";
import { useState } from "react";

import { ReturnDialog } from "@/components/return-dialog";
import type {
  ProductRecommendation,
  SignalIngestionResponse,
  SignalKind,
} from "@/lib/retailmind-types";

interface RecommendationCardProps {
  recommendation: ProductRecommendation;
  position: number;
  onLearning: (
    kind: SignalKind,
    productId: string,
    productName: string,
    update: SignalIngestionResponse,
  ) => Promise<void>;
}

const categoryArtwork: Record<string, string> = {
  dress: "from-[#ccdadd] via-[#e7dcce] to-[#b4c4b7]",
  top: "from-[#dbe4df] via-[#f0e9dc] to-[#afc7c0]",
  bottom: "from-[#d8d0bd] via-[#ebe4d8] to-[#9fb5a7]",
  set: "from-[#d8c7b3] via-[#ede4d6] to-[#adc3b4]",
  outerwear: "from-[#c8d2c8] via-[#e9e0d4] to-[#9aac9f]",
  swimwear: "from-[#aacbd0] via-[#e9dfcc] to-[#7da5a8]",
  shoes: "from-[#d4c4af] via-[#eee5d8] to-[#af9579]",
  accessory: "from-[#ded4bf] via-[#eee7d8] to-[#bda98a]",
};

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export function RecommendationCard({
  recommendation,
  position,
  onLearning,
}: RecommendationCardProps) {
  const { product, reason, score } = recommendation;
  const art = categoryArtwork[product.category] ?? categoryArtwork.accessory;
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [showReturn, setShowReturn] = useState(false);

  async function recordSignal(kind: SignalKind, reason?: string) {
    if (isSaving) return;
    setIsSaving(true);
    try {
      const response = await fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customerId: "demo-customer",
          productId: product.id,
          kind,
          reason,
        }),
      });
      if (!response.ok) return;

      const update = (await response.json()) as SignalIngestionResponse;
      const feedback = {
        wishlist: "Saved — we'll remember",
        skip: "Noted — showing less like this",
        purchase: "Purchase remembered",
        return: "Return learned — rankings updated",
        view: "Viewed",
        click: "Opened",
      }[kind];
      setMessage(feedback);
      setShowReturn(false);
      await onLearning(kind, product.id, product.name, update);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <>
      <article className="group overflow-hidden rounded-[1.75rem] border border-black/8 bg-white shadow-[0_18px_60px_rgb(33_48_40_/_7%)] transition duration-300 hover:-translate-y-1 hover:shadow-[0_24px_70px_rgb(33_48_40_/_12%)]">
        <div
          className={`relative aspect-[4/5] overflow-hidden bg-gradient-to-br ${art}`}
        >
          {product.imageUrl ? (
            <Image
              alt={product.name}
              className="object-cover transition duration-500 group-hover:scale-[1.02]"
              fill
              priority={position === 1}
              sizes="(min-width: 1280px) 31vw, (min-width: 768px) 48vw, 100vw"
              src={product.imageUrl}
            />
          ) : (
            <div className="absolute inset-[12%] rounded-[45%_55%_48%_52%] border border-white/50 bg-white/25" />
          )}
          <div className="absolute left-5 top-5 rounded-full bg-white/85 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--ink)] backdrop-blur">
            Match {position}
          </div>
          <div className="absolute bottom-5 right-5 grid size-12 place-items-center rounded-full bg-[var(--ink)] text-sm font-semibold text-white shadow-lg">
            {score}
          </div>
          <p className="absolute bottom-5 left-5 text-xs font-medium uppercase tracking-[0.2em] text-black/55">
            {product.category}
          </p>
        </div>

        <div className="p-5 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--accent)]">
                {product.brand}
              </p>
              <h2 className="mt-1 text-xl font-semibold leading-tight tracking-[-0.03em]">
                {product.name}
              </h2>
            </div>
            <p className="shrink-0 text-base font-semibold">
              {currency.format(product.price)}
            </p>
          </div>

          <p className="mt-3 text-sm leading-6 text-[var(--muted)]">
            {product.description}
          </p>

          <div className="mt-5 rounded-2xl bg-[var(--soft)] p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[var(--accent)]">
              Why it fits
            </p>
            <ul className="mt-2 space-y-2">
              {reason.evidence.slice(0, 3).map((item) => (
                <li
                  className="flex gap-2 text-xs leading-5 text-[var(--muted)]"
                  key={item}
                >
                  <span className="mt-[7px] size-1.5 shrink-0 rounded-full bg-[var(--accent)]" />
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-5 border-t border-black/8 pt-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-xs text-[var(--muted)]">
                <span className="font-semibold text-[var(--ink)]">
                  {product.totalStock}
                </span>{" "}
                in stock
              </p>
              {message ? (
                <p
                  className="text-right text-xs font-semibold text-[var(--accent)]"
                  role="status"
                >
                  {message}
                </p>
              ) : null}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
              <button
                className="card-action"
                disabled={isSaving}
                onClick={() => recordSignal("skip")}
                type="button"
              >
                Not for me
              </button>
              <button
                className="card-action"
                disabled={isSaving}
                onClick={() => recordSignal("wishlist")}
                type="button"
              >
                Save
              </button>
              <button
                className="card-action"
                disabled={isSaving}
                onClick={() => recordSignal("purchase")}
                type="button"
              >
                Bought
              </button>
              <button
                className="card-action card-action-emphasis"
                disabled={isSaving}
                onClick={() => setShowReturn(true)}
                type="button"
              >
                Return
              </button>
            </div>
          </div>
        </div>
      </article>

      {showReturn ? (
        <ReturnDialog
          isSubmitting={isSaving}
          onClose={() => setShowReturn(false)}
          onSubmit={(reason) => recordSignal("return", reason)}
          productName={product.name}
        />
      ) : null}
    </>
  );
}
