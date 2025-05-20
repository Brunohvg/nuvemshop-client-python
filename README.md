Resumo
Este projeto fornece um client em Python para a API da Nuvemshop, com classes separadas por recurso (produtos, pedidos, clientes etc.). Ele é empacotado via PEP 621 em pyproject.toml para facilitar instalação via PyPI ou diretamente do GitHub. Todos os métodos retornam JSON nativo do serviço e lançam exceções claras em caso de erro.

Índice
Funcionalidades

Pré-requisitos

Instalação

Estrutura do Projeto

Configuração

Uso

Client Principal

Recurso Products

Recurso Orders

Recurso Customers

Empacotamento & Publicação

Contribuição

Licença

Funcionalidades
Autenticação via Bearer Token (OAuth2) 
Nuvemshop DevHub

Endpoints principais: Products, Orders, Customers 
Tiendanube

Paginação automática de listagens

Tratamento de erros com requests.exceptions.HTTPError

Compatível com Python ≥3.7

Pré-requisitos
Python 3.7 ou superior

requests para chamadas HTTP 
GitHub

Instalação
Via PyPI (após publicação):

bash
Copiar
Editar
pip install nuvemshop-client
Via GitHub (versão de desenvolvimento):

bash
Copiar
Editar
pip install git+https://github.com/seunome/nuvemshop-client.git@main
Estrutura do Projeto
css
Copiar
Editar
nuvemshop-client/
├── src/
│   └── nuvemshop_client/
│       ├── __init__.py
│       ├── client.py
│       └── resources/
│           ├── products.py
│           ├── orders.py
│           └── customers.py
├── tests/
│   └── test_client.py
├── pyproject.toml
└── README.md
A configuração em pyproject.toml segue a especificação PEP 621 
Python Enhancement Proposals (PEPs)
packaging.python.org
.

Configuração
Crie um app na Nuvemshop Partners e obtenha seu access_token e store_id 
Tiendanube
.

bash
Copiar
Editar
# Exemplo de variáveis de ambiente
export NUVEMSHOP_TOKEN="seu_token_aqui"
export NUVEMSHOP_STORE_ID=123456
Uso
Client Principal
python
Copiar
Editar
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
O client básico encapsula GET, POST, PUT e DELETE com tratamento de erros claro 
GitHub
.

Recurso Products
python
Copiar
Editar
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
Uso ilustrativo:

python
Copiar
Editar
from nuvemshop_client.client import NuvemshopClient
from nuvemshop_client.resources.products import Products

client = NuvemshopClient("TOKEN")
products = Products(client, 123456)
print(products.list(limit=10))
``` :contentReference[oaicite:6]{index=6}

### Recurso Orders  
```python
# src/nuvemshop_client/resources/orders.py

class Orders:
    def __init__(self, client, store_id: int):
        self.client = client
        self.store_id = store_id

    def list(self, status: str = None, page: int = 1, limit: int = 50) -> dict:
        params = {'page': page, 'limit': limit}
        if status:
            params['status'] = status
        return self.client.get(f'/stores/{self.store_id}/orders', params=params)

    def get(self, order_id: int) -> dict:
        return self.client.get(f'/stores/{self.store_id}/orders/{order_id}')

    def update(self, order_id: int, data: dict) -> dict:
        return self.client.put(f'/stores/{self.store_id}/orders/{order_id}', data=data)
``` :contentReference[oaicite:7]{index=7}

### Recurso Customers  
```python
# src/nuvemshop_client/resources/customers.py

class Customers:
    def __init__(self, client, store_id: int):
        self.client = client
        self.store_id = store_id

    def list(self, page: int = 1, limit: int = 50) -> dict:
        return self.client.get(f'/stores/{self.store_id}/customers', params={'page': page, 'limit': limit})

    def get(self, customer_id: int) -> dict:
        return self.client.get(f'/stores/{self.store_id}/customers/{customer_id}')

    def create(self, data: dict) -> dict:
        return self.client.post(f'/stores/{self.store_id}/customers', data=data)
``` :contentReference[oaicite:8]{index=8}

## Empacotamento & Publicação  
1. **Configurar** `pyproject.toml` segundo PEP 621:  
   ```toml
   [build-system]
   requires = ["setuptools", "wheel"]
   build-backend = "setuptools.build_meta"

   [project]
   name = "nuvemshop-client"
   version = "0.1.0"
   description = "Client Python para a API da Nuvemshop"
   authors = [{ name = "Seu Nome", email = "seu@email.com" }]
   dependencies = ["requests>=2.25"]
   ``` :contentReference[oaicite:9]{index=9}  
2. **Construir** pacote:  
   ```bash
   python -m pip install --upgrade pip setuptools wheel  # pacotes atualizados 
   python -m build
Publicar no PyPI:

bash
Copiar
Editar
python -m pip install twine
python -m twine upload dist/*
Contribuição
Fork no GitHub

Branch com feature/bugfix

PR explicando mudanças

Aprovado, merge e release semântico

Licença
MIT © Seu Nome — consulte o LICENSE para detalhes.