---
name: open-notebook-notebook
version: 1.0.0
description: "管理笔记本，当用户需要列出笔记本、创建笔记本、查看笔记本详情时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook notebook --help"
---

# notebook

笔记本是笔记材料的容器。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook notebook list` | 列出所有笔记本 |
| `opennotebook notebook create <name>` | 创建笔记本 |
| `opennotebook notebook get <id>` | 获取笔记本详情 |
| `opennotebook notebook update <id>` | 更新笔记本 |
| `opennotebook notebook delete <id>` | 删除笔记本 |

## 示例

```bash
# 列出笔记本
opennotebook notebook list

# 创建新笔记本
opennotebook notebook create "AI 研究"

# 获取详情
opennotebook notebook get nb_xxx
```