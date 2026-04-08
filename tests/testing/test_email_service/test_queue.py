"""队列测试。"""

import pytest

from taolib.testing.email_service.models.enums import EmailPriority
from taolib.testing.email_service.queue.memory_queue import InMemoryEmailQueue


class TestInMemoryEmailQueue:
    @pytest.mark.asyncio
    async def test_enqueue_dequeue(self):
        queue = InMemoryEmailQueue()
        await queue.enqueue("email-1")
        result = await queue.dequeue(timeout=1)
        assert result == "email-1"

    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        queue = InMemoryEmailQueue()
        await queue.enqueue("low-1", EmailPriority.LOW)
        await queue.enqueue("high-1", EmailPriority.HIGH)
        await queue.enqueue("normal-1", EmailPriority.NORMAL)

        # 应按优先级顺序：high → normal → low
        r1 = await queue.dequeue(timeout=1)
        r2 = await queue.dequeue(timeout=1)
        r3 = await queue.dequeue(timeout=1)
        assert r1 == "high-1"
        assert r2 == "normal-1"
        assert r3 == "low-1"

    @pytest.mark.asyncio
    async def test_dequeue_empty_returns_none(self):
        queue = InMemoryEmailQueue()
        result = await queue.dequeue(timeout=1)
        assert result is None

    @pytest.mark.asyncio
    async def test_enqueue_bulk(self):
        queue = InMemoryEmailQueue()
        await queue.enqueue_bulk(["e1", "e2", "e3"], EmailPriority.NORMAL)

        results = []
        for _ in range(3):
            r = await queue.dequeue(timeout=1)
            if r:
                results.append(r)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_size(self):
        queue = InMemoryEmailQueue()
        await queue.enqueue("e1")
        await queue.enqueue("e2")
        size = await queue.size()
        assert size["total"] == 2



