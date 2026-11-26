---
name: knowledge-ingest
description: Classify authorized source material, check overlap, and prepare an attributed KnowledgeOS note.
---

# 知识摄取 / Knowledge Ingest

只读取获准来源。用可用的 MCP、CLI 或原生工具查重，保留标题、原件出处和相关笔记引用；优先补充现有主题。\
Read only approved sources. Use available MCP, CLI, or native tools to check overlap, retain title, provenance, and related links, and prefer an existing topic.

真实库 Agent 写入使用获准的原生编辑协议；Human 变更只交付提案。独立测试根可用 knowledgeos ingest 起草来源页，明确获准后才加 --apply 保存原件与来源页。\
Use approved native edits for real-vault Agent writes and proposals for Human notes. In a separate test root, knowledgeos ingest drafts a source page. Add --apply only with approval to preserve the original and write the source page.

核对文件及来源哈希，更新允许的索引和日志。仅已启用的严格合成模式使用 submit_knowledge、幂等键和 COMMITTED 核验。\
Verify the resulting file and source digest and update approved indexes and logs. Only enabled synthetic Strict mode uses submit_knowledge, an idempotency key, and COMMITTED verification.

按来源标识及内容哈希查重；保留原件，并将来源页关联到受影响的 Wiki 页面。按当前库协议复核索引和日志。\
Check source identifiers and content digests for duplicates. Preserve originals and link their source pages to the affected wiki notes. Verify the index and log under the current vault protocol.
