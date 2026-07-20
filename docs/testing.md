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
post-purchase messaging, delivery-delay escalation, brand profiles, and demo reset.

## Manual demo journey

1. Reset the demo from the storefront.
2. Request a beach-holiday outfit under INR 5,000.
3. Inspect the recommendation metrics and agent trace.
4. Return a recommended product with a material-related reason.
5. Confirm the before/after panel shows the changed ranking.
6. Simulate a three-day delivery delay and confirm no escalation.
7. Simulate an eight-day delay and confirm human escalation.

Gemini is optional. An `ai` trace proves the provider completed the step. A
`deterministic - fallback` trace means the provider failed or timed out and the validated local path
completed the request.
