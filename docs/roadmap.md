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

Implemented: event ingestion, audit history, explicit memory derivation, wishlist/skip/purchase/
return controls, return reasons, persistent Qdrant memory, and visible before/after reranking.

## Phase 4 — Orchestration depth

- Add inventory alternatives and low-stock messaging.
- Add post-purchase status and proactive delay communication.
- Add confidence-based human escalation with a context summary.

Implemented: inventory validation and alternatives, post-purchase purchase acknowledgement,
proactive delivery-delay communication, confidence-based human escalation with a context summary,
the provider-neutral Gemini boundary, structured intent, safe brand voice, deterministic fallbacks,
prompt versioning, provider metadata, and latency traces.

## Phase 5 — Demo polish

- Brand manager controls and two visibly different brand personalities.
- Agent trace/explanation panel.
- Seeded before/after customer journey and measurable demo metrics.

Implemented: three selectable brand personalities, agent trace/explanation panels, and an agent
operations demo for delivery-delay and escalation behavior. Seeded demo metrics remain future work.

## Recommended demo story

A returning shopper asks for a beach-holiday outfit. RetailMind remembers that they returned synthetic fabric, respects their usual budget, explains three in-stock choices, and speaks in the selected retailer voice. A return event updates memory, and the next session visibly changes the ranking.
