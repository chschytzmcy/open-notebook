---
name: open-notebook-source
version: 1.0.0
description: "管理笔记本中的来源（文件/URL），当用户需要添加内容、查看来源列表时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook source --help"
---

# source

来源是笔记本中的材料（文件、网页等）。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook source list [notebook_id]` | 列出来源 |
| `opennotebook source add <path> [--notebook-id <id>] [--title <title>] [--embed]` | 添加来源（文件或 URL）|
| `opennotebook source get <id>` | 获取来源详情 |
| `opennotebook source delete <id>` | 删除来源 |

## 示例

```bash
# 列出笔记本中的来源
opennotebook source list nb_xxx

# 添加 URL 来源到指定笔记本
opennotebook source add https://example.com/article --notebook-id nb_xxx

# 添加本地文件到指定笔记本
opennotebook source add /path/to/file.pdf --notebook-id nb_xxx

# 创建独立来源（不添加到任何笔记本）
opennotebook source add https://example.com/article
opennotebook source add /path/to/file.pdf

# 指定标题
opennotebook source add https://example.com/article --title "示例文章"

# 嵌入内容用于向量搜索
opennotebook source add https://example.com/article --embed
```