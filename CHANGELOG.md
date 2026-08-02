# Changelog

## 1.1.0 - 2026-08-02

- Added a responsive browser analysis demo.
- Added shipping, advertising, platform-fee, tax, return-reserve, currency, and target-margin inputs.
- Added a target-aware cost and profit model with a full response breakdown.
- Separated competition heuristics from trend scoring and added a competition adjustment to `final_score`.
- Added SQLite analysis history with protected list, detail, and deletion endpoints.
- Added optional API-key authentication, request rate limiting, request IDs, CORS allowlisting, and security headers.
- Expanded the automated test suite from 7 to 15 tests.

## 1.0.0 - 2026-08-01

- Unified analysis contracts around `final_score`.
- Added the FastAPI agent pipeline, Docker support, CI, tests, and public documentation.
- Changed current releases to the PolyForm Noncommercial License 1.0.0.
