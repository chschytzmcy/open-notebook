"""Open Notebook CLI - Credential 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


_credential_parser = None


def register(parser: argparse.ArgumentParser):
    """注册 credential 子命令"""
    global _credential_parser
    sub = parser.add_parser("credential", help="凭证管理")
    _credential_parser = sub
    sub.add_argument("action", choices=["list", "create", "test", "delete"],
                     nargs="?", default=None, help="操作 (留空显示帮助)")
    sub.add_argument("id", nargs="?", help="凭证 ID")
    sub.add_argument("--name", help="凭证名称")
    sub.add_argument("--provider", help="提供商 (openai, anthropic, etc.)")
    sub.add_argument("--api-key", help="API Key")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    action = args.action
    if action is None:
        _credential_parser.print_help()
        return
    if action == "list":
        _list(client)
    elif action == "create":
        _create(client, args.name, args.provider, args.api_key)
    elif action == "test":
        _test(client, args.id)
    elif action == "delete":
        _delete(client, args.id)


def _list(client: "OpenNotebookClient"):
    """列出凭证"""
    result = client.get("/credentials")
    credentials = result if isinstance(result, list) else []
    print(f"找到 {len(credentials)} 个凭证:")
    for c in credentials:
        print(f"  {c['id']} - {c.get('name', 'N/A')} ({c.get('provider', 'unknown')})")
        print(f"    模态: {', '.join(c.get('modalities', []))}")


def _create(client: "OpenNotebookClient", name: str, provider: str, api_key: str = None):
    """创建凭证"""
    if not name or not provider:
        print("Error: 请提供名称和提供商")
        return
    data = {"name": name, "provider": provider}
    if api_key:
        data["api_key"] = api_key
    result = client.post("/credentials", data)
    print(f"创建成功: {result['id']} - {result.get('name', name)}")


def _test(client: "OpenNotebookClient", credential_id: str):
    """测试凭证"""
    if not credential_id:
        print("Error: 请提供凭证 ID")
        return
    result = client.post(f"/credentials/{credential_id}/test", {})
    success = result.get("success", False)
    print(f"测试{'成功' if success else '失败'}: {result.get('message', '')}")


def _delete(client: "OpenNotebookClient", credential_id: str):
    """删除凭证"""
    if not credential_id:
        print("Error: 请提供凭证 ID")
        return
    client.delete(f"/credentials/{credential_id}")
    print(f"删除成功: {credential_id}")