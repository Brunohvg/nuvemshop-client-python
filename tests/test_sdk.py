# src/tests/test_sdk.py
"""
Comprehensive test suite for the Nuvemshop SDK.

Tests cover:
  - Exceptions (402, 429, 422 etc.)
  - Rate Limit Manager (preemptive/reactive, per-store, thread-safe)
  - Retry Policy (filtered status codes, backoff)
  - Webhook HMAC validation (valid, invalid, expired)
  - Pydantic models (extra="allow")
  - Product model enforcement (root stock block, auto-variant)
  - Inventory resource (variant-level only)
  - Idempotency (header presence)
  - Pagination (lazy generator)
"""

import hashlib
import hmac as hmac_mod
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

# --- Exceptions ---
from nuvemshop_sdk.exceptions import (
    ForbiddenError,
    NuvemshopError,
    RateLimitError,
    ServerError,
    StoreInactiveError,
    UnauthorizedError,
    ValidationError,
    raise_for_status,
)


class TestExceptions:
    """Test the exception layer and raise_for_status factory."""

    def test_401_raises_unauthorized(self):
        with pytest.raises(UnauthorizedError) as exc_info:
            raise_for_status(401, {"error": "invalid_token", "description": "Token expired"})
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "invalid_token"

    def test_402_raises_store_inactive(self):
        with pytest.raises(StoreInactiveError) as exc_info:
            raise_for_status(402, {"message": "Store subscription inactive"})
        assert exc_info.value.status_code == 402

    def test_403_raises_forbidden(self):
        with pytest.raises(ForbiddenError):
            raise_for_status(403, {"error": "insufficient_scope"})

    def test_422_raises_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            raise_for_status(422, {"error_code": "invalid_field", "error_description": "name is required"})
        assert exc_info.value.error_code == "invalid_field"
        assert exc_info.value.error_description == "name is required"

    def test_429_raises_rate_limit_with_retry_after(self):
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(
                429,
                {"error": "rate_limit_exceeded"},
                headers={"x-ratelimit-reset": "5.0"},
            )
        assert exc_info.value.retry_after == 5.0

    def test_500_raises_server_error(self):
        with pytest.raises(ServerError):
            raise_for_status(500, {"error": "internal_error"})

    def test_502_raises_server_error(self):
        with pytest.raises(ServerError):
            raise_for_status(502, "Bad Gateway")

    def test_unknown_4xx_raises_base(self):
        with pytest.raises(NuvemshopError):
            raise_for_status(418, {"message": "I'm a teapot"})

    def test_exception_repr(self):
        try:
            raise_for_status(422, {"error_code": "foo", "error_description": "bar"})
        except ValidationError as e:
            r = repr(e)
            assert "422" in r
            assert "foo" in r


# --- Rate Limit Manager ---
from nuvemshop_sdk.rate_limit import RateLimitManager


class TestRateLimitManager:
    """Test the rate-limit manager."""

    def test_update_from_headers(self):
        rl = RateLimitManager()
        rl.update_from_headers(1, "token", {
            "X-RateLimit-Remaining": "5",
            "X-RateLimit-Reset": str(time.time() + 10),
        })
        status = rl.get_status(1, "token")
        assert status.remaining == 5
        assert status.total_requests == 1

    def test_preemptive_wait_when_remaining_zero(self):
        rl = RateLimitManager()
        # Set remaining = 0 with reset in 0.1 seconds
        rl.update_from_headers(1, "token", {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(time.time() + 0.1),
        })
        start = time.monotonic()
        rl.wait_if_needed(1, "token")
        elapsed = time.monotonic() - start
        # Should have waited ~0.1s
        assert elapsed >= 0.05

    def test_handle_429_returns_wait_time(self):
        rl = RateLimitManager()
        wait = rl.handle_429(1, "token", {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(time.time() + 2.0),
        })
        assert wait > 0

    def test_per_store_isolation(self):
        rl = RateLimitManager()
        rl.update_from_headers(1, "token_a", {"X-RateLimit-Remaining": "3", "X-RateLimit-Reset": "0"})
        rl.update_from_headers(2, "token_b", {"X-RateLimit-Remaining": "10", "X-RateLimit-Reset": "0"})
        assert rl.get_status(1, "token_a").remaining == 3
        assert rl.get_status(2, "token_b").remaining == 10

    def test_thread_safety(self):
        """Run 10 concurrent updates — should not crash."""
        rl = RateLimitManager()
        errors = []

        def updater(i: int):
            try:
                for _ in range(100):
                    rl.update_from_headers(1, "token", {
                        "X-RateLimit-Remaining": str(i),
                        "X-RateLimit-Reset": str(time.time() + 1),
                    })
                    rl.get_status(1, "token")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=updater, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0

    def test_get_status_returns_snapshot(self):
        rl = RateLimitManager()
        status = rl.get_status(999, "x")
        assert status.remaining is None
        assert status.total_requests == 0


