from nuvemshop_client.client import NuvemshopClient
#from nuvemshop_client.resources.products import Products
client = NuvemshopClient(access_token='f1f4726c49ff3c65a69137cda413f9bfe5a24884', store_id='2686287')

print(client.webhooks.list())
"""print(client.webhooks.create(data={
  "event": "product/created",
  "url": "https://myapp.com/product_created_hook"
}))"""
#print(client.webhooks.delete(28575368))