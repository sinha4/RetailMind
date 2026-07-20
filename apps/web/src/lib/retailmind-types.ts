export interface ShoppingIntent {
  occasion: string | null;
  categories: string[];
  materials: string[];
  colors: string[];
  maxPrice: number | null;
  size: string | null;
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

export interface ProductRecommendation {
  product: Product;
  score: number;
  reason: {
    summary: string;
    evidence: string[];
  };
}

export interface AgentTraceStep {
  agent: string;
  summary: string;
  mode: "ai" | "deterministic" | "data";
  provider: string | null;
  latencyMs: number | null;
  promptVersion: string | null;
}

export interface ConversationMessageResponse {
  conversationId: string;
  assistantMessage: string;
  intent: ShoppingIntent;
  recommendations: ProductRecommendation[];
  trace: AgentTraceStep[];
  escalation: EscalationDecision;
}

export interface EscalationDecision {
  required: boolean;
  reason: string;
  confidence: number;
  contextSummary: string;
}

export type SignalKind =
  | "view"
  | "click"
  | "skip"
  | "wishlist"
  | "purchase"
  | "return";

export interface CustomerSignal {
  id: string;
  customerId: string;
  productId: string;
  kind: SignalKind;
  occurredAt: string;
  reason?: string;
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

export interface SignalIngestionResponse {
  signal: CustomerSignal;
  derivedMemories: MemoryFact[];
  agentMessage: string | null;
  trace: AgentTraceStep[];
}

export interface DeliveryDelayResponse {
  message: string;
  revisedDelivery: string;
  escalation: EscalationDecision;
  trace: AgentTraceStep[];
}

export interface CustomerContext {
  profile: {
    customerId: string;
    displayName: string;
    budget: { min: number; max: number; currency: "INR" };
    sizes: Record<string, string>;
  };
  memories: MemoryFact[];
}
