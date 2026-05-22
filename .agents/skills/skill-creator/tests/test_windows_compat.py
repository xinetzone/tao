import subprocess
import sys
from pathlib import Path

from scripts import run_eval, utils


def test_parse_skill_md_reads_utf8(monkeypatch):
    seen = {}
    sample = "---\nname: demo\ndescription: >\n  中文描述\n---\n"

    def fake_read_text(self, encoding=None, errors=None, newline=None):
        seen["encoding"] = encoding
        return sample

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    name, description, content = utils.parse_skill_md(Path("dummy"))

    assert seen["encoding"] == "utf-8"
    assert name == "demo"
    assert "中文描述" in description
    assert content == sample


def test_resolve_project_root_honors_override(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    resolved = run_eval.resolve_project_root(project_root)

    assert resolved == project_root


def test_iter_process_lines_reads_subprocess_output():
    command = [
        sys.executable,
        "-c",
        (
            "import json, sys, time; "
            "print(json.dumps({'type': 'first'})); sys.stdout.flush(); "
            "time.sleep(0.1); "
            "print(json.dumps({'type': 'second'})); sys.stdout.flush()"
        ),
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    try:
        lines = list(run_eval.iter_process_lines(process, timeout=2))
    finally:
        process.wait(timeout=5)

    assert len(lines) == 2
    assert '"first"' in lines[0]
    assert '"second"' in lines[1]
