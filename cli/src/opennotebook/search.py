"""Open Notebook CLI - Search 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


def register(parser: argparse.ArgumentParser):
    """注册 search 子命令"""
    sub = parser.add_parser("search", help="搜索内容")
    sub.add_argument("query", help="搜索关键词")
    sub.add_argument("--type", choices=["text", "vector"], default="text", help="搜索类型")
    sub.add_argument("--limit", type=int, default=10, help="结果数量")
    sub.add_argument("--sources", action="store_true", default=True, help="搜索来源")
    sub.add_argument("--notes", action="store_true", default=True, help="搜索笔记")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    _search(client, args.query, args.type, args.limit, args.sources, args.notes)


def _search(
    client: "OpenNotebookClient",
    query: str,
    search_type: str = "text",
    limit: int = 10,
    search_sources: bool = True,
    search_notes: bool = True,
):
    """执行搜索"""
    if not query:
        print("Error: 请提供搜索关键词")
        return

    data = {
        "query": query,
        "type": search_type,
        "limit": limit,
        "search_sources": search_sources,
        "search_notes": search_notes,
    }

    result = client.post("/search", data)
    results = result.get("results", [])
    print(f"找到 {result.get('total_count', len(results))} 条结果:")
    for r in results:
        score = r.get("score", 0)
        source_type = r.get("source_type", r.get("type", "unknown"))
        title = r.get("title", r.get("content", "")[:50])
        print(f"  [{score:.2f}] {source_type}: {title}")