# --- Retry Policy ---
from nuvemshop_sdk.retry_policy import RetryPolicy


class TestRetryPolicy:
    """Test the retry policy."""

    def test_retry_on_500(self):
        rp = RetryPolicy(max_retries=3)
        assert rp.should_retry(0, status_code=500) is True

    def test_retry_on_429(self):
        rp = RetryPolicy(max_retries=3)
        assert rp.should_retry(0, status_code=429) is True

    def test_no_retry_on_401(self):
        rp = RetryPolicy(max_retries=3)
        assert rp.should_retry(0, status_code=401) is False

    def test_no_retry_on_402(self):
        rp = RetryPolicy(max_retries=3)
        assert rp.should_retry(0, status_code=402) is False

    def test_no_retry_on_403(self):
        rp = RetryPolicy(max_retries=3)
        assert rp.should_retry(0, status_code=403) is False

    def test_no_retry_on_422(self):
        rp = RetryPolicy(max_retries=3)
        assert rp.should_retry(0, status_code=422) is False

    def test_retry_on_network_error(self):
        rp = RetryPolicy(max_retries=3)
        assert rp.should_retry(0, is_network_error=True) is True

    def test_max_retries_exhausted(self):
        rp = RetryPolicy(max_retries=2)
        assert rp.should_retry(2, status_code=500) is False

    def test_backoff_increases(self):
        rp = RetryPolicy(base_delay=1.0, jitter_range=0.0)
        d0 = rp.compute_delay(0)
        d1 = rp.compute_delay(1)
        d2 = rp.compute_delay(2)
        assert d0 < d1 < d2


# --- Webhook HMAC ---
from nuvemshop_sdk.utils.webhook import verify_webhook_signature


class TestWebhookValidation:
    """Test webhook HMAC validation."""

    def _sign(self, body: bytes, secret: str) -> str:
        return hmac_mod.new(
            key=secret.encode("utf-8"),
            msg=body,
            digestmod=hashlib.sha256,
        ).hexdigest()

    def test_valid_signature(self):
        body = b'{"event":"order/created"}'
        secret = "my_secret"
        sig = self._sign(body, secret)
        assert verify_webhook_signature(body, sig, secret) is True

    def test_invalid_signature(self):
        body = b'{"event":"order/created"}'
        assert verify_webhook_signature(body, "bad_sig", "my_secret") is False

    def test_expired_timestamp(self):
        body = b'{"event":"order/created"}'
        secret = "my_secret"
        sig = self._sign(body, secret)
        old_timestamp = time.time() - 600  # 10 min old
        assert verify_webhook_signature(
            body, sig, secret, timestamp=old_timestamp,
        ) is False

    def test_valid_timestamp(self):
        body = b'{"event":"order/created"}'
        secret = "my_secret"
        sig = self._sign(body, secret)
        now = time.time()
        assert verify_webhook_signature(
            body, sig, secret, timestamp=now,
        ) is True

    def test_string_body(self):
        body_str = '{"event":"order/created"}'
        body_bytes = body_str.encode("utf-8")
        secret = "my_secret"
        sig = self._sign(body_bytes, secret)
        assert verify_webhook_signature(body_str, sig, secret) is True


# --- Pydantic Models ---
from nuvemshop_sdk.models import Product, Variant, Customer


class TestModels:
    """Test Pydantic models with extra='allow'."""

    def test_variant_creation(self):
        v = Variant(id=1, sku="ABC", price="29.90", stock=10)
        assert v.id == 1
        assert v.sku == "ABC"

    def test_product_with_variants(self):
        p = Product(
            id=1,
            name={"pt": "Camiseta"},
            variants=[Variant(id=1, sku="A", stock=5)],
        )
        assert len(p.variants) == 1

    def test_extra_fields_allowed(self):
        """API evolution: unknown fields should be accepted, not rejected."""
        v = Variant(id=1, sku="X", some_future_field="hello")
        assert v.model_extra.get("some_future_field") == "hello"

    def test_customer_creation(self):
        c = Customer(id=1, name="João", email="joao@example.com")
        assert c.name == "João"


# --- Product Resource Enforcement ---
from nuvemshop_sdk.resources.products import ProductsResource
from nuvemshop_sdk.exceptions import ValidationError as SDKValidationError


