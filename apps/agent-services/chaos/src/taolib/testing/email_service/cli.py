"""邮件服务 CLI 入口。"""

import argparse
import asyncio


def main() -> None:
    """邮件服务 CLI。"""
    parser = argparse.ArgumentParser(description="Email Service CLI")
    subparsers = parser.add_subparsers(dest="command")

    # server 子命令
    server_parser = subparsers.add_parser("server", help="Start server")
    server_parser.add_argument("--host", default="0.0.0.0")
    server_parser.add_argument("--port", type=int, default=8002)
    server_parser.add_argument("--reload", action="store_true")

    # send 子命令
    send_parser = subparsers.add_parser("send", help="Send a test email")
    send_parser.add_argument("--to", required=True, help="Recipient email")
    send_parser.add_argument("--subject", required=True, help="Subject")
    send_parser.add_argument("--body", required=True, help="Body text")
    send_parser.add_argument("--sender", default="noreply@example.com")

    # templates 子命令
    subparsers.add_parser("templates", help="List templates")

    args = parser.parse_args()

    if args.command == "server":
        from taolib.testing.email_service.server.main import main as server_main

        server_main()
    elif args.command == "send":
        asyncio.run(_send_test(args))
    elif args.command == "templates":
        print("Use the API to manage templates: GET /api/v1/templates")
    else:
        parser.print_help()


async def _send_test(args) -> None:
    """发送测试邮件。"""
    print(f"Sending test email to {args.to}...")
    print(f"  Subject: {args.subject}")
    print(f"  From: {args.sender}")
    print("Note: CLI send requires a running server with configured providers.")
    print("Use the API endpoint POST /api/v1/emails for actual sending.")


if __name__ == "__main__":
    main()


