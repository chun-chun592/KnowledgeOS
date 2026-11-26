---
name: knowledge-maintenance
description: Maintain Agent links, indexes, logs and approved recovery within the configured KnowledgeOS mode.
---

# 知识维护 / Knowledge Maintenance

根据宿主选择 MCP、CLI 或原生工具做只读链接、引用和元数据检查。区分范围外不可见和已确认失效，Human 修复只交付提案。\
Select MCP, CLI, or native tools for read-only checks of links, references, and metadata. Distinguish out-of-scope targets from confirmed breakage. Human repairs remain proposals.

真实库按现有协议使用租约、哈希及备份，定点修改 Agent 索引或日志。遵循现有归档规则，真实库不使用测试根删除、恢复或全量同步工具。\
Follow real-vault leases, hashes, backups and targeted Agent index or log edits. Follow the vault archive policy. Real-vault maintenance does not use test-root delete, restore, or full sync tools.

独立 Native 测试根可以使用 native_note_change 或 knowledgeos restore 按备份哈希恢复，用 sync_native_wiki 或 knowledgeos sync 发现外部改动并重建托管区块。\
In a separate Native test root, use native_note_change or knowledgeos restore with a backup hash. Use sync_native_wiki or knowledgeos sync to observe external changes and rebuild managed blocks.

可选严格模式独立使用 knowledge_audit、文件身份及事务键，派生文件待修复时用 sync_agent_wiki 或 Broker CLI 的 sync_wiki。\
Optional Strict mode uses knowledge_audit, file identity, and transaction keys. For pending projections, use sync_agent_wiki or the Broker CLI sync_wiki operation.
