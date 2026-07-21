"""Shopping intent extraction, grounded ranking, and orchestrated presentation."""

import re
from dataclasses import dataclass
from uuid import uuid4

from retailmind_api.agents import evaluate_escalation
from retailmind_api.ai import (
    GeminiAdapter,
    LyzrAdapter,
    ModelAdapter,
    ModelOutput,
    parse_json_output,
)
from retailmind_api.catalog import get_catalog
from retailmind_api.config import get_settings
from retailmind_api.memory import get_customer_context
from retailmind_api.models import (
    AgentTraceStep,
    ConversationMessageRequest,
    ConversationMessageResponse,
    CustomerContext,
    Product,
    ProductRecommendation,
    RecommendationReason,
    ShoppingIntent,
)

KNOWN_OCCASIONS = ("beach", "holiday", "brunch", "dinner", "party", "travel", "casual", "pool")
KNOWN_MATERIALS = ("linen", "cotton", "viscose", "polyester", "leather", "jute")
KNOWN_COLORS = ("blue", "white", "green", "coral", "navy", "black", "tan", "natural")
CATEGORY_TERMS = {
    "dress": "dress",
    "dresses": "dress",
    "top": "top",
    "shirt": "top",
    "shirts": "top",
    "shorts": "bottom",
    "trousers": "bottom",
    "skirt": "bottom",
    "swimwear": "swimwear",
    "swimsuit": "swimwear",
    "shoes": "shoes",
    "sandals": "shoes",
    "accessories": "accessory",
}
SIZE_CATEGORY = {
    "dress": "dress",
    "top": "top",
    "bottom": "bottom",
    "set": "top",
    "outerwear": "top",
    "swimwear": "dress",
    "shoes": "shoes",
}
INTENT_PROMPT_VERSION = "intent-v1"
BRAND_PROMPT_VERSION = "brand-v1"


def extract_intent(message: str) -> ShoppingIntent:
    """Deterministic first-pass intent extraction, replaceable by an LLM adapter later."""
    normalized = message.casefold()
    occasion = next((item for item in KNOWN_OCCASIONS if item in normalized), None)
    materials = [item for item in KNOWN_MATERIALS if item in normalized]
    colors = [item for item in KNOWN_COLORS if item in normalized]
    categories = list(
        dict.fromkeys(
            category for term, category in CATEGORY_TERMS.items() if term in normalized.split()
        )
    )

    budget_match = re.search(
        r"(?:under|below|up\s+to|maximum|max)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)", normalized
    )
    max_price = int(budget_match.group(1).replace(",", "")) if budget_match else None

    size_match = re.search(r"\bsize\s+([a-z0-9/]+)", normalized)
    size = size_match.group(1).upper() if size_match else None

    return ShoppingIntent(
        occasion=occasion,
        categories=categories,
        materials=materials,
        colors=colors,
        maxPrice=max_price,
        size=size,
    )


@dataclass
class ScoredProduct:
    product: Product
    score: int
    evidence: list[str]


def _contains(values: list[str], preference: str) -> bool:
    wanted = preference.casefold()
    return any(wanted in value.casefold() for value in values)


