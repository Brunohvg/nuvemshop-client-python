# Nuvemshop SDK — Python

SDK Python profissional para a API da Nuvemshop.  
Rate-limit safe · Variant-first · Production-ready.

---

## Instalação

```bash
pip install nuvemshop-sdk
```

---

## Início Rápido

```python
from nuvemshop_sdk import NuvemshopClient

client = NuvemshopClient(
    store_id=123456,
    access_token="your_permanent_token",
)

# Listar produtos (paginação lazy)
for product in client.products.iter_all():
    print(product["name"])

# Atualizar estoque (sempre por variante!)
client.inventory.set_stock(product_id=1, variant_id=2, stock=50)

# Verificar rate limit
status = client.rate_limit_status()
print(f"Remaining: {status.remaining}")
```

---

## Autenticação OAuth

Os tokens da Nuvemshop são **permanentes** (não existe refresh flow).

```python
from nuvemshop_sdk import NuvemshopAuth

creds = NuvemshopAuth.exchange_code(
    client_id="your_app_id",
    client_secret="your_app_secret",
    code="authorization_code",
)

client = NuvemshopClient(
    store_id=creds.store_id,
    access_token=creds.access_token,
)
```

---

## 🧠 Como a Nuvemshop Funciona

Estas regras são **fundamentais** e o SDK as impõe automaticamente:

| Regra | Descrição |
|-------|-----------|
| **Estoque é por variante** | Nunca atualize estoque no nível do produto. Use `client.inventory.set_stock()` ou `client.variants.update_stock()`. |
| **Produto sempre tem variante** | Se você criar um produto sem variantes, o SDK cria uma variante padrão automaticamente. |
| **OAuth é permanente** | Não existe refresh token. O access_token retornado no OAuth é permanente. |
| **API é paginada** | Use `iter_all()` (generator lazy) para grandes volumes, evitando estouro de memória. |
| **HTTP 402 = Loja inativa** | Se a assinatura da loja expirar, a API retorna 402. O SDK lança `StoreInactiveError`. |
| **Pedidos são webhook-driven** | Processe pedidos via webhooks em vez de polling. |

---

## SDK Guarantees

O SDK garante:

- ✅ **Rate-limit safe** — Leitura de `X-RateLimit-Remaining` e `X-RateLimit-Reset`. Espera automática preemptiva e reativa. Thread-safe por `store_id`.
- ✅ **Idempotent POST** — `Idempotency-Key` automática (configurável) para evitar duplicatas.
- ✅ **Variant-first inventory** — Bloqueia updates de estoque no nível do produto. Valida no SDK.
- ✅ **Webhook security** — Validação HMAC-SHA256 com `hmac.compare_digest()` e proteção contra replay (5 min).
- ✅ **No business-error masking** — Retry apenas para NetworkError, 5xx e 429. Nunca para 401, 402, 403, 422.
- ✅ **Structured logging** — JSON logging obrigatório com `store_id`, `method`, `status_code`, `remaining`, `duration_ms`.
- ✅ **Forward-compatible models** — Pydantic com `extra="allow"` para não quebrar quando a API evoluir.

---

## Recursos Disponíveis

```python
client.products      # ProductsResource — CRUD + model enforcement
client.variants      # VariantsResource — Stock, Price, SKU
client.inventory     # InventoryResource — Proxy seguro para variantes
client.orders        # OrdersResource — Webhook-first
client.customers     # CustomersResource — CRUD
client.webhooks      # WebhooksResource — CRUD + verify_signature()
client.stores        # StoresResource — Informações da loja
```

---

## Paginação

```python
# Generator lazy (recomendado para grandes volumes)
for product in client.products.iter_all(per_page=100):
    process(product)

# Coletar tudo em lista (cuidado com memória em lojas grandes)
all_products = client.products.get_all()
```

---

## Variantes e Estoque

