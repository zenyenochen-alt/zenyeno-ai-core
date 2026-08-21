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
- 工作台新增商品列表、商品异常、AI分析、标题与卖点草稿；商品通过现有 n8n -> TikTok Shop 官方 API 只读链路同步，异常采用可解释规则，草稿只使用已观察事实。
- 免费选品雷达已加入：利润、需求、竞争、差异化、合规共 100 分；任一关键数据未知时该项记 0 并保留 locking_unknowns，只有无阻断且总分至少 70 才进入人工复核，永不直接发布。
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
- 第二组自动测试通过：官方只读商品合同、商品缓存、不可售/缺SKU异常识别、事实草稿保存和 publish_allowed=false。
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
## 2026-08-21 第二阶段本地生产准备

### 新增能力

- 员工账号支持老板修改角色、启用/停用、重新分配多家店和重置临时密码；老板账号不能通过员工接口修改。
- TikTok官方只读同步现在验证返回地区必须与当前店铺一致，并保存官方店名和最近验证时间；若身份不一致则整次同步被阻止。
- 免费公开选品发现接入固定的 DuckDuckGo HTML 公开搜索源，只接受 `shop.tiktok.com` 且路径包含 `/pdp/` 的结果。公开快照只生成 `research_required` 候选，不提供实时销量或成本证明。
- 免费公开搜索源实时可访问：HTTP 200，本次测试页包含11个搜索结果链接；候选解析与白名单通过自动合同测试。
- 老板工作台新增“立即备份”；`workbench_backup.py` 使用SQLite在线备份API、SHA-256清单和 `PRAGMA quick_check`，保留最近30份。恢复要求明确确认词，并在恢复前自动创建第二份保护备份。
- 已为真实 `workbench.db` 创建首个备份并独立验证：哈希匹配、`sqlite_quick_check=ok`。
- 老板批准商品后只生成 `tiktok_listing_draft` 待执行项。每项包含唯一幂等键、供应链快照哈希、载荷哈希和第二次人工批准要求；当前无执行按钮。
- 出单后采购请求必须重新提交采购价、库存、发货天数、SKU映射与原始快照哈希。任何变化或库存不足都会阻止请求；一致时只生成 `supplier_purchase` 待执行项，仍不付款。

### 新增入口

- `PUT /os/api/employees/{employee_id}`：修改员工角色、状态与店铺。
- `POST /os/api/employees/{employee_id}/reset-password`：老板重置员工临时密码。
- `POST /os/api/admin/backup`：创建并验证数据库备份。
- `POST /os/api/discovery/public-search`：免费公开发现候选。
- `POST /os/api/candidates/{candidate_id}/purchase-request`：采购前二次核验并进入待执行队列。
- `backup-now.cmd`：命令行立即备份。
- 恢复命令：`python workbench_backup.py restore <备份文件> --confirm RESTORE_WORKBENCH`；恢复前应停止工作台服务。

### 验收

- 三组E2E全部通过：账号与多店权限；候选、1688绑定、评分、审批与待执行队列；官方只读同步、异常与事实草稿；备份、哈希验证、错误恢复确认拦截和显式恢复。
- 真实运行检查：工作台正常、n8n HTTP 200、Ollama可用、全部新增路由存在、`operation_outbox`表与店铺官方身份字段完成迁移。
- `mutation_routes_enabled=false`；没有TikTok上架、改价、库存变更、1688下单或付款调用。

### 仍需外部条件

- 公网员工访问仍需要云服务器、公司域名、HTTPS、PostgreSQL和异地备份目标；当前仅绑定 `127.0.0.1`。
- 1688实时商品与采购API需要合法开放平台应用和凭证；当前二次核验由人工录入事实快照。
- TikTok写入API需要单独申请写权限、沙箱验证、第二审批、结果回读与对账；当前只创建待执行项。
- LinkFox/EchoTik/FastMoss真实市场数据仍受积分余额限制。免费公开搜索不能替代实时市场数据库。

## 2026-08-22 中央服务器部署包与隔离联调

### 已实现的部署包

云端部署目录：`outputs/ai-ecommerce-os/deploy/cloud`。

