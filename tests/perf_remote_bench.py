"""远程模块性能基准测试。

包含探测功能性能测试、正确性验证和历史性能对比。"""

import json
import sys
import tempfile
import time
from collections.abc import Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from taolib.remote import (
    DEFAULT_PROBE_CMD,
    RemoteExecutionError,
    RemoteProbeCommands,
    RemoteProber,
    RemoteProbeRunOptions,
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

    def __enter__(self) -> FakeConnectionLatency:
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
            return FakeResult(
                stdout="", ok=self.probe_ok, exited=0 if self.probe_ok else 1
            )
        if (
            "|| exit 127" in command
            and "command -v conda" in command
            and DEFAULT_PROBE_CMD in command
        ):
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


def legacy_probe(
    conn: FakeConnectionLatency,
    commands: RemoteProbeCommands,
    options: RemoteProbeRunOptions,
) -> None:
    merged_run_kwargs = options.merged_run_kwargs()
    uname_result = conn.run(commands.uname_cmd, **{"hide": True, **merged_run_kwargs})
    uname = (getattr(uname_result, "stdout", "") or "").strip()
    if not uname:
        raise RemoteExecutionError("uname 输出为空", command=commands.uname_cmd)

    with remote_prefixes(conn, commands.tools_env_cmd, commands.conda_activate_cmd):
        conda_result = conn.run(
            commands.check_conda_cmd,
            **{"warn": True, "hide": True, **merged_run_kwargs},
        )
        if not getattr(conda_result, "ok", False):
            if options.raise_on_conda_missing:
                raise RemoteExecutionError(
                    "conda 不可用或未找到", command=commands.check_conda_cmd
                )
            return

        probe_result = conn.run(
            commands.probe_cmd, **{"warn": True, **merged_run_kwargs}
        )
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


def bench_probe_success(
    *, iterations: int = 200, latency_ms: float = 3.0
) -> dict[str, Any]:
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions()
    latency_s = latency_ms / 1000.0

    def _run_new() -> int:
        conn = FakeConnectionLatency(
            latency_s=latency_s, conda_ok=True, probe_ok=True, host="h", user="u"
        )
        prober = RemoteProber(
            connection_factory=lambda **kw: conn, commands=commands, options=options
        )
        prober.probe({"host": "h", "user": "u"})
        return conn.run_count

    def _run_legacy() -> int:
        conn = FakeConnectionLatency(
            latency_s=latency_s, conda_ok=True, probe_ok=True, host="h", user="u"
        )
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
            "legacy": {
                **_summarize(legacy_samples),
                "mean_run_calls": mean(legacy_run_counts),
            },
        }
    }


def bench_probe_conda_missing(
    *, iterations: int = 200, latency_ms: float = 3.0
) -> dict[str, Any]:
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions(
        raise_on_conda_missing=False, raise_on_probe_failure=False
    )
    latency_s = latency_ms / 1000.0

    def _run_new() -> int:
        conn = FakeConnectionLatency(
            latency_s=latency_s, conda_ok=False, probe_ok=True, host="h", user="u"
        )
        prober = RemoteProber(
            connection_factory=lambda **kw: conn, commands=commands, options=options
        )
        prober.probe({"host": "h", "user": "u"})
        return conn.run_count

    def _run_legacy() -> int:
        conn = FakeConnectionLatency(
            latency_s=latency_s, conda_ok=False, probe_ok=True, host="h", user="u"
        )
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
            "legacy": {
                **_summarize(legacy_samples),
                "mean_run_calls": mean(legacy_run_counts),
            },
        }
    }


def bench_probe_failure(
    *, iterations: int = 200, latency_ms: float = 3.0
) -> dict[str, Any]:
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions(
        raise_on_conda_missing=False, raise_on_probe_failure=False
    )
    latency_s = latency_ms / 1000.0

    def _run_new() -> int:
        conn = FakeConnectionLatency(
            latency_s=latency_s, conda_ok=True, probe_ok=False, host="h", user="u"
        )
        prober = RemoteProber(
            connection_factory=lambda **kw: conn, commands=commands, options=options
        )
        prober.probe({"host": "h", "user": "u"})
        return conn.run_count

    def _run_legacy() -> int:
        conn = FakeConnectionLatency(
            latency_s=latency_s, conda_ok=True, probe_ok=False, host="h", user="u"
        )
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
            "legacy": {
                **_summarize(legacy_samples),
                "mean_run_calls": mean(legacy_run_counts),
            },
        }
    }


