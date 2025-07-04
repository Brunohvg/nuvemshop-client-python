# src/nuvemshop_client/resources/base.py

from typing import Union, Any
from ..exception import NuvemshopClientError

class BaseResource:
    """Classe base que armazena a instância do cliente para os recursos."""
    def __init__(self, client: Any):
        self.client = client

class ResourceCRUD(BaseResource):
    """
    Classe genérica para recursos da API que suportam operações padrão (CRUD):
    list, get, create, update, delete.
    """
    endpoint: str = ""

    def list(self, page: int = 1, per_page: int = 20, **filters) -> Union[list, dict]:
        """
        Lista recursos da API com suporte a paginação e filtros.

        Raises:
            NuvemshopClientError: Se ocorrer um erro na chamada da API.
        """
        params = {"page": page, "per_page": per_page}
        params.update(filters)
        try:
            return self.client.get(self.endpoint, params=params)
        except NuvemshopClientError as e:
            # Relança a exceção com mais contexto para o método específico
            raise NuvemshopClientError(f"Erro ao listar recursos de '{self.endpoint}': {e}")
        
    def list_all(self, per_page: int = 100, **filters) -> list:
        """
        Lista todos os recursos de um endpoint, tratando a paginação automaticamente.

        Args:
            per_page (int, optional): Itens a serem buscados por requisição.
                                      Um valor maior (como 100 ou 200) é mais eficiente.
            **filters: Filtros a serem aplicados na busca.

        Returns:
            list: Uma lista única contendo todos os recursos encontrados.
        """
        all_resources = []
        page = 1
        while True:
            try:
                # Busca uma página de resultados
                response = self.list(page=page, per_page=per_page, **filters)
                if not response:
                    # Se a resposta estiver vazia, encerra o loop
                    break
                
                all_resources.extend(response)
                page += 1
            except NuvemshopClientError as e:
                # Se ocorrer um erro, lança a exceção para o usuário tratar
                raise NuvemshopClientError(f"Erro durante a paginação automática: {e}")
        
        return all_resources

    def get(self, resource_id: int) -> dict:
        """
        Busca um recurso específico pelo seu ID.

        Raises:
            NuvemshopClientError: Se o recurso não for encontrado ou ocorrer outro erro.
        """
        try:
            return self.client.get(f"{self.endpoint}/{resource_id}")
        except NuvemshopClientError as e:
            raise NuvemshopClientError(f"Erro ao buscar o recurso '{resource_id}' em '{self.endpoint}': {e}")

    def create(self, data: dict) -> dict:
        """
        Cria um novo recurso.

        Raises:
            NuvemshopClientError: Se ocorrer um erro durante a criação.
        """
        try:
            return self.client.post(self.endpoint, data=data)
        except NuvemshopClientError as e:
            raise NuvemshopClientError(f"Erro ao criar recurso em '{self.endpoint}': {e}")

    def update(self, resource_id: int, data: dict) -> dict:
        """
        Atualiza um recurso existente.

        Raises:
            NuvemshopClientError: Se ocorrer um erro durante a atualização.
        """
        try:
            return self.client.put(f"{self.endpoint}/{resource_id}", data=data)
        except NuvemshopClientError as e:
            raise NuvemshopClientError(f"Erro ao atualizar recurso '{resource_id}' em '{self.endpoint}': {e}")

    def delete(self, resource_id: int) -> dict:
        """
        Deleta um recurso existente.

        Raises:
            NuvemshopClientError: Se ocorrer um erro durante a deleção.
        """
        try:
            # O retorno aqui pode ser um dicionário vazio em caso de sucesso (status 204)
            return self.client.delete(f"{self.endpoint}/{resource_id}")
        except NuvemshopClientError as e:
            raise NuvemshopClientError(f"Erro ao deletar recurso '{resource_id}' em '{self.endpoint}': {e}")