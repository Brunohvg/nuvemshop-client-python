# Autenticação e OAuth

A Nuvemshop utiliza o protocolo OAuth 2.0 para autorização. Este guia explica como gerenciar tokens usando o SDK.

## Conceitos Fundamentais

1.  **Tokens Permanentes**: Após a troca bem-sucedida do `code`, a Nuvemshop fornece um `access_token` que **não expira**. Não existe fluxo de "Refresh Token".
2.  **Escopos (Scopes)**: Definem o que seu app pode acessar (ex: `read_products`, `write_orders`). Eles são definidos na configuração do seu app no painel de parceiros da Nuvemshop.

## Fluxo de Autenticação

O SDK facilita a troca do código de autorização pelo token permanente.

```python
from nuvemshop_sdk import NuvemshopAuth, NuvemshopClient

# 1. Trocar o 'code' recebido no redirect do seu app pelo token permanente
creds = NuvemshopAuth.exchange_code(
    client_id="seu_client_id",
    client_secret="seu_client_secret",
    code="código_recebido_da_nuvemshop",
)

print(f"Store ID: {creds.store_id}")
print(f"Access Token: {creds.access_token}")

# 2. Inicializar o cliente com as novas credenciais
client = NuvemshopClient(
    store_id=creds.store_id,
    access_token=creds.access_token,
)
```

## Cabeçalhos de Autenticação

O SDK gerencia automaticamente os cabeçalhos necessários em cada requisição:
- `Authentication: Bearer <token>`
- `User-Agent`: Inclui informações da versão do SDK e do Python para ajudar no suporte técnico.

## Segurança

> [!IMPORTANT]
> Nunca armazene o `client_secret` ou tokens de acesso em repositórios públicos. Use variáveis de ambiente.

```python
import os
from nuvemshop_sdk import NuvemshopClient

client = NuvemshopClient(
    store_id=int(os.environ["NUVEMSHOP_STORE_ID"]),
    access_token=os.environ["NUVEMSHOP_ACCESS_TOKEN"],
)
```
