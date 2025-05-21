
from nuvemshop_client.client import NuvemshopClient
#from nuvemshop_client.resources.products import Products
client = NuvemshopClient(access_token='f1f4726c49ff3c65a69137cda413f9bfe5a24884', store_id='2686287')

# Produtos
#print(client.products.list())
print(client.products.get_by_sku('PS000123'))
#print(client.products.delete(148710932))
#print(client.orders.list())
#pedidos = client.orders.get(1695438851, )
#name = pedidos.get('customer', '').get('name', '')
#print(name)

#customers = client.abandoned_checkouts.list(page=1)
#print(customers)