- `Dockerfile`：固定 Python 3.12.10，使用非 root 用户，包含工作台、备份程序、云端应用和内部只读连接器。
- `compose.yaml`：工作台、内部 TikTok 只读连接器、n8n、Caddy、备份任务；Ollama 为可选 profile。
- `Caddyfile`：自动 HTTPS、HTTP 跳转、HSTS、禁止 iframe、关闭摄像头/麦克风/定位权限，并隐藏 Server 响应头。
- `workflows/tiktok-shop-readonly-cloud.json`：新实例首次启动时自动导入并发布；只允许 TH/PH 和 1–100 条，只调用 Docker 内网 `connector:8010`。
- `.env.example` 与 `initialize-env.ps1`：生成首次设置令牌和 n8n 加密密钥；真实 `.env` 已被 `.gitignore` 和项目根 `.dockerignore` 排除。
- `validate-deployment.ps1`：占位域名、短密钥、占位 TikTok 只读密钥或无效域名都会阻止部署。
- `deploy.ps1`：验证后构建并启动。
- `backup.ps1`：离线网络模式运行 SQLite 在线备份、SHA-256 和 `PRAGMA quick_check`。

### 网络与密钥边界

- 只有 Caddy 发布主机 `80/443`；工作台、n8n、内部连接器没有主机端口。
- 工作台同时连接 `edge` 和 `automation`；n8n/connector 只在 `automation`；Caddy 只在 `edge`。
- n8n 工作流没有 Credential、API Key 或外部 Worker 地址，也不能读取宿主环境变量。
- `TIKTOK_READONLY_API_KEY` 只存在于 connector 容器环境；connector 的外部目标固定为允许名单中的 Cloudflare Worker。
- n8n 明确禁止未验证社区包；平台写入仍为 `mutation_routes_enabled=false`。
- `.dockerignore` 排除 `.env`、数据库、备份、日志、浏览器 profile、runtimes、sources 和 demo evidence，防止进入镜像构建上下文。

### 2026-08-22 实际验收结果

- Docker Compose 配置解析通过；Caddy `2.10.2-alpine` 配置验证为 `Valid configuration`。
- 工作台/connector/backup 镜像重新构建成功，构建上下文约 2.27 KB，未携带本地资料。
- 使用独立项目名 `ai-ecommerce-cloud-smoke` 从空卷启动：connector、n8n、workbench 均为 healthy。
- n8n CLI 可列出并发布固定工作流 `TikTokShopCloudReadonly001`。
- 错误输入 `{region: US, page_size: 0}` 返回 HTTP 400、`ok=false`、`status=invalid_input`。
- 测试只读密钥被上游拒绝时返回 HTTP 502、`ok=false`、`status=upstream_error`，没有 HTTP 200 假成功。
- 错误首次设置令牌返回 HTTP 403；正确临时令牌创建测试老板返回 HTTP 200，Cookie 同时包含 Secure、HttpOnly、SameSite=Lax。
- 云端备份任务成功：98,304 bytes，SHA-256 已生成，`sqlite_quick_check=ok`。
- 本地与云端共 8 项 unittest 通过：多店权限、官方只读同步、异常、事实草稿、审批/待执行队列、备份恢复、首次设置令牌、云端网络/失败语义。
- 隔离测试完成后，临时容器、临时数据库卷、临时账号和临时备份已全部删除。
- 本机实际服务仍健康：工作台 `:8000`、n8n `:5678`、Ollama `:11434` 均返回 HTTP 200。
- 结构化验收证据：`demo-evidence/cloud-deployment/2026-08-22/smoke-result.json`。

### 真实服务器部署步骤

