"""推送服务全面单元测试。

覆盖：连接管理、频道订阅、ACK/重传机制、心跳检测、
离线消息缓冲、在线状态追踪、HTTP 轮询、事件发布、
PubSub 桥接路由、连接统计。
"""
import asyncio
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from taolib.config_center.events.publisher import EventPublisher
from taolib.config_center.events.types import ConfigChangedEvent
from taolib.config_center.server.websocket.heartbeat import HeartbeatMonitor
from taolib.config_center.server.websocket.manager import WebSocketConnectionManager
from taolib.config_center.server.websocket.message_buffer import (
    InMemoryMessageBuffer,
)
from taolib.config_center.server.websocket.models import (
    ConnectionInfo,
    ConnectionStats,
    ConnectionStatus,
    MessagePriority,
    MessageType,
    PushMessage,
    UserPresence,
)
from taolib.config_center.server.websocket.presence import InMemoryPresenceTracker
from taolib.config_center.server.websocket.pubsub_bridge import PubSubBridge

from .conftest import FakeWebSocket, MockRedis

# ======================================================================
# Models
# ======================================================================


class TestPushMessage:
    def test_to_dict_and_from_dict_roundtrip(self):
        msg = PushMessage(
            channel="config:dev:auth",
            event_type="config_changed",
            data={"key": "db.host"},
            priority=MessagePriority.HIGH,
            requires_ack=True,
            sender_id="inst-1",
        )
        d = msg.to_dict()
        assert d["channel"] == "config:dev:auth"
        assert d["priority"] == "high"
        assert d["requires_ack"] is True

        restored = PushMessage.from_dict(d)
        assert restored.channel == msg.channel
        assert restored.event_type == msg.event_type
        assert restored.priority == MessagePriority.HIGH
        assert restored.id == msg.id

    def test_from_dict_defaults(self):
        msg = PushMessage.from_dict({"channel": "test"})
        assert msg.event_type == "push"
        assert msg.priority == MessagePriority.NORMAL
        assert msg.requires_ack is False

    def test_message_priority_values(self):
        assert MessagePriority.HIGH == "high"
        assert MessagePriority.NORMAL == "normal"
        assert MessagePriority.LOW == "low"

    def test_connection_status_values(self):
        assert ConnectionStatus.ONLINE == "online"
        assert ConnectionStatus.OFFLINE == "offline"
        assert ConnectionStatus.RECONNECTING == "reconnecting"

    def test_message_type_values(self):
        assert MessageType.ACK == "ack"
        assert MessageType.PING == "ping"
        assert MessageType.CONFIG_CHANGED == "config_changed"


class TestConnectionStats:
    def test_to_dict(self):
        stats = ConnectionStats(
            total_connections=100,
            active_connections=50,
            total_messages_sent=1000,
        )
        d = stats.to_dict()
        assert d["total_connections"] == 100
        assert d["active_connections"] == 50
        assert d["total_messages_sent"] == 1000


class TestUserPresence:
    def test_to_dict(self):
        p = UserPresence(
            user_id="u1",
            status=ConnectionStatus.ONLINE,
            connection_count=2,
            active_channels=["config:dev:auth"],
        )
        d = p.to_dict()
        assert d["user_id"] == "u1"
        assert d["status"] == "online"
        assert d["connection_count"] == 2


# ======================================================================
# InMemoryMessageBuffer
# ======================================================================


