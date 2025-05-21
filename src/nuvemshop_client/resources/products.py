# src/nuvemshop_client/resources/products.py

from .base import ResourceCRUD

class Products(ResourceCRUD):
    endpoint = "products"
    
    def get_by_sku(self, sku: str) -> dict:
        return self.client.get(f"{self.endpoint}/sku/{sku}")