"""Deterministic post-purchase, escalation, and brand-profile agents."""

from datetime import UTC, datetime, timedelta

from retailmind_api.catalog import get_catalog
from retailmind_api.memory import CustomerNotFoundError, get_customer_context
from retailmind_api.models import (
    AgentTraceStep,
    BrandProfile,
    DeliveryDelayRequest,
    DeliveryDelayResponse,
    EscalationDecision,
    ProductRecommendation,
)

BRAND_PROFILES = [
    BrandProfile(
        id="warm", name="Warm concierge", description="Reassuring, personal, and helpful."
    ),
    BrandProfile(id="minimal", name="Modern minimal", description="Direct, concise, and factual."),
    BrandProfile(
        id="bold", name="Bold stylist", description="Confident, energetic, and expressive."
    ),
]


def retention_message(customer_id: str, product_name: str) -> str:
    customer = get_customer_context(customer_id).profile.display_name
    return f"Great choice, {customer}. I’ll remember {product_name} and shape your next edit."


def evaluate_escalation(
    customer_id: str, recommendations: list[ProductRecommendation]
) -> EscalationDecision:
    context = get_customer_context(customer_id)
    top_score = recommendations[0].score if recommendations else 0
    confidence = round(top_score / 100, 2)
    required = not recommendations or top_score < 45
    reason = (
        "No sufficiently confident in-stock recommendation was found."
        if required
        else "Recommendation confidence is sufficient for self-service."
    )
    return EscalationDecision(
        required=required,
        reason=reason,
        confidence=confidence,
        contextSummary=(
            f"{context.profile.display_name}; budget up to ₹{context.profile.budget.max:,}; "
            f"{len(context.memories)} attributable preference facts available."
        ),
    )


def handle_delivery_delay(request: DeliveryDelayRequest) -> DeliveryDelayResponse:
    try:
        context = get_customer_context(request.customer_id)
    except CustomerNotFoundError:
        raise
    product = next((item for item in get_catalog() if item.id == request.product_id), None)
    if product is None:
        raise LookupError(request.product_id)

    revised = datetime.now(UTC).date() + timedelta(days=request.delay_days)
    date_label = revised.strftime("%d %B %Y")
    if request.brand_voice == "minimal":
        message = f"Order {request.order_id} is delayed. New delivery: {date_label}."
    elif request.brand_voice == "bold":
        message = f"A quick update: {product.name} is running late. We’re targeting {date_label}."
    else:
        message = (
            f"I’m sorry, {context.profile.display_name}—{product.name} is delayed. "
            f"Your revised delivery date is {date_label}."
        )

    escalation = EscalationDecision(
        required=request.delay_days >= 7,
        reason=(
            "Delay is seven days or longer; a support specialist should review the order."
            if request.delay_days >= 7
            else "Delay is within the automated communication threshold."
        ),
        confidence=1.0,
        contextSummary=(
            f"Order {request.order_id}; {product.name}; {request.delay_days}-day delay; "
            f"customer {context.profile.display_name}."
        ),
    )
    return DeliveryDelayResponse(
        message=message,
        revisedDelivery=revised.isoformat(),
        escalation=escalation,
        trace=[
            AgentTraceStep(
                agent="post-purchase",
                summary=f"Detected and explained a {request.delay_days}-day delivery delay.",
                mode="deterministic",
            ),
            AgentTraceStep(
                agent="human-escalation",
                summary=escalation.reason,
                mode="deterministic",
            ),
            AgentTraceStep(
                agent="brand-voice",
                summary=f"Presented the update in the {request.brand_voice} voice.",
                mode="deterministic",
            ),
        ],
    )
