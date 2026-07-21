import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RecommendationComparison } from "@/components/recommendation-comparison";
import type { ProductRecommendation } from "@/lib/retailmind-types";

function recommendation(id: string, name: string): ProductRecommendation {
  return {
    product: {
      id,
      name,
      brand: "Test",
      category: "dress",
      description: "Test product",
      price: 3000,
      currency: "INR",
      colors: ["blue"],
      sizes: ["M"],
      materials: ["linen"],
      styleTags: ["relaxed"],
      occasions: ["beach"],
      imageUrl: null,
      productUrl: `/products/${id}`,
      inventory: { M: 2 },
      totalStock: 2,
    },
    score: 80,
    reason: { summary: "Good match", evidence: ["In stock"] },
  };
}

describe("RecommendationComparison", () => {
  it("explains when a recommendation moves after learning", () => {
    const first = recommendation("one", "Azure Dress");
    const second = recommendation("two", "Linen Set");

    render(
      <RecommendationComparison
        after={[second, first]}
        before={[first, second]}
        returnedName="Azure Dress"
      />,
    );

    expect(
      screen.getByText(/ranking changed after returning Azure Dress/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/#1 Linen Set · was #2/i)).toBeInTheDocument();
    expect(screen.getByText(/#2 Azure Dress · was #1/i)).toBeInTheDocument();
  });

  it("shows a newly introduced recommendation without a previous rank", () => {
    const first = recommendation("one", "Azure Dress");
    const newMatch = recommendation("three", "Cotton Cover-up");

    render(
      <RecommendationComparison
        after={[newMatch]}
        before={[first]}
        returnedName="Azure Dress"
      />,
    );

    expect(screen.getByText("#1 Cotton Cover-up")).toBeInTheDocument();
    expect(screen.queryByText(/was #/i)).not.toBeInTheDocument();
  });
});
