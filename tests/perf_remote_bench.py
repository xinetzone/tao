import json
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from taolib.remote import (
    DEFAULT_PROBE_CMD,
    RemoteExecutionError,
    RemoteProbeCommands,
    RemoteProbeRunOptions,
    RemoteProber,
    load_ssh_config,
    remote_prefixes,
)


@dataclass(slots=True)
class FakeResult:
    stdout: str = ""
    ok: bool = True
    exited: int = 0


class FakeConnectionLatency:
    def __init__(
        self,
        *,
        latency_s: float,
        conda_ok: bool,
        probe_ok: bool,
        uname_stdout: str = "Linux fake 1.0\n",
        **ssh_config: Any,
    ) -> None:
        self.ssh_config = ssh_config
        self.latency_s = latency_s
        self.conda_ok = conda_ok
        self.probe_ok = probe_ok
        self.uname_stdout = uname_stdout
        self.prefix_stack: list[str] = []
        self.run_count = 0

    def __enter__(self) -> "FakeConnectionLatency":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    @contextmanager
    def prefix(self, command: str):
        self.prefix_stack.append(command)
        try:
            yield
        finally:
            self.prefix_stack.pop()

    def run(self, command: str, **kwargs: Any) -> FakeResult:
        self.run_count += 1
        if self.latency_s:
            time.sleep(self.latency_s)
        if command == "uname -a":
            return FakeResult(stdout=self.uname_stdout, ok=True, exited=0)
        if command == "command -v conda":
            return FakeResult(
                stdout="/usr/bin/conda\n" if self.conda_ok else "",
                ok=self.conda_ok,
                exited=0 if self.conda_ok else 1,
            )
        if command == DEFAULT_PROBE_CMD:
            return FakeResult(stdout="", ok=self.probe_ok, exited=0 if self.probe_ok else 1)
        if "|| exit 127" in command and "command -v conda" in command and DEFAULT_PROBE_CMD in command:
            if not self.conda_ok:
                return FakeResult(stdout="", ok=False, exited=127)
            if self.probe_ok:
                return FakeResult(stdout="", ok=True, exited=0)
            return FakeResult(stdout="", ok=False, exited=1)
        return FakeResult(stdout="", ok=True, exited=0)


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return d0 + d1


def legacy_probe(conn: FakeConnectionLatency, commands: RemoteProbeCommands, options: RemoteProbeRunOptions) -> None:
    merged_run_kwargs = options.merged_run_kwargs()
    uname_result = conn.run(commands.uname_cmd, **{"hide": True, **merged_run_kwargs})
    uname = (getattr(uname_result, "stdout", "") or "").strip()
    if not uname:
        raise RemoteExecutionError("uname 输出为空", command=commands.uname_cmd)

    with remote_prefixes(conn, commands.tools_env_cmd, commands.conda_activate_cmd):
        conda_result = conn.run(commands.check_conda_cmd, **{"warn": True, "hide": True, **merged_run_kwargs})
        if not getattr(conda_result, "ok", False):
            if options.raise_on_conda_missing:
                raise RemoteExecutionError("conda 不可用或未找到", command=commands.check_conda_cmd)
            return

        probe_result = conn.run(commands.probe_cmd, **{"warn": True, **merged_run_kwargs})
        if options.raise_on_probe_failure and not getattr(probe_result, "ok", False):
            raise RemoteExecutionError("探测命令执行失败", command=commands.probe_cmd)


def _bench(fn, iterations: int) -> list[float]:
    samples: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
    return samples


def _summarize(samples: Iterable[float]) -> dict[str, float]:
    values = sorted(float(x) for x in samples)
    return {
        "n": float(len(values)),
        "mean_ms": mean(values) * 1000.0 if values else 0.0,
        "p50_ms": median(values) * 1000.0 if values else 0.0,
        "p95_ms": _percentile(values, 95) * 1000.0 if values else 0.0,
    }


