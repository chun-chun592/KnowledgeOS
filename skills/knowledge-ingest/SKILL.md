---
name: knowledge-ingest
description: Compile authorized material through Raw, Source, and Wiki, checking duplication, provenance, and reuse.
---

# 知识摄取 / Knowledge Ingest

按来源标识与内容 SHA-256 查重，复用相同原件和已有来源页。保留原件、出处、证据定位和访问约束，再建立或补充 Source 页。\
Check source identifiers and content SHA-256 for duplicates. Reuse identical originals and existing Source pages. Preserve original bytes, provenance, evidence anchors, and access restrictions, then create or extend the Source page.

查找相关概念、实体或主题，决定引用、补充、更新或新建。证据冲突时保留各方及适用范围，必要时组合 knowledge-research、knowledge-synthesis 或 knowledge-update。每份来源产生多少知识页由内容决定。\
Find related concepts, entities, or topics and decide whether to cite, extend, update, or create. Preserve conflicting evidence and its scope, combining knowledge-research, knowledge-synthesis, or knowledge-update as needed. Let the material determine how many knowledge pages are useful.

检查来源与受影响 Wiki 页的关联，核对文件和来源哈希，按库内协议维护必要的索引及日志。\
Verify links between the source and affected wiki notes and check file and source hashes. Maintain affected index entries and the log under the vault protocol.

按宿主选择 MCP、CLI 或原生工具。真实库沿用获准的原生写入和 Human 提案边界。独立测试根可用 knowledgeos ingest 起草，获准时用 --apply 保存原件与来源页；Strict 专用字段仅适用于已启用的严格合成模式。\
Choose MCP, CLI, or native tools according to the host. Follow approved native writes and the Human proposal boundary in the real vault. In a separate test root, knowledgeos ingest can draft a Source page, and --apply saves it and the original when authorized. Strict-specific fields apply only in enabled synthetic Strict mode.

从目标库的 AGENTS.md 和现行规范确认目录语言，使用该库实际的相对路径。目录语言不限定笔记正文语言。\
Confirm the layout using the target vault’s AGENTS.md and current rules. Use its actual relative paths. Directory language does not constrain note content.
