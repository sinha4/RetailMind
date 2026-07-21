# Lyzr Studio setup

RetailMind uses a deployed Lyzr agent for brand-consistent customer presentation. Gemini extracts
structured shopping intent, Qdrant stores customer memory, and deterministic code owns product
truth and ranking.

## Create the agent

1. Sign in to [Lyzr Studio](https://studio.lyzr.ai).
2. Create a new agent named **RetailMind Brand Concierge**.
3. Choose an available text model.
4. Use the configuration below.
5. Test it with the suggested cases.
6. Deploy the agent and copy its Agent ID from the Agent API panel.
7. Open **Account & API Key** from the organization menu and copy the API key.

### Role

Retail brand concierge and safe presentation agent.

### Goal

Present a curated shopping selection in the requested retailer voice without changing or inventing
any product, price, inventory, size, material, quantity, delivery, or policy fact.

### Instructions

```text
You are RetailMind's final customer-facing brand voice agent.

Rewrite only the meaning supplied in the user message as one short retailer greeting. Match the
requested voice: warm, minimal, or bold. Do not add markdown. Stay under 180 characters.

Never mention or invent product names, prices, stock, sizes, materials, quantities, delivery dates,
returns, discounts, guarantees, or policies. Those facts are owned by deterministic services and
rendered separately. Never include a number. If the input is unclear, return a neutral greeting that
says the curated edit is ready.
```

### Suggested tests

- Warm: expect a reassuring one-sentence greeting.
- Minimal: expect a concise, direct greeting.
- Bold: expect an energetic but factual greeting.
- Prompt asking it to invent a discount: it must not provide one.
- Prompt containing product facts: it must not repeat or alter them.

## Connect RetailMind

Add these values to the root `.env` file:

```env
LYZR_API_KEY=your_api_key
LYZR_AGENT_ID=your_deployed_agent_id
LYZR_API_URL=https://agent-prod.studio.lyzr.ai/v3/inference/chat/
LYZR_USER_ID=retailmind-demo
```

Restart the API. Submit a recommendation request and expand the agent trace. A successful complete
configuration shows:

- Intent: `ai - google-gemini`
- Customer intelligence: `data - qdrant`
- Brand voice: `ai - lyzr-agent`

If Lyzr is unavailable, brand voice shows `deterministic - fallback` and the safe local response is
used. The API key is never sent to the browser or written to logs.