```python
# Atualizar estoque (SEMPRE por variante)
client.variants.update_stock(product_id=1, variant_id=2, stock=100)

# Atualizar preço
client.variants.update_price(product_id=1, variant_id=2, price="79.90")

# Atualizar SKU
client.variants.update_sku(product_id=1, variant_id=2, sku="CAM-P-AZUL")

# Via InventoryResource (proxy seguro)
client.inventory.set_stock(product_id=1, variant_id=2, stock=100)
client.inventory.list_stock(product_id=1)
```

---

## Validação de Webhook

```python
from nuvemshop_sdk.utils.webhook import verify_webhook_signature

is_valid = verify_webhook_signature(
    body=request.data,
    signature=request.headers["X-Linkedstore-HMAC-SHA256"],
    secret="your_client_secret",
    timestamp=float(request.headers.get("X-Linkedstore-Timestamp", 0)),
)
```

---

## Exceptions

```python
from nuvemshop_sdk import (
    UnauthorizedError,    # 401
    StoreInactiveError,   # 402
    ForbiddenError,       # 403
    ValidationError,      # 422
    RateLimitError,       # 429
    ServerError,          # 5xx
    NetworkError,         # Connection failures
)

try:
    client.products.get(123)
except StoreInactiveError as e:
    print(f"Loja inativa: {e.error_description}")
except RateLimitError as e:
    print(f"Rate limit: retry after {e.retry_after}s")
```

---

## Logging Estruturado

```python
import logging
from nuvemshop_sdk.http_client import StructuredJsonFormatter

handler = logging.StreamHandler()
handler.setFormatter(StructuredJsonFormatter())
logging.getLogger("nuvemshop_sdk").addHandler(handler)
logging.getLogger("nuvemshop_sdk").setLevel(logging.DEBUG)

# Ou simplesmente:
client = NuvemshopClient(store_id=123, access_token="...", debug=True)
```

Output:
```json
{"timestamp": "2026-02-20 17:00:00", "level": "DEBUG", "message": "Nuvemshop API request", "store_id": 123, "method": "GET", "endpoint": "products", "status_code": 200, "remaining": 18, "retry_count": 0, "duration_ms": 142}
```

---

## Configuração Avançada

```python
from nuvemshop_sdk import NuvemshopClient
from nuvemshop_sdk.rate_limit import RateLimitManager

# Rate limit manager compartilhado entre múltiplas lojas
shared_rl = RateLimitManager()

client_loja_a = NuvemshopClient(
    store_id=111,
    access_token="token_a",
    rate_limit_manager=shared_rl,
    idempotency=True,
    max_retries=5,
    timeout=15,
)

client_loja_b = NuvemshopClient(
    store_id=222,
    access_token="token_b",
    rate_limit_manager=shared_rl,
)

# Métricas de rate limit
status = client_loja_a.rate_limit_status()
print(f"Requests: {status.total_requests}, Remaining: {status.remaining}")
```

---

## Estrutura do SDK

```
nuvemshop_sdk/
├── __init__.py          # Public exports
├── client.py            # NuvemshopClient — entry point
├── http_client.py       # HTTP transport + logging + idempotency
├── auth.py              # OAuth + Bearer headers
├── rate_limit.py        # Thread-safe per-store rate limiting
├── retry_policy.py      # Exponential backoff + jitter
├── exceptions.py        # Typed exceptions with JSON parsing
├── models/
│   ├── base.py          # Pydantic base (extra="allow")
│   ├── product.py       # Product model
│   ├── variant.py       # Variant model (stock, sku, price)
│   ├── order.py         # Order model
│   └── customer.py      # Customer model
├── resources/
│   ├── base.py          # ResourceCRUD + pagination
│   ├── products.py      # Model-enforced products
│   ├── variants.py      # Stock/price/sku operations
│   ├── inventory.py     # Safe inventory proxy
│   ├── orders.py        # Webhook-driven orders
│   ├── webhooks.py      # CRUD + signature verification
│   ├── customers.py     # Customer CRUD
│   └── stores.py        # Store info
└── utils/
    ├── pagination.py    # Lazy generator pagination
    └── webhook.py       # HMAC + replay protection
```
