# Three-minute demo script

## 0:00-0:25 - Problem and promise

"Retail recommendations usually forget why a customer rejected an item. RetailMind is a personal
shopping orchestrator that remembers attributable positive and negative signals, keeps catalog
facts grounded, and explains every recommendation."

Show the storefront, preference chips, and the default beach-holiday request.

## 0:25-1:10 - Personalized recommendation

1. Click **Reset demo** for a repeatable starting point.
2. Submit: `Find me a beach holiday outfit under INR 5,000`.
3. Point out product images, scores, in-stock quantities, and evidence.
4. Expand **How RetailMind chose these**.
5. Point out `google-gemini` on intent, `lyzr-agent` on brand voice, and Qdrant on customer memory.
6. Explain that `deterministic - fallback` proves the safe local path completed when a provider was
   unavailable.

## 1:10-2:00 - Learning loop

1. Return one recommendation.
2. Choose a fabric or material reason.
3. Confirm the return.
4. Show the new avoidance chip and **Before vs after learning** ranking.
5. Explain that the memory fact is explicit, attributable, and persisted in Qdrant.

## 2:00-2:35 - Post-purchase orchestration

1. Scroll to **Agent operations demo**.
2. Run a three-day delay: automated communication, no escalation.
3. Run an eight-day delay: human escalation with a context summary.
4. Switch between Warm, Minimal, and Bold voices.

## 2:35-3:00 - Engineering proof

Show the GitHub README, architecture diagram, CI workflow, test output, and security automation.
Close with: "RetailMind combines explainable personalization, negative-signal learning, safe AI
fallbacks, and operational agent handoffs in one end-to-end retail journey."
