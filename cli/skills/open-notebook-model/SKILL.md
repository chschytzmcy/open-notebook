---
name: open-notebook-model
version: 1.0.0
description: "管理 AI 模型，当用户需要查看已配置模型时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook model --help"
---

# model

管理 AI 模型配置。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook model list` | 列出模型 |

## 示例

```bash
# 列出所有模型
opennotebook model list
```