# nuvemshop_sdk — Production-Grade SDK for the Nuvemshop API
#
# Usage:
#   from nuvemshop_sdk import NuvemshopClient
#
#   client = NuvemshopClient(
#       store_id=123,
#       access_token="your_token",
#   )
#   for product in client.products.iter_all():
#       print(product)

from .client import NuvemshopClient
from .exceptions import (
    NuvemshopError,
    UnauthorizedError,
    ForbiddenError,
    StoreInactiveError,
    RateLimitError,
    ValidationError,
    ServerError,
    NetworkError,
)
from .auth import NuvemshopAuth

__all__ = [
    "NuvemshopClient",
    "NuvemshopAuth",
    "NuvemshopError",
    "UnauthorizedError",
    "ForbiddenError",
    "StoreInactiveError",
    "RateLimitError",
    "ValidationError",
    "ServerError",
    "NetworkError",
]

__version__ = "1.0.0"
