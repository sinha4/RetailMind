from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class Product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    brand: str
    category: str
    description: str
    price: int = Field(gt=0)
    currency: str = "INR"
    colors: list[str] = Field(min_length=1)
    sizes: list[str] = Field(min_length=1)
    materials: list[str] = Field(min_length=1)
    style_tags: list[str] = Field(alias="styleTags", min_length=1)
    occasions: list[str] = Field(min_length=1)
    image_url: str | None = Field(default=None, alias="imageUrl")
    product_url: str = Field(alias="productUrl")
    inventory: dict[str, int]

    @computed_field(alias="totalStock")
    @property
    def total_stock(self) -> int:
        return sum(self.inventory.values())


class ProductList(BaseModel):
    count: int
    products: list[Product]


class Budget(BaseModel):
    min: int = Field(ge=0)
    max: int = Field(gt=0)
    currency: str = "INR"


class CustomerProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    display_name: str = Field(alias="displayName")
    budget: Budget
    sizes: dict[str, str]


class MemoryFact(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    customer_id: str = Field(alias="customerId")
    attribute: str
    value: str
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0, le=1)
    source: Literal["profile", "conversation", "event", "return"]
    occurred_at: datetime = Field(alias="occurredAt")
    evidence: str
    product_id: str | None = Field(default=None, alias="productId")


class CustomerContext(BaseModel):
    profile: CustomerProfile
    memories: list[MemoryFact]


class ShoppingIntent(BaseModel):
    occasion: str | None = None
    categories: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    max_price: int | None = Field(default=None, alias="maxPrice")
    size: str | None = None


class ConversationMessageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    message: str = Field(min_length=1, max_length=1000)
    brand_voice: Literal["warm", "minimal", "bold"] = Field(default="warm", alias="brandVoice")


class RecommendationReason(BaseModel):
    summary: str
    evidence: list[str] = Field(min_length=1)


class ProductRecommendation(BaseModel):
    product: Product
    score: int = Field(ge=0, le=100)
    reason: RecommendationReason


class AgentTraceStep(BaseModel):
    agent: str
    summary: str
    mode: Literal["ai", "deterministic", "data"]
    provider: str | None = None
    latency_ms: int | None = Field(default=None, alias="latencyMs")
    prompt_version: str | None = Field(default=None, alias="promptVersion")


class EscalationDecision(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    required: bool
    reason: str
    confidence: float = Field(ge=0, le=1)
    context_summary: str = Field(alias="contextSummary")


class ConversationMessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    conversation_id: str = Field(alias="conversationId")
    assistant_message: str = Field(alias="assistantMessage")
    intent: ShoppingIntent
    recommendations: list[ProductRecommendation]
    trace: list[AgentTraceStep]
    escalation: EscalationDecision | None = None


class CustomerSignalRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    product_id: str = Field(alias="productId")
    kind: Literal["view", "click", "skip", "wishlist", "purchase", "return"]
    reason: str | None = Field(default=None, max_length=500)


class CustomerSignal(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    customer_id: str = Field(alias="customerId")
    product_id: str = Field(alias="productId")
    kind: Literal["view", "click", "skip", "wishlist", "purchase", "return"]
    occurred_at: datetime = Field(alias="occurredAt")
    reason: str | None = None


class SignalIngestionResponse(BaseModel):
    signal: CustomerSignal
    derived_memories: list[MemoryFact] = Field(alias="derivedMemories")
    agent_message: str | None = Field(default=None, alias="agentMessage")
    trace: list[AgentTraceStep] = Field(default_factory=list)


class DeliveryDelayRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    order_id: str = Field(alias="orderId", min_length=1)
    product_id: str = Field(alias="productId")
    delay_days: int = Field(alias="delayDays", ge=1, le=30)
    brand_voice: Literal["warm", "minimal", "bold"] = Field(default="warm", alias="brandVoice")


class DeliveryDelayResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    revised_delivery: str = Field(alias="revisedDelivery")
    escalation: EscalationDecision
    trace: list[AgentTraceStep]


class BrandProfile(BaseModel):
    id: Literal["warm", "minimal", "bold"]
    name: str
    description: str
