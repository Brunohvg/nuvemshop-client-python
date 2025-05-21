# src/nuvemshop_client/resources/orders.py

from .base import ResourceCRUD

class Orders(ResourceCRUD):
    endpoint = "orders"
