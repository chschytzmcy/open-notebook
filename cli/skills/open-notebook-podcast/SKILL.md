---
name: open-notebook-podcast
version: 1.0.0
description: "生成 AI 播客，当用户需要将研究材料转换为播客时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook podcast --help"
---

# podcast

将笔记本内容转换为 AI 播客。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook podcast list [notebook_id]` | 列出播客 |
| `opennotebook podcast create <notebook_id>` | 创建播客 |
| `opennotebook podcast get <id>` | 获取播客详情 |
| `opennotebook podcast retry <id>` | 重试失败的任务 |

## 示例

```bash
# 创建播客
opennotebook podcast create nb_xxx

# 查看详情
opennotebook podcast get ep_xxx
```