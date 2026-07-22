# Testing and verification

RetailMind verifies the deterministic business path independently from optional AI availability.
This keeps catalog truth, memory behavior, ranking, inventory checks, and escalation reproducible.

## Local checks

Run the full automated suite from the repository root:

```bash
npm run check
npm run build
MEMORY_BACKEND=seeded PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests
PYTHONPATH=apps/api/src .venv/bin/ruff check apps/api/src apps/api/tests
```

The API tests cover health and readiness, catalog filters, seeded and persistent memory behavior,
event-to-memory derivation, grounded recommendations, AI adapter validation, deterministic fallback,
post-purchase messaging, delivery-delay escalation, brand profiles, Prometheus metrics, request IDs,
and demo reset. Lyzr tests verify authenticated v3 chat payloads, deployed Agent IDs, response
parsing, provider routing, and separation from structured intent. Qdrant migration tests verify
version tracking, payload backfills, and repeat execution. The suite contains 26 backend tests at
88% coverage and eight frontend tests at 100% statement and line coverage for the traced demo views
and API proxy failure boundary.

CI repeats these checks on pushes to `main` and pull requests, audits JavaScript and Python
dependencies, and builds the API and web production containers independently.

## Manual demo journey

1. Reset the demo from the storefront.
2. Request a beach-holiday outfit under INR 5,000.
3. Inspect the recommendation metrics and agent trace.
4. Return a recommended product with a material-related reason.
5. Confirm the before/after panel shows the changed ranking.
6. Simulate a three-day delivery delay and confirm no escalation.
7. Simulate an eight-day delay and confirm human escalation.

Gemini and Lyzr are optional. An `ai` trace proves the named provider completed the step. A
`deterministic - fallback` trace means the provider failed or timed out and the validated local path
completed the request.
