"""logging_config.py 模块单元测试。"""

import logging
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from taolib.testing.logging_config import (
    RemoteLogHandler,
    SensitiveDataFilter,
    configure_logging,
    configure_remote_logging,
    get_logger,
)


class TestConfigureLogging(unittest.TestCase):
    """测试 configure_logging 函数。"""

    def setUp(self) -> None:
        """每个测试前重置日志配置。"""
        logging.root.handlers.clear()

    def tearDown(self) -> None:
        """每个测试后关闭并清除所有 handlers，避免 Windows 文件锁。"""
        for handler in logging.root.handlers[:]:
            handler.close()
        logging.root.handlers.clear()

    def test_default_level(self) -> None:
        """测试默认日志级别。"""
        configure_logging()
        logger = get_logger("test")
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)

    def test_custom_level(self) -> None:
        """测试自定义日志级别。"""
        configure_logging(level="DEBUG")
        logger = get_logger("test")
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)

    def test_file_output(self) -> None:
        """测试文件输出。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            configure_logging(level="DEBUG", log_file=log_file)

            logger = get_logger("test_file")
            logger.debug("test message")

            self.assertTrue(log_file.exists())
            content = log_file.read_text(encoding="utf-8")
            self.assertIn("test message", content)

            # Windows 下需在退出临时目录前关闭文件句柄，否则删除失败
            for handler in logging.root.handlers[:]:
                handler.close()
            logging.root.handlers.clear()

    def test_custom_format(self) -> None:
        """测试自定义格式。"""
        custom_format = "%(levelname)s: %(message)s"
        configure_logging(format_string=custom_format)

        logger = get_logger("test_format")
        handler = logger.handlers[0] if logger.handlers else logging.root.handlers[0]
        formatter = handler.formatter
        self.assertEqual(formatter._fmt, custom_format)

    def test_invalid_level_defaults_to_info(self) -> None:
        """测试无效级别默认为 INFO。"""
        configure_logging(level="INVALID")
        logger = get_logger("test")
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)

    def test_all_valid_log_levels(self) -> None:
        """测试所有有效的日志级别。"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        expected_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level, expected in zip(levels, expected_levels):
            logging.root.handlers.clear()
            configure_logging(level=level)
            logger = get_logger(f"test_{level}")
            self.assertEqual(logger.getEffectiveLevel(), expected)

    def test_log_file_creates_parent_directory(self) -> None:
        """测试日志文件会自动创建父目录。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "subdir" / "nested" / "test.log"
            self.assertFalse(log_file.parent.exists())

            configure_logging(level="DEBUG", log_file=log_file)
            logger = get_logger("test_nested")
            logger.debug("test nested message")

            self.assertTrue(log_file.exists())
            self.assertTrue(log_file.parent.exists())

            # Windows 下需在退出临时目录前关闭文件句柄
            for handler in logging.root.handlers[:]:
                handler.close()
            logging.root.handlers.clear()

    def test_log_file_as_string_path(self) -> None:
        """测试日志文件路径可以是字符串。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = f"{temp_dir}/test_string.log"
            configure_logging(level="DEBUG", log_file=log_file)

            logger = get_logger("test_string_path")
            logger.debug("test string path message")

            log_path = Path(log_file)
            self.assertTrue(log_path.exists())
            content = log_path.read_text(encoding="utf-8")
            self.assertIn("test string path message", content)

            for handler in logging.root.handlers[:]:
                handler.close()
            logging.root.handlers.clear()

    def test_custom_date_format(self) -> None:
        """测试自定义日期格式。"""
        custom_date_format = "%d/%m/%Y"
        configure_logging(date_format=custom_date_format)

        logger = get_logger("test_date")
        handler = logger.handlers[0] if logger.handlers else logging.root.handlers[0]
        formatter = handler.formatter
        self.assertEqual(formatter.datefmt, custom_date_format)

    def test_empty_logger_name(self) -> None:
        """测试空名称 logger 返回 root logger。"""
        logger = get_logger("")
        self.assertEqual(logger.name, "root")

    def test_logger_with_dots_in_name(self) -> None:
        """测试带点号的 logger 名称（模拟模块层次结构）。"""
        logger = get_logger("taolib.testing.remote.config")
        self.assertEqual(logger.name, "taolib.testing.remote.config")
        self.assertIsInstance(logger, logging.Logger)


