# src/nuvemshop_client/client.py

import requests
from typing import Optional, Any
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
    API_URL_BASE = "https://api.nuvemshop.com.br"
    # URL para o fluxo de autenticação OAuth é diferente e fixa
    AUTH_URL_BASE = "https://www.tiendanube.com"

    def __init__(self,
                 store_id: int,
                 access_token: str,
                 api_version: str = "v1", # Ajustado para um valor mais comum como 'v1'
                 user_agent: str = "Nuvemshop Python Client (github.com/Brunohvg/nuvemshop-client-python)",
                 timeout: int = 30,
                 retries: int = 3):
        """
        Inicializa um cliente para interagir com uma loja JÁ AUTENTICADA.

        Args:
            store_id (int): O ID da loja do usuário (user_id).
            access_token (str): O token de acesso para autenticação.
            api_version (str, optional): A versão da API a ser usada.
            user_agent (str, optional): User-Agent para identificar sua aplicação.
            timeout (int, optional): Tempo máximo em segundos para esperar por uma resposta.
            retries (int, optional): Número de retentativas em caso de falhas específicas.
        """
        if not store_id or not access_token:
            raise ValueError("store_id e access_token são obrigatórios para instanciar o cliente.")

        self.store_id = store_id
        self.access_token = access_token
        self.api_version = api_version
        self.user_agent = user_agent
        self.timeout = timeout
        self.session = self._create_session(retries)

        # Factory de recursos
        self.products = Products(self)
        self.orders = Orders(self)
        self.customers = Customers(self)
        self.stores = Stores(self)
        self.abandoned_checkouts = AbandonedCheckouts(self)
        self.webhooks = Webhooks(self)

    @staticmethod
    def authenticate(client_id: str, client_secret: str, code: str) -> dict:
        """
        Método estático para o passo de autenticação OAuth 2.0.

        Troca um código de autorização por um access token. Por ser estático,
        pode ser chamado antes de ter uma instância do cliente.

        Exemplo de uso:
        credentials = NuvemshopClient.authenticate(
            client_id="seu_id",
            client_secret="seu_secret",
            code="codigo_recebido"
        )
        client = NuvemshopClient(
            store_id=credentials['store_id'],
            access_token=credentials['access_token']
        )

        Args:
            client_id (str): ID da sua aplicação Nuvemshop.
            client_secret (str): Segredo da sua aplicação Nuvemshop.
            code (str): O código de autorização temporário recebido pela Nuvemshop.

        Returns:
            dict: Um dicionário com 'store_id', 'access_token', e 'scope'.

        Raises:
            ValueError: Se client_id, client_secret ou code não forem fornecidos.
            NuvemshopClientAuthenticationError: Em caso de falha na autenticação com a API.
        """
        if not client_id or not client_secret or not code:
            raise ValueError("client_id, client_secret e code são obrigatórios para a autenticação.")

        url = f"{NuvemshopClient.AUTH_URL_BASE}/apps/authorize/token"
        headers = {"Content-Type": "application/json"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()  # Lança exceção para erros HTTP 4xx/5xx
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_details = "Detalhes do erro não puderam ser extraídos."
            try:
                error_details = e.response.json().get("error_description", e.response.text)
            except requests.exceptions.JSONDecodeError:
                error_details = e.response.text
            raise NuvemshopClientAuthenticationError(f"Falha ao obter o access token: {error_details}")
        except requests.exceptions.RequestException as e:
            raise NuvemshopClientAuthenticationError(f"Erro de conexão durante a autenticação: {e}")

    def _create_session(self, retries: int) -> requests.Session:
        """Cria uma sessão de requests com estratégia de retentativas."""
        session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _get_full_url(self, endpoint: str) -> str:
        """Monta a URL completa para um endpoint da API."""
        return f"{self.API_URL_BASE}/{self.api_version}/{self.store_id}/{endpoint}"

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
            return response.json() if response.status_code != 204 else {}

        try:
            error_data = response.json()
            error_message = error_data.get("message", "Sem detalhes adicionais.")
            error_description = error_data.get("description", response.text)
            error_detail = f"{error_message} - {error_description}"
        except requests.exceptions.JSONDecodeError:
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
            response = self.session.request(
                method, url, headers=headers, params=params, json=data, timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise NuvemshopClientError(f"Erro de conexão com a API: {e}")

    def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: dict) -> Any:
        return self._request("POST", endpoint, data=data)


    def put(self, endpoint: str, data: dict) -> Any:
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Any:
        return self._request("DELETE", endpoint)
