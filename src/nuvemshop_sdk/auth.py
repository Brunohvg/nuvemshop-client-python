# src/nuvemshop_sdk/auth.py
"""
Authentication module for the Nuvemshop SDK.

Responsibilities:
  - OAuth code → access_token exchange
  - Access token persistence per store_id
  - API version configuration
  - Environment switching (production / sandbox)
  - Standardized User-Agent header

Important Nuvemshop Model Rule:
  OAuth tokens are **permanent** — there is no refresh flow.
  Tokens must be stored per store_id by the calling application.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import requests

from .exceptions import NuvemshopError, UnauthorizedError, NetworkError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SDK_VERSION = "1.0.0"
API_VERSION = "2025-03"
DEFAULT_USER_AGENT = f"nuvemshop-sdk/{SDK_VERSION} (Python)"


class Environment(str, Enum):
    """Nuvemshop API environments."""
    PRODUCTION = "production"
    SANDBOX = "sandbox"


_ENV_URLS: dict[Environment, dict[str, str]] = {
    Environment.PRODUCTION: {
        "api": "https://api.tiendanube.com",
        "auth": "https://www.tiendanube.com",
    },
    Environment.SANDBOX: {
        "api": "https://api.tiendanube.com",
        "auth": "https://www.tiendanube.com",
    },
}


# ---------------------------------------------------------------------------
# OAuth result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OAuthCredentials:
    """Immutable result of a successful OAuth exchange."""
    store_id: int
    access_token: str
    scope: str


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

class NuvemshopAuth:
    """Handles OAuth and builds authenticated headers.

    Usage::

        # Step 1: Exchange the authorization code for a permanent token
        creds = NuvemshopAuth.exchange_code(
            client_id="my_app_id",
            client_secret="my_app_secret",
            code="temporary_code",
        )

        # Step 2: Create an authenticated client
        from nuvemshop_sdk import NuvemshopClient
        client = NuvemshopClient(
            store_id=creds.store_id,
            access_token=creds.access_token,
        )
    """

    @staticmethod
    def exchange_code(
        client_id: str,
        client_secret: str,
        code: str,
        *,
        environment: Environment = Environment.PRODUCTION,
        timeout: int = 30,
    ) -> OAuthCredentials:
        """Exchange an authorization code for a **permanent** access token.

        Args:
            client_id: Your application's client ID on Nuvemshop.
            client_secret: Your application's client secret.
            code: The temporary authorization code from the OAuth redirect.
            environment: Target environment (production or sandbox).
            timeout: HTTP timeout in seconds.

        Returns:
            An :class:`OAuthCredentials` dataclass.

        Raises:
            ValueError: If any required argument is empty.
            UnauthorizedError: If the API rejects the credentials.
            NetworkError: On connection / DNS failures.
        """
        if not client_id or not client_secret or not code:
            raise ValueError(
                "client_id, client_secret, and code are all required "
                "for the OAuth exchange."
            )

        auth_url = _ENV_URLS[environment]["auth"]
        url = f"{auth_url}/apps/authorize/token"

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": DEFAULT_USER_AGENT,
                },
                timeout=timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise NetworkError(
                f"Connection failure during OAuth exchange: {exc}"
            ) from exc

        if not response.ok:
            _raise_auth_error(response)

        data: dict[str, Any] = response.json()
        return OAuthCredentials(
            store_id=int(data["user_id"]),
            access_token=data["access_token"],
            scope=data.get("scope", ""),
        )

    # ------------------------------------------------------------------
    # Header builders
    # ------------------------------------------------------------------

    @staticmethod
    def build_headers(
        access_token: str,
        user_agent: Optional[str] = None,
    ) -> dict[str, str]:
        """Return the standard headers for every Nuvemshop API request.

        Header format::

            Authorization: Bearer {access_token}
            User-Agent: nuvemshop-sdk/1.0 (Python)
            Content-Type: application/json
        """
        return {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": user_agent or DEFAULT_USER_AGENT,
            "Content-Type": "application/json",
        }

    @staticmethod
    def get_api_url(environment: Environment = Environment.PRODUCTION) -> str:
        """Return the base API URL for the given environment."""
        return _ENV_URLS[environment]["api"]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _raise_auth_error(response: requests.Response) -> None:
    """Parse an error response during OAuth and raise the right exception."""
    try:
        body = response.json()
        description = body.get("error_description", body.get("error", ""))
    except Exception:
        description = response.text

    raise UnauthorizedError(
        f"OAuth exchange failed: {description}",
        status_code=response.status_code,
        error_description=description,
    )