1. 准备一台 Linux 云服务器，开放入站 TCP 80/443，并安装 Docker Engine 与 Compose plugin。
2. 把 `ai-ecommerce-os` 项目复制到服务器，但不要复制本机 `.env`、数据库、浏览器 profile、Cookie 或 DPAPI 文件。
3. 进入 `deploy/cloud`，运行：`powershell -NoProfile -ExecutionPolicy Bypass -File ./initialize-env.ps1`。Linux 没有 PowerShell 时，按照 `.env.example` 手工创建 `.env`，首次设置令牌和 n8n 加密密钥至少 48 字符随机值。
4. 设置 `OS_DOMAIN=os.<公司主域名>` 和服务器专用的 `TIKTOK_READONLY_API_KEY`。不要在聊天、Git、截图或员工电脑中传递密钥。
5. 在域名服务商将该子域名 A/AAAA 记录指向服务器公网 IP。
6. 运行 `validate-deployment.ps1`；验证通过后运行 `deploy.ps1`。Linux 等效命令：`docker compose --env-file .env -f compose.yaml config --quiet`，然后 `docker compose --env-file .env -f compose.yaml up -d --build`。
7. 等待 DNS 生效和 Caddy 自动签发证书，打开 `https://os.<公司主域名>/os/setup`。
8. 使用服务器 `.env` 中的首次设置令牌，自行创建老板账号和强密码；不要把老板密码交给 Codex。
9. 创建测试员工，只授权一家测试店，先完成只读同步、候选、1688 SKU 绑定、审批和操作日志演练。
10. 设置每天运行 `backup.ps1`，并把备份复制到另一台机器或对象存储；只保存在同一服务器不算异地备份。

### 当前仍未执行

- 尚未购买/指定真实云服务器和公司域名，因此没有公网 URL、真实 DNS 或正式 HTTPS 证书。
- 云端中央服务器模式已经迁移到内部 PostgreSQL；真实公网部署、异地备份和多实例高可用仍未执行。
- 服务器专用 TikTok 只读密钥尚未写入真实服务器；本次只验证了拒绝路径，未把本机秘密复制到云端。
- 1688 官方实时 API、采购接口和异地备份目标仍需要外部账号/凭证或存储位置。
- TikTok 上架、改价、库存、订单、1688 下单和付款仍全部关闭。后续即使取得写权限，也必须经过第二人工审批、幂等键、执行后回读和对账。

## 2026-08-22 PostgreSQL 中央数据库完成

本节覆盖前文“云端仍使用 SQLite / PostgreSQL 未执行”的旧状态。现在的准确状态是：本机单人模式继续使用 SQLite；`deploy/cloud` 中央服务器模式默认使用 PostgreSQL。

### 实现

- 新增 `services/product-worker/workbench_db.py`：保留 SQLite 行为，同时支持 `DATABASE_URL=postgresql://...`。
- PostgreSQL 兼容层处理参数占位符、`INSERT OR IGNORE`、自增主键、返回 ID、行的名称/序号访问、事务提交/回滚、唯一约束异常和表字段检查。
- 云端镜像固定 `psycopg[binary]==3.3.4`；该版本于 2026-08-22 从官方 PyPI 版本页核对并在镜像中安装成功。
- `compose.yaml` 新增内部 `postgres:17.10-alpine3.23` 服务、健康检查、`postgres_data` 持久卷；镜像实际拉取摘要为 `sha256:8189a1f6e40904781fc9e2612687877791d21679866db58b1de996b31fc312e4`。
- PostgreSQL 仅加入 Docker `automation` 网络并只 `expose 5432`，没有发布主机端口。
- `.env.example`、`initialize-env.ps1`、`validate-deployment.ps1` 已加入 `POSTGRES_DB`、`POSTGRES_USER` 和随机十六进制 `POSTGRES_PASSWORD`；密码过短或格式错误会阻止部署。
- 工作台 `/os/status` 会明确返回 `database=postgresql` 或 `database=sqlite`。
- PostgreSQL 模式下，老板页面的 SQLite 备份按钮返回 HTTP 409 并指向服务器备份任务，避免制造一份错误的 SQLite 备份。

### PostgreSQL 真实业务 E2E

使用独立项目 `ai-ecommerce-postgres-smoke` 从空卷启动，PostgreSQL、connector、n8n、workbench 全部 healthy；数据库自动建立 13 张 public 表。随后通过真实 HTTP 接口完成：

