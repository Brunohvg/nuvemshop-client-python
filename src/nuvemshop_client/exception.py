class NuvemshopClientError(Exception):
    """Erro genérico da API da Nuvemshop."""
    pass

class NuvemshopClientAuthenticationError(NuvemshopClientError):
    """Erro de autenticação com a API da Nuvemshop."""
    pass

class NuvemshopClientNotFoundError(NuvemshopClientError):
    """Recurso não encontrado na API da Nuvemshop."""
    pass 
