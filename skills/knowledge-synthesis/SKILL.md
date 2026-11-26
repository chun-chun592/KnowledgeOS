---
name: knowledge-synthesis
description: Synthesize scoped notes and evidence across KnowledgeOS regions.
---

# knowledge-synthesis

Check source independence, agreements and conflicts. Propose revisions to existing Shared conclusions.

先读目标库 AGENTS.md 和归属规则。按知识任务发现并组合所需 Skills。使用宿主已配置的根路径，遵循 en-US、zh-CN 或 zh-en 的实际相对路径。按需选用 MCP、CLI 或原生文件工具。
Read the vault entry and ownership rules. Use the configured vault root, actual localized paths, and available tools. No tool is mandatory.

Agent 私有知识按所属范围自主维护。公共知识只自主新建及追加该条目的索引、日志。已有公共知识与 Human 私有变更需当前可信交互中的具体批准。核对范围、操作、原始哈希或不存在状态、准确内容及冲突；用原生工具获准执行。无法确认或执行时交付完整手工提案。
Maintain assigned Agent knowledge autonomously. Shared creation may append its index and log entries. Changes to existing Shared or Human private knowledge require exact approval from the current trusted interaction. Check scope, operation, base hash or absence, exact content and conflicts; use permitted native tools. Fall back to a full manual proposal when confirmation or execution is unavailable.

保留可追溯来源、写前备份及租约，写后重读并记日志。用自动反链。读取私有资料的许可与共享许可分别核对。真实库 MCP 和 CLI 保持只读。独立测试根可用现有 Native 命令，Strict Mode 保持可选。
Preserve traceable sources, leases and backups. Verify writes and append audit events. Use computed backlinks. Check private read and sharing grants independently. Real-vault MCP and CLI are read-only. Native test-root tools and optional Strict Mode stay separate.