class TestGetLogger(unittest.TestCase):
    """测试 get_logger 函数。"""

    def test_get_logger_returns_logger(self) -> None:
        """测试返回 Logger 实例。"""
        logger = get_logger("test_module")
        self.assertIsInstance(logger, logging.Logger)

    def test_get_logger_same_name_returns_same_instance(self) -> None:
        """测试相同名称返回相同实例。"""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        self.assertIs(logger1, logger2)

    def test_get_logger_different_names(self) -> None:
        """测试不同名称返回不同实例。"""
        logger1 = get_logger("name1")
        logger2 = get_logger("name2")
        self.assertIsNot(logger1, logger2)


class TestRemoteLogHandler(unittest.TestCase):
    """测试 RemoteLogHandler 类。"""

    def setUp(self) -> None:
        """创建 handler 实例，flush_interval 设置极大以避免后台 daemon 干扰。"""
        self.handler = RemoteLogHandler(
            endpoint="http://localhost:8100/api/v1/logs/ingest",
            service="test-service",
            api_key="test-key",
            batch_size=5,
            flush_interval=999,
        )

    def tearDown(self) -> None:
        """关闭 handler 防止线程泄漏。"""
        self.handler.close()

    def test_constructor_starts_daemon_thread(self) -> None:
        """验证初始化时启动 daemon flush 线程。"""
        self.assertTrue(self.handler._flush_thread.is_alive())
        self.assertTrue(self.handler._flush_thread.daemon)

    def test_constructor_default_params(self) -> None:
        """验证属性正确赋值。"""
        self.assertEqual(
            self.handler.endpoint, "http://localhost:8100/api/v1/logs/ingest"
        )
        self.assertEqual(self.handler.service, "test-service")
        self.assertEqual(self.handler.api_key, "test-key")
        self.assertEqual(self.handler.batch_size, 5)
        self.assertEqual(self.handler.flush_interval, 999)
        self.assertTrue(self.handler._running)
        self.assertEqual(self.handler._buffer, [])

    def test_close_stops_running_flag(self) -> None:
        """验证 close() 将 _running 置为 False。"""
        self.handler.close()
        self.assertFalse(self.handler._running)

    def test_close_flushes_remaining_buffer(self) -> None:
        """验证 close() 刷新缓冲区中的剩余日志。"""
        with patch.object(self.handler, "_send_logs") as mock_send:
            record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
            self.handler.emit(record)
            self.handler.close()
            mock_send.assert_called_once()

    def test_emit_appends_to_buffer(self) -> None:
        """验证 emit 将日志条目添加到缓冲区，字段完整。"""
        record = logging.LogRecord(
            "test.logger",
            logging.WARNING,
            "test.py",
            42,
            "hello %s",
            ("world",),
            None,
        )
        record.funcName = "test_func"
        self.handler.emit(record)

        self.assertEqual(len(self.handler._buffer), 1)
        entry = self.handler._buffer[0]
        self.assertEqual(entry["service"], "test-service")
        self.assertEqual(entry["level"], "WARNING")
        self.assertEqual(entry["message"], "hello world")
        self.assertEqual(entry["logger"], "test.logger")
        self.assertEqual(entry["function"], "test_func")
        self.assertEqual(entry["line"], 42)
        self.assertIn("timestamp", entry)
        self.assertNotIn("exception", entry)

    def test_emit_with_exception_info(self) -> None:
        """验证 exc_info 时生成 exception 字段。"""
        try:
            raise ValueError("boom")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            "test", logging.ERROR, "", 0, "error occurred", (), exc_info
        )
        self.handler.emit(record)

        self.assertEqual(len(self.handler._buffer), 1)
        self.assertIn("exception", self.handler._buffer[0])
        self.assertIn("ValueError: boom", self.handler._buffer[0]["exception"])

    def test_emit_triggers_flush_at_batch_size(self) -> None:
        """验证达到 batch_size 时自动触发 flush。"""
        with patch.object(self.handler, "_send_logs") as mock_send:
            for i in range(self.handler.batch_size):
                record = logging.LogRecord(
                    "test", logging.INFO, "", 0, f"msg-{i}", (), None
                )
                self.handler.emit(record)
            mock_send.assert_called_once()
            # flush 成功后 buffer 应为空
            self.assertEqual(len(self.handler._buffer), 0)

    def test_emit_below_batch_size_no_flush(self) -> None:
        """验证不够 batch_size 时不触发 flush。"""
        with patch.object(self.handler, "_send_logs") as mock_send:
            for i in range(self.handler.batch_size - 1):
                record = logging.LogRecord(
                    "test", logging.INFO, "", 0, f"msg-{i}", (), None
                )
                self.handler.emit(record)
            mock_send.assert_not_called()
            self.assertEqual(len(self.handler._buffer), self.handler.batch_size - 1)

    def test_emit_error_graceful_degradation(self) -> None:
        """验证 emit 内部异常时调用 handleError 而非崩溃。"""
        with patch.object(self.handler, "handleError") as mock_handle:
            with patch.object(
                self.handler._formatter,
                "formatTime",
                side_effect=RuntimeError("format fail"),
            ):
                record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
                self.handler.emit(record)
            mock_handle.assert_called_once()

    def test_flush_empty_buffer_noop(self) -> None:
        """验证空缓冲区 flush 不调用 _send_logs。"""
        with patch.object(self.handler, "_send_logs") as mock_send:
            self.handler._flush()
            mock_send.assert_not_called()

    def test_flush_clears_buffer_on_success(self) -> None:
        """验证 flush 成功后缓冲区清空。"""
        with patch.object(self.handler, "_send_logs"):
            self.handler._buffer = [{"msg": "test"}]
            self.handler._flush()
            self.assertEqual(len(self.handler._buffer), 0)

    def test_flush_failure_restores_buffer(self) -> None:
        """验证 _send_logs 抛异常时日志放回缓冲区。"""
        with patch.object(
            self.handler, "_send_logs", side_effect=ConnectionError("fail")
        ):
            self.handler._buffer = [{"msg": "log1"}, {"msg": "log2"}]
            self.handler._flush()
            # 日志应被放回
            self.assertEqual(len(self.handler._buffer), 2)
            self.assertEqual(self.handler._buffer[0]["msg"], "log1")

    def test_buffer_overflow_truncation(self) -> None:
        """验证缓冲区超过 batch_size*10 时截断到 batch_size*5。"""
        bs = self.handler.batch_size  # 5
        with patch.object(
            self.handler, "_send_logs", side_effect=ConnectionError("fail")
        ):
            # 填充 > batch_size*10 条
            self.handler._buffer = [{"msg": f"log-{i}"} for i in range(bs * 10 + 1)]
            self.handler._flush()
            self.assertEqual(len(self.handler._buffer), bs * 5)
            # 保留的是最新的 batch_size*5 条
            self.assertEqual(self.handler._buffer[-1]["msg"], f"log-{bs * 10}")

    def test_send_logs_httpx_missing(self) -> None:
        """验证 httpx 未安装时抛出 RuntimeError。"""
        with patch.dict(sys.modules, {"httpx": None}):
            with self.assertRaises(RuntimeError) as ctx:
                self.handler._send_logs([{"msg": "test"}])
            self.assertIn("log-client", str(ctx.exception))

    def test_send_logs_with_api_key(self) -> None:
        """验证带 api_key 时 headers 含 Authorization。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response

        with patch("httpx.Client", return_value=mock_client):
            self.handler._send_logs([{"msg": "test"}])

            call_kwargs = mock_client.post.call_args
            headers = call_kwargs.kwargs.get(
                "headers", call_kwargs[1].get("headers", {})
            )
            self.assertIn("Authorization", headers)
            self.assertEqual(headers["Authorization"], "Bearer test-key")

    def test_send_logs_without_api_key(self) -> None:
        """验证无 api_key 时 headers 不含 Authorization。"""
        handler = RemoteLogHandler(
            endpoint="http://localhost:8100/api/v1/logs/ingest",
            service="test-service",
            api_key=None,
            batch_size=5,
            flush_interval=999,
        )
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response

        with patch("httpx.Client", return_value=mock_client):
            handler._send_logs([{"msg": "test"}])

            call_kwargs = mock_client.post.call_args
            headers = call_kwargs.kwargs.get(
                "headers", call_kwargs[1].get("headers", {})
            )
            self.assertNotIn("Authorization", headers)
        handler.close()

    def test_flush_loop_respects_running(self) -> None:
        """验证 _running=False 时 flush_loop 退出。"""
        handler = RemoteLogHandler(
            endpoint="http://localhost:8100/test",
            service="test",
            flush_interval=0.05,
        )
        # 让线程运行一小段时间
        time.sleep(0.1)
        self.assertTrue(handler._flush_thread.is_alive())
        handler._running = False
        handler._flush_thread.join(timeout=2.0)
        self.assertFalse(handler._flush_thread.is_alive())
        handler.close()


class TestConfigureRemoteLogging(unittest.TestCase):
    """测试 configure_remote_logging 函数。"""

    def setUp(self) -> None:
        """重置 root logger。"""
        logging.root.handlers.clear()
        self._handlers_to_close: list[logging.Handler] = []

    def tearDown(self) -> None:
        """关闭所有 handler 防止线程泄漏。"""
        for handler in self._handlers_to_close:
            handler.close()
        for handler in logging.root.handlers[:]:
            handler.close()
        logging.root.handlers.clear()

    def test_returns_handler_instance(self) -> None:
        """验证返回 RemoteLogHandler 实例。"""
        handler = configure_remote_logging(
            endpoint="http://localhost:8100/test",
            service="test",
            flush_interval=999,
        )
        self._handlers_to_close.append(handler)
        self.assertIsInstance(handler, RemoteLogHandler)

    def test_adds_handler_to_root_logger(self) -> None:
        """验证 RemoteLogHandler 被添加到 root logger。"""
        handler = configure_remote_logging(
            endpoint="http://localhost:8100/test",
            service="test",
            flush_interval=999,
        )
        self._handlers_to_close.append(handler)
        remote_handlers = [
            h for h in logging.root.handlers if isinstance(h, RemoteLogHandler)
        ]
        self.assertEqual(len(remote_handlers), 1)

    def test_configures_local_logging(self) -> None:
        """验证同时配置了本地 StreamHandler。"""
        handler = configure_remote_logging(
            endpoint="http://localhost:8100/test",
            service="test",
            flush_interval=999,
        )
        self._handlers_to_close.append(handler)
        stream_handlers = [
            h
            for h in logging.root.handlers
            if isinstance(h, logging.StreamHandler)
            and not isinstance(h, RemoteLogHandler)
        ]
        self.assertGreaterEqual(len(stream_handlers), 1)

    def test_with_log_file(self) -> None:
        """验证同时有文件和远程 handler。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "remote_test.log"
            handler = configure_remote_logging(
                endpoint="http://localhost:8100/test",
                service="test",
                flush_interval=999,
                log_file=log_file,
            )
            self._handlers_to_close.append(handler)

            file_handlers = [
                h for h in logging.root.handlers if isinstance(h, logging.FileHandler)
            ]
            remote_handlers = [
                h for h in logging.root.handlers if isinstance(h, RemoteLogHandler)
            ]
            self.assertEqual(len(file_handlers), 1)
            self.assertEqual(len(remote_handlers), 1)

            # 关闭文件 handler 防止 Windows 文件锁
            for h in logging.root.handlers[:]:
                h.close()
            logging.root.handlers.clear()


