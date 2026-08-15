# Local AI Ecommerce OS Runtime

## Canonical paths

- Project root: `%USERPROFILE%\Documents\Codex\2026-08-13\ji-xu\outputs\ai-ecommerce-os`
- n8n compose: `n8n\compose.yaml`
- n8n workflow source: `n8n\ai-ecommerce-demo-workflow.json`
- Product Worker: `services\product-worker\app.py`
- Browser Use venv: `runtimes\browser-use\.venv`
- Demo runner: `demo-evidence\run-demo.ps1`
- Latest result: `demo-evidence\latest-result.json`
- Live browser evidence: `demo-evidence\browser-use-live-product-page.png`
- Obsidian note: `%USERPROFILE%\Documents\Obsidian Vault\04 跨境电商\AI Ecommerce OS\AI Ecommerce OS - 端到端运行手册.md`

## Runtime architecture

`POST n8n webhook -> Browser Use worker -> n8n scoring -> Ollama with strict validation -> source-facts fallback if needed -> human approval gate -> JSON response`

- n8n: `http://127.0.0.1:5678`, container `ai-ecommerce-n8n`.
- Worker: `http://127.0.0.1:8000`.
- Ollama: `http://127.0.0.1:11434`, model `qwen3:4b`.
- Product analysis workflow: `AI Ecommerce OS - 自动发现与商品分析`, ID `AiEcomDemo001`, version `1.1.0`.
- Worker version: `1.2.0`; official TikTok Shop API workflow: `TikTokShopApiReadonly001`.
- Production webhook: `POST http://127.0.0.1:5678/webhook/ai-ecommerce-demo`.
- Default live source: `https://www.doogusa.com/products/3-in-1-water-bottle-bowl`.

## Discovery and source status

Automatic discovery order:

1. Use a valid read-only marketplace analytics API when configured.
2. Try a public TikTok search or PDP URL in an independent Browser Use session.
3. If TikTok presents CAPTCHA or Security Check, record the blocker and choose an accessible public product source.
4. Never reuse the user's default Chrome profile, cookies, or login state without explicit approval.

Known TikTok URLs:

- Search: `https://shop.tiktok.com/us/k/water-bottle-for-dogs`.
- PDP: `https://shop.tiktok.com/us/pdp/portable-pet-dog-water-bottle-leak-proof-design-abs-plastic-material/1732234765220746081`.

As of 2026-08-15, Browser Use reaches TikTok but receives `Security Check`; direct TikTok DOM extraction is not verified. The configured `LINKFOXAGENT_API_KEY` is an invalid 7-character non-ASCII placeholder, so EchoTik search is not connected. Never write the key value to output.

The verified public fallback is the DOOG product page. It is live marketplace data, not demo data. Costs, demand, competition, and compliance remain unknown unless separately collected.

## Official TikTok Shop API

Use the official API for long-term authorized shop operations. Browser collection is only a fallback and must not be used to evade region restrictions or Security Check.

Local routes:

- Setup UI: `http://127.0.0.1:8000/tiktok/api/setup`.
- Status: `GET /tiktok/api/status`.
- OAuth start/callback: `GET /tiktok/api/oauth/start` and `/tiktok/api/oauth/callback`.
- Authorized shops: `GET /tiktok/api/shops`.
- Read-only seller products: `POST /tiktok/api/products/search`.
- n8n webhook: `POST http://127.0.0.1:5678/webhook/tiktok-shop-products`.

Security and protocol:

- Configure App Key, App Secret, Service ID, market, and Redirect URI only in the localhost setup page. Never request secrets in chat.
- Config, OAuth state, access token, and refresh token are encrypted with Windows DPAPI under `runtimes\secrets`; never sync that directory.
- OAuth uses Seller authorization, validates `state`, exchanges the one-time code, and refreshes access tokens before expiry.
- Business API requests use official HMAC-SHA256 signing and `x-tts-access-token`.
- Current routes are read-only and report `mutation_routes_enabled=false`.
- Seller Product API reads the authorized seller's catalog. Do not describe it as arbitrary public competitor search.

Acceptance:

- Before configuration, `/tiktok/api/status` must return `configured=false`, `authorized=false`.
- Before authorization, shop/product calls must fail explicitly; n8n must return structured `ok=false`, not an empty success.
- After authorization, verify `code=0`, expected seller `user_type`, required scopes, authorized shop cipher, token expiry, and one read-only product search.
- Keep publishing, repricing, inventory, campaigns, orders, and destructive actions disabled until separately implemented and explicitly approved.

As of 2026-08-15, code and no-credential failure paths are verified, but Partner Center credentials are not configured. Do not claim the official API is authorized until the OAuth callback succeeds and a real shop/product response is recorded.
## Health checks

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5678/healthz
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Expected:

- n8n HTTP 200.
- Worker `status=ok`, `browser_use=true`, `ollama=true`.
- Ollama lists `qwen3:4b`.
- Worker allow-list includes `shop.tiktok.com`, `doogusa.com`, and localhost.

## Start and stop

Start n8n with `n8n\start-n8n.cmd`. Stop it with `n8n\stop-n8n.cmd`. Never use `docker compose down -v` unless deletion of the n8n data volume is explicitly authorized.

Start the worker with `services\product-worker\start-worker.cmd`. If port 8000 already listens, verify `/health` before starting another process.

Run the complete workflow:

```powershell
$projectRoot = Join-Path $env:USERPROFILE 'Documents\Codex\2026-08-13\ji-xu\outputs\ai-ecommerce-os'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot 'demo-evidence\run-demo.ps1')
```

