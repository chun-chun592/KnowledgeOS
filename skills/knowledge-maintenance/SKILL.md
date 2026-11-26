---
name: knowledge-maintenance
description: Maintain the Agent wiki by checking references, reviewing committed transactions, or deleting and restoring specific Agent notes through the configured KnowledgeOS tools.
---

# 知识维护 / Knowledge Maintenance

在原生模式下，使用 native_note_change 或 markdown_native.py 执行 Agent 范围恢复；用 sync_native_wiki 或 CLI sync 发现外部改动、重建索引及日志。\
In Native mode, use native_note_change or markdown_native.py for Agent-scope restoration. Use sync_native_wiki or CLI sync to discover external edits and rebuild the index and log.

先用 `lint_knowledge` 查找问题，再用 `knowledge_links` 核对目标笔记、反向链接和歧义引用。\
Use `lint_knowledge` to find issues, then use `knowledge_links` to check targets, backlinks, and ambiguous references.

修改链接时先读取涉及的笔记；只提交已明确请求的 Agent 区变更，Human 区变更交付完整 Markdown 和 diff。\
Read the affected notes before editing links, submit only requested Agent changes, and deliver complete Markdown and a diff for Human changes.

删除须指定单篇 Agent 笔记，并使用同一次读取返回的文件身份和 SHA-256；恢复须引用已提交的删除事务并检查原路径为空。\
Deletion requires one specific Agent note and the identity and SHA-256 from the same read. Restoration requires the committed deletion transaction and a vacant original path.

使用已连接的 MCP，或在配置了 Broker CLI 的脚本环境中选择 CLI；保留原幂等键并核对提交状态。\
Use the connected MCP or choose the Broker CLI in a configured scripting environment. Preserve the original idempotency key and verify the transaction status.

用 `knowledge_audit` 或 Broker CLI 的 `audit` 查看已提交的 Agent 事务；派生文件显示 `SYNC_PENDING`、需要重建或有失效条目时，调用 `sync_agent_wiki` 或 CLI 的 `sync_wiki`。\
Use `knowledge_audit` or the Broker CLI's `audit` to review committed Agent transactions. Use `sync_agent_wiki` or CLI `sync_wiki` after `SYNC_PENDING`, to rebuild, or to remove stale entries.
