import tempfile
import unittest
from contextlib import contextmanager
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import sys

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from taolib.remote import (
    DEFAULT_PROBE_CMD,
    RemoteConfigError,
    RemoteExecutionError,
    RemoteProbeCommands,
    RemoteProbeRunOptions,
    RemoteProber,
    load_ssh_config,
    probe_remote,
    redact_ssh_config,
    remote_prefixes,
)


@dataclass(slots=True)
class FakeResult:
    stdout: str = ""
    ok: bool = True


class FakeConnection:
    def __init__(
        self,
        *,
        conda_ok: bool = True,
        probe_ok: bool = True,
        uname_stdout: str = "Linux fake 1.0\n",
        **ssh_config: Any,
    ) -> None:
        self.ssh_config = ssh_config
        self.conda_ok = conda_ok
        self.probe_ok = probe_ok
        self.uname_stdout = uname_stdout
        self.prefix_stack: list[str] = []
        self.runs: list[tuple[list[str], str, dict[str, Any]]] = []

    def __enter__(self) -> "FakeConnection":
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
        self.runs.append((list(self.prefix_stack), command, dict(kwargs)))
        if command == "uname -a":
            return FakeResult(stdout=self.uname_stdout, ok=True)
        if command == "command -v conda":
            return FakeResult(stdout="/usr/bin/conda\n" if self.conda_ok else "", ok=self.conda_ok)
        if command == DEFAULT_PROBE_CMD:
            return FakeResult(stdout="", ok=self.probe_ok)
        return FakeResult(stdout="", ok=True)


class TestConfig(unittest.TestCase):
    def test_load_ssh_config_returns_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg_path = Path(temp_dir) / "ssh.toml"
            cfg_path.write_text(
                'host = "example.com"\nuser = "alice"\n[connect_kwargs]\npassword = "p"\n',
                encoding="utf-8",
            )
            cfg1 = load_ssh_config(cfg_path)
            cfg1["host"] = "mutated"
            cfg2 = load_ssh_config(cfg_path)
            self.assertEqual(cfg2["host"], "example.com")

    def test_load_ssh_config_missing_file_raises(self) -> None:
        with self.assertRaises(RemoteConfigError):
            load_ssh_config("this_file_should_not_exist_ssh.toml")

    def test_redact_ssh_config_masks_password(self) -> None:
        masked = redact_ssh_config({"host": "h", "user": "u", "connect_kwargs": {"password": "p"}})
        self.assertEqual(masked["connect_kwargs"]["password"], "***")

    def test_redact_ssh_config_does_not_mutate_input(self) -> None:
        cfg = {"host": "h", "user": "u", "connect_kwargs": {"password": "p"}}
        masked = redact_ssh_config(cfg)
        self.assertEqual(cfg["connect_kwargs"]["password"], "p")
        self.assertEqual(masked["connect_kwargs"]["password"], "***")

    def test_load_ssh_config_thread_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg_path = Path(temp_dir) / "ssh.toml"
            cfg_path.write_text('host = "example.com"\nuser = "alice"\n', encoding="utf-8")

            def _load() -> str:
                return load_ssh_config(cfg_path)["host"]

            with ThreadPoolExecutor(max_workers=8) as pool:
                hosts = list(pool.map(lambda _: _load(), range(32)))
            self.assertTrue(all(h == "example.com" for h in hosts))


class TestSession(unittest.TestCase):
    def test_remote_prefixes_ignores_blank(self) -> None:
        conn = FakeConnection(host="h", user="u")
        with remote_prefixes(conn, "  ", "export A=1"):
            conn.run("echo ok")
        prefixes, _, _ = conn.runs[-1]
        self.assertEqual(prefixes, ["export A=1"])


