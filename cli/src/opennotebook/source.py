"""Open Notebook CLI - Source 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


def register(parser: argparse.ArgumentParser):
    """注册 source 子命令"""
    sub = parser.add_parser("source", help="来源管理 (文件/URL)")
    sub.add_argument("action", choices=["list", "add", "get", "delete"], help="操作")
    sub.add_argument("notebook_id", nargs="?", help="笔记本 ID")
    sub.add_argument("path", nargs="?", help="文件路径或 URL")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    action = args.action
    if action == "list":
        _list(client, args.notebook_id)
    elif action == "add":
        _add(client, args.notebook_id, args.path)
    elif action == "get":
        _get(client, args.path)
    elif action == "delete":
        _delete(client, args.path)


def _list(client: "OpenNotebookClient", notebook_id: str = None):
    """列出笔记本的来源"""
    if not notebook_id:
        # 获取所有来源
        result = client.get("/sources")
        sources = result if isinstance(result, list) else []
    else:
        result = client.get(f"/notebooks/{notebook_id}/sources")
        sources = result if isinstance(result, list) else []

    print(f"找到 {len(sources)} 个来源:")
    for src in sources:
        title = src.get("title", "Untitled")
        print(f"  {src['id']} - {title}")
        print(f"    类型: {src.get('asset_type', 'unknown')}")


def _add(client: "OpenNotebookClient", notebook_id: str, path: str):
    """添加来源"""
    if not notebook_id or not path:
        print("Error: 请提供笔记本 ID 和文件路径或 URL")
        return

    # 判断是 URL 还是文件
    is_url = path.startswith("http://") or path.startswith("https://")
    data = {
        "notebook_id": notebook_id,
        "asset": {"url": path} if is_url else {"file_path": path},
    }

    result = client.post("/sources", data)
    print(f"添加成功: {result['id']} - {result.get('title', path)}")
    print(f"处理命令: {result.get('command_id', 'N/A')}")


def _get(client: "OpenNotebookClient", source_id: str):
    """获取来源详情"""
    if not source_id:
        print("Error: 请提供来源 ID")
        return
    result = client.get(f"/sources/{source_id}")
    print(f"来源详情:")
    print(f"  ID: {result['id']}")
    print(f"  标题: {result.get('title', 'N/A')}")
    print(f"  类型: {result.get('asset_type', 'unknown')}")
    print(f"  话题: {', '.join(result.get('topics', [])) or 'N/A'}")


def _delete(client: "OpenNotebookClient", source_id: str):
    """删除来源"""
    if not source_id:
        print("Error: 请提供来源 ID")
        return
    client.delete(f"/sources/{source_id}")
    print(f"删除成功: {source_id}")