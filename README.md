
# 🧰 nuvemshop-client-python

Um cliente Python robusto e intuitivo para a API da Nuvemshop (Tiendanube).  
Desenvolvido para simplificar a criação de integrações, automações e SDKs, com foco em organização, reuso e manutenção fácil.

## 🚀 Funcionalidades

- ✅ **Cliente HTTP Resiliente**  
  Requisições, autenticação e tratamento de erros automáticos, com suporte a timeouts e retentativas.

- ✅ **Paginação Automática**  
  Busque todos os recursos com `.list_all()` sem precisar iterar páginas manualmente.

- ✅ **Fluxo de Autenticação OAuth 2.0 Simplificado**  
  Um método estático para obter `access_token` e `store_id` de novas lojas de forma clara e explícita.

- ✅ **Recursos Modulares**  
  Operações da API organizadas por recursos: Products, Orders, Customers, etc.

- ✅ **Interface Fluida**  
  Interaja naturalmente: `client.products.get()`, `client.orders.list()`, etc.

- ✅ **Estrutura Extensível**  
  A classe `ResourceCRUD` permite criar novos recursos com 1 linha.

- ✅ **Instalável com pip**  
  Empacotado com `pyproject.toml` para facilitar distribuição.

## 📦 Instalação

```bash
git clone https://github.com/Brunohvg/nuvemshop-client-python.git
cd nuvemshop-client-python
pip install -e .
```

Você também pode usar `uv` se preferir.

## ⚙️ Configuração e Autenticação

### Passo 1: Obter as Credenciais da Loja

Primeiro, você precisa trocar o code temporário (que a Nuvemshop envia para sua aplicação após o lojista autorizar) por um `access_token` e `store_id` permanentes.

```python
from nuvemshop_client import NuvemshopClient, NuvemshopClientAuthenticationError
import os

meu_client_id = os.getenv("CLIENT_ID")
meu_client_secret = os.getenv("CLIENT_SECRET")
codigo_recebido = "codigo_que_a_nuvemshop_enviou_para_minha_app"

try:
    credentials = NuvemshopClient.authenticate(
        client_id=meu_client_id,
        client_secret=meu_client_secret,
        code=codigo_recebido
    )

    access_token = credentials.get("access_token")
    store_id = credentials.get("store_id")

    print(f"Credenciais obtidas com sucesso para a loja ID: {store_id}")

except NuvemshopClientAuthenticationError as e:
    print(f"Ocorreu um erro durante a autenticação: {e}")
except ValueError as e:
    print(f"Erro de configuração: {e}")
```

### Passo 2: Usar o Cliente para Interagir com a Loja

```python
from nuvemshop_client import NuvemshopClient

client = NuvemshopClient(
    store_id=store_id,
    access_token=access_token,
    timeout=45,
    retries=5
)

produto = client.products.get(12345)
todos_pedidos = client.orders.list_all()
```

## ✨ Funcionalidades Avançadas

### 🔄 Paginação automática

```python
produtos = client.products.list_all(per_page=200)
print(f"Total de produtos encontrados: {len(produtos)}")
```

## 🛡 Resiliência

Parâmetros extras ao instanciar o cliente:

- `timeout`: tempo máximo de espera por resposta (padrão: 30s)
- `retries`: número de retentativas em caso de erro de rede, `429` ou `5xx` (padrão: 3)

## 📚 Recursos Suportados

Cada um possui métodos como `.list()`, `.get()`, `.create()`, `.update()`, `.delete()` e o auxiliar `.list_all()`:

- `client.products`
- `client.orders`
- `client.customers`
- `client.abandoned_checkouts`
- `client.webhooks`
- `client.stores`

## ⚠️ Tratamento de Erros

Use `try/except` com as exceções customizadas para tratar erros da API de forma granular:

```python
from nuvemshop_client.exception import (
    NuvemshopClientError,
    NuvemshopClientNotFoundError
)

try:
    produto = client.products.get(99999999)
except NuvemshopClientNotFoundError:
    print("O produto solicitado não foi encontrado.")
except NuvemshopClientError as e:
    print(f"Ocorreu um erro genérico ao acessar a API: {e}")
```

## 📄 Licença

MIT. Veja LICENSE para mais detalhes.  
Feito com 💚 por Brunohvg
