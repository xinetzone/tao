#!/usr/bin/env python3
"""
EU AI Act 合规检查工作流本地模拟器
模拟 GitHub Actions 工作流的执行环境和日志输出
"""

import os
import sys

# Windows 终端 UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class Colors:
    """终端颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def log_header(title: str, icon: str = "🔍"):
    """打印分组标题"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{icon} {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def log_info(message: str):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def log_success(message: str):
    """打印成功"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def log_warning(message: str):
    """打印警告"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def log_error(message: str):
    """打印错误"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def log_step(step: str, message: str):
    """打印步骤"""
    print(f"{Colors.MAGENTA}[{step}]{Colors.RESET} {message}")


def simulate_github_env():
    """模拟 GitHub Actions 环境变量"""
    env = {
        'GITHUB_REPOSITORY': 'owner/repo',
        'GITHUB_REF_NAME': 'feature/eu-ai-act-compliance',
        'GITHUB_SHA': 'abc123def456789',
        'GITHUB_WORKFLOW': 'EU AI Act Compliance Check',
        'GITHUB_RUN_ID': '1234567890',
        'GITHUB_EVENT_NAME': 'pull_request',
        'COMPLIANCE_THRESHOLD': '90',
    }

    for key, value in env.items():
        os.environ[key] = value

    return env


def check_agents_directory():
    """Step 1: 检查 .agents/ 目录"""
    log_header("Step 1: 验证 .agents/ 目录完整性", "📁")

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    log_info(f"检查时间: {timestamp}")
    log_info(f"工作目录: {os.getcwd()}")

    agents_dir = Path('.agents')
    if agents_dir.exists():
        log_success(".agents/ 目录存在")

        # 列出关键文件
        scripts_dir = agents_dir / 'scripts'
        if scripts_dir.exists():
            log_info("脚本文件:")
            for f in scripts_dir.glob('*.py'):
                print(f"    - {f.relative_to('.')}")

        rules_dir = agents_dir / 'rules'
        if rules_dir.exists():
            log_info("规则文件:")
            for f in rules_dir.glob('*.md'):
                print(f"    - {f.relative_to('.')}")

        return True
    else:
        log_warning(".agents/ 目录不存在")
        return False


def run_check_script(script_name: str, description: str) -> dict:
    """运行检查脚本"""
    script_path = Path(f'.agents/scripts/{script_name}')

    result = {
        'script': script_name,
        'description': description,
        'exists': script_path.exists(),
        'success': False,
        'output': '',
        'exit_code': -1
    }

    if not script_path.exists():
        log_warning(f"脚本不存在: {script_path}")
        return result

    log_step("RUN", f"执行 {script_name}")
    print("-" * 40)

    try:
        # Windows 编码支持
        proc = subprocess.run(
            ['uv', 'run', str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )

        result['output'] = proc.stdout + proc.stderr
        result['exit_code'] = proc.returncode
        result['success'] = proc.returncode == 0

        # 输出结果
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(f"{Colors.YELLOW}{proc.stderr}{Colors.RESET}")

        print("-" * 40)

        if result['success']:
            log_success(f"{description} 通过")
        else:
            log_warning(f"{description} 发现问题 (退出码: {proc.returncode})")

    except subprocess.TimeoutExpired:
        log_error(f"脚本执行超时")
        result['output'] = 'Timeout'
    except Exception as e:
        log_error(f"执行失败: {e}")
        result['output'] = str(e)

    return result


def generate_report(checks: list) -> dict:
    """生成合规报告"""
    log_header("Step 4: 生成合规报告", "📝")

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    report = {
        'metadata': {
            'timestamp': timestamp,
            'repository': os.environ.get('GITHUB_REPOSITORY', 'local'),
            'branch': os.environ.get('GITHUB_REF_NAME', 'local'),
            'commit': os.environ.get('GITHUB_SHA', 'local'),
            'workflow': os.environ.get('GITHUB_WORKFLOW', 'local'),
            'run_id': os.environ.get('GITHUB_RUN_ID', 'local')
        },
        'checks': {},
        'governance_score': 0,
        'threshold': int(os.environ.get('COMPLIANCE_THRESHOLD', 90)),
        'status': 'placeholder',
        'note': 'Local simulation - enable Inkog CLI for actual scanning'
    }

    for check in checks:
        report['checks'][check['script'].replace('.py', '')] = {
            'status': 'passed' if check['success'] else ('skipped' if not check['exists'] else 'failed'),
            'description': check['description'],
            'exit_code': check['exit_code']
        }

    # 输出报告
    log_info("报告内容:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 保存报告
    report_path = Path('compliance-report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log_success(f"报告已保存: {report_path}")

    return report


def print_summary(checks: list, report: dict):
    """打印检查摘要"""
    log_header("检查摘要", "📋")

    print(f"""
{Colors.BOLD}{'='*50}{Colors.RESET}
{Colors.BOLD}       EU AI Act 合规检查摘要{Colors.RESET}
{Colors.BOLD}{'='*50}{Colors.RESET}

