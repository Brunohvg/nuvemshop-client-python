# src/nuvemshop_client/client.py

import requests

class NuvemshopClient:
    BASE_URL = 'https://api.nuvemshop.com.br'

    def __init__(self, access_token: str):
        self.token = access_token

    def _headers(self) -> dict:
        return {
            'Authentication': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def get(self, path: str, params: dict = None) -> dict:
        resp = requests.get(f'{self.BASE_URL}{path}', headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, data: dict) -> dict:
        resp = requests.post(f'{self.BASE_URL}{path}', headers=self._headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    def put(self, path: str, data: dict) -> dict:
        resp = requests.put(f'{self.BASE_URL}{path}', headers=self._headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    def delete(self, path: str) -> None:
        resp = requests.delete(f'{self.BASE_URL}{path}', headers=self._headers())
        resp.raise_for_status()
