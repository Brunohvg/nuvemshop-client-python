# Tratamento de Exceções

O SDK Nuvemshop possui uma hierarquia de exceções tipadas para que você possa reagir de forma granular a diferentes erros da API.

## Hierarquia de Exceções

```plaintext
NuvemshopError (Base)
├── UnauthorizedError (401)
├── StoreInactiveError (402)
├── ForbiddenError (403)
├── ValidationError (422)
├── RateLimitError (429)
├── ServerError (5xx)
└── NetworkError (Erros de conexão/timeout)
```

## Capturando Erros de Validação (422)

Quando a API retorna um erro de validação, o SDK expõe o dicionário de erros detalhado no atributo `errors`.

```python
from nuvemshop_sdk import ValidationError

try:
    client.products.create({"name": ""})  # Nome vazio é inválido
except ValidationError as e:
    print(f"Erro: {e.error_description}")
    # e.errors conterá detalhes como {"name": ["is required"]}
    for field, messages in e.errors.items():
        print(f"Campo {field}: {', '.join(messages)}")
```

## Gerenciando Rate Limit (429)

O SDK lida com rate limits automaticamente, mas se o limite for atingido mesmo após os retries configurados, um `RateLimitError` será lançado.

```python
from nuvemshop_sdk import RateLimitError

try:
    # Muitas requisições pesadas simultâneas
    ...
except RateLimitError as e:
    print(f"Limite atingido. Tente novamente em {e.retry_after} segundos.")
```

## Erros de Rede e Retries

O SDK diferencia erros de "negócio" (ex: 401, 403, 422) de erros de "transporte" (ex: timeout, DNS).
- Erros de transporte e 5xx são **retentados automaticamente** conforme sua configuração de `max_retries`.
- Se mesmo assim falharem, um `NetworkError` ou `ServerError` é lançado.

## Práticas Recomendadas

Sempre use blocos `try/except` ao redor de chamadas que afetam o faturamento ou estoque para lidar com `StoreInactiveError` (402).

```python
from nuvemshop_sdk import StoreInactiveError

try:
    client.inventory.set_stock(product_id=1, variant_id=2, stock=10)
except StoreInactiveError:
    # Lógica para avisar o usuário que a loja dele está inativa na Nuvemshop
    ...
```
