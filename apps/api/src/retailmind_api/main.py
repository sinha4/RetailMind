from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from retailmind_api.config import get_settings

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

