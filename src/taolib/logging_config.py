"""日志配置模块。

提供统一的日志配置功能，支持控制台、文件输出和远程日志平台。
"""

import json
import logging
import os
import re
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Literal

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class JSONFormatter(logging.Formatter):
    """JSON 行格式日志格式化器。

    输出每行一个 JSON 对象，便于 ELK/Loki 等日志聚合系统解析。

    Args:
        service: 服务名称，写入每条日志的 ``service`` 字段。
        datefmt: 时间格式字符串，默认为 ISO 8601。
    """

    def __init__(self, service: str = "", datefmt: str | None = None) -> None:
        super().__init__(datefmt=datefmt)
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if self.service:
            entry["service"] = self.service
        if record.module:
            entry["module"] = record.module
        if record.funcName:
            entry["function"] = record.funcName
        entry["line"] = record.lineno
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "request_id"):
            entry["request_id"] = record.request_id
        return json.dumps(entry, ensure_ascii=False, default=str)


class SensitiveDataFilter(logging.Filter):
    """日志敏感数据脱敏过滤器。

    对日志消息中的敏感数据进行脱敏处理，支持密码、JWT密钥、API密钥、
    邮箱、手机号和IP地址等多种敏感数据类型。

    Args:
        enable_password: 是否启用密码脱敏，默认为 True。
        enable_jwt: 是否启用 JWT 密钥脱敏，默认为 True。
        enable_api_key: 是否启用 API 密钥脱敏，默认为 True。
        enable_email: 是否启用邮箱脱敏，默认为 True。
        enable_phone: 是否启用手机号脱敏，默认为 True。
        enable_ip: 是否启用 IP 地址脱敏，默认为 True。
        custom_rules: 自定义脱敏规则列表，每条规则为 (pattern, replacement) 元组。

    Example:
        >>> filter = SensitiveDataFilter()
        >>> logger = logging.getLogger("test")
        >>> logger.addFilter(filter)
        >>> logger.info("password=secret123")  # 输出: password=***
    """

    def __init__(
        self,
        enable_password: bool = True,
        enable_jwt: bool = True,
        enable_api_key: bool = True,
        enable_email: bool = True,
        enable_phone: bool = True,
        enable_ip: bool = True,
        custom_rules: list[tuple[str, str]] | None = None,
    ) -> None:
        super().__init__()
        self.enable_password = enable_password
        self.enable_jwt = enable_jwt
        self.enable_api_key = enable_api_key
        self.enable_email = enable_email
        self.enable_phone = enable_phone
        self.enable_ip = enable_ip
        self.custom_rules = custom_rules or []

        self._patterns: list[tuple[re.Pattern, Callable[[re.Match], str]]] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """编译所有启用的脱敏模式。"""
        if self.enable_password:
            self._patterns.append(
                (
                    re.compile(
                        r'(password|passwd|pwd|密码)(["\s:=]+)(["\']?)([^"\'\s,;}\]]+)\3',
                        re.IGNORECASE,
                    ),
                    lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}***{m.group(3)}',
                )
            )

        if self.enable_jwt:
            self._patterns.append(
                (
                    re.compile(
                        r'(jwt[_-]?secret|jwt[_-]?key|secret[_-]?key)(["\s:=]+)(["\']?)([^"\'\s,;}\]]+)\3',
                        re.IGNORECASE,
                    ),
                    lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}***{m.group(3)}',
                )
            )

        if self.enable_api_key:
            self._patterns.append(
                (
                    re.compile(
                        r'(api[_-]?key|apikey|access[_-]?key)(["\s:=]+)(["\']?)([a-zA-Z0-9_-]+)\3',
                        re.IGNORECASE,
                    ),
                    self._mask_api_key,
                )
            )

        if self.enable_email:
            self._patterns.append(
                (
                    re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'),
                    self._mask_email,
                )
            )

        if self.enable_phone:
            self._patterns.append(
                (
                    re.compile(r'\b(1[3-9]\d)(\d{4})(\d{4})\b'),
                    lambda m: f'{m.group(1)}***{m.group(3)}',
                )
            )

        if self.enable_ip:
            self._patterns.append(
                (
                    re.compile(r'\b(\d{1,3}\.\d{1,3})\.(\d{1,3}\.\d{1,3})\b'),
                    lambda m: f'{m.group(1)}.***',
                )
            )

        for pattern, replacement in self.custom_rules:
            self._patterns.append((re.compile(pattern), lambda m, r=replacement: r))

    def _mask_api_key(self, match: re.Match) -> str:
        """对 API 密钥进行脱敏处理。

        Args:
            match: 正则匹配对象。

        Returns:
            脱敏后的字符串，保留前4位和后4位。
        """
        prefix = match.group(1)
        separator = match.group(2)
        quote = match.group(3) or ""
        key = match.group(4)

        masked = "***" if len(key) <= 8 else f"{key[:4]}***{key[-4:]}"

        return f'{prefix}{separator}{quote}{masked}{quote}'

    def _mask_email(self, match: re.Match) -> str:
        """对邮箱地址进行脱敏处理。

        Args:
            match: 正则匹配对象。

        Returns:
            脱敏后的字符串，保留首字符和域名。
        """
        local = match.group(1)
        domain = match.group(2)

        masked_local = "***" if len(local) <= 1 else f"{local[0]}***"

        return f"{masked_local}@{domain}"

    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录，对敏感数据进行脱敏。

        Args:
            record: 日志记录对象。

        Returns:
            始终返回 True，允许所有日志记录通过。
        """
        if record.msg and isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)

        if record.args:
            record.args = self._sanitize_args(record.args)

        return True

    def _sanitize(self, message: str) -> str:
        """对消息进行脱敏处理。

        Args:
            message: 原始消息字符串。

        Returns:
            脱敏后的消息字符串。
        """
        result = message
        for pattern, replacer in self._patterns:
            result = pattern.sub(replacer, result)
        return result

    def _sanitize_args(self, args: tuple | dict) -> tuple | dict:
        """对日志参数进行脱敏处理。

        Args:
            args: 日志参数，可以是元组或字典。

        Returns:
            脱敏后的参数。
        """
        if isinstance(args, dict):
            return {k: self._sanitize_value(v) for k, v in args.items()}
        elif isinstance(args, tuple):
            return tuple(self._sanitize_value(arg) for arg in args)
        return args

    def _sanitize_value(self, value) -> str:
        """对单个值进行脱敏处理。

        Args:
            value: 原始值。

        Returns:
            脱敏后的字符串表示。
        """
        if isinstance(value, str):
            return self._sanitize(value)
        return value


def configure_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    log_file: Path | str | None = None,
    format_string: str | None = None,
    date_format: str | None = None,
    enable_sanitize: bool = True,
    sanitize_config: dict | None = None,
    format_mode: Literal["text", "json"] | None = None,
    service: str = "",
) -> SensitiveDataFilter | None:
    """配置日志系统。

    Args:
        level: 日志级别，默认为 "INFO"。
        log_file: 日志文件路径，如果为 None 则只输出到控制台。
        format_string: 日志格式字符串，如果为 None 则使用默认格式。仅 text 模式生效。
        date_format: 日期格式字符串，如果为 None 则使用默认格式。
        enable_sanitize: 是否启用敏感数据脱敏，默认为 True。
        sanitize_config: 脱敏配置字典，支持以下键：
            - enable_password: 是否启用密码脱敏
            - enable_jwt: 是否启用 JWT 密钥脱敏
            - enable_api_key: 是否启用 API 密钥脱敏
            - enable_email: 是否启用邮箱脱敏
            - enable_phone: 是否启用手机号脱敏
            - enable_ip: 是否启用 IP 地址脱敏
            - custom_rules: 自定义脱敏规则列表
        format_mode: 日志输出格式，``"text"``（默认）或 ``"json"``。
            设为 ``None`` 时读取环境变量 ``LOG_FORMAT``，未设置则默认 ``"text"``。
        service: 服务名称，仅 json 模式下写入日志。

    Returns:
        如果启用脱敏，返回 SensitiveDataFilter 实例；否则返回 None。

    Example:
        >>> configure_logging(level="DEBUG", enable_sanitize=True)
        >>> configure_logging(format_mode="json", service="config-center")
    """
    if format_mode is None:
        format_mode = os.environ.get("LOG_FORMAT", "text")  # type: ignore[assignment]

    log_level = getattr(logging, level.upper(), logging.INFO)
    log_date_fmt = date_format or _DATE_FORMAT
    use_json = format_mode == "json"

    if use_json:
        formatter: logging.Formatter = JSONFormatter(service=service, datefmt=log_date_fmt)
    else:
        log_fmt = format_string or _LOG_FORMAT
        formatter = logging.Formatter(log_fmt, datefmt=log_date_fmt)

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True,
    )

    sanitize_filter: SensitiveDataFilter | None = None
    if enable_sanitize:
        sanitize_filter = SensitiveDataFilter(
            **(sanitize_config or {})
        )
        root_logger = logging.getLogger()
        root_logger.addFilter(sanitize_filter)

    return sanitize_filter


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器。

    Args:
        name: 日志记录器名称，通常使用 __name__。

    Returns:
        配置好的 Logger 实例。
    """
    return logging.getLogger(name)


