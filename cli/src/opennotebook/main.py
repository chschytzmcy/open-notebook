"""Open Notebook CLI - 主入口"""

import argparse
import os
import sys
from typing import Callable, Dict

# Clear proxy environment variables (socks proxy not supported by httpx)
proxy_vars = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY", "ftp_proxy", "FTP_PROXY"]
for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]

from opennotebook import __version__


# 全局子命令解析器
_subparsers: argparse.ArgumentParser = None


def get_subparsers():
    """获取子命令解析器"""
    global _subparsers
    return _subparsers


def set_subparsers(parser: argparse.ArgumentParser):
    """设置子命令解析器"""
    global _subparsers
    _subparsers = parser


def create_parser() -> argparse.ArgumentParser:
    """创建 CLI 参数解析器"""
    parser = argparse.ArgumentParser(
        prog="opennotebook",
        description="Open Notebook CLI - 研究笔记本管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--server",
        help="API 服务器地址 (默认: http://localhost:5055)",
        default="http://localhost:5055",
    )
    parser.add_argument(
        "--password",
        help="API 认证密码 (默认: open-notebook-change-me，或通过 OPEN_NOTEBOOK_PASSWORD 环境变量)",
        default="open-notebook-change-me",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"opennotebook {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    set_subparsers(subparsers)

    # 导入并注册子命令模块
    from opennotebook import notebook, source, note, chat, podcast, search, credential, model

    notebook.register(subparsers)
    source.register(subparsers)
    note.register(subparsers)
    chat.register(subparsers)
    podcast.register(subparsers)
    search.register(subparsers)
    credential.register(subparsers)
    model.register(subparsers)

    return parser


def main():
    """CLI 主入口"""
    from opennotebook.client import get_client

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 获取 API 客户端
    client = get_client(server=args.server, password=args.password)

    # 调用子命令处理函数（通过 handler 属性）
    handler = getattr(args, 'handler', None)
    if handler:
        try:
            handler(args, client)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()