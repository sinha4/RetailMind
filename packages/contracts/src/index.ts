export type SignalKind =
  | "view"
  | "click"
  | "skip"
  | "wishlist"
  | "purchase"
  | "return";

export interface CustomerSignal {
  customerId: string;
  productId: string;
  kind: SignalKind;
  occurredAt: string;
  reason?: string;
}

export interface RecommendationReason {
  summary: string;
  evidence: string[];
}

export interface Recommendation {
  productId: string;
  score: number;
  reason: RecommendationReason;
}