class TestInMemoryMessageBuffer:
    @pytest.fixture
    def buffer(self):
        return InMemoryMessageBuffer(max_messages=100)

    @pytest.mark.asyncio
    async def test_push_and_flush(self, buffer):
        msg1 = PushMessage(channel="ch1", event_type="e1", data={"v": 1})
        msg2 = PushMessage(channel="ch1", event_type="e2", data={"v": 2})
        await buffer.push("user1", msg1)
        await buffer.push("user1", msg2)

        flushed = await buffer.flush("user1")
        assert len(flushed) == 2
        assert flushed[0].data == {"v": 1}
        assert flushed[1].data == {"v": 2}

        # Flush again should be empty
        again = await buffer.flush("user1")
        assert len(again) == 0

    @pytest.mark.asyncio
    async def test_flush_with_limit(self, buffer):
        for i in range(10):
            await buffer.push(
                "user1", PushMessage(channel="ch", event_type="e", data={"i": i})
            )
        flushed = await buffer.flush("user1", limit=3)
        assert len(flushed) == 3

    @pytest.mark.asyncio
    async def test_push_to_channel_and_get_recent(self, buffer):
        t0 = datetime.now(UTC)
        msg = PushMessage(channel="ch1", event_type="e", data={})
        await buffer.push_to_channel("ch1", msg)

        recent = await buffer.get_recent("ch1", since=t0 - timedelta(seconds=1))
        assert len(recent) == 1

    @pytest.mark.asyncio
    async def test_get_recent_empty_channel(self, buffer):
        recent = await buffer.get_recent("nonexistent", since=datetime.now(UTC))
        assert recent == []

    @pytest.mark.asyncio
    async def test_flush_nonexistent_user(self, buffer):
        assert await buffer.flush("nobody") == []


# ======================================================================
# InMemoryPresenceTracker
# ======================================================================


class TestInMemoryPresenceTracker:
    @pytest.fixture
    def tracker(self):
        return InMemoryPresenceTracker()

    @pytest.mark.asyncio
    async def test_set_online_and_get_status(self, tracker):
        await tracker.set_online("u1", "inst-1")
        presence = await tracker.get_status("u1")
        assert presence is not None
        assert presence.status == ConnectionStatus.ONLINE
        assert presence.connection_count == 1

    @pytest.mark.asyncio
    async def test_multiple_connections_increment_count(self, tracker):
        await tracker.set_online("u1", "inst-1")
        await tracker.set_online("u1", "inst-2")
        presence = await tracker.get_status("u1")
        assert presence.connection_count == 2

    @pytest.mark.asyncio
    async def test_set_offline_decrements_count(self, tracker):
        await tracker.set_online("u1", "inst-1")
        await tracker.set_online("u1", "inst-2")
        await tracker.set_offline("u1", "inst-1")
        presence = await tracker.get_status("u1")
        assert presence.connection_count == 1
        assert presence.status == ConnectionStatus.ONLINE

    @pytest.mark.asyncio
    async def test_fully_offline(self, tracker):
        await tracker.set_online("u1", "inst-1")
        await tracker.set_offline("u1", "inst-1")
        presence = await tracker.get_status("u1")
        assert presence.status == ConnectionStatus.OFFLINE
        assert presence.connection_count == 0

    @pytest.mark.asyncio
    async def test_get_all_online(self, tracker):
        await tracker.set_online("u1", "inst-1")
        await tracker.set_online("u2", "inst-1")
        await tracker.set_online("u3", "inst-1")
        await tracker.set_offline("u3", "inst-1")

        online = await tracker.get_all_online()
        user_ids = {p.user_id for p in online}
        assert user_ids == {"u1", "u2"}

    @pytest.mark.asyncio
    async def test_get_status_unknown_user(self, tracker):
        assert await tracker.get_status("nobody") is None

    @pytest.mark.asyncio
    async def test_refresh(self, tracker):
        await tracker.set_online("u1", "inst-1")
        old_time = tracker._state["u1"].last_seen
        await asyncio.sleep(0.01)
        await tracker.refresh("u1")
        assert tracker._state["u1"].last_seen >= old_time


# ======================================================================
# WebSocketConnectionManager
# ======================================================================