1. 首次老板账号初始化；
2. 两个店铺种子数据；
3. 创建员工并只授权一家店；
4. 创建候选商品；
5. 绑定 1688 供应商、OFFER、精确 SKU 和属性快照；
6. 提交人工审批；
7. 生成 `tiktok_listing_draft` 待执行项；
8. 创建 `supplier_purchase` 待执行项；
9. 重复采购请求返回同一个 outbox ID，幂等通过；
10. 员工访问未授权店铺返回 HTTP 403；
11. 全程 `marketplace_write_executed=false`、`payment_executed=false`。

### 备份与恢复验收

- `postgres-backup.sh` 使用 `pg_dump --format=custom`，随后执行 `pg_restore --list` 和 SHA-256。
- 最新测试备份生成成功并恢复到临时数据库 `ai_ecommerce_restore_verify`。
- SHA-256 核对为 `ok`，恢复为 `ok`；恢复库回读 `users=2`、`candidates=1`、`operation_outbox=2`。
- 核验后临时恢复数据库、测试容器、测试账号、PostgreSQL 卷和测试备份卷全部删除。
- 结构化证据：`demo-evidence/cloud-deployment/2026-08-22/postgres-smoke-result.json`。

### 最终回归

- 本地 SQLite、采集机安全与云端配置共 15 项 unittest 全部通过。
- 最终镜像重新构建成功；`.dockerignore` 后构建上下文为 474 bytes，测试脚本、`.env`、数据库、备份、浏览器资料和日志未进入生产镜像。
- 本机工作台已重启加载最新代码；`/os/status` 返回 `database=sqlite`、`mutation_routes_enabled=false`，n8n 和 Ollama 仍为 HTTP 200。

### 真实上线仍需要的外部输入

- 一台真实 Linux 云服务器；
- 一个公司主域名/子域名及 DNS 修改权限；
- 服务器专用 TikTok 只读 API Key；
- 一个异地备份目标；
- 1688 官方 API 应用与凭证。

这些外部输入到位前，不能声称员工已能从公网登录。TikTok/1688 写入、下单和付款仍全部关闭。

### Linux 一键部署与备份脚本

- `initialize-env.sh`：从 `/dev/urandom` 生成 64 位十六进制 PostgreSQL 密码、首次设置令牌和 n8n 加密密钥，并将 `.env` 权限设为 `600`。
- `validate-deployment.sh`：验证真实域名、PostgreSQL变量、TikTok只读密钥、Docker和Compose配置；占位域名会直接阻止部署。
- `deploy.sh`：先验证，再构建和启动中央服务。
- `backup.sh`：运行 PostgreSQL custom-format 备份。
- `verify-latest-backup.sh`：核对最新备份 SHA-256 和 `pg_restore --list` 目录。
- 六个 shell 脚本均在 `postgres:17.10-alpine3.23` 的 `/bin/sh` 中通过语法检查；临时初始化测试确认 `.env=600`、三项随机密钥长度均为64、占位域名守卫生效。
- 加入 Linux 脚本检查后，本地自动测试为 15 项全部通过。
- 结构化证据：`demo-evidence/cloud-deployment/2026-08-22/linux-deployment-scripts-result.json`。

Linux 服务器执行顺序：

```sh
cd deploy/cloud
sh ./initialize-env.sh
# 编辑 .env，填写真实 OS_DOMAIN 和 TIKTOK_READONLY_API_KEY
sh ./validate-deployment.sh
sh ./deploy.sh
sh ./backup.sh
sh ./verify-latest-backup.sh
```

## 2026-08-22 证据化选品雷达与审核硬门槛

本次把“系统选品 → 人工审核 → 1688 精确 SKU → 上架草稿队列”从可演示流程升级为有证据硬门槛的流程。平台写入、采购执行和付款仍关闭。

### 新增实现