def bench_load_ssh_config(*, iterations: int = 2000) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp_dir:
        cfg_path = Path(temp_dir) / "ssh.toml"
        cfg_path.write_text(
            'host = "example.com"\nuser = "alice"\n[connect_kwargs]\npassword = "p"\n',
            encoding="utf-8",
        )

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


def bench_concurrent_probes(*, n_threads: int = 4, iters: int = 50) -> dict[str, Any]:
    """并发探测基准：多线程同时执行探测，验证线程安全性和吞吐量。"""
    import threading

    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions(
        raise_on_conda_missing=False, raise_on_probe_failure=False
    )
    errors: list[str] = []

    def _worker(thread_id: int, results_out: list[float]) -> None:
        for _ in range(iters):
            conn = FakeConnectionLatency(
                latency_s=0.001,
                conda_ok=True,
                probe_ok=True,
                host="h",
                user="u",
            )
            prober = RemoteProber(
                connection_factory=lambda **kw: conn,
                commands=commands,
                options=options,
            )
            t0 = time.perf_counter()
            try:
                prober.probe({"host": "h", "user": "u"})
            except Exception as exc:
                errors.append(f"thread-{thread_id}: {exc}")
            results_out.append(time.perf_counter() - t0)

    all_samples: list[list[float]] = [[] for _ in range(n_threads)]
    threads = [
        threading.Thread(target=_worker, args=(i, all_samples[i]))
        for i in range(n_threads)
    ]
    wall_t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall_elapsed = time.perf_counter() - wall_t0

    flat = [s for per_thread in all_samples for s in per_thread]
    total_ops = n_threads * iters
    return {
        "concurrent_probes": {
            "n_threads": n_threads,
            "iters_per_thread": iters,
            "total_ops": total_ops,
            "wall_time_s": round(wall_elapsed, 4),
            "throughput_ops_s": round(total_ops / wall_elapsed, 1)
            if wall_elapsed
            else 0,
            "errors": len(errors),
            **_summarize(flat),
        }
    }


def bench_thread_safety_config_cache(
    *, n_threads: int = 8, iters: int = 500
) -> dict[str, Any]:
    """配置缓存线程安全基准：多线程并发读取同一 TOML 配置文件。"""
    import threading

    from taolib.remote.config import clear_ssh_config_cache

    with tempfile.TemporaryDirectory() as temp_dir:
        cfg_path = Path(temp_dir) / "ssh.toml"
        cfg_path.write_text(
            'host = "bench.example.com"\nuser = "bench"\n[connect_kwargs]\npassword = "s"\n',
            encoding="utf-8",
        )

        errors: list[str] = []
        all_samples: list[list[float]] = [[] for _ in range(n_threads)]

        def _worker(thread_id: int, results_out: list[float]) -> None:
            for _ in range(iters):
                t0 = time.perf_counter()
                try:
                    cfg = load_ssh_config(cfg_path)
                    assert cfg["host"] == "bench.example.com"
                except Exception as exc:
                    errors.append(f"thread-{thread_id}: {exc}")
                results_out.append(time.perf_counter() - t0)

        clear_ssh_config_cache()
        threads = [
            threading.Thread(target=_worker, args=(i, all_samples[i]))
            for i in range(n_threads)
        ]
        wall_t0 = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wall_elapsed = time.perf_counter() - wall_t0
        clear_ssh_config_cache()

        flat = [s for per_thread in all_samples for s in per_thread]
        total_ops = n_threads * iters
        return {
            "config_cache_thread_safety": {
                "n_threads": n_threads,
                "iters_per_thread": iters,
                "total_ops": total_ops,
                "wall_time_s": round(wall_elapsed, 4),
                "throughput_ops_s": round(total_ops / wall_elapsed, 1)
                if wall_elapsed
                else 0,
                "errors": len(errors),
                **_summarize(flat),
            }
        }


