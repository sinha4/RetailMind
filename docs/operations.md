# Operations and observability

The FastAPI boundary emits one JSON log record per request with a request ID, method, path, status,
and latency. It never logs request bodies, customer messages, or API keys. Clients can send an
`X-Request-ID`; otherwise the API creates one and returns it in the response header.

Agent-level observability is returned in the response trace. Each step records its mode, provider,
latency when available, prompt version when applicable, and a safe fallback reason. This makes the
demo usable without an external model while keeping provider failures visible.

Production deployments should forward the JSON stream to their log platform and alert on elevated
5xx rates, latency, repeated provider fallbacks, and human-escalation volume.
