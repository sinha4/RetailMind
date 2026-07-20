# Hackathon roadmap

## Phase 1 — Foundation (this repository state)

- Monorepo, environment template, local Qdrant, web/API shells, shared contracts, linting, and smoke tests.

## Phase 2 — Thin vertical slice

- Seed a small fashion catalog.
- Accept a natural-language shopping request.
- Retrieve a demo customer profile from Qdrant.
- Rank three products with structured reasons.
- Render results in the web experience through one configurable brand voice.

Implemented through the API: catalog, seeded/Qdrant-ready customer memory, structured intent,
deterministic ranking, inventory validation, explanations, and configurable presentation. The web
experience is the remaining Phase 2 task.

## Phase 3 — Learning loop

- Capture clicks, skips, wishlist events, purchases, returns, and return reasons.
- Convert events into positive/negative memory facts.
- Demonstrate a later recommendation changing because of a previous return.

In progress: event ingestion, event audit history, and explicit memory derivation are implemented.
The customer experience currently exposes wishlist and skip signals; purchase and return flows can
use the same API.

## Phase 4 — Orchestration depth

- Add inventory alternatives and low-stock messaging.
- Add post-purchase status and proactive delay communication.
- Add confidence-based human escalation with a context summary.

## Phase 5 — Demo polish

- Brand manager controls and two visibly different brand personalities.
- Agent trace/explanation panel.
- Seeded before/after customer journey and measurable demo metrics.

## Recommended demo story

A returning shopper asks for a beach-holiday outfit. RetailMind remembers that they returned synthetic fabric, respects their usual budget, explains three in-stock choices, and speaks in the selected retailer voice. A return event updates memory, and the next session visibly changes the ranking.