def bench_probe_high_latency(
    *, iters: int = 50, latency_ms: float = 100.0
) -> dict[str, Any]:
    """高延迟场景基准：模拟高网络延迟下的探测性能。"""
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions()
    latency_s = latency_ms / 1000.0

    run_counts: list[int] = []

    def _once() -> None:
        conn = FakeConnectionLatency(
            latency_s=latency_s,
            conda_ok=True,
            probe_ok=True,
            host="h",
            user="u",
        )
        prober = RemoteProber(
            connection_factory=lambda **kw: conn,
            commands=commands,
            options=options,
        )
        prober.probe({"host": "h", "user": "u"})
        run_counts.append(conn.run_count)

    samples = _bench(_once, iters)
    avg_calls = mean(run_counts)
    theoretical_min_ms = avg_calls * latency_ms

    return {
        "probe_high_latency": {
            "latency_ms_per_run": latency_ms,
            "iterations": iters,
            "mean_run_calls": avg_calls,
            "theoretical_min_ms": round(theoretical_min_ms, 2),
            **_summarize(samples),
            "overhead_pct": round(
                (
                    (_summarize(samples)["mean_ms"] - theoretical_min_ms)
                    / theoretical_min_ms
                    * 100
                )
                if theoretical_min_ms > 0
                else 0,
                2,
            ),
        }
    }


def validate_correctness(*, latency_ms: float = 3.0) -> dict[str, Any]:
    """验证新旧实现的功能正确性。

    比较新旧实现的输出是否一致。
    """
    commands = RemoteProbeCommands()
    options = RemoteProbeRunOptions(
        raise_on_conda_missing=False, raise_on_probe_failure=False
    )
    latency_s = latency_ms / 1000.0

    results: dict[str, Any] = {
        "probe_success": {"new": None, "legacy": None, "match": False},
        "probe_conda_missing": {"new": None, "legacy": None, "match": False},
        "probe_failure": {"new": None, "legacy": None, "match": False},
    }

    # 测试 1: 正常探测
    conn_new = FakeConnectionLatency(
        latency_s=latency_s, conda_ok=True, probe_ok=True, host="h", user="u"
    )
    prober = RemoteProber(
        connection_factory=lambda **kw: conn_new, commands=commands, options=options
    )
    report_new = prober.probe({"host": "h", "user": "u"})

    conn_legacy = FakeConnectionLatency(
        latency_s=latency_s, conda_ok=True, probe_ok=True, host="h", user="u"
    )
    legacy_probe(conn_legacy, commands, options)
    report_legacy = {"run_count": conn_legacy.run_count, "ok": True}

    results["probe_success"]["new"] = {"run_count": conn_new.run_count, "ok": True}
    results["probe_success"]["legacy"] = report_legacy
    results["probe_success"]["match"] = conn_new.run_count == conn_legacy.run_count

    # 测试 2: conda 缺失
    options_no_conda = RemoteProbeRunOptions(
        raise_on_conda_missing=False, raise_on_probe_failure=False
    )
    conn_new = FakeConnectionLatency(
        latency_s=latency_s, conda_ok=False, probe_ok=True, host="h", user="u"
    )
    prober = RemoteProber(
        connection_factory=lambda **kw: conn_new,
        commands=commands,
        options=options_no_conda,
    )
    prober.probe({"host": "h", "user": "u"})

    conn_legacy = FakeConnectionLatency(
        latency_s=latency_s, conda_ok=False, probe_ok=True, host="h", user="u"
    )
    legacy_probe(conn_legacy, commands, options_no_conda)

    results["probe_conda_missing"]["new"] = {"run_count": conn_new.run_count}
    results["probe_conda_missing"]["legacy"] = {"run_count": conn_legacy.run_count}
    results["probe_conda_missing"]["match"] = (
        conn_new.run_count == conn_legacy.run_count
    )

    # 测试 3: 探测失败
    options_no_fail = RemoteProbeRunOptions(
        raise_on_conda_missing=False, raise_on_probe_failure=False
    )
    conn_new = FakeConnectionLatency(
        latency_s=latency_s, conda_ok=True, probe_ok=False, host="h", user="u"
    )
    prober = RemoteProber(
        connection_factory=lambda **kw: conn_new,
        commands=commands,
        options=options_no_fail,
    )
    prober.probe({"host": "h", "user": "u"})

    conn_legacy = FakeConnectionLatency(
        latency_s=latency_s, conda_ok=True, probe_ok=False, host="h", user="u"
    )
    legacy_probe(conn_legacy, commands, options_no_fail)

    results["probe_failure"]["new"] = {"run_count": conn_new.run_count}
    results["probe_failure"]["legacy"] = {"run_count": conn_legacy.run_count}
    results["probe_failure"]["match"] = conn_new.run_count == conn_legacy.run_count

    return {
        "correctness_validation": results,
        "all_match": all(r["match"] for r in results.values()),
    }


