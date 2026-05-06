"""Open Notebook CLI - Note 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


def register(parser: argparse.ArgumentParser):
    """注册 note 子命令"""
    sub = parser.add_parser("note", help="笔记管理")
    sub.add_argument("action", choices=["list", "create", "get", "update", "delete"], help="操作")
    sub.add_argument("source_id", nargs="?", help="来源 ID")
    sub.add_argument("id_or_title", nargs="?", help="笔记 ID 或标题")
    sub.add_argument("--content", help="笔记内容")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    action = args.action
    if action == "list":
        _list(client, args.source_id)
    elif action == "create":
        _create(client, args.source_id, args.id_or_title, args.content)
    elif action == "get":
        _get(client, args.id_or_title)
    elif action == "update":
        _update(client, args.id_or_title, args.content)
    elif action == "delete":
        _delete(client, args.id_or_title)


def _list(client: "OpenNotebookClient", source_id: str = None):
    """列出笔记"""
    if not source_id:
        result = client.get("/notes")
    else:
        result = client.get(f"/sources/{source_id}/notes")
    notes = result if isinstance(result, list) else []
    print(f"找到 {len(notes)} 条笔记:")
    for n in notes:
        note_type = n.get("note_type", "unknown")
        content = n.get("content", "")[:50]
        print(f"  {n['id']} - [{note_type}] {n.get('title', 'Untitled')}")
        print(f"    {content}...")


def _create(client: "OpenNotebookClient", source_id: str, title: str, content: str = None):
    """创建笔记"""
    if not source_id or not title:
        print("Error: 请提供来源 ID 和标题")
        return
    data = {"title": title, "note_type": "human"}
    if content:
        data["content"] = content
    result = client.post(f"/sources/{source_id}/notes", data)
    print(f"创建成功: {result['id']} - {result['title']}")


def _get(client: "OpenNotebookClient", note_id: str):
    """获取笔记详情"""
    if not note_id:
        print("Error: 请提供笔记 ID")
        return
    result = client.get(f"/notes/{note_id}")
    print(f"笔记详情:")
    print(f"  ID: {result['id']}")
    print(f"  标题: {result.get('title', 'N/A')}")
    print(f"  类型: {result.get('note_type', 'unknown')}")
    print(f"  内容: {result.get('content', '')[:200]}...")


def _update(client: "OpenNotebookClient", note_id: str, content: str = None):
    """更新笔记"""
    if not note_id:
        print("Error: 请提供笔记 ID")
        return
    data = {}
    if content:
        data["content"] = content
    if not data:
        print("Error: 请提供要更新的内容")
        return
    result = client.put(f"/notes/{note_id}", data)
    print(f"更新成功: {result['id']} - {result.get('title', '')}")


def _delete(client: "OpenNotebookClient", note_id: str):
    """删除笔记"""
    if not note_id:
        print("Error: 请提供笔记 ID")
        return
    client.delete(f"/notes/{note_id}")
    print(f"删除成功: {note_id}")