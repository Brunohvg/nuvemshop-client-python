# src/nuvemshop_sdk/http_client.py
"""
Production-grade HTTP client for the Nuvemshop SDK.

Features:
  - Configurable ``BASE_API_URL``
  - Explicit ``get / post / put / patch / delete`` methods
  - Integrated :class:`RateLimitManager` (thread-safe, per store)
  - Integrated :class:`RetryPolicy` (exponential backoff + jitter)
  - Configurable idempotency policy (``Idempotency-Key`` header)
  - Mandatory structured JSON logging

Logging contract — every request emits at least::

    {
        "store_id": 123,
        "method": "POST",
        "endpoint": "/products",
        "status_code": 200,
        "remaining": 18,
        "retry_count": 1,
        "duration_ms": 142
    }
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry as Urllib3Retry

from .auth import API_VERSION, DEFAULT_USER_AGENT, Environment, NuvemshopAuth
from .exceptions import (
    NetworkError,
    NuvemshopError,
    raise_for_status,
)
from .rate_limit import RateLimitManager
from .retry_policy import RetryPolicy

logger = logging.getLogger("nuvemshop_sdk.http")


# ---------------------------------------------------------------------------
# Structured JSON log formatter (optional — users can attach to the logger)
# ---------------------------------------------------------------------------

class StructuredJsonFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects.

    Attach it to the ``nuvemshop_sdk`` logger hierarchy::

        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        logging.getLogger("nuvemshop_sdk").addHandler(handler)
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra fields passed via ``extra=``
        for key in ("store_id", "method", "endpoint", "status_code",
                     "duration_ms", "remaining", "retry_count",
                     "wait_seconds", "reset_timestamp", "attempt",
                     "max_retries", "delay_seconds", "idempotency_key"):
            val = getattr(record, key, None)
            if val is not None:
                log_entry[key] = val
        return json.dumps(log_entry, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Idempotency helper
# ---------------------------------------------------------------------------

class IdempotencyPolicy:
    """Controls whether an ``Idempotency-Key`` header is sent.

    By default the policy is **disabled**.  Enable it globally or per-request::

        # Global
        client = NuvemshopClient(..., idempotency=True)

        # Per-request override
        client.products.create(data, idempotency_key="my-key")
    """

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = enabled

    def generate_key(self, override: Optional[str] = None) -> Optional[str]:
        """Return a key if idempotency is enabled, or ``None``."""
        if override:
            return override
        if self.enabled:
            return str(uuid.uuid4())
        return None


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------

class HttpClient:
    """
    Cliente HTTP de baixo nível que integra limites de taxa, retentativas,
    idempotência e logging estruturado.

    Esta classe não deve ser usada diretamente pelos usuários finais.
    O :class:`~nuvemshop_sdk.client.NuvemshopClient` a utiliza internamente
    em conjunto com a camada de recursos.

    Args:
        store_id (int): ID da loja Nuvemshop.
        access_token (str): Token de acesso permanente.
        api_version (str): Versão da API (padrão "v1").
        base_url (str, optional): URL base para as requisições.
        environment (Environment): Ambiente (Production/Sandbox).
        user_agent (str, optional): Cabeçalho User-Agent.
        timeout (int): Tempo limite das requisições.
        rate_limit_manager (RateLimitManager, optional): Gerenciador de limites.
        retry_policy (RetryPolicy, optional): Política de retentativas.
        idempotency_policy (IdempotencyPolicy, optional): Política de idempotência.
    """

    def __init__(
        self,
        store_id: int,
        access_token: str,
        *,
        api_version: str = API_VERSION,
        base_url: Optional[str] = None,
        environment: Environment = Environment.PRODUCTION,
        user_agent: Optional[str] = None,
        timeout: int = 10,
        rate_limit_manager: Optional[RateLimitManager] = None,
        retry_policy: Optional[RetryPolicy] = None,
        idempotency_policy: Optional[IdempotencyPolicy] = None,
    ) -> None:
        if not store_id or not access_token:
            raise ValueError("store_id and access_token are required.")

        self.store_id = store_id
        self.access_token = access_token
        self.api_version = api_version
        self.timeout = timeout or 10  # Never allow None/0
        self.user_agent = user_agent or DEFAULT_USER_AGENT

        # Resolve base URL
        self.base_url = base_url or NuvemshopAuth.get_api_url(environment)

        # Integrations
        self.rate_limiter = rate_limit_manager or RateLimitManager()
        self.retry_policy = retry_policy or RetryPolicy()
        self.idempotency = idempotency_policy or IdempotencyPolicy()

        # Session (connection pooling, but NO urllib3 retry — we do it)
        self._session = self._create_session()

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    @staticmethod
    def _create_session() -> requests.Session:
        session = requests.Session()
        # Disable urllib3's own retry so we fully control the loop
        adapter = HTTPAdapter(
            max_retries=Urllib3Retry(total=0),
            pool_maxsize=10,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    # ------------------------------------------------------------------
    # URL builder
    # ------------------------------------------------------------------

    def _build_url(self, endpoint: str) -> str:
        # Ensure endpoint starts without a slash for clean joining
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{self.api_version}/{self.store_id}/{endpoint}"

    # ------------------------------------------------------------------
    # Header builder
    # ------------------------------------------------------------------

    def _build_headers(
        self,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, str]:
        headers = NuvemshopAuth.build_headers(
            access_token=self.access_token,
            user_agent=self.user_agent,
        )
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    # ------------------------------------------------------------------
    # Core request loop
    # ------------------------------------------------------------------

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        """Execute an HTTP request and return the parsed JSON body."""
        body, _ = self._request_internal(
            method,
            endpoint,
            params=params,
            data=data,
            idempotency_key=idempotency_key,
        )
        return body

    def _request_internal(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> tuple[Any, dict[str, str]]:
        """Internal logic for request execution. Returns (body, headers)."""
        resolved_key = self.idempotency.generate_key(idempotency_key)
        headers = self._build_headers(idempotency_key=resolved_key)
        
        # If endpoint is a full URL (from Link header), use it directly.
        url = endpoint if endpoint.startswith("http") else self._build_url(endpoint)
        
        attempt = 0

        while True:
            # 1. Pre-request: preemptive rate-limit wait
            self.rate_limiter.wait_if_needed(self.store_id, self.access_token)

            start = time.monotonic()
            status_code: Optional[int] = None
            remaining: Optional[int] = None

            try:
                response = self._session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=self.timeout,
                )
                status_code = response.status_code
                duration_ms = round((time.monotonic() - start) * 1000)

                # 2. Post-response: update rate-limit state
                self.rate_limiter.update_from_headers(
                    self.store_id,
                    self.access_token,
                    dict(response.headers),
                )
                rl_status = self.rate_limiter.get_status(
                    self.store_id, self.access_token,
                )
                remaining = rl_status.remaining

                # 3. Structured log
                self._log_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    remaining=remaining,
                    retry_count=attempt,
                    idempotency_key=headers.get("Idempotency-Key"),
                )

                # 4. Success path
                if response.ok:
                    res_body = {} if response.status_code == 204 else response.json()
                    return res_body, dict(response.headers)

                # 5. Handle 429 reactively
                if status_code == 429:
                    if self.retry_policy.should_retry(
                        attempt, status_code=429,
                    ):
                        wait = self.rate_limiter.handle_429(
                            self.store_id,
                            self.access_token,
                            dict(response.headers),
                        )
                        time.sleep(wait)
                        attempt += 1
                        continue
                    self._raise_from_response(response)

                # 6. Retryable 5xx
                if self.retry_policy.should_retry(
                    attempt, status_code=status_code,
                ):
                    self.retry_policy.wait(attempt)
                    attempt += 1
                    continue

                self._raise_from_response(response)

            except requests.exceptions.RequestException as exc:
                duration_ms = round((time.monotonic() - start) * 1000)
                self._log_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=None,
                    duration_ms=duration_ms,
                    remaining=remaining,
                    retry_count=attempt,
                    idempotency_key=headers.get("Idempotency-Key"),
                )

                if self.retry_policy.should_retry(
                    attempt, is_network_error=True,
                ):
                    self.retry_policy.wait(attempt)
                    attempt += 1
                    continue

                raise NetworkError(
                    f"Network error after {attempt + 1} attempt(s): {exc}",
                ) from exc

    # ------------------------------------------------------------------
    # Response → Exception
    # ------------------------------------------------------------------

    @staticmethod
    def _raise_from_response(response: requests.Response) -> None:
        try:
            body = response.json()
        except Exception:
            body = response.text
        raise_for_status(
            status_code=response.status_code,
            body=body,
            headers=dict(response.headers),
        )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log_request(
        self,
        *,
        method: str,
        endpoint: str,
        status_code: Optional[int],
        duration_ms: int,
        remaining: Optional[int],
        retry_count: int,
        idempotency_key: Optional[str] = None,
    ) -> None:
        level = logging.WARNING if (status_code and status_code >= 400) else logging.DEBUG
        logger.log(
            level,
            "Nuvemshop API request",
            extra={
                "store_id": self.store_id,
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "remaining": remaining,
                "retry_count": retry_count,
                "idempotency_key": idempotency_key,
            },
        )

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        return self.request("GET", endpoint, params=params)

    def get_with_headers(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> tuple[Any, dict[str, str]]:
        """Execute a GET request and return both (body, headers)."""
        return self._request_internal("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        return self.request(
            "POST", endpoint, data=data, idempotency_key=idempotency_key,
        )

    def put(self, endpoint: str, data: dict[str, Any]) -> Any:
        return self.request("PUT", endpoint, data=data)

    def patch(self, endpoint: str, data: dict[str, Any]) -> Any:
        return self.request("PATCH", endpoint, data=data)

    def delete(self, endpoint: str) -> Any:
        return self.request("DELETE", endpoint)