def compare_with_baseline(
    current: dict[str, Any], baseline_file: str = "baseline_perf.json"
) -> dict[str, Any]:
    """与历史性能基线对比。

    如果基线文件存在，加载并比较；否则保存当前结果为基线。
    """
    baseline_path = Path(__file__).parent / baseline_file
    comparison = {"has_baseline": False, "regression_detected": False}

    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        comparison["has_baseline"] = True
        comparison["baseline_n"] = baseline.get("timestamp", "unknown")
        comparison["changes"] = {}

        for key in ["probe_success", "probe_conda_missing", "probe_failure"]:
            if key in baseline and key in current:
                baseline_ms = baseline[key]["new"]["mean_ms"]
                current_ms = current[key]["new"]["mean_ms"]
                change_pct = (
                    ((current_ms - baseline_ms) / baseline_ms * 100)
                    if baseline_ms > 0
                    else 0
                )
                comparison["changes"][key] = {
                    "baseline_ms": round(baseline_ms, 2),
                    "current_ms": round(current_ms, 2),
                    "change_pct": round(change_pct, 2),
                    "regression": change_pct > 10,  # 超过 10% 视为退化
                }
                if change_pct > 10:
                    comparison["regression_detected"] = True

        if not comparison["regression_detected"]:
            comparison["summary"] = "性能无显著退化"
        else:
            regressions = [
                k for k, v in comparison["changes"].items() if v.get("regression")
            ]
            comparison["summary"] = f"检测到性能退化：{', '.join(regressions)}"
    else:
        # 保存基线
        baseline_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "probe_success": current.get("probe_success", {}).get("new", {}),
            "probe_conda_missing": current.get("probe_conda_missing", {}).get(
                "new", {}
            ),
            "probe_failure": current.get("probe_failure", {}).get("new", {}),
        }
        baseline_path.write_text(json.dumps(baseline_data, indent=2), encoding="utf-8")
        comparison["summary"] = "基线文件不存在，已保存当前结果为基线"

    return {"baseline_comparison": comparison}


def main() -> None:
    results: dict[str, Any] = {}

    # 1. 功能正确性验证
    print("=== 功能正确性验证 ===", file=sys.stderr)
    correctness = validate_correctness()
    results.update(correctness)
    print(f"新旧实现一致: {correctness['all_match']}", file=sys.stderr)

    # 2. 性能基准测试
    print("\n=== 性能基准测试 ===", file=sys.stderr)
    results.update(bench_probe_success())
    results.update(bench_probe_conda_missing())
    results.update(bench_probe_failure())
    results.update(bench_load_ssh_config())

    # 3. 并发与高延迟基准测试
    print("\n=== 并发与高延迟基准测试 ===", file=sys.stderr)
    concurrent_result = bench_concurrent_probes()
    results.update(concurrent_result)
    cr = concurrent_result["concurrent_probes"]
    print(
        f"并发探测: {cr['throughput_ops_s']} ops/s, 错误: {cr['errors']}",
        file=sys.stderr,
    )

    cache_result = bench_thread_safety_config_cache()
    results.update(cache_result)
    ct = cache_result["config_cache_thread_safety"]
    print(
        f"配置缓存线程安全: {ct['throughput_ops_s']} ops/s, 错误: {ct['errors']}",
        file=sys.stderr,
    )

    high_lat_result = bench_probe_high_latency()
    results.update(high_lat_result)
    hl = high_lat_result["probe_high_latency"]
    print(
        f"高延迟探测: 平均 {hl['mean_ms']:.1f}ms, 开销 {hl['overhead_pct']}%",
        file=sys.stderr,
    )

    # 4. 与历史基线对比
    print("\n=== 历史性能对比 ===", file=sys.stderr)
    baseline_comparison = compare_with_baseline(results)
    results.update(baseline_comparison)
    print(baseline_comparison["baseline_comparison"]["summary"], file=sys.stderr)

    # 输出完整结果
    print("\n=== 完整结果 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # 检查是否有性能退化
    if baseline_comparison["baseline_comparison"].get("regression_detected"):
        print("\n警告：检测到性能退化！", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
