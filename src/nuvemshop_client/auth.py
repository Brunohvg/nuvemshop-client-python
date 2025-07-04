import requests
from decouple import config
from .exception import NuvemshopClientAuthenticationError

# É uma boa prática carregar as variáveis uma vez e reutilizá-las.
CLIENT_ID = config("CLIENT_ID", default=None)
CLIENT_SECRET = config("CLIENT_SECRET", default=None)

def get_access_token(code: str) -> dict:
    """
    Troca um código de autorização por um access token na API da Nuvemshop/Tiendanube.

    Este é o segundo passo do fluxo de autorização OAuth 2.0.

    Args:
        code (str): O código de autorização recebido após o usuário autorizar a aplicação.

    Returns:
        dict: Um dicionário contendo 'access_token' e 'store_id' em caso de sucesso.
              Exemplo: {'store_id': 12345, 'access_token': 'xyz...', 'scope': 'read_products'}

    Raises:
        ValueError: Se CLIENT_ID ou CLIENT_SECRET não estiverem configurados.
        NuvemshopClientAuthenticationError: Se a API retornar um erro (ex: código inválido).
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("As variáveis de ambiente CLIENT_ID e CLIENT_SECRET são necessárias.")

    url = "https://www.tiendanube.com/apps/authorize/token"
    headers = {"Content-Type": "application/json"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        # Lança uma exceção para respostas com status de erro (4xx ou 5xx)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Captura o erro HTTP e o relança como uma exceção específica da nossa biblioteca
        # para manter a consistência.
        error_details = e.response.json().get("error_description", e.response.text)
        raise NuvemshopClientAuthenticationError(f"Falha ao obter o access token: {error_details}")
    except requests.exceptions.RequestException as e:
        # Erros de conexão, timeout, etc.
        raise NuvemshopClientAuthenticationError(f"Erro de conexão ao tentar obter o token: {e}")