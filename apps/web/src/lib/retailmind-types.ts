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
}

export interface ConversationMessageResponse {
  conversationId: string;
  assistantMessage: string;
  intent: ShoppingIntent;
  recommendations: ProductRecommendation[];
  trace: AgentTraceStep[];
}
