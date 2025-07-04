# 🧰 nuvemshop-client-python

Um cliente Python robusto e intuitivo para a [API da Nuvemshop (Tiendanube)](https://developers.nuvemshop.com.br/).

Desenvolvido para simplificar a criação de integrações, automações e SDKs, com foco em **organização**, **reuso** e **manutenção fácil**.

---

## 🚀 Funcionalidades

* ✅ **Cliente HTTP Resiliente**
  Requisições, autenticação e tratamento de erros automáticos, com suporte a timeouts e retentativas.

* ✅ **Paginação Automática**
  Busque todos os recursos com `.list_all()` sem precisar iterar páginas manualmente.

* ✅ **Fluxo de Autenticação OAuth 2.0**
  Módulo auxiliar para obter `access_token` e `store_id` de novas lojas.

* ✅ **Recursos Modulares**
  Operações da API organizadas por recursos: `Products`, `Orders`, `Customers`, etc.

* ✅ **Interface Fluida**
  Interaja naturalmente: `client.products.get()`, `client.orders.list()`, etc.

* ✅ **Estrutura Extensível**
  A classe `ResourceCRUD` permite criar novos recursos com 1 linha.

* ✅ **Instalável com pip**
  Empacotado com `pyproject.toml` para facilitar distribuição.

---

## 📦 Instalação

```bash
git clone https://github.com/Brunohvg/nuvemshop-client-python.git
cd nuvemshop-client-python
uv pip install -e .
```

> Usa `uv`? Perfeito, tudo funciona com ele. Também funciona com `pip` se preferir.

---

## ⚙️ Configuração

Crie um `.env` com suas credenciais da aplicação Nuvemshop:

```env
CLIENT_ID="SEU_CLIENT_ID"
CLIENT_SECRET="SEU_CLIENT_SECRET"
```

A lib usa `python-decouple` para carregar isso automaticamente.

---

## 🔐 Autenticação OAuth (passo 1)

Troque o `code` recebido pela Nuvemshop por um token de acesso:

```python
from nuvemshop_client.auth import get_access_token

credentials = get_access_token("codigo_recebido_pela_nuvemshop")
access_token = credentials.get("access_token")
store_id = credentials.get("store_id")
```

---

## 🔗 Usando o cliente (passo 2)

```python
from nuvemshop_client import NuvemshopClient

client = NuvemshopClient(
    store_id=store_id,
    access_token=access_token,
    timeout=45,  # opcional
    retries=5    # opcional
)

# Obter um produto
produto = client.products.get(12345)

# Buscar TODOS os pedidos (automaticamente paginado)
todos_pedidos = client.orders.list_all()
```

---

## ✨ Funcionalidades Avançadas

### 🔄 Paginação automática

```python
produtos = client.products.list_all(per_page=200)
print(f"Total de produtos: {len(produtos)}")
```

---

### 🛡 Resiliência

Parâmetros extras ao instanciar o client:

* `timeout`: tempo máximo de espera por resposta (padrão: 30s)
* `retries`: número de retentativas em caso de erro de rede, 429, 5xx (padrão: 3)

---

## 📚 Recursos Suportados

Cada um possui `.list()`, `.get()`, `.create()`, `.update()`, `.delete()` e `.list_all()`:

```python
client.products
client.orders
client.customers
client.abandoned_checkouts
client.webhooks
client.stores
```

---

## ⚠️ Tratamento de Erros

Use `try/except` com as exceções customizadas:

```python
from nuvemshop_client.exception import (
    NuvemshopClientError,
    NuvemshopClientNotFoundError
)

try:
    produto = client.products.get(99999999)
except NuvemshopClientNotFoundError:
    print("Produto não encontrado.")
except NuvemshopClientError as e:
    print(f"Erro ao acessar a API: {e}")
```

---

## 📄 Licença

MIT. Veja [LICENSE](./LICENSE) para mais detalhes.

---

Feito com 💚 por [Brunohvg](https://github.com/Brunohvg)
