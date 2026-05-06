# Open Notebook CLI

命令行工具，用于管理 Open Notebook 研究笔记本。

## 构建

```bash
make build
```

构建产物：`dist/opennotebook/`

## 安装

```bash
make install
```

安装到：`~/.local/bin/opennotebook`

## 测试

```bash
make test
# 或
./dist/opennotebook/opennotebook --help
```

## 使用

```bash
# 笔记本管理
opennotebook notebook list
opennotebook notebook create "我的笔记本"
opennotebook notebook get <id>

# 来源管理
opennotebook source list <notebook_id>
opennotebook source add <notebook_id> <path_or_url>

# 笔记管理
opennotebook note list <source_id>
opennotebook note create <source_id> <title>

# 对话
opennotebook chat <notebook_id> "问题内容"

# 播客
opennotebook podcast list
opennotebook podcast create <notebook_id>

# 搜索
opennotebook search "关键词"

# 凭证
opennotebook credential list

# 模型
opennotebook model list
```

## 默认值

- API 地址：`http://localhost:5055`
- 认证密码：`open-notebook-change-me`

可通过环境变量覆盖：
```bash
export OPEN_NOTEBOOK_SERVER=http://localhost:5055
export OPEN_NOTEBOOK_PASSWORD=your-password
```