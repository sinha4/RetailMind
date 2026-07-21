# Security policy

## Reporting

Do not open a public issue for a suspected vulnerability or exposed credential. Contact the
repository owner privately through their GitHub profile with reproduction steps and impact.

## Supported version

The latest `main` branch is supported during the hackathon. Dependency updates are monitored by
Dependabot, CodeQL scans JavaScript/TypeScript and Python, and CI rejects high-severity npm audit
findings.

## Data and model safety

- `.env` and local Qdrant storage are ignored by Git.
- API keys are server-side only and are never sent to the browser.
- Request logs exclude bodies, messages, memory facts, and credentials.
- Prices, stock, ranking, and policies remain deterministic and outside Gemini.
- Model failures are visible in the agent trace and fall back to validated local logic.
