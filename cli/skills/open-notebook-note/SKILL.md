---
name: open-notebook-note
version: 1.0.0
description: "管理笔记，当用户需要创建笔记、查看笔记内容时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook note --help"
---

# note

笔记是用户在笔记本中创建的内容。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook note list [source_id]` | 列出笔记 |
| `opennotebook note create <source_id> <title>` | 创建笔记 |
| `opennotebook note get <id>` | 获取笔记详情 |
| `opennotebook note update <id>` | 更新笔记 |
| `opennotebook note delete <id>` | 删除笔记 |

## 示例

```bash
# 列出笔记
opennotebook note list src_xxx

# 创建笔记
opennotebook note create src_xxx "重要发现"

# 查看笔记
opennotebook note get note_xxx
```