def _score_product(
    product: Product, intent: ShoppingIntent, context: CustomerContext
) -> ScoredProduct | None:
    if product.total_stock <= 0:
        return None
    if intent.categories and product.category not in intent.categories:
        return None
    if intent.materials and not any(
        _contains(product.materials, item) for item in intent.materials
    ):
        return None
    if intent.colors and not any(_contains(product.colors, item) for item in intent.colors):
        return None

    max_price = intent.max_price or context.profile.budget.max
    if product.price > max_price:
        return None

    negative_materials = [
        fact
        for fact in context.memories
        if fact.attribute == "material" and fact.sentiment == "negative" and fact.confidence >= 0.8
    ]
    if any(_contains(product.materials, fact.value) for fact in negative_materials):
        return None

    product_memories = [
        fact
        for fact in context.memories
        if fact.attribute == "product" and fact.value == product.id
    ]
    if any(fact.sentiment == "negative" and fact.confidence >= 0.9 for fact in product_memories):
        return None

    profile_size_key = SIZE_CATEGORY.get(product.category)
    preferred_size = intent.size or (
        context.profile.sizes.get(profile_size_key) if profile_size_key else None
    )
    if preferred_size and product.inventory.get(preferred_size, 0) <= 0:
        return None

    score = 15
    evidence = [f"₹{product.price:,} is within the ₹{max_price:,} budget."]

    if intent.occasion and intent.occasion in product.occasions:
        score += 25
        evidence.append(f"Designed for {intent.occasion} occasions.")
    if intent.materials and any(_contains(product.materials, item) for item in intent.materials):
        score += 20
        evidence.append(f"Matches the requested {', '.join(intent.materials)} material.")
    if intent.colors and any(_contains(product.colors, item) for item in intent.colors):
        score += 10
        evidence.append(f"Matches the requested {', '.join(intent.colors)} color.")
    if preferred_size:
        score += 15
        evidence.append(f"Size {preferred_size} is currently in stock.")

    for fact in context.memories:
        if fact.sentiment != "positive":
            continue
        values = {
            "material": product.materials,
            "color": product.colors,
            "style": product.style_tags,
            "occasion": product.occasions,
        }.get(fact.attribute)
        if values and _contains(values, fact.value):
            points = round(15 * fact.confidence)
            score += points
            evidence.append(f"Matches your preference for {fact.value}.")

    score += min(10, product.total_stock)
    evidence.append(f"Available now with {product.total_stock} units across sizes.")
    for fact in product_memories:
        if fact.sentiment == "positive":
            score += round(15 * fact.confidence)
            evidence.append("You previously saved or purchased this piece.")
        elif fact.sentiment == "negative":
            score -= round(20 * fact.confidence)
            evidence.append("Deprioritized because you previously skipped this piece.")
    return ScoredProduct(product=product, score=min(score, 100), evidence=evidence)


def recommend(
    intent: ShoppingIntent, context: CustomerContext, limit: int = 3
) -> list[ProductRecommendation]:
    scored = [
        result
        for product in get_catalog()
        if (result := _score_product(product, intent, context)) is not None
    ]
    scored.sort(key=lambda item: (-item.score, item.product.price, item.product.id))

    return [
        ProductRecommendation(
            product=item.product,
            score=item.score,
            reason=RecommendationReason(
                summary=f"{item.product.name} fits your request and known preferences.",
                evidence=item.evidence,
            ),
        )
        for item in scored[:limit]
    ]


def _present(recommendations: list[ProductRecommendation], name: str, voice: str) -> str:
    if not recommendations:
        return (
            f"I couldn't find a suitable in-stock match, {name}. Try widening the budget or style."
        )
    if voice == "minimal":
        return f"{len(recommendations)} matches, selected for fit, preferences, and availability."
    return (
        f"I found {len(recommendations)} promising options for you, {name}. "
        "Each one is in stock and grounded in what you've told us."
    )


async def _ai_intent(message: str, adapter: ModelAdapter) -> tuple[ShoppingIntent, ModelOutput]:
    schema = {
        "type": "object",
        "properties": {
            "occasion": {"type": "string", "nullable": True},
            "categories": {"type": "array", "items": {"type": "string"}},
            "materials": {"type": "array", "items": {"type": "string"}},
            "colors": {"type": "array", "items": {"type": "string"}},
            "maxPrice": {"type": "integer", "nullable": True},
            "size": {"type": "string", "nullable": True},
        },
        "required": ["occasion", "categories", "materials", "colors", "maxPrice", "size"],
    }
    prompt = (
        "Extract retail shopping constraints from the user request. Normalize categories to "
        "dress, top, bottom, set, outerwear, swimwear, shoes, or accessory. Use INR for budget. "
        "Do not invent constraints.\n\nUser request: " + message
    )
    output = await adapter.generate(prompt, response_schema=schema)
    return ShoppingIntent.model_validate(parse_json_output(output)), output


