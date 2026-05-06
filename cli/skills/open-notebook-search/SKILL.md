---
name: open-notebook-search
version: 1.0.0
description: "搜索笔记本内容，当用户需要查找研究材料时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook search --help"
---

# search

搜索笔记本中的来源和笔记。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook search <query>` | 搜索内容 |

## 示例

```bash
# 文本搜索
opennotebook search "机器学习"

# 向量搜索
opennotebook search "深度学习" --type vector
```