Pass an approved URL as the first parameter only when intentionally overriding the default.

## End-to-end acceptance criteria

Parse `latest-result.json` and require all of the following:

- The file is non-empty valid JSON.
- `product.product_name`, `product.marketplace`, and `evidence.source_url` are non-empty.
- The screenshot path in `evidence.screenshot` exists and has non-zero size.
- `score` is numeric, `scorecard` is present, and `workflow_version=1.1.0`.
- Unknown cost data produces `contribution_before_ads=null` and margin score 0.
- Unknown market data produces demand and competition scores 0.
- Any blocking unknown produces `decision=research_required` and a non-empty `blocking_unknowns` list.
- `generation.facts_only=true`.
- `generation.provider` is `ollama` or `source-facts-fallback`. A fallback must include `fallback_reason`, and its bullets must exactly match observed source facts.
- No generated numeric claim may be absent from observed product facts.
- `approval.status=pending_human_review` and `approval.publish_allowed=false`.

Verified 2026-08-15 result:

- Product `3 in 1 Water Bottle/Bowl`, price `17.99 USD`, five observed features.
- Score 15: only differentiation scored; cost, demand, competition, and compliance were not invented.
- Decision `research_required` with three blocking unknowns.
- Ollama failed the strict trace check twice, so the source-facts fallback returned five exact page facts.
- Evidence contains source URL, retrieval time, collector, observed fields, assumptions, and a real-page screenshot.

## Content quality gate

Ollama is a local development provider and requires no API key. `qwen3:4b` can be slow and can hallucinate. The Worker therefore uses:

- JSON Schema output constraints.
- Placeholder rejection.
- Unsupported numeric-claim rejection.
- Exact `source_fact` verification.
- Bullet-to-trace matching.
- Risky semantic inference rejection.
- Two attempts, then `source-facts-fallback` instead of unsafe prose or a false success.

Official OpenAI or Anthropic API models can later be added through n8n Credentials or an ignored local `.env`. Keep the same gates even with a stronger model.

## Data and safety boundaries

- Domain allow-lists are mandatory.
- CAPTCHA or login challenges are blockers, not permission to reuse personal sessions.
- Demo values must never be mixed with live marketplace data.
- Missing purchase price, freight, fees, ads, tax, returns, exchange-rate risk, demand, competition, or compliance stays null or unknown.
- Publishing, repricing, ordering, inventory mutation, and destructive changes require explicit human approval.
- Never store API keys, cookies, `.env`, browser profiles, customer records, or marketplace credentials in a Skill or Git repository.

## Update protocol

1. Change project source, not the installed Skill copy.
2. Run health checks and the end-to-end acceptance test.
3. Update the Obsidian note with facts, failures, fallbacks, and unresolved blockers.
4. Update this Skill reference when paths, endpoints, models, workflow IDs, scoring, discovery, or acceptance criteria change.
5. Validate with the official `quick_validate.py`.
6. Copy the validated Skill to `%USERPROFILE%\.codex\skills\ecommerce`.
7. Inspect Git diff and status for secrets and unrelated files.
8. Commit only relevant files, then push. Never claim GitHub synchronization unless push succeeds.

## 2026-08-15 TikTok Shop 官方 API 只读链路验收

### 已验证架构

`n8n Webhook -> 本机 Product Worker 双层鉴权代理 -> Cloudflare Worker -> TikTok Shop 官方 API`

- Cloudflare Worker：`https://tiktok-shop-connector.zenyenochen.workers.dev`
- Cloudflare 部署版本：`f5f2918b-2bce-403e-a570-f2b329d70b15`
- 本机状态：`GET http://127.0.0.1:8000/tiktok/api/cloud/status`
- 本机店铺读取：`GET /tiktok/api/cloud/shops`（要求 `X-Local-Automation-Key`）
- 本机商品读取：`POST /tiktok/api/cloud/products/search`，body 为 `{"region":"TH|PH","page_size":1..100}`
- n8n 生产 Webhook：`POST http://127.0.0.1:5678/webhook/tiktok-shop-products`
- n8n 工作流：`TikTokShopApiReadonly001`

### 验收证据

- Cloudflare `/health`：`status=ok`、`token_stored=true`、`shops_stored=true`。
- 官方授权店铺读取成功：泰国与菲律宾各 1 家，店名均为 `Ozawas Fun Life Studio`。
- 官方商品读取成功：TH 返回 1 条，PH 返回 1 条（测试 `page_size=5`）。
- n8n 生产 Webhook 对 TH、PH 均返回 `ok=true`，来源为 `tiktok_shop_official_api_via_cloudflare`。
- 使用只读密钥访问 `/api/internal/summary` 返回 HTTP 401。
- 不带本地自动化密钥访问本机店铺代理返回 HTTP 401。
- `mutation_routes_enabled=false`；没有发布、改价、库存、订单或广告写入。

### 凭证与维护

- Cloudflare `READONLY_API_KEY` 是独立 Secret，旧 `INTERNAL_API_KEY` 未替换。
- 云端只读密钥与 n8n 本地密钥经当前 Windows 用户 DPAPI 加密保存于 `runtimes/secrets/tiktok-shop-cloud-proxy.dpapi`。
- n8n 本地密钥保存于 n8n Credentials，不写入工作流 JSON、Skill、Obsidian 或 Git。
- Partner Center 的实际 OAuth 回调属于 Cloudflare Worker；本地旧 OAuth 状态不再作为当前连接判据。
- 当前“已连接”只指授权店铺和商品的官方只读接口。写入操作仍必须单独实现、测试并人工确认。