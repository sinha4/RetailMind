"use client";

import { FormEvent, useState } from "react";

interface ReturnDialogProps {
  productName: string;
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (reason: string) => Promise<void>;
}

const returnReasons = [
  "The fabric felt too hot",
  "The material felt itchy",
  "The fit was too tight",
  "It looked different than expected",
];

export function ReturnDialog({
  productName,
  isSubmitting,
  onClose,
  onSubmit,
}: ReturnDialogProps) {
  const [reason, setReason] = useState(returnReasons[0]);

  async function submitReturn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(reason);
  }

  return (
    <div
      aria-label={`Return ${productName}`}
      aria-modal="true"
      className="fixed inset-0 z-50 grid place-items-center bg-[rgb(18_27_22_/_48%)] p-4 backdrop-blur-sm"
      onKeyDown={(event) => {
        if (event.key === "Escape" && !isSubmitting) onClose();
      }}
      role="dialog"
    >
      <form
        className="w-full max-w-md rounded-[1.75rem] bg-[var(--card)] p-6 shadow-2xl sm:p-8"
        onSubmit={submitReturn}
      >
        <p className="eyebrow">Help us learn</p>
        <h2 className="mt-3 text-2xl font-semibold tracking-[-0.04em]">
          Why are you returning it?
        </h2>
        <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
          Your reason will improve future recommendations for {productName} and
          similar pieces.
        </p>

        <fieldset className="mt-6 space-y-2">
          <legend className="sr-only">Return reason</legend>
          {returnReasons.map((option, index) => (
            <label
              className="flex cursor-pointer items-center gap-3 rounded-xl border border-black/8 bg-white px-4 py-3 text-sm has-checked:border-[var(--accent)] has-checked:bg-[var(--soft)]"
              key={option}
            >
              <input
                autoFocus={index === 0}
                checked={reason === option}
                className="accent-[var(--accent)]"
                name="return-reason"
                onChange={() => setReason(option)}
                type="radio"
                value={option}
              />
              {option}
            </label>
          ))}
        </fieldset>

        <div className="mt-7 flex justify-end gap-2">
          <button
            className="rounded-full px-5 py-2.5 text-sm font-semibold text-[var(--muted)] hover:bg-[var(--soft)]"
            disabled={isSubmitting}
            onClick={onClose}
            type="button"
          >
            Cancel
          </button>
          <button
            className="rounded-full bg-[var(--ink)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? "Updating memory…" : "Confirm return"}
          </button>
        </div>
      </form>
    </div>
  );
}
