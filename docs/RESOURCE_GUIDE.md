# Guia de Recursos e Modelos

Cada recurso no SDK (`client.products`, `client.orders`, etc.) fornece métodos para interagir com a API Nuvemshop.

## Produtos (`client.products`)

| Método | Retorno | Descrição |
|--------|---------|-------------|
| `get(id)` | `dict` | Busca um produto pelo ID. |
| `list(page, per_page)` | `list[dict]` | Lista uma página de produtos. |
| `iter_all()` | `Generator` | Itera por todos os produtos (lazy). |
| `create(data)` | `dict` | Cria um novo produto. |
| `update(id, data)` | `dict` | Atualização total (PUT). |
| `delete(id)` | `dict` | Remove o produto. |

### Exemplo de Criação de Produto

```python
new_product = client.products.create({
    "name": "Camiseta Geek",
    "description": "Uma camiseta incrível.",
    "variants": [
        {"price": "59.90", "stock": 100, "sku": "GEO-001"}
    ]
})
```

## Variantes (`client.variants`)

Variantes são sub-itens de produtos (tamanhos, cores). **Estoque e preço são sempre gerenciados aqui.**

```python
# Atualizar apenas o estoque de uma variante
client.variants.update_stock(product_id=123, variant_id=456, stock=50)

# Atualizar o preço
client.variants.update_price(product_id=123, variant_id=456, price="69.90")
```

## Estoque (`client.inventory`)

O `InventoryResource` é um proxy simplificado para operações de estoque.

```python
# Listar todos os estoques de um produto
stocks = client.inventory.list_all(product_id=123)

# Definir estoque absoluto
client.inventory.set_stock(product_id=123, variant_id=456, stock=100)
```

## Pedidos (`client.orders`)

O SDK recomenda uma abordagem focada em webhooks para pedidos, mas permite consulta direta.

```python
order = client.orders.get(789)
print(f"Status do pedido: {order['status']}")
```

## Webhooks (`client.webhooks`)

Permite que seu sistema seja notificado em tempo real sobre eventos.

```python
# Criar um novo webhook
client.webhooks.create({
    "url": "https://seu-dominio.com/webhook",
    "event": "order/created"
})

# Listar webhooks ativos
all_webhooks = client.webhooks.get_all()
```

## Modelos Pydantic

Internamente, os recursos usam modelos Pydantic localizados em `src/nuvemshop_sdk/models/`. Embora os métodos retornem `dict` por conveniência, os dados são validados contra estes modelos:

- `ProductModel`: Valida campos de nome, descrição, marcas e variantes relacionadas.
- `VariantModel`: Valida preço, estoque e SKUs.
- `OrderModel`: Valida status de pagamento, envio e itens.
- `CustomerModel`: Valida emails e endereços.
