from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from retailmind_api.catalog import filter_catalog, get_catalog
from retailmind_api.config import get_settings
from retailmind_api.events import ProductNotFoundError, ingest_signal, list_customer_events
from retailmind_api.memory import CustomerNotFoundError, get_customer_context
from retailmind_api.models import (
    ConversationMessageRequest,
    ConversationMessageResponse,
    CustomerContext,
    CustomerSignal,
    CustomerSignalRequest,
    Product,
    ProductList,
    SignalIngestionResponse,
)
from retailmind_api.recommendations import handle_shopping_turn

settings = get_settings()

app = FastAPI(
    title="RetailMind API",
    version="0.1.0",
    description="Orchestration boundary for personalized retail agents.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "retailmind-api"}


@app.get("/ready", tags=["system"])
async def ready() -> dict[str, str]:
    # Dependency checks will be added as provider adapters are implemented.
    return {"status": "ready"}


@app.get("/v1/products", response_model=ProductList, tags=["catalog"])
async def list_products(
    category: str | None = None,
    material: str | None = None,
    occasion: str | None = None,
    max_price: int | None = Query(default=None, alias="maxPrice", gt=0),
    size: str | None = None,
    in_stock: bool = Query(default=True, alias="inStock"),
) -> ProductList:
    products = filter_catalog(
        category=category,
        material=material,
        occasion=occasion,
        max_price=max_price,
        size=size,
        in_stock=in_stock,
    )
    return ProductList(count=len(products), products=products)


@app.get("/v1/products/{product_id}", response_model=Product, tags=["catalog"])
async def get_product(product_id: str) -> Product:
    product = next((item for item in get_catalog() if item.id == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get(
    "/v1/customers/{customer_id}/context",
    response_model=CustomerContext,
    tags=["customers"],
)
async def customer_context(customer_id: str) -> CustomerContext:
    try:
        return get_customer_context(customer_id)
    except CustomerNotFoundError as error:
        raise HTTPException(status_code=404, detail="Customer not found") from error


@app.post(
    "/v1/conversations/messages",
    response_model=ConversationMessageResponse,
    tags=["shopping"],
)
async def conversation_message(
    request: ConversationMessageRequest,
) -> ConversationMessageResponse:
    try:
        return handle_shopping_turn(request)
    except CustomerNotFoundError as error:
        raise HTTPException(status_code=404, detail="Customer not found") from error


@app.post("/v1/events", response_model=SignalIngestionResponse, tags=["events"])
async def create_event(request: CustomerSignalRequest) -> SignalIngestionResponse:
    try:
        return ingest_signal(request)
    except CustomerNotFoundError as error:
        raise HTTPException(status_code=404, detail="Customer not found") from error
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail="Product not found") from error


@app.get(
    "/v1/customers/{customer_id}/events",
    response_model=list[CustomerSignal],
    tags=["events"],
)
async def customer_events(customer_id: str) -> list[CustomerSignal]:
    try:
        return list_customer_events(customer_id)
    except CustomerNotFoundError as error:
        raise HTTPException(status_code=404, detail="Customer not found") from error
