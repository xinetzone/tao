"""Ollama本地模型提供商。

集成Ollama本地运行的大模型,无需API KEY。
"""

import asyncio
import time
from typing import AsyncGenerator
from datetime import UTC, datetime

import httpx

from taolib.testing.multi_agent.errors import (
    LLMError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from taolib.testing.multi_agent.llm.protocols import BaseLLMProvider
from taolib.testing.multi_agent.models import ModelConfig, ModelStatus


class OllamaProvider(BaseLLMProvider):
    """Ollama本地模型提供商。"""

    def __init__(self, config: ModelConfig):
        """初始化Ollama提供商。

        Args:
            config: 模型配置
        """
        super().__init__(config)
        self._base_url = config.base_url or "http://localhost:11434"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端。

        Returns:
            httpx.AsyncClient: HTTP客户端
        """
        if self._client is None:
            timeout = httpx.Timeout(self._config.timeout_seconds)
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=timeout)
        return self._client

    async def health_check(self) -> bool:
        """检查Ollama服务是否健康可用。

        Returns:
            bool: 服务是否健康
        """
        from datetime import UTC, datetime

        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            is_healthy = response.status_code == 200

            if is_healthy:
                self._stats.last_health_check_at = datetime.now(UTC)
                self._stats.last_error_at = None
                self._stats.last_error_message = ""
            else:
                self._stats.last_error_at = datetime.now(UTC)
                self._stats.last_error_message = f"HTTP {response.status_code}"

            return is_healthy
        except Exception as e:
            from datetime import UTC, datetime

            self._stats.last_error_at = datetime.now(UTC)
            self._stats.last_error_message = str(e)
            return False

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs,
    ) -> str:
        """使用Ollama生成文本。

        Args:
            prompt: 用户输入的提示词
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_prompt: 系统提示词
            **kwargs: 其他参数

        Returns:
            str: 生成的文本

        Raises:
            ModelUnavailableError: 模型不可用
            ModelTimeoutError: 请求超时
            LLMError: 其他生成错误
        """
        start_time = time.time()
        temp = temperature if temperature is not None else self._config.temperature
        max_toks = max_tokens if max_tokens is not None else self._config.max_tokens

        try:
            client = await self._get_client()

            messages = []
            if system_prompt or self._config.system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt or self._config.system_prompt,
                })
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self._config.model_name,
                "messages": messages,
                "stream": False,
                "options": {},
            }

            if temp is not None:
                payload["options"]["temperature"] = temp
            if max_toks is not None:
                payload["options"]["num_predict"] = max_toks

            response = await client.post("/api/chat", json=payload)

            if response.status_code != 200:
                self._update_stats_failure()
                raise LLMError(f"Ollama API error: {response.status_code} - {response.text}")

            result = response.json()
            generated_text = result.get("message", {}).get("content", "")

            latency = time.time() - start_time
            self._update_stats_success(latency)

            return generated_text

        except httpx.TimeoutException as e:
            self._update_stats_failure()
            raise ModelTimeoutError(f"Ollama request timed out: {e}")
        except httpx.ConnectError as e:
            self._update_stats_failure()
            raise ModelUnavailableError(f"Cannot connect to Ollama: {e}")
        except Exception as e:
            self._update_stats_failure()
            raise LLMError(f"Ollama generation failed: {e}")

    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """使用Ollama流式生成文本。

        Args:
            prompt: 用户输入的提示词
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_prompt: 系统提示词
            **kwargs: 其他参数

        Yields:
            str: 生成的文本片段

        Raises:
            ModelUnavailableError: 模型不可用
            ModelTimeoutError: 请求超时
            LLMError: 其他生成错误
        """
        start_time = time.time()
        temp = temperature if temperature is not None else self._config.temperature
        max_toks = max_tokens if max_tokens is not None else self._config.max_tokens

        try:
            client = await self._get_client()

            messages = []
            if system_prompt or self._config.system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt or self._config.system_prompt,
                })
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self._config.model_name,
                "messages": messages,
                "stream": True,
                "options": {},
            }

            if temp is not None:
                payload["options"]["temperature"] = temp
            if max_toks is not None:
                payload["options"]["num_predict"] = max_toks

            async with client.stream("POST", "/api/chat", json=payload) as response:
                if response.status_code != 200:
                    self._update_stats_failure()
                    raise LLMError(f"Ollama API error: {response.status_code}")

                full_text = ""
                async for line in response.aiter_lines():
                    if line.strip():
                        import json
                        data = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            full_text += chunk
                            yield chunk

                latency = time.time() - start_time
                self._update_stats_success(latency)

        except httpx.TimeoutException as e:
            self._update_stats_failure()
            raise ModelTimeoutError(f"Ollama stream timed out: {e}")
        except httpx.ConnectError as e:
            self._update_stats_failure()
            raise ModelUnavailableError(f"Cannot connect to Ollama: {e}")
        except Exception as e:
            self._update_stats_failure()
            raise LLMError(f"Ollama stream generation failed: {e}")

    async def close(self) -> None:
        """关闭HTTP客户端。"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
