"""Open Notebook CLI - Chat 子命令"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opennotebook.client import OpenNotebookClient


_chat_parser = None


def register(parser: argparse.ArgumentParser):
    """注册 chat 子命令"""
    global _chat_parser
    sub = parser.add_parser("chat", help="与笔记本对话")
    _chat_parser = sub
    sub.add_argument("notebook_id", nargs="?", default=None, help="笔记本 ID")
    sub.add_argument("message", nargs="?", default=None, help="对话消息")
    sub.add_argument("--model", help="指定模型")
    sub.set_defaults(handler=lambda a, c: _handle(a, c))


def _handle(args: argparse.Namespace, client: "OpenNotebookClient"):
    if args.notebook_id is None or args.message is None:
        _chat_parser.print_help()
        return
    _chat(client, args.notebook_id, args.message, args.model)


def _chat(client: "OpenNotebookClient", notebook_id: str, message: str, model: str = None):
    """发送聊天消息"""
    if not notebook_id or not message:
        print("Error: 请提供笔记本 ID 和消息")
        return

    data = {
        "notebook_id": notebook_id,
        "message": message,
    }
    if model:
        data["model_override"] = model

    result = client.post("/chat", data)
    print(f"回复:")
    print(result.get("response", result.get("message", str(result))))