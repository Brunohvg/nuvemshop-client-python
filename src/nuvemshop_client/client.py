# src/nuvemshop_client/client.py

import requests
from typing import Optional, Any
# Imports necessários para a lógica de retentativas
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .exception import (
    NuvemshopClientError,
    NuvemshopClientAuthenticationError,
    NuvemshopClientNotFoundError,
)

# Importações dos recursos
from .resources.products import Products
from .resources.orders import Orders
from .resources.customers import Customers
from .resources.stores import Stores
from .resources.abandoned_checkouts import AbandonedCheckouts
from .resources.webhooks import Webhooks


class NuvemshopClient:
    """
    Cliente principal para interagir com a API da Nuvemshop.
    Gerencia a autenticação, a construção de URLs e o tratamento de respostas HTTP.
    """
    URL_BASE = "https://api.nuvemshop.com.br"

    def __init__(self,
                 store_id: int,
                 access_token: str,
                 api_version: str = "2025-03",
                 user_agent: str = "Nuvemshop Python Client (contato@email.com)",
                 timeout: int = 30,
                 retries: int = 3):
        """
        Inicializa o cliente da Nuvemshop.

        Args:
            store_id (int): O ID da loja do usuário (user_id).
            access_token (str): O token de acesso para autenticação.
            api_version (str, optional): A versão da API a ser usada.
            user_agent (str, optional): User-Agent para identificar sua aplicação.
            timeout (int, optional): Tempo máximo em segundos para esperar por uma resposta.
            retries (int, optional): Número de retentativas em caso de falhas específicas.
        """
        if not store_id or not access_token:
            raise ValueError("store_id e access_token são obrigatórios.")

        self.store_id = store_id
        self.access_token = access_token
        self.api_version = api_version
        self.user_agent = user_agent
        self.timeout = timeout

        # --- INÍCIO DA LÓGICA DE RETENTATIVAS ---

        # 1. Criamos uma "sessão", que persiste informações entre requisições.
        self.session = requests.Session()

        # 2. Definimos a estratégia de retentativas.
        retry_strategy = Retry(
            total=retries,  # Número total de tentativas
            status_forcelist=[429, 500, 502, 503, 504],  # Códigos de erro que disparam a retentativa
            backoff_factor=1  # Tempo de espera entre tentativas (1s, 2s, 4s...)
        )

        # 3. Criamos um "adaptador" com a nossa estratégia.
        adapter = HTTPAdapter(max_retries=retry_strategy)

        # 4. Montamos o adaptador na sessão para todas as requisições HTTPS.
        self.session.mount("https://", adapter)

        # --- FIM DA LÓGICA DE RETENTATIVAS ---

        # Factory de recursos
        self.products = Products(self)
        self.orders = Orders(self)
        self.customers = Customers(self)
        self.stores = Stores(self)
        self.abandoned_checkouts = AbandonedCheckouts(self)
        self.webhooks = Webhooks(self)

    def _get_full_url(self, endpoint: str) -> str:
        """Monta a URL completa para um endpoint da API, incluindo a versão."""
        return f"{self.URL_BASE}/{self.api_version}/{self.store_id}/{endpoint}"

    def _get_headers(self) -> dict:
        """Monta os headers padrão para as requisições."""
        return {
            "Authentication": f"bearer {self.access_token}",
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: requests.Response) -> Any:
        """Trata a resposta da API, retornando os dados ou lançando uma exceção."""
        if response.ok:
            if response.status_code == 204: # No Content
                return {}
            try:
                return response.json()
            except ValueError:
                return response.content

        try:
            error_data = response.json()
            error_message = error_data.get("message", "Sem detalhes adicionais.")
            error_description = error_data.get("description", response.text)
            error_detail = f"{error_message} - {error_description}"
        except ValueError:
            error_detail = response.text

        if response.status_code == 401:
            raise NuvemshopClientAuthenticationError(f"Token de acesso inválido ou sem permissão. Detalhes: {error_detail}")
        elif response.status_code == 404:
            raise NuvemshopClientNotFoundError(f"Recurso não encontrado. Detalhes: {error_detail}")
        else:
            raise NuvemshopClientError(f"Erro na requisição: {response.status_code}. Detalhes: {error_detail}")

    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None) -> Any:
        """Método base para realizar todas as requisições HTTP."""
        url = self._get_full_url(endpoint)
        headers = self._get_headers()

        try:
            # **MUDANÇA PRINCIPAL AQUI**
            # Usamos a `self.session` em vez de `requests`
            # e adicionamos o `timeout`.
            response = self.session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise NuvemshopClientError(f"Erro de conexão com a API: {e}")

    def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """Executa uma requisição GET."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: dict) -> Any:
        """Executa uma requisição POST."""
        return self._request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: dict) -> Any:
        """Executa uma requisição PUT."""
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Any:
        """Executa uma requisição DELETE."""
        return self._request("DELETE", endpoint)