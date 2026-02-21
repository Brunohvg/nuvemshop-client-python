"""
Exemplo de autenticação OAuth com a Nuvemshop.

Este script demonstra como trocar o 'code' recebido após o redirecionamento
do usuário pelo token de acesso permanente.
"""

import os
from nuvemshop_sdk import NuvemshopAuth, NuvemshopClient

# Substitua por suas credenciais do painel de parceiros Nuvemshop
CLIENT_ID = os.environ.get("NUVEMSHOP_CLIENT_ID", "seu_id")
CLIENT_SECRET = os.environ.get("NUVEMSHOP_CLIENT_SECRET", "seu_secret")

def main():
    # 1. O 'code' é enviado pela Nuvemshop para a sua URL de redirect
    # como um parâmetro query (?code=xxxxx)
    auth_code = "código_recebido_na_querystring"

    print("--- Iniciando troca de Token ---")
    
    try:
        # 2. Troca o código pelo token permanente
        creds = NuvemshopAuth.exchange_code(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            code=auth_code,
        )

        print(f"Sucesso!")
        print(f"Store ID: {creds.store_id}")
        print(f"Access Token: {creds.access_token}")

        # 3. Agora você pode usar o token para criar um cliente
        client = NuvemshopClient(
            store_id=creds.store_id,
            access_token=creds.access_token,
        )
        
        # Testar conexão
        shop_info = client.stores.get()
        print(f"Conectado à loja: {shop_info['name']}")

    except Exception as e:
        print(f"Erro na autenticação: {e}")

if __name__ == "__main__":
    main()
