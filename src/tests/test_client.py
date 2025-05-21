from decouple import config
from nuvemshop_client.client import NuvemshopClient
#from nuvemshop_client.resources.products import Products
client = NuvemshopClient(access_token=config('ACCESS_TOKEN'), store_id=config("STORE_ID"))

# Produtos
#print(client.products.list())
#print(client.products.get(148710932))
#print(client.products.delete(148710932))
#print(client.orders.list())
pedidos = client.orders.get(1695438851)
name = pedidos.get('customer', '').get('name', '')
print(name)

