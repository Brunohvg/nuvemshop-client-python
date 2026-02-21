# src/nuvemshop_sdk/client.py
"""
NuvemshopClient — Main entry point for the Nuvemshop SDK.

Each client instance is **isolated per store**.

Usage::

    from nuvemshop_sdk import NuvemshopClient

    client = NuvemshopClient(
        store_id=123,
        access_token="your_permanent_token",
        timeout=10,
        environment="production",
    )

    # Products (variant-first model enforced)
    for product in client.products.iter_all():
        print(product["name"])

    # Inventory (variant-level only)
    client.inventory.set_stock(product_id=1, variant_id=2, stock=50)

    # Orders (webhook-first design)
    order = client.orders.get(789)

    # Rate-limit status
    status = client.rate_limit_status()
"""

from __future__ import annotations

import logging
from typing import Optional

from .auth import API_VERSION, Environment
from .http_client import HttpClient, IdempotencyPolicy, StructuredJsonFormatter
from .rate_limit import RateLimitManager, RateLimitStatus
from .resources.base import BaseResource
from .resources.categories import CategoriesResource
from .resources.coupons import CouponsResource
from .resources.customers import CustomersResource
from .resources.discounts import DiscountsResource
from .resources.inventory import InventoryResource
from .resources.metafields import MetafieldsResource
from .resources.orders import OrdersResource
from .resources.products import ProductsResource
from .resources.stores import StoresResource
from .resources.variants import VariantsResource
from .resources.webhooks import WebhooksResource
from .retry_policy import RetryPolicy

logger = logging.getLogger("nuvemshop_sdk")


class NuvemshopClient:
    """
    Cliente profissional para a API REST da Nuvemshop.

    Esta classe serve como o ponto de entrada principal para interagir com a API.
    Cada instância é isolada e thread-safe, permitindo o uso simultâneo para
    diferentes lojas.

    Attributes:
        products (ProductsResource): Operações de CRUD e modelos de produtos.
        variants (VariantsResource): Gestão de variantes, preços e estoque.
        categories (CategoriesResource): Gestão de categorias de produtos.
        coupons (CouponsResource): Gestão de cupons de desconto.
        discounts (DiscountsResource): Gestão de descontos da loja.
        orders (OrdersResource): Consulta e gestão de pedidos.
        customers (CustomersResource): Gestão de clientes da loja.
        webhooks (WebhooksResource): Criação e listagem de notificações.
        stores (StoresResource): Informações gerais da loja autenticada.
        inventory (InventoryResource): Proxy especializado para controle de estoque.
        metafields (MetafieldsResource): Gestão de metadados customizados.

    Args:
        store_id (int): ID da loja Nuvemshop.
        access_token (str): Token de acesso permanente (OAuth).
        api_version (str): Versão da API (padrão "v1").
        base_url (str, optional): URL base customizada para testes.
        environment (str): "production" ou "sandbox".
        user_agent (str, optional): User-Agent customizado.
        timeout (int): Timeout da requisição em segundos (padrão 10).
        max_retries (int): Número máximo de tentativas em caso de falha (padrão 3).
        idempotency (bool): Se True, envia Idempotency-Key automaticamente em POSTs.
        rate_limit_manager (RateLimitManager, optional): Gerenciador compartilhado de limites.
        debug (bool): Se True, habilita logs JSON estruturados em nível DEBUG.
    """

    def __init__(
        self,
        store_id: int,
        access_token: str,
        *,
        api_version: str = API_VERSION,
        base_url: Optional[str] = None,
        environment: str = "production",
        user_agent: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
        idempotency: bool = False,
        rate_limit_manager: Optional[RateLimitManager] = None,
        debug: bool = False,
    ) -> None:
        if not store_id or not access_token:
            raise ValueError(
                "store_id and access_token are required to create a client."
            )

        self.store_id = store_id
        self.access_token = access_token

        # Resolve environment
        env = Environment(environment)

        # Optional: attach structured JSON logging
        if debug:
            self._setup_debug_logging()

        # Shared rate-limit manager (allows multi-store isolation)
        self._rate_limit_manager = rate_limit_manager or RateLimitManager()

        # HTTP transport
        self._http = HttpClient(
            store_id=store_id,
            access_token=access_token,
            api_version=api_version,
            base_url=base_url,
            environment=env,
            user_agent=user_agent,
            timeout=timeout,
            rate_limit_manager=self._rate_limit_manager,
            retry_policy=RetryPolicy(max_retries=max_retries),
            idempotency_policy=IdempotencyPolicy(enabled=idempotency),
        )

        # Resource layer
        self.products = ProductsResource(self._http)
        self.variants = VariantsResource(self._http)
        self.categories = CategoriesResource(self._http)
        self.coupons = CouponsResource(self._http)
        self.discounts = DiscountsResource(self._http)
        self.orders = OrdersResource(self._http)
        self.customers = CustomersResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.stores = StoresResource(self._http)

        # Inventory is a safe proxy over variants
        self.inventory = InventoryResource(self.variants)
        self.metafields = MetafieldsResource(self._http)

    # ------------------------------------------------------------------
    # Rate-limit metrics
    # ------------------------------------------------------------------

    def rate_limit_status(self) -> RateLimitStatus:
        """Return the current rate-limit state for this store."""
        return self._rate_limit_manager.get_status(
            self.store_id, self.access_token,
        )

    # ------------------------------------------------------------------
    # Debug logging
    # ------------------------------------------------------------------

    @staticmethod
    def _setup_debug_logging() -> None:
        """Attach a JSON formatter to the SDK logger hierarchy."""
        sdk_logger = logging.getLogger("nuvemshop_sdk")
        if not sdk_logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(StructuredJsonFormatter())
            sdk_logger.addHandler(handler)
        sdk_logger.setLevel(logging.DEBUG)

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"NuvemshopClient(store_id={self.store_id}, "
            f"api_version={self._http.api_version!r})"
        )