📅 执行时间: {report['metadata']['timestamp']}
🌿 分支: {report['metadata']['branch']}
📝 提交: {report['metadata']['commit']}

📊 检查结果:
""")

    for check in checks:
        status_icon = '✅' if check['success'] else ('⏭️' if not check['exists'] else '❌')
        status_text = '通过' if check['success'] else ('跳过' if not check['exists'] else '失败')
        print(f"  {status_icon} {check['description']}: {status_text}")

    print(f"""
📁 产物:
  - compliance-report.json

{Colors.BOLD}{'='*50}{Colors.RESET}
""")

    # PR 评论模拟
    print(f"\n{Colors.CYAN}模拟 PR 评论:{Colors.RESET}")
    print("-" * 50)

    comment_lines = [
        "## 🇪🇺 EU AI Act 合规检查",
        "",
        "| 检查项 | 状态 |",
        "|--------|------|",
    ]

    for check in checks:
        status_icon = '✅' if check['success'] else ('⏭️' if not check['exists'] else '❌')
        status_text = '通过' if check['success'] else ('跳过' if not check['exists'] else '失败')
        comment_lines.append(f"| {check['description']} | {status_icon} {status_text} |")

    comment_lines.extend([
        "",
        f"> 📅 执行时间: `{report['metadata']['timestamp']}`",
        f"> 📝 提交: `{report['metadata']['commit']}`",
        "",
        "⚠️ 完整合规扫描需要启用 Inkog CLI",
        "",
        "📁 详细报告请查看 **Artifacts**"
    ])

    print('\n'.join(comment_lines))
    print("-" * 50)


def main():
    """主函数"""
    print(f"""
{Colors.BOLD}{Colors.BLUE}
╔════════════════════════════════════════════════════════════╗
║     EU AI Act 合规检查工作流 - 本地模拟器                  ║
╚════════════════════════════════════════════════════════════╝
{Colors.RESET}
""")

    # 模拟 GitHub 环境
    log_info("初始化模拟环境...")
    env = simulate_github_env()
    for key, value in env.items():
        log_step("ENV", f"{key}={value}")

    # Step 1: 检查目录
    agents_exists = check_agents_directory()

    # Step 2: 运行检查脚本
    log_header("Step 2: 运行合规检查脚本", "🔧")

    checks = []

    # 约束检查
    checks.append(run_check_script(
        'check_constraints.py',
        '约束检查'
    ))

    # EU AI Act 检查
    checks.append(run_check_script(
        'check_eu_ai_act.py',
        'EU AI Act 合规检查'
    ))

    # Step 3: Inkog 扫描 (模拟)
    log_header("Step 3: Inkog 合规扫描", "🔬")
    log_warning("Inkog CLI 未启用 - 跳过此步骤")
    log_info("取消工作流中的注释以启用完整扫描")

    checks.append({
        'script': 'inkog_scan',
        'description': 'Inkog 扫描',
        'exists': False,
        'success': False,
        'exit_code': -1
    })

    # Step 4: 生成报告
    report = generate_report(checks)

    # 打印摘要
    print_summary(checks, report)

    # 返回状态
    success_count = sum(1 for c in checks if c['success'])
    total_count = len([c for c in checks if c['exists']])

    if total_count > 0:
        log_info(f"检查完成: {success_count}/{total_count} 通过")
    else:
        log_warning("无可执行的检查脚本")

    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
