
from nuvemshop_client.client import NuvemshopClient
#from nuvemshop_client.resources.products import Products
client = NuvemshopClient(access_token='f1f4726c49ff3c65a69137cda413f9bfe5a24884', store_id='2686287')

# Produtos
#print(client.products.list())
#print(client.products.get_by_sku('PS000123'))
#print(client.products.delete(148710932))
#print(client.orders.list())
#pedidos = client.orders.get(1695438851, )
#name = pedidos.get('customer', '').get('name', '')
#print(name)

#customers = client.abandoned_checkouts.list(page=1)
#print(customers)

#print(client.abandoned_checkouts.get_cart_cupom(cart_id=1711369253, data={"coupon_id": 6891726}))

cupon_create = client.abandoned_checkouts.pos_cart_cupom(cart_id=1709806012,cupom_id=6891726,)
url_cart = cupon_create.get('abandoned_checkout_url', "")
print(cupon_create)
print(f'Aqui esta a url do carrinho com o cupom: {url_cart}')
