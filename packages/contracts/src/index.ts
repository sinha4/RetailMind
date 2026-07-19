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

export interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  description: string;
  price: number;
  currency: "INR";
  colors: string[];
  sizes: string[];
  materials: string[];
  styleTags: string[];
  occasions: string[];
  imageUrl: string | null;
  productUrl: string;
  inventory: Record<string, number>;
  totalStock: number;
}

export interface ProductList {
  count: number;
  products: Product[];
}

export interface CustomerProfile {
  customerId: string;
  displayName: string;
  budget: { min: number; max: number; currency: "INR" };
  sizes: Record<string, string>;
}

export interface MemoryFact {
  id: string;
  customerId: string;
  attribute: string;
  value: string;
  sentiment: "positive" | "negative" | "neutral";
  confidence: number;
  source: "profile" | "conversation" | "event" | "return";
  occurredAt: string;
  evidence: string;
  productId: string | null;
}

export interface CustomerContext {
  profile: CustomerProfile;
  memories: MemoryFact[];
}

export interface ShoppingIntent {
  occasion: string | null;
  categories: string[];
  materials: string[];
  colors: string[];
  maxPrice: number | null;
  size: string | null;
}

export interface ConversationMessageRequest {
  customerId: string;
  message: string;
  brandVoice?: "warm" | "minimal";
}

export interface ProductRecommendation {
  product: Product;
  score: number;
  reason: RecommendationReason;
}

export interface AgentTraceStep {
  agent: string;
  summary: string;
}

export interface ConversationMessageResponse {
  conversationId: string;
  assistantMessage: string;
  intent: ShoppingIntent;
  recommendations: ProductRecommendation[];
  trace: AgentTraceStep[];
}
