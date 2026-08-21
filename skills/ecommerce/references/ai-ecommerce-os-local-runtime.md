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

## 2026-08-15 市场研究四链路验收

### 结论

- EchoTik：代理、鉴权、输入限制和 Cloudflare 部署均完成；真实数据调用被供应商以 `LINKFOX_INSUFFICIENT_CREDITS` 阻止，当前未取得数据。
- FastMoss：代理、鉴权、跨境店过滤和 Cloudflare 部署均完成；真实数据调用被同一积分余额问题阻止，当前未取得数据。
- LinkFox 公开搜索：路由完成，但同样受 LinkFox 积分余额阻止；现在返回结构化 HTTP 402，不再显示 Cloudflare 1101。
- 独立公开网页搜索：成功发现 TikTok Shop TH/PH 的公开索引结果。搜索引擎结果属于公开快照，可能过期，不能当作实时审计销量。
- Browser Use：运行正常。TikTok 菲律宾公开 PDP 被重定向到越南域名并显示 `Security Check`，已保存截图且未绕过；公开回退商品页成功提取 `3 in 1 Water Bottle/Bowl`、`17.99 USD`、5 条特征及截图。

### 已部署接口

- `POST /api/market-data/echotik`
- `POST /api/market-data/fastmoss`
- `POST /api/market-data/search`
- Cloudflare Worker 版本：`609d08bf-f8ad-42c6-8a39-ac88f3972a59`
- 三条接口只接受现有 `READONLY_API_KEY`，限制 TH/PH、关键词和最多 10 条，不提供写入能力。

### 当前唯一人工阻塞

需要给现有 LinkFox 账户充值积分。充值后只需重新各调用一次 EchoTik、FastMoss 和 LinkFox Search 验收，不需要重新部署代码或重新配置密钥。不要把“积分不足”解释成空结果。

### 证据

- `demo-evidence/market-data/2026-08-15/market-research-status.json`
- `demo-evidence/browser-use-live-product-page.png`

## 2026-08-21 员工工作台与供应链绑定试运行

### 已部署

- 本地入口：`http://127.0.0.1:8000/os`；首次进入跳转 `/os/setup` 创建老板账号。
- 服务状态：`GET /os/status`；返回 `mutation_routes_enabled=false`。
- 老板可创建员工，并将一个员工分配到多家店；员工只会读取服务端分配给自己的店铺。
- 初始店铺占位：`TH-01 泰国店01`、`PH-01 菲律宾店01`。占位名称必须在正式使用前与 TikTok Shop 官方店铺 ID 复核。
- 员工可新增选品候选、绑定 1688 供应商与商品、提交审批；老板或管理员可批准、退回或拒绝。
- 操作日志记录登录、员工创建、候选创建、供应链绑定、提交和审批，不记录密码、Cookie 或 API Key。
- 数据库：`data/workbench.db`（本地 SQLite 试运行）；会话签名密钥在 `runtimes/secrets/workbench-session.key`，不得提交 Git。

### 1688 精确绑定硬门槛

仅保存一个链接不够。每个候选必须绑定：供应商 ID、供应商名称、1688 OFFER ID、`detail.1688.com` 或 `m.1688.com` 链接、店铺 SKU -> 1688 SKU ID、SKU 属性快照、当前采购价、币种、库存、发货天数和采集时间。系统为整个快照生成 SHA-256；缺少任一必要数字或 SKU 映射时禁止提交审批。

批准只表示“允许进入人工上架核验”，不会调用 TikTok Shop 上架、改价、库存、订单、1688 下单或付款接口。出单后采购仍需重新读取供应商价格、库存、SKU 属性和时效，并由人工确认。

### 启停与验收

- 启动：运行 `services/product-worker/start-worker.cmd`。
- 停止：只停止监听 `127.0.0.1:8000` 且命令行为 `uvicorn app:app` 的对应进程。
- 自动测试：在 `services/product-worker` 运行 `..\..\runtimes\browser-use\.venv\Scripts\python.exe -m unittest -v test_workbench.py`。
- 2026-08-21 验收通过：老板初始化、员工分店权限、越权拦截、候选、错误 1688 域名拦截、数字校验、SKU 映射、未绑定禁止提交、审批、重复/越权审批拦截、日志回读。
- 健康检查通过：Product Worker `status=ok`、Browser Use 可用、Ollama `qwen3:4b` 可用；工作台 `status=ok` 且平台写入关闭。
- Docker Desktop 恢复后，n8n /healthz 返回 HTTP 200；生产 Webhook 对 TH、PH 均返回 ok=true、mode=read_only、mutation_routes_enabled=false，本次 page_size=5 验收各回读 5 条商品。

### 仍未执行

- 未把工作台部署到云服务器，也未配置公司域名、HTTPS、PostgreSQL、自动备份或远程员工访问。
- 未将 TikTok 官方商品实时同步进工作台；现有 TikTok Shop 官方接口仍是独立只读链路。
- 未接入 1688 官方实时 API；当前由员工录入并保存证据快照。
- 未启用 TikTok 自动上架、1688 自动下单或付款。
- LinkFox/EchoTik/FastMoss 真实数据仍受积分不足阻塞，不能把受阻当作无结果。

### 老板下一步

打开 `http://127.0.0.1:8000/os/setup`，自行创建第一个老板账号和强密码。不要把密码发给 Codex。进入后先创建一名测试员工并只分配一家测试店，再用一条真实 1688 商品做候选和 SKU 绑定演练。