def bench_probe_success(*, iterations: int = 200, latency_ms: float = 3.0) -> dict[str, Any]:
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions()
    latency_s = latency_ms / 1000.0

    def _run_new() -> int:
        conn = FakeConnectionLatency(latency_s=latency_s, conda_ok=True, probe_ok=True, host="h", user="u")
        prober = RemoteProber(connection_factory=lambda **kw: conn, commands=commands, options=options)
        prober.probe({"host": "h", "user": "u"})
        return conn.run_count

    def _run_legacy() -> int:
        conn = FakeConnectionLatency(latency_s=latency_s, conda_ok=True, probe_ok=True, host="h", user="u")
        legacy_probe(conn, commands, options)
        return conn.run_count

    new_run_counts: list[int] = []
    legacy_run_counts: list[int] = []

    def _new_once() -> None:
        new_run_counts.append(_run_new())

    def _legacy_once() -> None:
        legacy_run_counts.append(_run_legacy())

    new_samples = _bench(_new_once, iterations)
    legacy_samples = _bench(_legacy_once, iterations)

    return {
        "probe_success": {
            "latency_ms_per_run": latency_ms,
            "iterations": iterations,
            "new": {**_summarize(new_samples), "mean_run_calls": mean(new_run_counts)},
            "legacy": {**_summarize(legacy_samples), "mean_run_calls": mean(legacy_run_counts)},
        }
    }


def bench_probe_conda_missing(*, iterations: int = 200, latency_ms: float = 3.0) -> dict[str, Any]:
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions(raise_on_conda_missing=False, raise_on_probe_failure=False)
    latency_s = latency_ms / 1000.0

    def _run_new() -> int:
        conn = FakeConnectionLatency(latency_s=latency_s, conda_ok=False, probe_ok=True, host="h", user="u")
        prober = RemoteProber(connection_factory=lambda **kw: conn, commands=commands, options=options)
        prober.probe({"host": "h", "user": "u"})
        return conn.run_count

    def _run_legacy() -> int:
        conn = FakeConnectionLatency(latency_s=latency_s, conda_ok=False, probe_ok=True, host="h", user="u")
        legacy_probe(conn, commands, options)
        return conn.run_count

    new_run_counts: list[int] = []
    legacy_run_counts: list[int] = []

    def _new_once() -> None:
        new_run_counts.append(_run_new())

    def _legacy_once() -> None:
        legacy_run_counts.append(_run_legacy())

    new_samples = _bench(_new_once, iterations)
    legacy_samples = _bench(_legacy_once, iterations)

    return {
        "probe_conda_missing": {
            "latency_ms_per_run": latency_ms,
            "iterations": iterations,
            "new": {**_summarize(new_samples), "mean_run_calls": mean(new_run_counts)},
            "legacy": {**_summarize(legacy_samples), "mean_run_calls": mean(legacy_run_counts)},
        }
    }


def bench_probe_failure(*, iterations: int = 200, latency_ms: float = 3.0) -> dict[str, Any]:
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions(raise_on_conda_missing=False, raise_on_probe_failure=False)
    latency_s = latency_ms / 1000.0

    def _run_new() -> int:
        conn = FakeConnectionLatency(latency_s=latency_s, conda_ok=True, probe_ok=False, host="h", user="u")
        prober = RemoteProber(connection_factory=lambda **kw: conn, commands=commands, options=options)
        prober.probe({"host": "h", "user": "u"})
        return conn.run_count

    def _run_legacy() -> int:
        conn = FakeConnectionLatency(latency_s=latency_s, conda_ok=True, probe_ok=False, host="h", user="u")
        legacy_probe(conn, commands, options)
        return conn.run_count

    new_run_counts: list[int] = []
    legacy_run_counts: list[int] = []

    def _new_once() -> None:
        new_run_counts.append(_run_new())

    def _legacy_once() -> None:
        legacy_run_counts.append(_run_legacy())

    new_samples = _bench(_new_once, iterations)
    legacy_samples = _bench(_legacy_once, iterations)

    return {
        "probe_failure": {
            "latency_ms_per_run": latency_ms,
            "iterations": iterations,
            "new": {**_summarize(new_samples), "mean_run_calls": mean(new_run_counts)},
            "legacy": {**_summarize(legacy_samples), "mean_run_calls": mean(legacy_run_counts)},
        }
    }


def bench_load_ssh_config(*, iterations: int = 2000) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp_dir:
        cfg_path = Path(temp_dir) / "ssh.toml"
        cfg_path.write_text('host = "example.com"\nuser = "alice"\n[connect_kwargs]\npassword = "p"\n', encoding="utf-8")

        def _once() -> None:
            cfg = load_ssh_config(cfg_path)
            _ = cfg["host"]

        samples = _bench(_once, iterations)
        return {
            "load_ssh_config_cached": {
                "iterations": iterations,
                **_summarize(samples),
            }
        }


def main() -> None:
    results: dict[str, Any] = {}
    results.update(bench_probe_success())
    results.update(bench_probe_conda_missing())
    results.update(bench_probe_failure())
    results.update(bench_load_ssh_config())
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
