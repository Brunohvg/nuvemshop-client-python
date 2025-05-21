# src/nuvemshop_client/resources/base.py

from typing import Union

class BaseResource:
    def __init__(self, client):
        self.client = client


class ResourceCRUD(BaseResource):
    """
    Classe genérica para recursos com operações padrão: list, get, create, update, delete.
    """
    endpoint: str = ""

    def list(self, page: int = 1, limit: int = 50) -> Union[dict, list]:
        return self.client.get(self.endpoint, params={"page": page, "limit": limit})

    def get(self, resource_id: int) -> dict:
        return self.client.get(f"{self.endpoint}/{resource_id}")

    def create(self, data: dict) -> dict:
        return self.client.post(self.endpoint, data=data)

    def update(self, resource_id: int, data: dict) -> dict:
        return self.client.put(f"{self.endpoint}/{resource_id}", data=data)

    def delete(self, resource_id: int) -> None:
        self.client.delete(f"{self.endpoint}/{resource_id}")