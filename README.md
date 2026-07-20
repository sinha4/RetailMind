# RetailMind

RetailMind is a hyper-personal shopping orchestrator that combines persistent customer memory, explainable recommendations, negative-signal learning, and brand-consistent customer communication.

This repository is the hackathon-ready foundation for the product. It currently contains the application shells, local infrastructure, shared contracts, and development tooling. Agent workflows and provider integrations are intentionally the next implementation phase.

## Repository layout

```text
apps/
  api/        FastAPI service and future agent orchestration
  web/        Next.js customer experience
packages/
  contracts/  Shared API/domain contracts
docs/         Architecture and delivery notes
```

## Prerequisites

- Node.js 22+
- Python 3.12
- Docker (for local Qdrant)

## Quick start

1. Create local environment files:

   ```bash
   cp .env.example .env
   cp .env.example apps/web/.env.local
   ```

2. Install dependencies:

   ```bash
   npm install
   python3.12 -m venv .venv
   .venv/bin/pip install -e 'apps/api[dev,agents]'
   ```

3. Start Qdrant and the applications (in separate terminals):

   ```bash
   docker compose up -d qdrant
   npm run dev:web
   .venv/bin/uvicorn retailmind_api.main:app --app-dir apps/api/src --reload
   ```

4. Open the web app at `http://localhost:3000` and API docs at `http://localhost:8000/docs`.

The seeded catalog is available at `http://localhost:8000/v1/products`. It supports optional
`category`, `material`, `occasion`, `maxPrice`, `size`, and `inStock` query parameters.

The demo shopper context is available at
`http://localhost:8000/v1/customers/demo-customer/context`. Development defaults to seeded
memory during tests. The application defaults to embedded Qdrant persistence in the ignored
`qdrant_storage/` directory. Set `QDRANT_URL` to an HTTP URL when using hosted or Docker Qdrant.

Send a grounded shopping turn to `POST http://localhost:8000/v1/conversations/messages`:

```json
{
  "customerId": "demo-customer",
  "message": "Find me a beach holiday outfit under ₹5,000",
  "brandVoice": "warm"
}
```

## Optional Gemini agents

Set `GEMINI_API_KEY` in `.env` to enable Gemini 3.5 Flash for structured intent extraction and
brand-voice presentation. Without a key—or when a request times out or fails validation—the API
uses deterministic fallbacks. Product selection, ranking, price, inventory, and memory remain
outside the language model in both modes.

## Useful commands

```bash
npm run check       # Type-check and lint the web app
npm run test:api    # Run API tests (after Python setup)
npm run format      # Check formatting
```

See [docs/architecture.md](docs/architecture.md) for the system boundaries and [docs/roadmap.md](docs/roadmap.md) for the suggested build order.
