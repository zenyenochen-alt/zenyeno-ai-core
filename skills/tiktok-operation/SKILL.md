---
name: tiktok-operation
description: Plan and execute TikTok Shop operations and automation. Use for catalog preparation, listing workflows, content-to-product linking, creator operations, campaign routines, operational monitoring, and future TikTok Shop API integrations.
---

# TikTok Shop Operations

1. Confirm shop region, account type, category, fulfillment model, and requested action.
2. Validate required catalog fields and media before any submission step.
3. Separate research and drafting from account mutations; require explicit approval before publish, price, inventory, campaign, or order actions.
4. Design API jobs with idempotency keys, rate-limit handling, retries, logs, and reconciliation.
5. Return the SOP or payload mapping, prerequisites, approval point, success check, and rollback or recovery path.

Do not treat browser automation as a permanent substitute for an available, authorized API.
## Official API Authorization

For the local AI Ecommerce OS official TikTok Shop integration:

1. Distinguish Seller, Creator, and Partner authorization before choosing endpoints or scopes.
2. Require a Partner Center App, exact Redirect URI, Service ID, App Key, App Secret, seller authorization, and the expected shop region.
3. Never request App Secret, access token, or refresh token in chat. Use the localhost setup page at `http://127.0.0.1:8000/tiktok/api/setup`; credentials are Windows-DPAPI encrypted.
4. Validate OAuth state, token response `code`, `user_type`, `granted_scopes`, expiry, refresh behavior, and authorized shop cipher.
5. Seller Product API is for the authorized seller catalog, not unrestricted public competitor research.
6. Keep `mutation_routes_enabled=false` until each write route has idempotency, reconciliation, and an explicit human approval gate.
7. Never claim the API is connected until OAuth succeeds and a real read-only shop/product call returns `code=0`.