- 新增 `candidate_observations` 追加式证据表；每条记录保存候选商品、来源名称、来源类型、公开 URL、观察事实、观察时间、采集人和创建时间。
- 新增 `POST /os/api/candidates/{candidate_id}/observations`；支持 `public_page`、`browser_use`、`official_api`、`echotik`、`fastmoss`、`supplier_quote` 和 `manual_research` 来源。
- 工作台“选品候选”增加“补充带证据数据”按钮，员工可录入售价、到岸成本、需求、竞争数量、可核实卖点、合规风险和币种；每个数值都会关联证据记录 ID、URL 与时间。
- 公开选品证据超过 30 天会被拒绝；1688 价格、库存和发货时效快照超过 7 天会被拒绝；未来时间和无时区时间会被拒绝。
- 严格评分仍为利润 25、需求 25、竞争 20、差异化 15、合规 15。字段有数值但没有证据时记 0，并列入 `blocking_unknowns`。
- 只有无阻断且总分至少 70 的候选才标记 `ready_for_human_review`；否则提交上架审核返回 HTTP 422。
- 已在等待审批或已经批准的候选不能直接改写选品证据或更换供应商绑定，避免审批后偷换商品。
- 普通员工只能调研和提交；任务审批接口继续只允许老板或经理。
- 供应链实质快照比较价格、库存、时效、供应商、OFFER 和精确 SKU；重新采集时间可以变化，但任何实质字段变化仍返回 HTTP 409 并阻止采购。

### 当前验收结果

- 本地 SQLite、采集机安全与云端配置共 15 项 unittest 全部通过。
- 隔离 Docker 栈中 PostgreSQL、connector、n8n、workbench 全部 healthy。
- PostgreSQL 当前创建 13 张 public 表，新增证据表自增 ID 在 PostgreSQL 兼容层中正确返回。
- 证据齐全的测试候选得到 100 分并进入人工审核；证据不足候选无法提交。
- 审批后生成 `tiktok_listing_draft`，采购请求生成 `supplier_purchase`，重复采购返回相同 outbox ID。
- 员工跨店访问返回 HTTP 403；全程 `marketplace_write_executed=false`、`payment_executed=false`。
- PostgreSQL custom-format 备份恢复成功；恢复库回读 `tables=13`、`candidate_observations=1`、`operation_outbox=2`。
- 临时恢复数据库、容器、网络、账号、测试数据库卷和备份卷全部删除。
- 结构化证据：`demo-evidence/selection-radar/2026-08-22/evidenced-selection-postgres-smoke.json`。
## 2026-08-22 Browser Use 接入员工工作台

### 实现

- 工作台候选商品新增“Browser Use自动采集”按钮，调用服务器配置的固定 `PRODUCT_COLLECTOR_URL`，员工不能把请求改向任意内网地址。
- 新增 `POST /os/api/candidates/{candidate_id}/collect-browser-facts`：先校验员工店铺权限，再调用采集器，并要求返回 `collector=browser-use`。
- 采集结果必须与候选商品同源；普通网页跳转到不同站点会被拒绝，TikTok Shop 官方域名之间的商品发现跳转例外。
- `candidate_observations.evidence_json` 保存截图路径、实际观察字段、采集器假设和发现过程；元数据超过 25KB 会被拒绝。
- 实时公开商品页只接受页面真正观察到的售价、币种、已售数量和卖点。不会把页面没有提供的到岸成本、月搜索量、竞品数量或合规结论写成事实。
- 只有受控本地演示页明确标记 `cost_data_complete=true`、`market_data_complete=true` 时，才允许导入到岸成本、需求与竞争数据。
- 本机模式默认启用采集器；`/os/status` 和 `/os/api/bootstrap` 明确返回 `browser_collector_enabled`。
- 中央云端 `compose.yaml` 明确设置 `PRODUCT_COLLECTOR_ENABLED=false`，员工页面隐藏按钮。原因是生产工作台镜像不携带Chrome、TikTok Cookie、紫鸟资料或浏览器Profile；评分、手工证据、审批和队列功能不受影响。

### 真实联调

在隔离临时数据库和临时老板账号中，工作台真实调用本机 Browser Use 打开 `http://127.0.0.1:8000/demo-product`：

- 保存截图及证据元数据；
- 保存售价、到岸成本、需求、竞争、卖点、合规和币种共 7 类字段；
- 严格评分为 87，结论为 `ready_for_human_review`；
- `observation_id` 正常生成；
- 未执行平台写入或付款；
- 测试结束后临时账号、数据库和服务进程全部删除。

