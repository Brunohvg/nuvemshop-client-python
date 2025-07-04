# src/nuvemshop_client/resources/products.py

from .base import ResourceCRUD
from ..exception import NuvemshopClientError

class Products(ResourceCRUD):
    endpoint = "products"  # CORREÇÃO: O endpoint correto é "products"

    def get_by_sku(self, sku: str) -> dict:
        """
        Busca um produto específico pelo seu SKU.

        Args:
            sku (str): O SKU do produto a ser buscado.

        Returns:
            dict: O produto encontrado.

        Raises:
            NuvemshopClientError: Se o produto não for encontrado ou ocorrer outro erro.
        """
        try:
            # Constrói a URL para o endpoint específico de SKU
            return self.client.get(f"{self.endpoint}/sku/{sku}")
        except NuvemshopClientError as e:
            # Relança a exceção com um contexto mais específico
            raise NuvemshopClientError(f"Erro ao buscar produto com SKU '{sku}': {e}")