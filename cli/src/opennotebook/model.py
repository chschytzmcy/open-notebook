"""Open Notebook CLI - Model 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


_model_parser = None


def register(parser: argparse.ArgumentParser):
    """注册 model 子命令"""
    global _model_parser
    sub = parser.add_parser("model", help="模型管理")
    _model_parser = sub
    sub.add_argument("action", choices=["list", "discover"],
                     nargs="?", default=None, help="操作 (留空显示帮助)")
    sub.add_argument("--provider", help="提供商名称")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    action = args.action
    if action is None:
        _model_parser.print_help()
        return
    if action == "list":
        _list(client, args.provider)
    elif action == "discover":
        _discover(client, args.provider)


def _list(client: "OpenNotebookClient", provider: str = None):
    """列出模型"""
    if provider:
        result = client.get(f"/models?provider={provider}")
    else:
        result = client.get("/models")
    models = result if isinstance(result, list) else result.get("models", [])
    print(f"找到 {len(models)} 个模型:")
    for m in models:
        print(f"  {m['id']} - {m['name']} ({m['provider']}) [{m['type']}]")


def _discover(client: "OpenNotebookClient", provider: str = None):
    """发现模型"""
    if not provider:
        print("Error: 请提供提供商")
        return
    result = client.post(f"/credentials/discover", {"provider": provider})
    discovered = result.get("models", [])
    print(f"发现 {len(discovered)} 个模型:")
    for m in discovered:
        print(f"  {m.get('model_id', m.get('id', 'N/A'))} - {m.get('name', 'N/A')}")