随后重新构建隔离云端 PostgreSQL 栈，工作台、n8n、connector、PostgreSQL 全部 healthy；13 张表和 `evidence_json` 列完成备份恢复，恢复库回读 `candidate_observations=1`。临时云端数据库、容器、网络和数据卷全部删除。

- 当前回归测试：15 项全部通过，工作台 JavaScript 语法检查通过。
- 真实联调证据：`demo-evidence/selection-radar/2026-08-22/browser-use-workbench-integration.json`。
- 云端回归证据：`demo-evidence/selection-radar/2026-08-22/browser-use-cloud-regression.json`。

### 尚未执行

云端专用 Browser Use 采集机尚未部署。不能直接把本机浏览器Profile或店铺Cookie上传到中央服务器。后续需要独立采集机、设备级访问控制、请求签名、允许域名清单和结果回传校验后，才能把云端开关打开。
## 2026-08-22 安全 Browser Use 采集机

### 架构

为避免把紫鸟环境、TikTok Cookie 或 Chrome Profile 上传中央服务器，新增独立 `browser_collector_agent.py`。正式链路设计为：

```text
中央工作台
  -> HMAC-SHA256签名任务
  -> HTTPS或私有VPN
  -> 老板/采集电脑的Browser Use Agent
  -> 本机浏览器采集与截图
  -> HMAC-SHA256签名结果
  -> 中央工作台验签后保存证据
```

### 安全门槛

- 请求和响应均采用 HMAC-SHA256；共享密钥至少 32 字节，初始化脚本生成 64 位十六进制随机值。
- 签名覆盖协议版本、消息类型、Unix时间、随机 nonce 和规范化 JSON 的 SHA-256。
- 请求时间允许偏差 90 秒；过期或未来请求返回 HTTP 401。
- nonce 在采集机内存中保存 180 秒；重复请求返回 HTTP 409，阻止重放。
- 中央工作台对非本机采集地址强制 `https://`；缺少强密钥返回 HTTP 503。
- 中央工作台同时验证响应时间、nonce 和响应签名；篡改结果返回 HTTP 502，不写入证据库。
- 采集机启动脚本只监听 `127.0.0.1:8012`，不能直接把8012端口暴露公网；必须通过HTTPS反向隧道或私有VPN连接。
- 健康接口明确返回 `writes_enabled=false`；采集机不包含上架、购买或付款接口。

### 文件与启动

- 协议实现：`services/product-worker/browser_collector_security.py`
- 采集机服务：`services/product-worker/browser_collector_agent.py`
- Windows启动：`services/product-worker/start-browser-collector-agent.cmd`

采集电脑先在本机环境变量中设置 `BROWSER_COLLECTOR_SHARED_SECRET`，然后运行启动脚本。中央服务器 `.env` 使用相同密钥，并设置：

```env
PRODUCT_COLLECTOR_ENABLED=true
PRODUCT_COLLECTOR_URL=https://真实采集机域名/v1/collect
PRODUCT_COLLECTOR_SHARED_SECRET=64位十六进制随机密钥
```

随后必须重新运行 `validate-deployment.ps1` 或 `validate-deployment.sh`。占位域名、HTTP地址或弱密钥都会阻止开启。

### 验收

- 自动回归现为 15 项，覆盖缺少签名、签名篡改、过期请求、nonce重放、响应验签、云端默认关闭和PowerShell 5.1兼容。
- 真实三段联调 `临时中央工作台 -> 签名采集机 -> Browser Use -> 签名回传` 成功；采集7类字段、评分87、保存截图和证据ID。
- 一次性共享密钥没有写入证据文件，临时账号、数据库、8011/8012服务和目录均删除。
- Windows PowerShell 5.1 和 Linux `/bin/sh` 初始化脚本均生成64位随机采集密钥；默认关闭验证通过，开启占位URL被阻止，真实HTTPS URL与强密钥验证通过。
- 云端生产镜像重新构建成功，PostgreSQL业务冒烟通过，`browser_collector_enabled=false` 为默认状态。
- 证据：`demo-evidence/selection-radar/2026-08-22/secure-browser-collector-deployment.json`。

### 仍需外部条件

