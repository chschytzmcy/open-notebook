---
name: open-notebook-credential
version: 1.0.0
description: "管理 AI 凭证，当用户需要配置 API Key、测试连接时使用"
metadata:
  requires:
    bins: ["opennotebook"]
  cliHelp: "opennotebook credential --help"
---

# credential

管理 AI 提供商的 API 凭证。

## 命令列表

| 命令 | 说明 |
|------|------|
| `opennotebook credential list` | 列出凭证 |
| `opennotebook credential create --name <name> --provider <p>` | 创建凭证 |
| `opennotebook credential test <id>` | 测试连接 |
| `opennotebook credential delete <id>` | 删除凭证 |

## 示例

```bash
# 列出凭证
opennotebook credential list

# 创建 OpenAI 凭证
opennotebook credential create --name my-openai --provider openai

# 测试
opennotebook credential test cred_xxx
```