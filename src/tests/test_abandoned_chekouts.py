from nuvemshop_client.client import NuvemshopClient
#from nuvemshop_client.resources.products import Products
client = NuvemshopClient(access_token='f1f4726c49ff3c65a69137cda413f9bfe5a24884', store_id='2686287')

cart_abandoned = client.abandoned_checkouts.list(per_page=1)
get_cart_abandoned = client.abandoned_checkouts.get(resource_id=1713033840)
#print(get_cart_abandoned)
aplication_cupom = client.abandoned_checkouts.post_cart_coupon(cart_id=1713033840, cupom_id=6891726)
print(aplication_cupom)