# src/nuvemshop_client/resources/products.py

from typing import Union
from .base import BaseResource

class Orders(BaseResource):
    def list(self, page: int = 1, limit: int = 50) -> Union[dict, list]:
        return self.client.get("orders/", params={"page": page, "limit": limit})

    def get(self, order_id: int) -> dict:
        return self.client.get(f"orders/{order_id}")

    def create(self, data: dict) -> dict:
        return self.client.post("orders", data=data)

    def update(self, order_id: int, data: dict) -> dict:
        return self.client.put(f"orders/{order_id}", data=data)

    def delete(self, order_id: int) -> None:
        self.client.delete(f"order/{order_id}")
