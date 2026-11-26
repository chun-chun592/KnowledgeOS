---
name: knowledge-update
description: Update an Agent note or prepare a manually applied Human proposal.
---

# 知识更新 / Knowledge Update

在获准范围内读取现有笔记、基线 SHA-256 和相关来源。用宿主可用的 MCP、CLI 或原生文件工具查重，保留出处、有效历史和原创建者。\
Read the note, base SHA-256, and relevant sources within approved scopes. Check overlap using the available MCP, CLI, or native tools. Preserve sources, useful history, and original authorship.

Human 目标只生成提案。可用 propose_human_update，也可用本地工具从同一基线生成完整 Markdown 和统一 diff。附目标、基础哈希、修改理由和来源，由 Human 用任意编辑器应用。\
For Human targets, prepare a proposal using propose_human_update or local tools against the same base. Include complete Markdown, a unified diff, the target, base hash, rationale, and sources. The Human applies it with any editor.

真实 Agent Wiki 按库内协议原生编辑：锁定共享文件，备份基线，写前复核 SHA-256，写后重读并定点更新索引及追加日志。真实库不调用 MCP／CLI 写入或测试根全量同步。\
For real Agent wiki edits, follow local rules: acquire shared leases, back up and recheck the base, reread the result, update relevant index entries, and append the log. Real-vault edits do not use MCP or CLI write tools or test-root full sync.

独立 Native 测试根可用 native_note_change 或 knowledgeos update／append-section。使用内容哈希核验变更，NATIVE_SYNC_PENDING 时先重读再同步。\
In a separate Native test root, use native_note_change or knowledgeos update or append-section. Verify the content hash. Reread before syncing when the result is NATIVE_SYNC_PENDING.

只在可选且可用的严格合成模式中提交已验证文件身份及原幂等键；以 COMMITTED 核验提交，OUTCOME_UNKNOWN 先查询原键。\
Only available synthetic Strict mode uses verified file identity and idempotency keys. Confirm COMMITTED; after OUTCOME_UNKNOWN query the original key.

使用当前模式允许的工具。真实库获准的 Agent 修改须检查租约和基础 SHA-256，保留备份及历史来源，复核后定点同步。Human 变更以完整 Markdown 和 diff 交付。\
Use tools permitted by the current mode. For approved real-vault Agent edits, check the lease and base SHA-256, preserve backups and provenance, and verify before targeted synchronization. Deliver Human changes as complete Markdown and a diff.
