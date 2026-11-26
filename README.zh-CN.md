# KnowledgeOS

[English](README.md)

KnowledgeOS 帮助你和 Agent 把已有笔记与来源材料整理成可复用的知识。它使用同一个 Markdown 文件夹。你可以用任意编辑器或文件管理器打开笔记，Obsidian 可按需使用。

## 可以做什么

- 检索相关笔记，跟踪引用，并在新建前检查内容重叠。
- 概括新来源，将其与已有知识综合，并保留引用和元数据来更新原笔记。
- 维护 Agent 索引和操作日志，使用哈希检查冲突、从备份恢复旧内容。
- 为 Human 笔记生成完整 Markdown、统一 diff 和基础 SHA-256。

Markdown 是知识的唯一事实来源。Human 和 Agent 是逻辑知识主体。Human 直接编辑自己的笔记；Agent 读取明确开放的 Human 范围，并在获准的 Agent 范围内写入。Human 提案由本人核对基础哈希后手工应用。

## 接入现有知识文件夹

1. 安装 Python 3.11 或更新版本，在项目目录执行 `python -m pip install -r requirements.txt`。
2. 使用已经包含 `10_Agent/wiki` 的目录，保持原结构，并先读取库内 `AGENTS.md` 及其引用规则。
3. 配置下列任一工具入口，然后直接用自然语言提问。

MCP 默认只读：

```text
python -B server.py --vault <vault-root>
```

已批准读取 Human 子目录时，可追加 `--human-read 00_Human/Resources` 或实际批准的精确相对路径。默认不加 Human 读取范围。只有 CLI 的宿主可将下面的 JSON 传入 `python write_client.py --vault <vault-root> inspect` 的标准输入。

```json
{"tool":"search_knowledge","arguments":{"query":"MCP"}}
```

## 接入 Agent 宿主

使用已安装依赖的 Python 注册本地 **stdio** MCP 服务，将 `-B <project>/server.py --vault <vault-root>` 分别作为参数传入。本机路径仅写入本地配置。用宿主支持的 Skills 发现机制开放所需的 `skills/<name>/SKILL.md`。Agent 可按任务选择或组合 Skills，并按环境选择 MCP、CLI 或原生文件工具。

| 宿主 | 配置入口 |
| --- | --- |
| Codex | 在项目 Codex 配置中添加带 `command` 和 `args` 的 `[mcp_servers.knowledgeos]`。 [MCP 指南](https://developers.openai.com/codex/mcp) |
| OpenCode | 在适用于所用版本的 OpenCode 项目配置中注册本地服务。 [MCP 指南](https://opencode.ai/docs/mcp-servers/) |
| Claude Code | 使用 `claude mcp add` 注册本地 stdio 服务并选择合适的配置范围。 [MCP 指南](https://code.claude.com/docs/en/mcp) |

可直接问：“查找这个主题已有哪些笔记，指出重复内容”“把这些来源补充进现有 Agent 笔记并保留引用”或“为这篇 Human 笔记起草修改建议并显示 diff”。

## 日常写入与限制

**Markdown Native 是日常推荐方式。** 真实库当前通过获准的原生文件编辑维护 Agent Wiki，遵循库内租约、备份、SHA-256、索引和日志规则。MCP 和 CLI 尚未开放真实库直接写入。原生编辑及文件观察不会生成严格 Writer 的 SQLite 提交记录。这些边界属于应用层治理。

在**单独获准的测试根目录**，先将 `KNOWLEDGEOS_PROTECTED_VAULT` 设为真实受保护库路径，再使用 `python markdown_native.py --vault <test-root> sync` 或以 `--native-write` 启动 MCP。测试根的创建、更新、删除与恢复遵循范围约束。外部编辑可在后续同步时发现，并可能与其他编辑器并发。

### 高级选项：严格模式

严格模式使用独立 Windows 主体、Broker、Secure Writer 和 SQLite，需要 `pywin32`、可信合成部署、受保护根配置以及预先配置的身份和 ACL。在该环境中以 `--synthetic-write-config` 启动服务。Publisher 保持禁用。 [架构说明](docs/Architecture.md)

## 项目与来源

项目尚待 GitHub 发布。附带的 Core 模块来自 KnowledgeOS Agent Kit，保留上游 MIT 许可证。 [上游许可证](knowledgeos/LICENSE)
