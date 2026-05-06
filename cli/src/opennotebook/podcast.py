"""Open Notebook CLI - Podcast 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


_podcast_parser = None


def register(parser: argparse.ArgumentParser):
    """注册 podcast 子命令"""
    global _podcast_parser
    sub = parser.add_parser("podcast", help="播客生成")
    _podcast_parser = sub
    sub.add_argument("action", choices=["list", "create", "get", "retry"],
                     nargs="?", default=None, help="操作 (留空显示帮助)")
    sub.add_argument("notebook_id", nargs="?", help="笔记本 ID")
    sub.add_argument("episode_id", nargs="?", help="剧集 ID")
    sub.add_argument("--title", help="播客标题")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    action = args.action
    if action is None:
        _podcast_parser.print_help()
        return
    if action == "list":
        _list(client, args.notebook_id)
    elif action == "create":
        _create(client, args.notebook_id, args.title)
    elif action == "get":
        _get(client, args.episode_id or args.notebook_id)
    elif action == "retry":
        _retry(client, args.episode_id or args.notebook_id)


def _list(client: "OpenNotebookClient", notebook_id: str = None):
    """列出播客"""
    if notebook_id:
        result = client.get(f"/notebooks/{notebook_id}/podcasts")
    else:
        result = client.get("/podcasts")
    podcasts = result if isinstance(result, list) else []
    print(f"找到 {len(podcasts)} 个播客:")
    for p in podcasts:
        print(f"  {p['id']} - {p.get('title', 'Untitled')}")


def _create(client: "OpenNotebookClient", notebook_id: str, title: str = None):
    """创建播客"""
    if not notebook_id:
        print("Error: 请提供笔记本 ID")
        return
    data = {}
    if title:
        data["title"] = title
    result = client.post(f"/notebooks/{notebook_id}/podcasts", data)
    print(f"创建成功: {result['id']}")
    print(f"状态: {result.get('status', 'pending')}")


def _get(client: "OpenNotebookClient", episode_id: str):
    """获取播客详情"""
    if not episode_id:
        print("Error: 请提供剧集 ID")
        return
    result = client.get(f"/podcasts/episodes/{episode_id}")
    print(f"剧集详情:")
    print(f"  ID: {result['id']}")
    print(f"  标题: {result.get('title', 'N/A')}")
    print(f"  状态: {result.get('status', 'unknown')}")
    if result.get("audio_url"):
        print(f"  音频: {result['audio_url']}")


def _retry(client: "OpenNotebookClient", episode_id: str):
    """重试播客生成"""
    if not episode_id:
        print("Error: 请提供剧集 ID")
        return
    result = client.post(f"/podcasts/episodes/{episode_id}/retry", {})
    print(f"重试成功: {result['id']}")
    print(f"新状态: {result.get('status', 'pending')}")