class TestConfigureLoggingEdgeCases(unittest.TestCase):
    """测试 configure_logging 的边界场景。"""

    def setUp(self) -> None:
        logging.root.handlers.clear()

    def tearDown(self) -> None:
        for handler in logging.root.handlers[:]:
            handler.close()
        logging.root.handlers.clear()

    def test_force_replaces_existing_handlers(self) -> None:
        """验证 force=True 不会重复添加 handler。"""
        configure_logging(level="INFO")
        count_before = len(logging.root.handlers)
        configure_logging(level="DEBUG")
        count_after = len(logging.root.handlers)
        # basicConfig(force=True) 应替换而非累加
        self.assertEqual(count_before, count_after)

    def test_console_handler_uses_stdout(self) -> None:
        """验证 StreamHandler 输出到 sys.stdout。"""
        configure_logging()
        stream_handlers = [
            h for h in logging.root.handlers if isinstance(h, logging.StreamHandler)
        ]
        self.assertGreaterEqual(len(stream_handlers), 1)
        self.assertIs(stream_handlers[0].stream, sys.stdout)

    def test_file_handler_utf8_encoding(self) -> None:
        """验证 FileHandler 使用 utf-8 编码。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "encoding_test.log"
            configure_logging(log_file=log_file)

            file_handlers = [
                h for h in logging.root.handlers if isinstance(h, logging.FileHandler)
            ]
            self.assertEqual(len(file_handlers), 1)
            self.assertEqual(file_handlers[0].encoding, "utf-8")

            for h in logging.root.handlers[:]:
                h.close()
            logging.root.handlers.clear()

    def test_sequential_level_changes(self) -> None:
        """验证连续切换级别，最后一次生效。"""
        configure_logging(level="DEBUG")
        configure_logging(level="ERROR")
        configure_logging(level="WARNING")
        self.assertEqual(logging.root.level, logging.WARNING)


class TestSensitiveDataFilter(unittest.TestCase):
    """测试 SensitiveDataFilter 类。"""

    def setUp(self) -> None:
        """每个测试前重置日志配置。"""
        logging.root.handlers.clear()
        logging.root.filters.clear()

    def tearDown(self) -> None:
        """每个测试后清除所有 filters。"""
        logging.root.filters.clear()
        for handler in logging.root.handlers[:]:
            handler.close()
        logging.root.handlers.clear()

    def test_password_masking(self) -> None:
        """测试密码脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "password=secret123", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "password=***")

    def test_password_with_quotes(self) -> None:
        """测试带引号的密码脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, 'password: "my_secret"', (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, 'password: "***"')

    def test_passwd_variant(self) -> None:
        """测试 passwd 变体脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "passwd=admin123", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "passwd=***")

    def test_pwd_variant(self) -> None:
        """测试 pwd 变体脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "pwd test123", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "pwd ***")

    def test_jwt_secret_masking(self) -> None:
        """测试 JWT 密钥脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "jwt_secret=myjwtkey123", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "jwt_secret=***")

    def test_api_key_masking(self) -> None:
        """测试 API 密钥脱敏（保留前4位和后4位）。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "api_key=abcd1234efgh5678ijkl", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "api_key=abcd***ijkl")

    def test_api_key_short(self) -> None:
        """测试短 API 密钥完全隐藏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "api_key=short", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "api_key=***")

    def test_email_masking(self) -> None:
        """测试邮箱脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "user@example.com logged in", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "u***@example.com logged in")

    def test_email_short_local(self) -> None:
        """测试短本地部分邮箱脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "a@b.com", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "***@b.com")

    def test_phone_masking(self) -> None:
        """测试手机号脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "phone: 13812345678", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "phone: 138***5678")

    def test_ip_masking(self) -> None:
        """测试 IP 地址脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "client IP: 192.168.1.100", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "client IP: 192.168.***")

    def test_multiple_sensitive_data(self) -> None:
        """测试多种敏感数据同时存在。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test",
            logging.INFO,
            "",
            0,
            "user=test@example.com, password=secret, ip=10.0.0.1",
            (),
            None,
        )
        filter_obj.filter(record)
        self.assertIn("***@example.com", record.msg)
        self.assertIn("password=***", record.msg)
        self.assertIn("10.0.***", record.msg)

    def test_disable_password_masking(self) -> None:
        """测试禁用密码脱敏。"""
        filter_obj = SensitiveDataFilter(enable_password=False)
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "password=secret123", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "password=secret123")

    def test_disable_email_masking(self) -> None:
        """测试禁用邮箱脱敏。"""
        filter_obj = SensitiveDataFilter(enable_email=False)
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "user@example.com", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "user@example.com")

    def test_custom_rules(self) -> None:
        """测试自定义脱敏规则。"""
        filter_obj = SensitiveDataFilter(
            custom_rules=[(r"token=\w+", "token=REDACTED")]
        )
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "token=abc123xyz", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "token=REDACTED")

    def test_filter_with_args_tuple(self) -> None:
        """测试带元组参数的日志记录。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "User %s logged in", ("test@example.com",), None
        )
        filter_obj.filter(record)
        self.assertIn("***@example.com", record.args[0])

    def test_filter_with_args_dict(self) -> None:
        """测试带字典参数的日志记录。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test",
            logging.INFO,
            "",
            0,
            "User %(email)s logged in",
            ({"email": "test@example.com"},),
            None,
        )
        filter_obj.filter(record)
        self.assertIn("***@example.com", record.args["email"])

    def test_configure_logging_with_sanitize(self) -> None:
        """测试 configure_logging 启用脱敏。"""
        sanitize_filter = configure_logging(enable_sanitize=True)
        self.assertIsInstance(sanitize_filter, SensitiveDataFilter)
        self.assertIn(sanitize_filter, logging.root.filters)

    def test_configure_logging_without_sanitize(self) -> None:
        """测试 configure_logging 禁用脱敏。"""
        sanitize_filter = configure_logging(enable_sanitize=False)
        self.assertIsNone(sanitize_filter)
        self.assertEqual(len(logging.root.filters), 0)

    def test_configure_logging_with_sanitize_config(self) -> None:
        """测试 configure_logging 自定义脱敏配置。"""
        sanitize_filter = configure_logging(
            enable_sanitize=True,
            sanitize_config={"enable_phone": False, "enable_ip": False},
        )
        self.assertIsInstance(sanitize_filter, SensitiveDataFilter)
        self.assertFalse(sanitize_filter.enable_phone)
        self.assertFalse(sanitize_filter.enable_ip)

    def test_chinese_password_field(self) -> None:
        """测试中文密码字段脱敏。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            "test", logging.INFO, "", 0, "密码=我的密码123", (), None
        )
        filter_obj.filter(record)
        self.assertEqual(record.msg, "密码=***")

    def test_non_string_message(self) -> None:
        """测试非字符串消息不崩溃。"""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, 12345, (), None)
        result = filter_obj.filter(record)
        self.assertTrue(result)
        self.assertEqual(record.msg, 12345)


if __name__ == "__main__":
    unittest.main()



