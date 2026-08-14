# Local AI Ecommerce OS Runtime

## Canonical paths

- Project root: `%USERPROFILE%\Documents\Codex\2026-08-13\ji-xu\outputs\ai-ecommerce-os`
- n8n compose: `n8n\compose.yaml`
- n8n workflow source: `n8n\ai-ecommerce-demo-workflow.json`
- Product Worker: `services\product-worker\app.py`
- Browser Use venv: `runtimes\browser-use\.venv`
- Demo runner: `demo-evidence\run-demo.ps1`
- Latest result: `demo-evidence\latest-result.json`
- Browser evidence: `demo-evidence\browser-use-product-page.png`
- Obsidian note: `%USERPROFILE%\Documents\Obsidian Vault\04 跨境电商\AI Ecommerce OS\AI Ecommerce OS - 端到端运行手册.md`

## Runtime architecture

`POST n8n webhook -> Browser Use worker -> n8n scoring -> Ollama qwen3:4b -> human approval gate -> JSON response`

- n8n: `http://127.0.0.1:5678`, container `ai-ecommerce-n8n`.
- Worker: `http://127.0.0.1:8000`.
- Ollama: `http://127.0.0.1:11434`, model `qwen3:4b`.
- Workflow ID: `AiEcomDemo001`.
- Production webhook: `POST http://127.0.0.1:5678/webhook/ai-ecommerce-demo`.

The default collection URL is the controlled local page `http://127.0.0.1:8000/demo-product`. Do not describe it as live TikTok, 1688, or marketplace data.

## Health checks

Run:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5678/healthz
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Expected:

- n8n HTTP 200.
- Worker `status=ok`, `browser_use=true`, `ollama=true`.
- Ollama lists `qwen3:4b`.

## Start and stop

Start n8n by running `n8n\start-n8n.cmd`. Stop it with `n8n\stop-n8n.cmd`. Never use `docker compose down -v` unless the user explicitly authorizes deletion of the n8n data volume.

Start the worker with `services\product-worker\start-worker.cmd`. If port 8000 is already listening, verify `/health` before starting another process.

## End-to-end acceptance test

Run:

```powershell
$projectRoot = Join-Path $env:USERPROFILE 'Documents\Codex\2026-08-13\ji-xu\outputs\ai-ecommerce-os'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot 'demo-evidence\run-demo.ps1')
```

Parse `latest-result.json` and require all of the following:

- `product.product_name` is non-empty.
- `score` is numeric and `scorecard` is present.
- `content.title` is specific and `content.bullet_points` has at least 3 entries.
- `generation.provider` is `ollama` and `generation.facts_only` is true.
- `approval.status` is `pending_human_review`.
- `approval.publish_allowed` is false.
- The browser screenshot exists and has non-zero size.

The verified 2026-08-14 controlled demo produced score 94, four bullet points, four fact-trace entries, and a pending human review result.

## Data and safety boundaries

- Allow-listed hosts default to `localhost` and `127.0.0.1`. Add a real domain through `ALLOWED_PRODUCT_HOSTS` only for a user-approved target.
- Keep publishing, repricing, ordering, inventory mutation, and destructive changes behind explicit human approval.
- Treat demo search volume and competitor counts as estimates.
- Do not treat purchase price as total cost. Add platform fees, shipping, ads, tax, returns, and currency risk before a real go/no-go decision.
- Never store API keys, cookies, `.env` files, browser profiles, customer records, or marketplace credentials in a Skill or Git repository.

## Model routing

Ollama local mode does not require an API key. It is the development and fallback provider. Official OpenAI, Anthropic, Google, or Browser Use Cloud keys may be added later through n8n Credentials or a local ignored `.env`; never hard-code them.

## Update protocol

After a material change:

1. Re-run health checks and the acceptance test.
2. Append the actual result and failure notes to the Obsidian operating note.
3. Update this reference if paths, endpoints, models, workflow IDs, scoring rules, or acceptance criteria changed.
4. Validate with the official Skill validator.
5. Copy the validated Skill to `%USERPROFILE%\.codex\skills\ecommerce`.
6. Inspect `git diff` and `git status` for secrets and unrelated files.
7. Commit only the relevant Skill and documentation changes, then push. Report a failed push as a blocker.
