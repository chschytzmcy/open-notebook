"""Open Notebook CLI - Notebook 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


def register(parser: argparse.ArgumentParser):
    """注册 notebook 子命令"""
    sub = parser.add_parser("notebook", help="笔记本管理")
    sub.add_argument("action", choices=["list", "create", "get", "update", "delete"], help="操作")
    sub.add_argument("id_or_name", nargs="?", help="笔记本 ID 或名称")
    sub.add_argument("--description", help="笔记本描述")
    sub.add_argument("--archived", action="store_true", help="归档状态")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    action = args.action
    if action == "list":
        _list(client)
    elif action == "create":
        _create(client, args.id_or_name, args.description)
    elif action == "get":
        _get(client, args.id_or_name)
    elif action == "update":
        _update(client, args.id_or_name, args.description, args.archived)
    elif action == "delete":
        _delete(client, args.id_or_name)


def _list(client: "OpenNotebookClient"):
    """列出所有笔记本"""
    result = client.get("/notebooks")
    notebooks = result if isinstance(result, list) else []
    print(f"找到 {len(notebooks)} 个笔记本:")
    for nb in notebooks:
        archived = " [已归档]" if nb.get("archived") else ""
        print(f"  {nb['id']} - {nb['name']}{archived}")
        print(f"    描述: {nb.get('description', '')[:50]}...")
        print(f"    来源: {nb.get('source_count', 0)}, 笔记: {nb.get('note_count', 0)}")


def _create(client: "OpenNotebookClient", name: str, description: str = None):
    """创建笔记本"""
    if not name:
        print("Error: 请提供笔记本名称")
        return
    data = {"name": name}
    if description:
        data["description"] = description
    result = client.post("/notebooks", data)
    print(f"创建成功: {result['id']} - {result['name']}")


def _get(client: "OpenNotebookClient", notebook_id: str):
    """获取笔记本详情"""
    if not notebook_id:
        print("Error: 请提供笔记本 ID")
        return
    result = client.get(f"/notebooks/{notebook_id}")
    print(f"笔记本详情:")
    print(f"  ID: {result['id']}")
    print(f"  名称: {result['name']}")
    print(f"  描述: {result.get('description', '')}")
    print(f"  归档: {result.get('archived', False)}")
    print(f"  创建: {result.get('created', '')}")
    print(f"  来源数: {result.get('source_count', 0)}")
    print(f"  笔记数: {result.get('note_count', 0)}")


def _update(client: "OpenNotebookClient", notebook_id: str, name: str = None, archived: bool = None):
    """更新笔记本"""
    if not notebook_id:
        print("Error: 请提供笔记本 ID")
        return
    data = {}
    if name:
        data["name"] = name
    if archived is not None:
        data["archived"] = archived
    if not data:
        print("Error: 请提供要更新的字段")
        return
    result = client.put(f"/notebooks/{notebook_id}", data)
    print(f"更新成功: {result['id']} - {result['name']}")


def _delete(client: "OpenNotebookClient", notebook_id: str):
    """删除笔记本"""
    if not notebook_id:
        print("Error: 请提供笔记本 ID")
        return
    client.delete(f"/notebooks/{notebook_id}")
    print(f"删除成功: {notebook_id}")