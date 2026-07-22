# Coding standards

These standards keep RetailMind changes consistent, reviewable, and safe across the Python API and
TypeScript storefront.

## Automated quality gates

- **TypeScript:** keep strict mode enabled. Do not use `any` when a domain type, `unknown`, or a
  provider-neutral interface can express the boundary.
- **ESLint:** follow the Next.js core-web-vitals and TypeScript rules. Fix warnings rather than
  suppressing them; a suppression requires a nearby explanation.
- **Python:** add type hints to public functions and provider boundaries. Ruff enforces imports,
  style, and common correctness rules.
- **Formatting:** Prettier owns JavaScript, TypeScript, JSON, Markdown, and YAML formatting; Ruff
  owns Python formatting. Avoid hand-formatting against either tool.
- **Tests:** every behavior change needs a focused test. External AI providers must be mocked in
  automated tests, while catalog, inventory, memory, and fallback behavior remain deterministic.

Run the complete local gate before opening a pull request:

```bash
npm run verify
PYTHONPATH=apps/api/src .venv/bin/python -m ruff check apps/api/src apps/api/tests
```

## Design and naming

- Use domain names such as `ShoppingIntent`, `MemoryFact`, and `ProductRecommendation`; avoid vague
  names such as `data`, `result`, or `handler` when a more precise name is available.
- Keep route handlers thin. Validation and HTTP translation belong at the boundary; business rules
  belong in the provider-neutral domain layer.
- Gemini and Lyzr may interpret or present information, but they never own price, stock, ranking,
  customer memory, or policy truth.
- Prefer small functions with explicit inputs and outputs. Add comments for non-obvious safety or
  architectural decisions, not for code that is already self-explanatory.
- Never log secrets, request bodies, customer messages, or raw provider credentials.

## Conventional Commits

Commit subjects use `<type>(optional-scope): description`. Keep the subject imperative, lowercase,
and no longer than 100 characters.

Common types:

- `feat`: user-visible capability
- `fix`: bug or security correction
- `test`: test-only change
- `docs`: documentation-only change
- `refactor`: internal change without behavior changes
- `chore`: tooling or dependency maintenance
- `ci`: workflow or automation change

Examples:

```text
feat(memory): add versioned Qdrant migrations
fix(web): distinguish upstream timeout responses
test(agents): cover deterministic provider fallback
docs: document the end-to-end demo journey
```

Validate the latest local commit with `npm run lint:commit`. Pull requests should remain focused,
describe user-visible impact and fallback behavior, and include the exact verification performed.
