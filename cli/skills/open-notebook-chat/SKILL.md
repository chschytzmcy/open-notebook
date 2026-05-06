---
name: open-notebook-chat
version: 1.0.0
description: "与笔记本对话，当用户需要询问笔记本内容、获取 AI 总结时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook chat --help"
---

# chat

与笔记本中的材料进行 AI 对话。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook chat <notebook_id> <message>` | 发送消息 |

## 示例

```bash
# 询问笔记本
opennotebook chat nb_xxx "总结主要内容"

# 详细提问
opennotebook chat nb_xxx "第三点详细解释"
```