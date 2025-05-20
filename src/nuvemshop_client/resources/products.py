# src/nuvemshop_client/resources/products.py

class Products:
    def __init__(self, client, store_id: int):
        self.client = client
        self.store_id = store_id

    def list(self, page: int = 1, limit: int = 50) -> dict:
        path = f'/stores/{self.store_id}/products'
        return self.client.get(path, params={'page': page, 'limit': limit})

    def get(self, product_id: int) -> dict:
        path = f'/stores/{self.store_id}/products/{product_id}'
        return self.client.get(path)

    def create(self, data: dict) -> dict:
        path = f'/stores/{self.store_id}/products'
        return self.client.post(path, data=data)

    def update(self, product_id: int, data: dict) -> dict:
        path = f'/stores/{self.store_id}/products/{product_id}'
        return self.client.put(path, data=data)

    def delete(self, product_id: int) -> None:
        path = f'/stores/{self.store_id}/products/{product_id}'
        self.client.delete(path)
