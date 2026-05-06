"""Symphony CLI 入口。

基于 Typer 的命令行接口，提供编排服务的启动、验证和版本查询功能。
"""

from pathlib import Path

import typer

from taolib.symphony import __version__
from taolib.symphony.config.loader import load_workflow
from taolib.symphony.config.resolver import resolve_config
from taolib.symphony.errors import WorkflowLoadError

app = typer.Typer(name="symphony", help="Symphony 编排服务")


@app.command()
def run(
    workflow: Path = typer.Argument(  # noqa: B008
        ...,
        exists=True,
        readable=True,
        help="WORKFLOW.md 文件路径",
    ),
    port: int | None = typer.Option(  # noqa: B008
        None,
        "--port",
        "-p",
        help="HTTP 服务端口（覆盖配置文件）",
    ),
    config: Path | None = typer.Option(  # noqa: B008
        None,
        "--config",
        "-c",
        help="symphony.toml 配置文件路径",
    ),
    logs_root: Path = typer.Option(  # noqa: B008
        Path("./log"),
        "--logs-root",
        "-l",
        help="日志输出根目录",
    ),
) -> None:
    """启动 Symphony 编排服务。"""
    try:
        resolved = resolve_config(
            cli_args={"port": port, "logs_root": logs_root},
            toml_path=config,
            workflow_path=workflow,
        )
    except (WorkflowLoadError, ValueError) as exc:
        typer.echo(f"配置解析失败: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Symphony 编排服务启动中...")
    typer.echo(f"  工作流: {workflow}")
    typer.echo(f"  跟踪器: {resolved.tracker.kind} ({resolved.tracker.project_slug})")
    typer.echo(f"  工作区根目录: {resolved.workspace.root}")
    typer.echo(f"  轮询间隔: {resolved.polling.interval_ms}ms")
    typer.echo(f"  最大并发 Agent: {resolved.agent.max_concurrent_agents}")
    if resolved.server.port is not None:
        typer.echo(f"  HTTP 端口: {resolved.server.port}")
    typer.echo(f"  日志目录: {logs_root}")

    # TODO: 集成 Orchestrator 启动循环


@app.command()
def validate(
    workflow: Path = typer.Argument(  # noqa: B008
        ...,
        exists=True,
        readable=True,
        help="WORKFLOW.md 文件路径",
    ),
) -> None:
    """验证 WORKFLOW.md 配置。"""
    try:
        wf = load_workflow(workflow)
    except WorkflowLoadError as exc:
        typer.echo(f"❌ 验证失败: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("✅ WORKFLOW.md 解析成功")
    typer.echo(f"  前置数据键: {', '.join(wf.config.keys()) or '(无)'}")
    typer.echo(f"  提示模板长度: {len(wf.prompt_template)} 字符")

    try:
        resolved = resolve_config(
            cli_args={},
            toml_path=None,
            workflow_path=workflow,
        )
    except ValueError as exc:
        typer.echo(f"❌ 配置校验失败: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("✅ 配置校验通过")
    typer.echo(f"  跟踪器类型: {resolved.tracker.kind}")
    typer.echo(f"  轮询间隔: {resolved.polling.interval_ms}ms")
    typer.echo(f"  最大并发: {resolved.agent.max_concurrent_agents}")


@app.command()
def version() -> None:
    """显示版本信息。"""
    typer.echo(f"symphony {__version__}")