class TestProbe(unittest.TestCase):
    def test_probe_remote_requires_host_and_user(self) -> None:
        with self.assertRaises(RemoteConfigError):
            probe_remote({"user": "u"}, connection_factory=lambda **kw: FakeConnection(**kw))
        with self.assertRaises(RemoteConfigError):
            probe_remote({"host": "h"}, connection_factory=lambda **kw: FakeConnection(**kw))

    def test_probe_remote_skips_when_conda_missing(self) -> None:
        report = probe_remote(
            {"host": "h", "user": "u"},
            connection_factory=lambda **kw: FakeConnection(conda_ok=False, **kw),
        )
        self.assertEqual(report.uname, "Linux fake 1.0")
        self.assertFalse(report.conda_available)
        self.assertFalse(report.probe_attempted)
        self.assertIsNone(report.probe_ok)

    def test_probe_remote_can_raise_when_conda_missing(self) -> None:
        with self.assertRaises(RemoteExecutionError):
            probe_remote(
                {"host": "h", "user": "u"},
                connection_factory=lambda **kw: FakeConnection(conda_ok=False, **kw),
                raise_on_conda_missing=True,
            )

    def test_probe_remote_runs_probe_when_conda_present(self) -> None:
        conn = FakeConnection(conda_ok=True, probe_ok=True, host="h", user="u")
        report = probe_remote(
            {"host": "h", "user": "u"},
            connection_factory=lambda **kw: conn,
        )
        self.assertTrue(report.conda_available)
        self.assertTrue(report.probe_attempted)
        self.assertTrue(report.probe_ok)
        ran_commands = [c for _, c, _ in conn.runs]
        self.assertIn("uname -a", ran_commands)
        self.assertIn("command -v conda", ran_commands)
        self.assertIn(DEFAULT_PROBE_CMD, ran_commands)

        probe_call = next(item for item in conn.runs if item[1] == DEFAULT_PROBE_CMD)
        prefixes, _, _ = probe_call
        self.assertGreaterEqual(len(prefixes), 2)

    def test_probe_remote_can_raise_when_probe_fails(self) -> None:
        with self.assertRaises(RemoteExecutionError):
            probe_remote(
                {"host": "h", "user": "u"},
                connection_factory=lambda **kw: FakeConnection(conda_ok=True, probe_ok=False, **kw),
                raise_on_probe_failure=True,
            )

    def test_probe_remote_empty_uname_raises(self) -> None:
        with self.assertRaises(RemoteExecutionError):
            probe_remote(
                {"host": "h", "user": "u"},
                connection_factory=lambda **kw: FakeConnection(uname_stdout="\n", **kw),
            )

    def test_probe_remote_closed_file_valueerror_is_keyboardinterrupt(self) -> None:
        class InterruptingConnection(FakeConnection):
            def run(self, command: str, **kwargs: Any) -> FakeResult:
                if command == "uname -a":
                    raise ValueError("I/O operation on closed file")
                return super().run(command, **kwargs)

        with self.assertRaises(KeyboardInterrupt):
            probe_remote(
                {"host": "h", "user": "u"},
                connection_factory=lambda **kw: InterruptingConnection(**kw),
            )

    def test_remote_prober_allows_command_overrides(self) -> None:
        class CustomConnection(FakeConnection):
            def run(self, command: str, **kwargs: Any) -> FakeResult:
                self.runs.append((list(self.prefix_stack), command, dict(kwargs)))
                if command == "echo uname":
                    return FakeResult(stdout="Linux custom 1.0\n", ok=True)
                if command == "echo conda":
                    return FakeResult(stdout="/usr/bin/conda\n", ok=True)
                if command == "echo probe":
                    return FakeResult(stdout="", ok=True)
                return super().run(command, **kwargs)

        conn = CustomConnection(conda_ok=True, probe_ok=True, host="h", user="u")
        prober = RemoteProber(
            connection_factory=lambda **kw: conn,
            commands=RemoteProbeCommands(
                tools_env_cmd="export X=1",
                conda_activate_cmd="export Y=1",
                probe_cmd="echo probe",
                check_conda_cmd="echo conda",
                uname_cmd="echo uname",
            ),
            options=RemoteProbeRunOptions(encoding="utf-8"),
        )
        report = prober.probe({"host": "h", "user": "u"})
        self.assertTrue(report.conda_available)
        ran_commands = [c for _, c, _ in conn.runs]
        self.assertIn("echo uname", ran_commands)
        self.assertIn("echo conda", ran_commands)
        self.assertIn("echo probe", ran_commands)

        probe_call = next(item for item in conn.runs if item[1] == "echo probe")
        prefixes, _, _ = probe_call
        self.assertEqual(prefixes, ["export X=1", "export Y=1"])


if __name__ == "__main__":
    unittest.main()
