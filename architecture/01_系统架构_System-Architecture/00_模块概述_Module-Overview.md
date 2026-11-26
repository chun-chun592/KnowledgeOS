# 系统架构 / System Architecture

[返回正式架构 / Architecture entry point](../README.md)

## 组件 / Components

宿主从 Skills 选择工作流。MCP 入口 `knowledgeos-mcp` 及 CLI `knowledgeos` 复用 Vault 范围读取、Schema 解析和链接图；Human 通过任意工具直接维护自己的文件。\
The host selects a workflow from Skills. The `knowledgeos-mcp` and `knowledgeos` commands reuse scoped Vault reading, schema parsing, and link graphs. Humans maintain their files with any editor.

## 日常数据流 / Daily Data Flow

自然语言任务 → 查重及读取 → 综合或变更提案 → 获准的 Agent 原生编辑或 Human 手工应用 → 重读核验 → 定点索引与日志。真实库 MCP／CLI 直写关闭。\
Natural-language task → overlap check and reads → synthesis or proposal → approved Agent native edit or manual Human application → reread and verify → targeted index and log updates. Real-vault MCP and CLI writes are closed.

## 独立写入面 / Separate Write Paths

`markdown_native.py` 在独立测试根中执行本地写入与同步。可选严格模式另由认证 IPC、Broker、Writer 和 SQLite 完成合成提交。两种写路径互斥配置，无后台服务或 Obsidian 启动依赖用于日常模式。\
`markdown_native.py` handles local writes and sync in a separate test root. Optional Strict mode uses authenticated IPC, Broker, Writer, and SQLite for synthetic transactions. The write modes are mutually exclusive in server configuration. Daily use requires neither background services nor Obsidian.