class TestWebSocketConnectionManager:
    @pytest.fixture
    def presence(self):
        return InMemoryPresenceTracker()

    @pytest.fixture
    def buffer(self):
        return InMemoryMessageBuffer()

    @pytest.fixture
    def manager(self, presence, buffer):
        return WebSocketConnectionManager(
            presence_tracker=presence,
            message_buffer=buffer,
            instance_id="test-inst",
            heartbeat_interval=9999,  # disable auto heartbeat in tests
            ack_timeout=2,
            max_retries=2,
        )

    # -- Connection lifecycle ---

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, manager, presence):
        ws = FakeWebSocket(client_id="ws1")
        await manager.connect(ws, "user1")

        assert ws.accepted
        stats = manager.get_stats()
        assert stats.active_connections == 1
        assert stats.total_connections == 1

        # Presence should be online
        p = await presence.get_status("user1")
        assert p is not None
        assert p.status == ConnectionStatus.ONLINE

        manager.disconnect(ws)
        stats = manager.get_stats()
        assert stats.active_connections == 0

    @pytest.mark.asyncio
    async def test_multi_device_connections(self, manager):
        ws1 = FakeWebSocket(client_id="ws1")
        ws2 = FakeWebSocket(client_id="ws2")
        await manager.connect(ws1, "user1")
        await manager.connect(ws2, "user1")

        stats = manager.get_stats()
        assert stats.active_connections == 2
        assert stats.online_users == 1

    @pytest.mark.asyncio
    async def test_disconnect_cleans_subscriptions(self, manager):
        ws = FakeWebSocket(client_id="ws1")
        await manager.connect(ws, "user1")
        await manager.subscribe(ws, "config:dev:auth")
        assert "config:dev:auth" in manager._subscriptions

        manager.disconnect(ws)
        assert "config:dev:auth" not in manager._subscriptions

    @pytest.mark.asyncio
    async def test_disconnect_unknown_ws_is_noop(self, manager):
        ws = FakeWebSocket()
        manager.disconnect(ws)  # should not raise

    # -- Auto-subscribe on connect ---

    @pytest.mark.asyncio
    async def test_auto_subscribe_on_connect(self, manager):
        ws = FakeWebSocket()
        await manager.connect(
            ws,
            "user1",
            environments=["dev", "staging"],
            services=["auth-svc"],
        )
        info = manager._connections[ws]
        assert "config:dev:auth-svc" in info.channels
        assert "config:staging:auth-svc" in info.channels

    # -- Offline message flush on connect ---

    @pytest.mark.asyncio
    async def test_offline_messages_flushed_on_connect(self, manager, buffer):
        # Pre-buffer a message
        msg = PushMessage(channel="ch1", event_type="e", data={"offline": True})
        await buffer.push("user1", msg)

        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        # The offline message should have been delivered
        assert len(ws.sent_messages) == 1
        payload = json.loads(ws.sent_messages[0])
        assert payload["data"]["offline"] is True

    # -- Channel subscriptions ---

    @pytest.mark.asyncio
    async def test_subscribe_and_unsubscribe(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        await manager.subscribe(ws, "config:dev:auth")
        info = manager._connections[ws]
        assert "config:dev:auth" in info.channels

        manager.unsubscribe(ws, "config:dev:auth")
        assert "config:dev:auth" not in info.channels

    @pytest.mark.asyncio
    async def test_subscribe_unknown_ws_is_noop(self, manager):
        ws = FakeWebSocket()  # not connected
        await manager.subscribe(ws, "test-channel")
        assert "test-channel" not in manager._subscriptions

    # -- Broadcast ---

    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self, manager):
        ws1 = FakeWebSocket(client_id="ws1")
        ws2 = FakeWebSocket(client_id="ws2")
        ws3 = FakeWebSocket(client_id="ws3")

        await manager.connect(ws1, "user1")
        await manager.connect(ws2, "user2")
        await manager.connect(ws3, "user3")

        await manager.subscribe(ws1, "config:dev:auth")
        await manager.subscribe(ws2, "config:dev:auth")
        # ws3 is NOT subscribed

        msg = PushMessage(
            channel="config:dev:auth",
            event_type="config_changed",
            data={"key": "db.host"},
        )
        delivered = await manager.broadcast("config:dev:auth", msg)
        assert delivered == 2
        assert len(ws1.sent_messages) == 1
        assert len(ws2.sent_messages) == 1
        assert len(ws3.sent_messages) == 0

    @pytest.mark.asyncio
    async def test_broadcast_empty_channel(self, manager):
        msg = PushMessage(channel="empty", event_type="e", data={})
        delivered = await manager.broadcast("empty", msg)
        assert delivered == 0

    @pytest.mark.asyncio
    async def test_broadcast_cleans_disconnected(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.subscribe(ws, "ch1")

        # Simulate broken connection
        await ws.close()

        msg = PushMessage(channel="ch1", event_type="e", data={})
        delivered = await manager.broadcast("ch1", msg)
        assert delivered == 0
        assert manager.get_stats().active_connections == 0

    # -- Send to user ---

    @pytest.mark.asyncio
    async def test_send_to_user(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        msg = PushMessage(
            channel="user:user1", event_type="notification", data={"text": "hi"}
        )
        count = await manager.send_to_user("user1", msg)
        assert count == 1
        assert len(ws.sent_messages) == 1

    @pytest.mark.asyncio
    async def test_send_to_offline_user_buffers(self, manager, buffer):
        msg = PushMessage(
            channel="user:user1", event_type="notification", data={"text": "missed"}
        )
        count = await manager.send_to_user("user1", msg)
        assert count == 0

        # Message should be in buffer
        buffered = await buffer.flush("user1")
        assert len(buffered) == 1
        assert buffered[0].data["text"] == "missed"

    # -- ACK mechanism ---

    @pytest.mark.asyncio
    async def test_ack_tracking(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        msg = PushMessage(
            channel="ch1",
            event_type="config_changed",
            data={},
            requires_ack=True,
        )
        await manager.broadcast("ch1", msg)  # ws not subscribed, manual deliver
        await manager._deliver_message(ws, manager._connections[ws], msg)

        info = manager._connections[ws]
        assert msg.id in info.pending_acks

        # Simulate client ACK
        await manager.handle_client_message(
            ws, json.dumps({"type": "ack", "message_id": msg.id})
        )
        assert msg.id not in info.pending_acks
        assert manager._stats.total_acks_received == 1

    @pytest.mark.asyncio
    async def test_non_ack_message_not_tracked(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        msg = PushMessage(channel="ch1", event_type="e", data={}, requires_ack=False)
        await manager._deliver_message(ws, manager._connections[ws], msg)

        info = manager._connections[ws]
        assert msg.id not in info.pending_acks

    # -- Client message handling ---

    @pytest.mark.asyncio
    async def test_handle_pong(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        old_time = manager._connections[ws].last_heartbeat

        await asyncio.sleep(0.01)
        await manager.handle_client_message(ws, json.dumps({"type": "pong"}))
        assert manager._connections[ws].last_heartbeat > old_time

    @pytest.mark.asyncio
    async def test_handle_subscribe_message(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.handle_client_message(
            ws, json.dumps({"type": "subscribe", "channel": "system_alerts"})
        )
        info = manager._connections[ws]
        assert "system_alerts" in info.channels

    @pytest.mark.asyncio
    async def test_handle_unsubscribe_message(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.subscribe(ws, "ch1")
        await manager.handle_client_message(
            ws, json.dumps({"type": "unsubscribe", "channel": "ch1"})
        )
        info = manager._connections[ws]
        assert "ch1" not in info.channels

    @pytest.mark.asyncio
    async def test_handle_invalid_json(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.handle_client_message(ws, "not-json!")
        # Should send an error response
        assert len(ws.sent_json_messages) == 1
        assert ws.sent_json_messages[0]["type"] == "error"

    @pytest.mark.asyncio
    async def test_handle_unknown_type(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.handle_client_message(ws, json.dumps({"type": "foobar"}))
        assert len(ws.sent_json_messages) == 1
        assert "未知" in ws.sent_json_messages[0]["detail"]

    # -- Stats ---

    @pytest.mark.asyncio
    async def test_get_stats(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.subscribe(ws, "ch1")

        stats = manager.get_stats()
        assert stats.active_connections == 1
        assert stats.total_channels == 1
        assert stats.online_users == 1

    @pytest.mark.asyncio
    async def test_get_user_presence(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.subscribe(ws, "ch1")
        await manager.subscribe(ws, "ch2")

        presence = manager.get_user_presence("user1")
        assert presence is not None
        assert presence.user_id == "user1"
        assert presence.status == ConnectionStatus.ONLINE
        assert set(presence.active_channels) == {"ch1", "ch2"}

    @pytest.mark.asyncio
    async def test_get_user_presence_unknown(self, manager):
        assert manager.get_user_presence("nobody") is None

    # -- Send personal (backward compat) ---

    @pytest.mark.asyncio
    async def test_send_personal(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.send_personal(ws, {"msg": "hello"})
        assert ws.sent_json_messages[-1] == {"msg": "hello"}

    # -- Disconnect buffers pending ACKs ---

    @pytest.mark.asyncio
    async def test_disconnect_buffers_pending_acks(self, manager, buffer):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        msg = PushMessage(
            channel="ch", event_type="e", data={"x": 1}, requires_ack=True
        )
        await manager._deliver_message(ws, manager._connections[ws], msg)

        manager.disconnect(ws)

        # Give time for background task to complete
        await asyncio.sleep(0.05)

        buffered = await buffer.flush("user1")
        assert len(buffered) == 1
        assert buffered[0].data["x"] == 1

    # -- ACK cleanup ---

    @pytest.mark.asyncio
    async def test_ack_cleanup_retries(self, manager):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        msg = PushMessage(
            channel="ch",
            event_type="e",
            data={},
            requires_ack=True,
            # Set timestamp in the past to trigger ACK timeout
            timestamp=datetime.now(UTC) - timedelta(seconds=30),
        )
        info = manager._connections[ws]
        info.pending_acks[msg.id] = msg

        await manager._cleanup_pending_acks()

        # Should have retried (retry_count incremented)
        # Message was re-delivered, check sent_messages
        assert len(ws.sent_messages) >= 1

    @pytest.mark.asyncio
    async def test_ack_cleanup_exceeds_max_retries(self, manager, buffer):
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        msg = PushMessage(
            channel="ch",
            event_type="e",
            data={"lost": True},
            requires_ack=True,
            timestamp=datetime.now(UTC) - timedelta(seconds=30),
            retry_count=10,  # exceed max_retries (2)
            max_retries=2,
        )
        info = manager._connections[ws]
        info.pending_acks[msg.id] = msg

        await manager._cleanup_pending_acks()

        # Should have been moved to buffer
        assert manager._stats.total_acks_timeout == 1
        buffered = await buffer.flush("user1")
        assert len(buffered) == 1


# ======================================================================
# HeartbeatMonitor
# ======================================================================


class TestHeartbeatMonitor:
    @pytest.mark.asyncio
    async def test_stale_connection_detection(self):
        stale_ws_list: list = []

        async def on_stale(ws):
            stale_ws_list.append(ws)

        monitor = HeartbeatMonitor(interval=30, timeout=5, on_stale=on_stale)

        # Create a connection with old heartbeat
        ws = FakeWebSocket()
        info = ConnectionInfo(
            user_id="user1",
            last_heartbeat=datetime.now(UTC) - timedelta(seconds=100),
        )
        connections = {ws: info}

        await monitor._check_all(connections)

        assert ws in stale_ws_list

    @pytest.mark.asyncio
    async def test_healthy_connection_gets_ping(self):
        monitor = HeartbeatMonitor(interval=30, timeout=70)

        ws = FakeWebSocket()
        info = ConnectionInfo(user_id="user1")
        connections = {ws: info}

        await monitor._check_all(connections)

        # Should have sent a ping
        assert len(ws.sent_messages) == 1
        ping_data = json.loads(ws.sent_messages[0])
        assert ping_data["type"] == "ping"

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        monitor = HeartbeatMonitor(interval=9999, timeout=70)
        await monitor.start(lambda: {})
        assert monitor._task is not None

        await monitor.stop()
        assert monitor._task is None


# ======================================================================
# EventPublisher
# ======================================================================


class TestEventPublisher:
    @pytest.fixture
    def mock_redis(self):
        return MockRedis()

    @pytest.fixture
    def msg_buffer(self):
        return InMemoryMessageBuffer()

    @pytest.fixture
    def publisher(self, mock_redis, msg_buffer):
        return EventPublisher(
            redis_client=mock_redis,
            message_buffer=msg_buffer,
            instance_id="pub-inst",
        )

    @pytest.mark.asyncio
    async def test_publish_config_changed(self, publisher, mock_redis):
        event = ConfigChangedEvent(
            config_id="cfg-1",
            config_key="database.host",
            environment="development",
            service="auth-service",
            change_type="update",
            version=3,
            changed_by="admin",
            timestamp=datetime.now(UTC),
            new_value="new-host:5432",
        )

        msg_id = await publisher.publish_config_changed(event)
        assert msg_id  # non-empty

        # Should have published to Redis
        channel = "push:broadcast:config:development:auth-service"
        assert channel in mock_redis._pubsub_channels
        assert len(mock_redis._pubsub_channels[channel]) == 1

        # Parse the published payload
        payload = json.loads(mock_redis._pubsub_channels[channel][0])
        assert payload["type"] == "config_changed"
        assert payload["priority"] == "high"
        assert payload["requires_ack"] is True

    @pytest.mark.asyncio
    async def test_publish_generic(self, publisher, mock_redis):
        msg_id = await publisher.publish(
            "system",
            "alert",
            {"severity": "warning"},
            priority=MessagePriority.HIGH,
        )
        assert msg_id
        assert "push:broadcast:system" in mock_redis._pubsub_channels

    @pytest.mark.asyncio
    async def test_publish_to_user(self, publisher, mock_redis):
        msg_id = await publisher.publish_to_user(
            "user123",
            "notification",
            {"text": "hello"},
        )
        assert msg_id
        assert "push:broadcast:user:user123" in mock_redis._pubsub_channels

    @pytest.mark.asyncio
    async def test_publish_system_alert(self, publisher, mock_redis):
        msg_id = await publisher.publish_system_alert({"msg": "maintenance"})
        assert msg_id
        channel = "push:broadcast:system"
        assert channel in mock_redis._pubsub_channels
        payload = json.loads(mock_redis._pubsub_channels[channel][0])
        assert payload["requires_ack"] is True

    @pytest.mark.asyncio
    async def test_publish_batch(self, publisher, mock_redis):
        messages = [
            PushMessage(channel="ch1", event_type="e1", data={"i": 0}),
            PushMessage(channel="ch2", event_type="e2", data={"i": 1}),
        ]
        ids = await publisher.publish_batch(messages)
        assert len(ids) == 2
        assert "push:broadcast:ch1" in mock_redis._pubsub_channels
        assert "push:broadcast:ch2" in mock_redis._pubsub_channels

    @pytest.mark.asyncio
    async def test_publish_batch_empty(self, publisher):
        ids = await publisher.publish_batch([])
        assert ids == []

    @pytest.mark.asyncio
    async def test_publish_writes_to_buffer(self, publisher, msg_buffer):
        await publisher.publish("ch1", "e1", {"data": True})
        recent = await msg_buffer.get_recent(
            "ch1", since=datetime.now(UTC) - timedelta(seconds=5)
        )
        assert len(recent) == 1

    @pytest.mark.asyncio
    async def test_publish_redis_failure_does_not_raise(self, msg_buffer):
        """Redis publish failure should be logged, not raised."""
        failing_redis = MockRedis()
        failing_redis.publish = AsyncMock(side_effect=ConnectionError("Redis down"))

        publisher = EventPublisher(
            redis_client=failing_redis,
            message_buffer=msg_buffer,
            instance_id="fail-inst",
        )
        # Should not raise
        msg_id = await publisher.publish("ch", "e", {"x": 1})
        assert msg_id


# ======================================================================
# PubSubBridge
# ======================================================================


class TestPubSubBridge:
    @pytest.fixture
    def mock_redis(self):
        return MockRedis()

    @pytest.fixture
    def mock_manager(self):
        mgr = AsyncMock()
        mgr.broadcast = AsyncMock(return_value=1)
        return mgr

    @pytest.fixture
    def bridge(self, mock_redis, mock_manager):
        return PubSubBridge(
            redis_client=mock_redis,
            websocket_manager=mock_manager,
            instance_id="bridge-inst",
            health_check_interval=9999,
        )

    @pytest.mark.asyncio
    async def test_start_and_stop(self, bridge):
        await bridge.start()
        assert bridge.healthy is True
        assert bridge._listen_task is not None
        assert bridge._health_task is not None

        await bridge.stop()
        assert bridge.healthy is False
        assert bridge._listen_task is None
        assert bridge._health_task is None

    @pytest.mark.asyncio
    async def test_publish_convenience(self, bridge, mock_redis):
        msg = PushMessage(
            channel="config:dev:auth", event_type="config_changed", data={}
        )
        await bridge.publish(msg)

        channel = "push:broadcast:config:dev:auth"
        assert channel in mock_redis._pubsub_channels

    @pytest.mark.asyncio
    async def test_instance_id(self, bridge):
        assert bridge.instance_id == "bridge-inst"

    @pytest.mark.asyncio
    async def test_setup_pubsub_subscribes_pattern(self, bridge):
        await bridge._setup_pubsub()
        assert bridge._pubsub is not None


# ======================================================================
# Manager lifecycle (start/stop)
# ======================================================================


class TestManagerLifecycle:
    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        manager = WebSocketConnectionManager(
            instance_id="lifecycle-inst",
            heartbeat_interval=9999,
        )
        await manager.start()
        assert manager._ack_task is not None

        ws = FakeWebSocket()
        await manager.connect(ws, "user1")

        await manager.stop()
        assert manager._ack_task is None
        assert manager.get_stats().active_connections == 0


# ======================================================================
# Integration: EventPublisher -> Manager broadcast
# ======================================================================


class TestIntegrationPublishToBroadcast:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """EventPublisher -> Redis -> PubSubBridge -> Manager -> WebSocket client."""
        buffer = InMemoryMessageBuffer()
        presence = InMemoryPresenceTracker()
        manager = WebSocketConnectionManager(
            presence_tracker=presence,
            message_buffer=buffer,
            instance_id="int-inst",
            heartbeat_interval=9999,
        )

        # Connect a client
        ws = FakeWebSocket()
        await manager.connect(ws, "user1")
        await manager.subscribe(ws, "config:dev:auth-svc")

        # Publish a config change
        mock_redis = MockRedis()
        publisher = EventPublisher(
            redis_client=mock_redis,
            message_buffer=buffer,
            instance_id="int-inst",
        )

        event = ConfigChangedEvent(
            config_id="cfg-1",
            config_key="db.host",
            environment="dev",
            service="auth-svc",
            change_type="update",
            version=2,
            changed_by="admin",
            timestamp=datetime.now(UTC),
        )
        await publisher.publish_config_changed(event)

        # Simulate PubSub bridge receiving the message and routing it
        channel = "push:broadcast:config:dev:auth-svc"
        raw_payload = mock_redis._pubsub_channels[channel][0]
        message = PushMessage.from_dict(json.loads(raw_payload))

        # Broadcast via manager (as the bridge would)
        delivered = await manager.broadcast("config:dev:auth-svc", message)
        assert delivered == 1
        assert len(ws.sent_messages) == 1

        payload = json.loads(ws.sent_messages[0])
        assert payload["type"] == "config_changed"
        assert payload["data"]["config_key"] == "db.host"
