"""Tests for OAuth cache (state store)."""

import pytest

from taolib.oauth.cache.state_store import OAuthStateStore


class TestOAuthStateStore:
    @pytest.fixture
    def state_store(self, mock_redis):
        return OAuthStateStore(mock_redis, ttl_seconds=600)

    @pytest.mark.asyncio
    async def test_create_state(self, state_store, mock_redis):
        state = await state_store.create_state()
        assert isinstance(state, str)
        assert len(state) > 0
        # State should be stored in Redis
        assert len(mock_redis._data) == 1

    @pytest.mark.asyncio
    async def test_create_state_with_extra_data(self, state_store, mock_redis):
        state = await state_store.create_state({"link_to_user_id": "user-123"})
        assert isinstance(state, str)

    @pytest.mark.asyncio
    async def test_validate_and_consume_valid(self, state_store, mock_redis):
        state = await state_store.create_state()
        result = await state_store.validate_and_consume(state)
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_and_consume_invalid(self, state_store):
        result = await state_store.validate_and_consume("invalid-state")
        assert result is None

    @pytest.mark.asyncio
    async def test_state_is_single_use(self, state_store):
        state = await state_store.create_state()
        # First consume should succeed
        result1 = await state_store.validate_and_consume(state)
        assert result1 is not None
        # Second consume should fail (single-use)
        result2 = await state_store.validate_and_consume(state)
        assert result2 is None