class RemoteLogHandler(logging.Handler):
    """远程日志平台 Handler。

    将日志记录通过 HTTP 发送到远程日志平台，支持批量发送和优雅降级。

    Args:
        endpoint: 远程日志平台的 HTTP 端点 URL。
        service: 当前服务的名称。
        api_key: API 认证密钥（可选）。
        batch_size: 批量发送的日志条数，默认为 50。
        flush_interval: 刷新间隔（秒），默认为 5.0。
        level: 日志级别，默认为 INFO。

    Example:
        >>> from taolib.logging_config import RemoteLogHandler
        >>> handler = RemoteLogHandler(
        ...     endpoint="http://localhost:8100/api/v1/logs/ingest",
        ...     service="my-app",
        ... )
        >>> logging.getLogger().addHandler(handler)
    """

    def __init__(
        self,
        endpoint: str,
        service: str,
        api_key: str | None = None,
        batch_size: int = 50,
        flush_interval: float = 5.0,
        level: int = logging.INFO,
    ) -> None:
        super().__init__(level)
        self.endpoint = endpoint
        self.service = service
        self.api_key = api_key
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._buffer: list[dict] = []
        self._lock = threading.RLock()
        self._running = True
        self._formatter = logging.Formatter(datefmt=_DATE_FORMAT)
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()

    def emit(self, record: logging.LogRecord) -> None:
        """发送日志记录到远程平台。

        Args:
            record: 日志记录对象。
        """
        try:
            log_entry = {
                "timestamp": self._formatter.formatTime(record, _DATE_FORMAT),
                "service": self.service,
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            if record.exc_info and record.exc_info[0] is not None:
                log_entry["exception"] = self._formatter.formatException(
                    record.exc_info
                )

            with self._lock:
                self._buffer.append(log_entry)
                if len(self._buffer) >= self.batch_size:
                    self._flush()

        except Exception:
            # 优雅降级：远程日志失败不影响应用
            self.handleError(record)

    def _flush_loop(self) -> None:
        """定期刷新缓冲区。"""
        while self._running:
            time.sleep(self.flush_interval)
            self._flush()

    def _flush(self) -> None:
        """将缓冲区日志发送到远程平台。"""
        with self._lock:
            if not self._buffer:
                return
            logs_to_send = self._buffer[:]
            self._buffer.clear()

        try:
            self._send_logs(logs_to_send)
        except Exception:
            # 发送失败，将日志放回缓冲区
            with self._lock:
                self._buffer[:0] = logs_to_send
                # 防止缓冲区无限增长
                if len(self._buffer) > self.batch_size * 10:
                    self._buffer = self._buffer[-self.batch_size * 5 :]

    def _send_logs(self, logs: list[dict]) -> None:
        """发送日志到远程平台。

        Args:
            logs: 日志条目列表。

        Raises:
            Exception: 如果发送失败。
        """
        # 延迟导入，避免在未安装 log-client 依赖时出错
        try:
            import httpx
        except ImportError:
            raise RuntimeError(
                "需要安装 log-client 依赖: pip install taolib[log-client]"
            )

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "logs": logs,
            "source": self.service,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()

    def close(self) -> None:
        """关闭 Handler 并刷新缓冲区。"""
        self._running = False
        self._flush()
        super().close()


def configure_remote_logging(
    endpoint: str,
    service: str,
    api_key: str | None = None,
    batch_size: int = 50,
    flush_interval: float = 5.0,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    log_file: Path | str | None = None,
) -> RemoteLogHandler:
    """配置同时输出到本地和远程日志平台。

    该函数会先调用 configure_logging() 配置本地日志输出，
    然后添加 RemoteLogHandler 到 root logger。

    Args:
        endpoint: 远程日志平台的 HTTP 端点 URL。
        service: 当前服务的名称。
        api_key: API 认证密钥（可选）。
        batch_size: 批量发送的日志条数，默认为 50。
        flush_interval: 刷新间隔（秒），默认为 5.0。
        level: 日志级别，默认为 "INFO"。
        log_file: 本地日志文件路径，如果为 None 则只输出到控制台。

    Returns:
        配置好的 RemoteLogHandler 实例。

    Example:
        >>> from taolib.logging_config import configure_remote_logging
        >>> handler = configure_remote_logging(
        ...     endpoint="http://localhost:8100/api/v1/logs/ingest",
        ...     service="my-app",
        ... )
    """
    # 配置本地日志
    configure_logging(level=level, log_file=log_file)

    # 创建并添加远程日志 Handler
    log_level = getattr(logging, level.upper(), logging.INFO)
    remote_handler = RemoteLogHandler(
        endpoint=endpoint,
        service=service,
        api_key=api_key,
        batch_size=batch_size,
        flush_interval=flush_interval,
        level=log_level,
    )

    logging.getLogger().addHandler(remote_handler)

    return remote_handler
