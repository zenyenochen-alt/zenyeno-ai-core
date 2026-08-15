---
name: ecommerce
description: Design and operate end-to-end cross-border ecommerce workflows. Use for process mapping, marketplace operations, automation boundaries, approval gates, SOPs, and coordinating product data from discovery through listing and post-launch review.
---

# Ecommerce Operations

1. Confirm marketplace, country, product category, objective, constraints, and available source data.
2. Map inputs, transformations, outputs, owners, failure paths, and human approval gates.
3. Keep irreversible actions such as publishing, repricing, ordering, or deleting behind explicit approval.
4. Prefer an auditable pipeline: ingest, normalize, analyze, score, generate, review, publish, monitor.
5. Return the proposed workflow, required fields, acceptance criteria, risks, and next executable step.

For n8n workflows, make each node idempotent where possible and record source URL, retrieval time, workflow version, and decision reason.

When the user asks the system to find a product itself, perform public discovery before asking for a URL. Prefer a valid read-only analytics API; otherwise use public search and an independent Browser Use session. Never reuse the user's personal browser profile, cookies, or login state without explicit approval. Treat CAPTCHA or Security Check as a recorded blocker and use an auditable public-source fallback rather than claiming the marketplace was collected.

## Local AI Ecommerce OS

When the user asks to start, run, demonstrate, diagnose, or update their local AI Ecommerce OS, read `references/ai-ecommerce-os-local-runtime.md` before acting.

For every material runtime change:

1. Run the health checks and end-to-end acceptance test.
2. Update the Obsidian operating note with the change and observed result.
3. Update this Skill source or its runtime reference.
4. Validate the Skill, sync the installed copy, inspect the Git diff for secrets, commit, and push to the configured GitHub remote.
5. Never claim GitHub synchronization unless the push succeeds.
