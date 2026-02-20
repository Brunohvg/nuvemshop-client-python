# src/nuvemshop_sdk/resources/__init__.py
from .products import ProductsResource
from .variants import VariantsResource
from .orders import OrdersResource
from .inventory import InventoryResource
from .webhooks import WebhooksResource
from .customers import CustomersResource
from .stores import StoresResource

__all__ = [
    "ProductsResource",
    "VariantsResource",
    "OrdersResource",
    "InventoryResource",
    "WebhooksResource",
    "CustomersResource",
    "StoresResource",
]
