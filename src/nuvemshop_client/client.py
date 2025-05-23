# src/nuvemshop_client/client.py

import requests
from .exception import (
    NuvemshopClientError,
    NuvemshopClientAuthenticationError,
    NuvemshopClientNotFoundError,
)

from .resources.products import Products
from .resources.orders import Orders
from .resources.customers import Customers
from .resources.stores import Stores
from .resources.abandoned_checkouts import AbandonedCheckouts
from .resources.webhooks import Webhooks
class NuvemshopClient:
    URL_BASE = "https://api.nuvemshop.com.br/2025-03/"

    def __init__(self, store_id, access_token):
        self.store_id = store_id
        self.access_token = access_token

        # Factory de recursos
        self.products = Products(self)
        self.orders = Orders(self)
        self.customers = Customers(self)
        self.stores = Stores(self)
        self.abandoned_checkouts = AbandonedCheckouts(self)
        self.webhooks = Webhooks(self)
    
    def _get_headers(self, token=None):
        token = token or self.access_token
        return {
            "Authentication": f"bearer {token}",
            "User-Agent": "CloudStore (cloudstore@email.com)",
            "Content-Type": "application/json",
        }


    def _get_full_url(self, endpoint):
        return f"{self.URL_BASE}{self.store_id}/{endpoint}"

    def _handle_response(self, response):
        if response.status_code == 401:
            raise NuvemshopClientAuthenticationError("Token de acesso inválido.")
        elif response.status_code == 404:
            raise NuvemshopClientNotFoundError("ESTOU AQUI NESSE ERRO Recurso não encontrado.")
        elif response.ok:
            try:
                return response.json()
            except ValueError:
                return response.content
        else:
            try:
                error_detail = f" - {response.json()}"
            except ValueError:
                error_detail = f" - {response.text}"
            raise NuvemshopClientError(f"Erro na requisição: {response.status_code}{error_detail}")

    def get(self, endpoint, token=None, params=None):
        url = self._get_full_url(endpoint)
        response = requests.get(url, headers=self._get_headers(token), params=params)
        return self._handle_response(response)

    def post(self, endpoint, data, token=None):
        url = self._get_full_url(endpoint)
        response = requests.post(url, headers=self._get_headers(token), json=data)
        return self._handle_response(response)

    def put(self, endpoint, data, token=None):
        url = self._get_full_url(endpoint)
        response = requests.put(url, headers=self._get_headers(token), json=data)
        return self._handle_response(response)

    def delete(self, endpoint, token=None):
        url = self._get_full_url(endpoint)
        response = requests.delete(url, headers=self._get_headers(token))
        return self._handle_response(response)
