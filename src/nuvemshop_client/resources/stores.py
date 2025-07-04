# src/nuvemshop_client/resources/stores.py
from .base import ResourceCRUD

class Stores(ResourceCRUD):
    endpoint = "store"