代码与本机安全链路已经完成，但真实远程配对尚未执行，因为仍缺少公网员工服务器、公司域名和采集机HTTPS/VPN地址。取得这些资源后才能把云端 `PRODUCT_COLLECTOR_ENABLED` 改为 `true`。

## 2026-08-22 Restic 加密异地备份闭环

本节覆盖前文“异地备份尚未实现”的旧状态。准确状态是：加密 S3 兼容备份、下载、隔离验证和真实 PostgreSQL 恢复代码已经完成；由于尚未提供真实对象存储端点和访问凭证，生产 `.env` 仍保持 `OFFSITE_BACKUP_ENABLED=false`，当前没有真实公网异地副本。

### 实现

- 固定使用官方 `restic/restic:0.19.1` 镜像；Restic 在上传前客户端加密。
- `offsite-backup.ps1/.sh` 先创建并验证 PostgreSQL custom-format dump，再上传 dump 与校验文件。
- PostgreSQL SHA-256 清单改为可移动的相对文件名；恢复验证同时兼容旧的绝对路径清单。
- 生产仓库只允许 `s3:https://`；明文 HTTP 只能在显式隔离测试模式使用，而生产验证器强制禁止测试模式。
- 真实启用必须提供强 `RESTIC_PASSWORD`、S3 access key、secret key 和非占位仓库地址。
- `RESTIC_AUTO_INIT=true` 只用于第一次创建仓库，首个备份成功后恢复为 `false`。
- 每次上传后运行 `restic check --read-data-subset`；生产默认抽查 5%，隔离测试读取 100%。
- 恢复只进入独立 `offsite_restore` 卷；目标非空时拒绝恢复，不会覆盖在线 PostgreSQL。
- 没有自动 `forget`/`prune`，避免未经审批删除远端快照。

### 每日自动调度

生产 Linux 服务器提供 systemd 定时器模板与受控安装器：

```sh
sudo sh ./systemd/install-backup-timer.sh /opt/ai-ecommerce-os/deploy/cloud ai-ecommerce
sh ./systemd/backup-timer-status.sh
```

- 固定每天北京时间 03:15 运行，随机延迟最多 15 分钟，避免多台服务器同时冲击对象存储；
- `Persistent=true`，服务器关机错过时间后会补跑；
- 服务以指定部署用户运行，要求该用户具备 Docker 权限；
- `.env` 未启用、仓库不是 HTTPS 或仍为占位值时拒绝安装；
- `UMask=0077`、`NoNewPrivileges=true`，输出与失败进入 systemd journal；
- 状态脚本显示计时器、下次运行时间与最近 100 行备份日志；
- 安装动作只应在真实服务器和真实 S3 凭证齐备后执行，本机没有伪造 systemd 安装状态。

一次性容器安装验收已验证模板能正确渲染绝对部署路径、服务用户和北京时间，且生成文件不残留占位符。
### 验收

在没有公网端口的临时 Docker 网络中启动 PostgreSQL 与 S3 兼容对象存储：

1. 创建带 1 条探针记录的数据库并生成 custom-format dump；
2. 初始化临时加密仓库并上传；
3. 验证对象名不含数据库 dump、`.dump` 或 `.sha256` 文件名；
4. 使用错误口令访问，确认被拒绝；
5. 从对象存储恢复到新的空卷；
6. 验证 SHA-256 与 `pg_restore --list`；
7. 将 dump 恢复到新的 PostgreSQL 数据库，回读探针记录为 1；
8. 删除临时数据库、对象存储、容器、网络和卷。

结果：16 项项目回归测试通过；全程 `live_database_overwritten=false`、`marketplace_writes_enabled=false`、`credentials_persisted=false`。结构化证据：`demo-evidence/cloud-deployment/2026-08-22/encrypted-offsite-backup-smoke.json`。

### 真实上线仍需

- 老板选择一个 S3 兼容对象存储并创建专用私有存储桶；
- 创建只允许该存储桶路径的最小权限访问键；
- 在服务器 `.env` 填写真实端点、区域和访问键；
- 首次初始化后立即关闭 `RESTIC_AUTO_INIT`；
- 设置每日备份计划，并至少每月执行一次隔离恢复演练。

