# src/nuvemshop_client/resources/products.py

from typing import Union
from .base import BaseResource

class Products(BaseResource):
    def list(self, page: int = 1, limit: int = 50) -> Union[dict, list]:
        return self.client.get("products", params={"page": page, "limit": limit})

    def get(self, product_id: int) -> dict:
        return self.client.get(f"products/{product_id}")

    def create(self, data: dict) -> dict:
        return self.client.post("products", data=data)

    def update(self, product_id: int, data: dict) -> dict:
        return self.client.put(f"products/{product_id}", data=data)

    def delete(self, product_id: int) -> None:
        self.client.delete(f"products/{product_id}")
