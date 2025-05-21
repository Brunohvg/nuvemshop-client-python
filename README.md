# 🧰 nuvemshop-client-python

Cliente Python simples e direto para a API da Nuvemshop.  
Feito para ser usado em integrações, scripts ou SDKs com foco em organização, reuso e fácil manutenção.

---

## 🚀 Funcionalidades

- ✅ Cliente HTTP com tratamento de erros e autenticação
- ✅ Recursos separados por módulo (`Products`, `Orders`, `Customers`)
- ✅ Factory embutida no client (`client.products.list()`, etc)
- ✅ Base genérica para criar novos recursos rapidamente
- ✅ Projeto modular com suporte a instalação via pip (`pip install -e .`)

---

## 📦 Instalação

```bash
git clone https://github.com/Brunohvg/nuvemshop-client-python.git
cd nuvemshop-client-python
pip install -e src
```

---

## 🔧 Como usar

```python
from nuvemshop_client import NuvemshopClient

client = NuvemshopClient("seu_store_id", "seu_token")

# Produtos
produtos = client.products.list()
produto = client.products.get(123)
client.products.create({"name": "Produto X"})

# Pedidos
pedidos = client.orders.list()

# Clientes
cliente = client.customers.get(456)
```

---

## 🧠 Organização do Código

```
src/nuvemshop_client/
├── client.py       # Classe principal que gerencia a autenticação e rotas
├── exception.py    # Erros customizados para tratar falhas de API
├── resources/
│   ├── base.py         # Classe base para todos os recursos
│   ├── products.py     # Métodos da API relacionados a produtos
│   ├── orders.py       # Métodos da API relacionados a pedidos
│   └── customers.py    # Métodos da API relacionados a clientes
```

---

## 📚 Recursos suportados

### Produtos (`client.products`)
- `.list(page=1, limit=50)`
- `.get(product_id)`
- `.create(data)`
- `.update(product_id, data)`
- `.delete(product_id)`

### Pedidos (`client.orders`)
- `.list(page=1, limit=50)`
- `.get(order_id)`

### Clientes (`client.customers`)
- `.list(page=1, limit=50)`
- `.get(customer_id)`

---

## ❗ Tratamento de erros

O client pode lançar essas exceções:

- `NuvemshopClientError`: erro genérico da API
- `NuvemshopClientAuthenticationError`: token inválido ou expirado
- `NuvemshopClientNotFoundError`: recurso não encontrado

Use `try/except` para capturar e tratar esses erros.

---

## 💡 Como criar novos recursos

Basta herdar de `BaseResource` e usar `self.client.get/post/put/delete(...)`.  
Exemplo:

```python
from .base import BaseResource

class MyResource(BaseResource):
    def list(self):
        return self.client.get("my-resource")
```

---

## 📜 Licença

MIT - Livre para usar, copiar, clonar, melhorar, quebrar e reconstruir.