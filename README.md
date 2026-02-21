# Nuvemshop SDK — Python

SDK Python profissional, robusto e amigável para a API da Nuvemshop (Tiendanube).  
**Rate-limit safe · Idempotent · Production-ready.**

---

## ⚡ Instalação

```bash
pip install nuvemshop-sdk
```

## 🚀 Início Rápido (Quick Start)

```python
from nuvemshop_sdk import NuvemshopClient

# Inicialize o cliente por loja
client = NuvemshopClient(
    store_id=123456,
    access_token="seu_token_permanente",
)

# Listar produtos (paginação lazy automática)
for product in client.products.iter_all():
    print(f"Produto: {product['name']}")

# Atualizar estoque (sempre via variante!)
client.inventory.set_stock(product_id=1, variant_id=2, stock=50)
```

## 📚 Documentação Completa

Para detalhes avançados, consulte nossos guias técnicos:

- [**Guia de Autenticação**](./docs/AUTHENTICATION.md): Fluxo OAuth, tokens e segurança.
- [**Recursos e Modelos**](./docs/RESOURCE_GUIDE.md): Detalhes de Produtos, Pedidos, Variantes, etc.
- [**Tratamento de Exceções**](./docs/EXCEPTIONS.md): Como lidar com erros de validação e rate limit.
- [**Arquitetura Interna**](./docs/ARCHITECTURE.md): Design do SDK, thread-safety e resiliência.

## 🛠 Exemplos Práticos

Confira a pasta [`examples/`](./examples/) para scripts prontos para uso:
- [Fluxo de Autenticação OAuth](./examples/oauth_flow.py)
- [Hander de Webhooks com FastAPI](./examples/webhook_handler.py)

---

## 💎 Garantias do SDK

O SDK foi construído para ser o mais confiável possível em ambientes de produção:

- ✅ **Resiliência a Rate-Limit**: Espera automática preemptiva e reativa (429). Thread-safe por loja.
- ✅ **Idempotência Automática**: Envio de `Idempotency-Key` em requisições POST para evitar duplicatas em retries.
- ✅ **Variant-First Inventory**: Bloqueia atualizações de estoque no nível do produto, forçando o uso correto da API.
- ✅ **Logging JSON**: Pronto para Datadog/CloudWatch/ELK, com `store_id`, durações e status.
- ✅ **Compatibilidade Futura**: Modelos Pydantic que aceitam campos novos sem quebrar (`extra="allow"`).

---

## Contribuindo

Pull requests são bem-vindos! Para mudanças maiores, abra uma issue primeiro.

## License

MIT © [Sua Empresa/Seu Nome]
