from pathlib import Path
from typing import Any

import scripts.generate_report as generate_report
import scripts.run_eval as run_eval
import scripts.run_loop as run_loop


class _FakeFuture:
    def __init__(self, value: bool) -> None:
        self._value = value

    def result(self) -> bool:
        return self._value


class _FakeExecutor:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.futures: list[_FakeFuture] = []

    def __enter__(self) -> "_FakeExecutor":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    def submit(self, func: Any, query: str, *args: Any) -> _FakeFuture:
        future = _FakeFuture(True)
        self.futures.append(future)
        return future


def test_run_eval_keeps_duplicate_queries_as_distinct_items(monkeypatch):
    monkeypatch.setattr(run_eval, "ProcessPoolExecutor", _FakeExecutor)
    monkeypatch.setattr(run_eval, "as_completed", lambda futures: list(futures))

    output = run_eval.run_eval(
        eval_set=[
            {
                "id": "positive-duplicate",
                "query": "same prompt",
                "should_trigger": True,
            },
            {
                "id": "negative-duplicate",
                "query": "same prompt",
                "should_trigger": False,
            },
        ],
        skill_name="demo-skill",
        description="demo description",
        num_workers=1,
        timeout=1,
        project_root=Path("."),
        runs_per_query=2,
        trigger_threshold=0.5,
    )

    results = output["results"]

    assert len(results) == 2
    assert [result["eval_item_id"] for result in results] == [
        "positive-duplicate",
        "negative-duplicate",
    ]
    assert [result["pass"] for result in results] == [True, False]


def test_run_loop_splits_train_and_test_by_item_id(monkeypatch, tmp_path):
    monkeypatch.setattr(
        run_loop,
        "parse_skill_md",
        lambda skill_path: ("demo-skill", "current description", "# skill"),
    )
    monkeypatch.setattr(
        run_loop,
        "split_eval_set",
        lambda eval_set, holdout: ([eval_set[0]], [eval_set[1]]),
    )
    monkeypatch.setattr(
        run_loop,
        "run_eval",
        lambda **kwargs: {
            "results": [
                {
                    "eval_item_id": "train-item",
                    "query": "same prompt",
                    "should_trigger": True,
                    "trigger_rate": 1.0,
                    "triggers": 1,
                    "runs": 1,
                    "pass": True,
                },
                {
                    "eval_item_id": "test-item",
                    "query": "same prompt",
                    "should_trigger": False,
                    "trigger_rate": 1.0,
                    "triggers": 1,
                    "runs": 1,
                    "pass": False,
                },
            ]
        },
    )

    output = run_loop.run_loop(
        eval_set=[
            {
                "eval_item_id": "train-item",
                "query": "same prompt",
                "should_trigger": True,
            },
            {
                "eval_item_id": "test-item",
                "query": "same prompt",
                "should_trigger": False,
            },
        ],
        skill_path=tmp_path,
        description_override=None,
        num_workers=1,
        timeout=1,
        max_iterations=1,
        runs_per_query=1,
        trigger_threshold=0.5,
        holdout=0.5,
        model="test-model",
        verbose=False,
        live_report_path=None,
        log_dir=None,
        project_root=tmp_path,
    )

    history_entry = output["history"][0]

    assert [result["eval_item_id"] for result in history_entry["train_results"]] == [
        "train-item"
    ]
    assert [result["eval_item_id"] for result in history_entry["test_results"]] == [
        "test-item"
    ]


def test_generate_report_keeps_duplicate_query_columns_distinct():
    html = generate_report.generate_html(
        {
            "history": [
                {
                    "iteration": 1,
                    "description": "candidate",
                    "train_passed": 1,
                    "train_failed": 1,
                    "train_total": 2,
                    "train_results": [
                        {
                            "eval_item_id": "first",
                            "query": "same prompt",
                            "should_trigger": True,
                            "triggers": 1,
                            "runs": 1,
                            "pass": True,
                        },
                        {
                            "eval_item_id": "second",
                            "query": "same prompt",
                            "should_trigger": False,
                            "triggers": 1,
                            "runs": 1,
                            "pass": False,
                        },
                    ],
                    "test_results": [],
                }
            ]
        }
    )

    assert html.count(">same prompt</th>") == 2
    assert html.count('class="result pass">✓<span class="rate">1/1</span></td>') == 1
    assert html.count('class="result fail">✗<span class="rate">1/1</span></td>') == 1