async def _ai_brand_message(
    fallback: str, name: str, voice: str, adapter: ModelAdapter
) -> tuple[str, ModelOutput]:
    prompt = (
        f"Write one short {voice} retailer greeting for {name}. It introduces a curated product "
        "selection. Do not mention product facts, prices, stock, materials, sizes, quantities, or "
        "policies. Do not add markdown. Keep it under 180 characters.\n\n"
        f"Meaning to preserve: {fallback}"
    )
    output = await adapter.generate(prompt)
    message = output.text.strip().strip('"')
    if not message or len(message) > 180 or any(character.isdigit() for character in message):
        raise ValueError("Brand output failed safety validation")
    return message, output


async def handle_shopping_turn(
    request: ConversationMessageRequest, adapter: ModelAdapter | None = None
) -> ConversationMessageResponse:
    settings = get_settings()
    intent_adapter = adapter
    brand_adapter = adapter
    if adapter is None:
        if settings.gemini_api_key or settings.google_api_key:
            intent_adapter = GeminiAdapter(settings)
            brand_adapter = intent_adapter
        if settings.lyzr_api_key and settings.lyzr_agent_id:
            brand_adapter = LyzrAdapter(settings)

    intent_output: ModelOutput | None = None
    intent_error: str | None = None
    intent = extract_intent(request.message)
    if intent_adapter:
        try:
            intent, intent_output = await _ai_intent(request.message, intent_adapter)
        except Exception as error:
            intent_error = type(error).__name__
            intent = extract_intent(request.message)

    context = get_customer_context(request.customer_id)
    recommendations = recommend(intent, context)
    fallback_message = _present(recommendations, context.profile.display_name, request.brand_voice)
    brand_message = fallback_message
    brand_output: ModelOutput | None = None
    brand_error: str | None = None
    if brand_adapter:
        try:
            brand_message, brand_output = await _ai_brand_message(
                fallback_message,
                context.profile.display_name,
                request.brand_voice,
                brand_adapter,
            )
        except Exception as error:
            brand_error = type(error).__name__
            brand_message = fallback_message

    escalation = evaluate_escalation(request.customer_id, recommendations)

    return ConversationMessageResponse(
        conversationId=str(uuid4()),
        assistantMessage=brand_message,
        intent=intent,
        recommendations=recommendations,
        escalation=escalation,
        trace=[
            AgentTraceStep(
                agent="intent",
                summary=(
                    "Converted the request into typed constraints."
                    if not intent_error
                    else f"AI unavailable ({intent_error}); used validated intent fallback."
                ),
                mode="ai" if intent_output else "deterministic",
                provider=intent_output.provider
                if intent_output
                else ("fallback" if intent_error else None),
                latencyMs=intent_output.latency_ms if intent_output else None,
                promptVersion=INTENT_PROMPT_VERSION if intent_output else None,
            ),
            AgentTraceStep(
                agent="customer-intelligence",
                summary=f"Retrieved {len(context.memories)} attributable memory facts.",
                mode="data",
                provider="qdrant" if settings.memory_backend == "qdrant" else "seeded-memory",
            ),
            AgentTraceStep(
                agent="personalization",
                summary=f"Ranked {len(get_catalog())} catalog products against intent and memory.",
                mode="deterministic",
            ),
            AgentTraceStep(
                agent="inventory",
                summary="Removed unavailable sizes and preserved catalog prices.",
                mode="data",
                provider="catalog",
            ),
            AgentTraceStep(
                agent="brand-voice",
                summary=(
                    f"Presented results in the {request.brand_voice} voice."
                    if not brand_error
                    else f"AI unavailable ({brand_error}); used safe brand fallback."
                ),
                mode="ai" if brand_output else "deterministic",
                provider=brand_output.provider
                if brand_output
                else ("fallback" if brand_error else None),
                latencyMs=brand_output.latency_ms if brand_output else None,
                promptVersion=BRAND_PROMPT_VERSION if brand_output else None,
            ),
            AgentTraceStep(
                agent="human-escalation",
                summary=escalation.reason,
                mode="deterministic",
            ),
        ],
    )