## 2026-08-22 员工登录与权限安全基线

本节覆盖此前仅有基础登录、但会话无法由服务端撤销的旧状态。员工工作台现已实现以下生产前安全基线：

- 密码使用 PBKDF2-HMAC-SHA256，默认 600,000 轮；旧 310,000 轮哈希在用户成功登录后自动升级，不保存明文密码。
- 密码最少 12 个字符；用户名、密码输入均有限长，避免异常大请求。
- Cookie 中只保存带 HMAC 签名的随机会话 ID；会话哈希、用户、到期时间和撤销时间保存在数据库 `auth_sessions`。
- 默认会话有效期 8 小时；登出、管理员重置员工密码、修改员工权限都会撤销对应服务端会话。
- 员工重新登录后需重新获取 CSRF 令牌；所有认证后的 POST、PUT、PATCH、DELETE 请求都必须携带 `x-csrf-token`。
- 设置老板账号和登录接口只接受 JSON；跨站 `Origin`、`Referer` 或 `Sec-Fetch-Site` 请求被拒绝。
- 登录失败记录保存在 `login_guards`，按隐私化 HMAC 键统计；15 分钟窗口内失败 5 次后临时阻断 15 分钟，并返回 HTTP 429。
- 不存在的用户名仍执行一次虚拟密码哈希验证，缩小用户名枚举的时间差。
- 云端Cookie启用 `Secure`、`HttpOnly`、`SameSite=Strict`；页面返回 CSP、`X-Frame-Options: DENY`、`nosniff`、`no-referrer`、COOP/CORP 和禁用摄像头/麦克风/定位的权限策略。
- `/os` 与认证接口使用 `Cache-Control: no-store`；云端启用一年 HSTS。
- 由于当前页面仍内嵌脚本和样式，CSP暂时保留 `unsafe-inline`；迁移到独立静态文件或 nonce 后才能进一步收紧，不能将当前CSP描述为最终状态。

安全升级后，旧版无状态Cookie会失效。用户只需在工作台重新登录一次；不需要重新授权TikTok店铺，也不会改动商品或订单。

### 验收结果

- 前端 JavaScript `node --check`：通过。
- Python编译：通过。
- 工作台、云部署与Browser采集器回归：19项通过。
- 本地运行时：`/os/status` HTTP 200，认证安全状态全部启用，平台写入路由仍关闭。
- 独立Docker/PostgreSQL空卷测试：connector、n8n、workbench和PostgreSQL全部健康。
- PostgreSQL真实HTTP流程：老板设置、员工创建、两家店、跨店403、选品证据门槛、1688准确SKU绑定、人工审批、采购任务幂等、退出与重新登录全部通过。
- 数据库包含15张public表，其中认证表为 `auth_sessions` 和 `login_guards`。
- PostgreSQL custom-format备份通过SHA-256验证，并实际恢复到独立临时数据库；恢复后15张表和2张认证表完整存在。
- 验收发现并修复 `verify-latest-backup.sh` 未进入 `/backups` 目录就校验相对SHA-256清单的问题。
- 临时容器、网络和数据卷已删除；原有n8n健康检查仍为HTTP 200。
- 全程没有执行TikTok Shop写入，也没有执行采购付款。

结构化证据：`demo-evidence/cloud-deployment/2026-08-22/employee-auth-security.json`。

### 运维规则

1. 正式发布后通知员工重新登录，不保留旧Cookie兼容入口。
2. 不要把会话签名密钥、数据库密码、TikTok密钥或CSRF令牌写入Git、Obsidian或聊天记录。
3. 管理员修改员工负责店铺或重置密码后，员工必须重新登录，这是预期行为。
4. 生产故障排查先看 `/os/status` 的非敏感状态，再查服务日志；不要输出Cookie或密码。
5. 在没有真实域名、DNS、HTTPS和服务器前，不声称公网员工工作台已经上线。
6. 写入类API继续保持关闭；以后开放商品发布必须经过来源证据、SKU快照、人工批准、幂等键和写后回读。

实现依据：OWASP Password Storage、CSRF Prevention 与 Session Management Cheat Sheet。
