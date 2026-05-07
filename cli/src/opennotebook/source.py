"""Open Notebook CLI - Source 子命令"""

import argparse
import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


_source_parser = None


def register(parser: argparse.ArgumentParser):
    """注册 source 子命令"""
    global _source_parser
    sub = parser.add_parser("source", help="来源管理 (文件/URL)")
    _source_parser = sub
    sub.add_argument("action", choices=["list", "add", "get", "delete"],
                     nargs="?", default=None, help="操作 (留空显示帮助)")
    sub.add_argument("path", nargs="?", help="文件路径或 URL")
    sub.add_argument("--notebook-id", dest="notebook_id", default=None, help="笔记本 ID（可选，不指定则创建独立来源）")
    sub.add_argument("--title", dest="title", default=None, help="来源标题（可选）")
    sub.add_argument("--embed", dest="embed", action="store_true", help="嵌入内容用于向量搜索")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    action = args.action
    if action is None:
        _source_parser.print_help()
        return
    if action == "list":
        _list(client, args.notebook_id)
    elif action == "add":
        _add(client, args.notebook_id, args.path, args.title, args.embed)
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


def _add(client: "OpenNotebookClient", notebook_id: str, path: str, title: str = None, embed: bool = False):
    """添加来源"""
    if not path:
        print("Error: 请提供文件路径或 URL")
        return

    # 判断是 URL 还是文件
    is_url = path.startswith("http://") or path.startswith("https://")
    if is_url:
        data = {
            "type": "link",
            "url": path,
        }
        result = client.post("/sources/json", data)
        print(f"添加成功: {result['id']} - {result.get('title', path)}")
        print(f"处理命令: {result.get('command_id', 'N/A')}")
        return

    # 文件上传 - 使用 FormData 方式
    if not os.path.exists(path):
        print(f"Error: 文件不存在: {path}")
        return

    file_size = os.path.getsize(path)
    print(f"上传文件: {path} ({file_size / 1024:.1f} KB)")

    with open(path, "rb") as f:
        file_content = f.read()

    data = {
        "type": "upload",
        "embed": "true" if embed else "false",
        "async_processing": "true",
    }
    if notebook_id:
        data["notebooks"] = json.dumps([notebook_id])
    if title:
        data["title"] = title

    files = {
        "file": (os.path.basename(path), file_content, "application/octet-stream"),
    }

    result = client.post_formdata("/sources", data=data, files=files)
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