class TestProductEnforcement:
    """Test Nuvemshop model enforcement in ProductsResource."""

    def _create_resource(self) -> ProductsResource:
        mock_http = MagicMock()
        mock_http.post.return_value = {"id": 1}
        mock_http.put.return_value = {"id": 1}
        mock_http.patch.return_value = {"id": 1}
        return ProductsResource(mock_http)

    def test_block_root_stock_on_create(self):
        res = self._create_resource()
        with pytest.raises(SDKValidationError) as exc_info:
            res.create({"name": {"pt": "Test"}, "stock": 10})
        assert "variant" in str(exc_info.value).lower()

    def test_block_root_inventory_on_update(self):
        res = self._create_resource()
        with pytest.raises(SDKValidationError):
            res.update(1, {"inventory_quantity": 5})

    def test_auto_create_variant_when_missing(self):
        res = self._create_resource()
        data = {"name": {"pt": "Test"}}
        res.create(data)
        # The data dict should now have a variants key
        assert "variants" in data
        assert len(data["variants"]) == 1

    def test_valid_create_with_variants_passes(self):
        res = self._create_resource()
        res.create({
            "name": {"pt": "Camiseta"},
            "variants": [{"price": "29.90", "stock": 10}],
        })
        res._http.post.assert_called_once()


# --- Inventory Resource ---
from nuvemshop_sdk.resources.inventory import InventoryResource
from nuvemshop_sdk.resources.variants import VariantsResource


class TestInventoryResource:
    """Test inventory resource enforces variant-level operations."""

    def test_set_stock_delegates_to_variants(self):
        mock_http = MagicMock()
        mock_http.patch.return_value = {"id": 1, "stock": 50}
        variants = VariantsResource(mock_http)
        inventory = InventoryResource(variants)
        result = inventory.set_stock(product_id=1, variant_id=2, stock=50)
        mock_http.patch.assert_called_once_with(
            "products/1/variants/2", data={"stock": 50},
        )

    def test_negative_stock_raises(self):
        mock_http = MagicMock()
        variants = VariantsResource(mock_http)
        inventory = InventoryResource(variants)
        with pytest.raises(SDKValidationError):
            inventory.set_stock(product_id=1, variant_id=2, stock=-1)


# --- Idempotency ---
from nuvemshop_sdk.http_client import IdempotencyPolicy


class TestIdempotency:
    """Test idempotency key generation."""

    def test_disabled_by_default(self):
        policy = IdempotencyPolicy()
        assert policy.generate_key() is None

    def test_enabled_generates_uuid(self):
        policy = IdempotencyPolicy(enabled=True)
        key = policy.generate_key()
        assert key is not None
        assert len(key) == 36  # UUID format

    def test_override_key(self):
        policy = IdempotencyPolicy(enabled=False)
        key = policy.generate_key(override="my-custom-key")
        assert key == "my-custom-key"

    def test_override_takes_precedence(self):
        policy = IdempotencyPolicy(enabled=True)
        key = policy.generate_key(override="custom")
        assert key == "custom"


# --- Pagination ---
from nuvemshop_sdk.utils.pagination import paginate, paginate_collect


class TestPagination:
    """Test lazy pagination."""

    def test_single_page(self):
        def fetcher(*, page, per_page, **kw):
            if page == 1:
                return [{"id": 1}, {"id": 2}]
            return []

        items = list(paginate(fetcher, per_page=10))
        assert len(items) == 2

    def test_multi_page(self):
        def fetcher(*, page, per_page, **kw):
            if page == 1:
                return [{"id": i} for i in range(per_page)]
            elif page == 2:
                return [{"id": i} for i in range(3)]
            return []

        items = list(paginate(fetcher, per_page=5))
        assert len(items) == 8  # 5 + 3

    def test_empty_first_page(self):
        def fetcher(*, page, per_page, **kw):
            return []

        items = list(paginate(fetcher, per_page=10))
        assert len(items) == 0

    def test_collect(self):
        def fetcher(*, page, per_page, **kw):
            if page == 1:
                return [{"id": 1}]
            return []

        items = paginate_collect(fetcher, per_page=10)
        assert isinstance(items, list)
        assert len(items) == 1

    def test_stops_on_partial_page(self):
        """If a page returns fewer items than per_page, stop."""
        call_count = {"n": 0}

        def fetcher(*, page, per_page, **kw):
            call_count["n"] += 1
            if page == 1:
                return [{"id": i} for i in range(3)]  # 3 < per_page=5
            return []

        items = list(paginate(fetcher, per_page=5))
        assert len(items) == 3
        assert call_count["n"] == 1  # Should not fetch page 2


# --- Auth ---
from nuvemshop_sdk.auth import NuvemshopAuth, DEFAULT_USER_AGENT


class TestAuth:
    """Test auth header building."""

    def test_build_headers_has_bearer(self):
        headers = NuvemshopAuth.build_headers("my_token")
        assert headers["Authorization"] == "Bearer my_token"
        assert "User-Agent" in headers
        assert headers["Content-Type"] == "application/json"

    def test_default_user_agent(self):
        headers = NuvemshopAuth.build_headers("t")
        assert "nuvemshop-sdk" in headers["User-Agent"]

    def test_custom_user_agent(self):
        headers = NuvemshopAuth.build_headers("t", user_agent="MyApp/1.0")
        assert headers["User-Agent"] == "MyApp/1.0"
